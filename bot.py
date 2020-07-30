from dotenv import load_dotenv
import logging
import os
import pickle
import redis
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)
from telegram import (ReplyKeyboardMarkup)
import telegram
import time
import timer
import re


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


def start(update, context):
    reply_keyboard = [['/start', '/help']]
    update.message.reply_text(
        "Hi, i can show users with the same channels - type their names separated by commas :)",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    logger.info(update)


def help(update, context):
    update.message.reply_text(
        "Hey, you can choose some channels, so I'll show you all users who follows at least two of them. Enjoy :)")


r = redis.StrictRedis(host='redis', port=6379, db=0)
reply_n = ''


def choose(update, context):
    text = str(update.message.text)
    update.message.reply_text("Data collection in progress, please wait...")
    urls = text.split(',')
    r.set('urls', str(urls))
    global chat_id
    chat_id = update.message.chat_id


def result(reply):
    msg = ''
    for key in reply:
        print('txt writing started...')
        msg = ''.join((msg, key, ' - ', re.sub(r"[[\]']", "", str(reply[key])), '\n'))
    with open(''.join(re.sub(r"[[\]']", "", str(r.get('urls').decode('utf-8')))) + '.txt', 'w', encoding='utf8') as outfile:
        outfile.writelines(msg)
    file = open(''.join(re.sub(r"[[\]']", "", str(r.get('urls').decode('utf-8')))) + '.txt', 'rb')
    r.delete('urls')
    r.delete('result')
    bot.send_document(chat_id=chat_id, document=file)
    file.close()


def error(bot_token, update, error):
    logger.warning('Update "{u}" caused error "{e}"'.format(u=update, e=error))


def main():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(MessageHandler(Filters.text, choose))

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
                time.sleep(2)
                return result(new_reply)
            else:
                time.sleep(1)
            reply_n = new_reply
            time.sleep(5)
        except TypeError:
            print('waiting for update...')
            time.sleep(5)
        try:
            trouble = r.get('trouble').decode('utf-8')
            if trouble == "Sorry, I don't understand, please, make sure you type chat names correctly":
                bot.send_message(chat_id=chat_id, text=trouble)
            r.delete('trouble')
            time.sleep(3)
        except AttributeError:
            print('waiting for update...')
            time.sleep(5)


rt = timer.RepeatedTimer(5, check_for_updates)  # it auto-starts, no need of rt.start()
#rt.stop()

if __name__ == '__main__':
    main()
