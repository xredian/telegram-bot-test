# Telegram Bot Common Channels

This is a Telegram Bot that allows you to know about users with common channels. 
This allows you to know about the intersection of common channels.

# Getting Started

```
git clone git@github.com:xredian/telegram-bot-test.git
```

# Creating .env

Before installation you need to create **.env** file as in an example below.

```
# token for telegram bot
TOKEN=your-bot-token

# api_id and api_hash for telegram client
API_ID=123456
API_HASH=1234567890
```

# Installation

Create Docker build for bot.
```
docker build -t app-tg-bot -f Dockerfile_bot .
```
Create Docker build for client.
```
docker build -t app-tg-client -f Dockerfile_client .
```

# Creating virtual environment
```
docker-compose up 
```

# Usage

After starting the bot, write the usernames of the channels to which you have access **separated by commas**. 
Then the bot will return you a json file with the result.

## Authors

* **Uliana Diakova** - *Test project* - [xredian](https://github.com/xredian)

