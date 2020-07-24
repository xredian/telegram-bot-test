from dotenv import load_dotenv
import logging
import json
import os
import pickle
import redis
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, Handler)
from telegram import (ReplyKeyboardMarkup)
import telegram
import time
import timer


load_dotenv()

# telegram bot token
bot_token = os.getenv("TOKEN")
bot = telegram.Bot(token=bot_token)

# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")


# We have to manually call "start" if we want an explicit bot token


def start(bot_token, update):
    reply_keyboard = [['/start', '/help']]
    update.message.reply_text(
        "Hi, i can show users with the same channels :)", reply_markup=ReplyKeyboardMarkup(reply_keyboard))


def help(bot_token, update):
    update.message.reply_text(
        "Hey, you can choose some channels, so I'll show you all users who follows at least two of them. Enjoy :)")


def echo(bot_token, update):
    update.message.reply_text("I don't understand you. Please press button /start, /help or wait for answer "
                              "if you've already choose the channels")
    logger.info(update)


r = redis.Redis(host='localhost', port=6379, db=0)
reply_n = ''


def choose(bot_token, update):
    text = str(update.message.text)
    update.message.reply_text("Data collection in progress, please wait...")
    urls = text.split(', ')
    r.set('urls', str(urls))
    global chat_id
    chat_id = update.message.chat_id


def result(bot_token, reply):
    msg = ''
    for key in reply:
        print('json writing started...')
        msg = msg + key + ' - ' + str((str(reply[key])[2:-2]).split("', '")) + '\n'
    with open(''.join(str(r.get('urls').decode('utf-8'))) + '.json', 'w', encoding='utf8') as outfile:
        json.dump(msg, outfile, ensure_ascii=False)
    file = open(''.join(str(r.get('urls').decode('utf-8'))) + '.json', 'rb')
    bot.send_document(chat_id=chat_id, document=file)
    file.close()


def error(bot_token, update, error):
    logger.warning('Update "{u}" caused error "{e}"'.format(u=update, e=error))


def main():
    updater = Updater(bot_token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(MessageHandler(Filters.text, choose))
    dp.add_handler(MessageHandler(not Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


def check_for_updates():
    while True:
        global reply_n
        new_reply = r.get('result')
        try:
            new_reply = pickle.loads(new_reply)
            if new_reply != reply_n and new_reply != '':
                r.delete('result')
                return result(bot_token, new_reply)
            else:
                time.sleep(1)
            reply_n = new_reply
            time.sleep(5)
        except TypeError:
            print('waiting for update...')
            time.sleep(5)
        trouble = r.get('trouble').decode('utf-8')
        if trouble == "Sorry, I don't understand, please, make sure you type chat names correctly":
            bot.send_message(chat_id=chat_id, text=trouble)
        r.delete('trouble')
        time.sleep(3)


rt = timer.RepeatedTimer(5, check_for_updates)  # it auto-starts, no need of rt.start()
try:
    # your long-running job goes here...
    if __name__ == '__main__':
        main()
finally:
    rt.stop()
