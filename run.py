from twitterbot.bot import TwitterBot
import logging
import json
from setproctitle import setproctitle


if __name__ == "__main__":
    logging.basicConfig(filename='twitterbot.log', level=logging.DEBUG)

    with open('settings.json') as data_file:
        settings = json.load(data_file)

    proctitle = 'TwitterBot ({0})'.format(settings.get('username'))
    setproctitle(proctitle)

    bot = TwitterBot(settings)
    bot.run(block=False)
    bot.twitter.auto_restart()
    exit()
