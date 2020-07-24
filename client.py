from collections import defaultdict
from dotenv import load_dotenv
import os
import pickle
import redis
from telethon import TelegramClient
import time


load_dotenv()

# telegram bot token
bot_token = os.getenv("TOKEN")

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
username = os.getenv("USERNAME")


bot = TelegramClient(username, api_id, api_hash).start(bot_token=bot_token)
r = redis.Redis(host='localhost', port=6379, db=0)
urls = ''


async def dump_all_participants(channel):
    print('dump collection started...')
    all_participants = []
    participants = await bot.get_participants(channel)
    for participant in participants:
        if participant.username is not None:
            all_participants.append(participant.username)
    return all_participants


def compare(dumps):
    global result
    result = defaultdict(list)
    for dump in dumps:
        for person in dumps[dump]:
            if person in dumps[dump]:
                result[person].append(dump)
    result_c = result.copy()
    for key in result_c:
        if len(result[key]) < 2:
            result.pop(key)
    p_mydict = pickle.dumps(result)
    r.set('result', p_mydict)
    return result


async def main():
    while True:
        print('updating...')
        global urls
        dumps = dict.fromkeys(urls[2:-2].split("', '"))
        new_urls = r.get('urls').decode("utf-8")
        if new_urls != urls and new_urls != '' and urls != '':
            urls = urls[2:-2].split("', '")
            try:
                for url in urls:
                    channel = await bot.get_entity(url)
                    dump = await dump_all_participants(channel)
                    dumps[url] = dump
                res = compare(dumps)
            except ValueError:
                sorry = "Sorry, I don't understand, please, make sure you type chat names correctly"
                r.set('trouble', sorry)
        else:
            time.sleep(2)
        urls = new_urls


with bot:
    bot.loop.run_until_complete(main())

