from twitterbot.bot import TwitterBot
import logging
import json


if __name__ == "__main__":
    logging.basicConfig(filename='twitterbot.log', level=logging.DEBUG)

    with open('settings.json') as data_file:
        settings = json.load(data_file)

    bot = TwitterBot(settings)
    bot.run(block=True)

    bot.twitter.stream.disconnect()
    exit()
