> Please Note: This project has not undergone a security review.

# flowbot-twitter
A twitter bot for [SpiderOak Semaphor](https://spideroak.com/opendownload). This bot can watch twitter users and post their tweet inside Semaphor channels. You can even configure the bot to notify you when a tweet's author has over a given number of followers.

## Download & Install
1. Make sure you've installed Docker on your machine.
2. Clone this repo: `git clone git@github.com:SpiderOak/flowbot-twitter.git`
3. Create a `settings.json` file with your settings (see `settings.json.example` for example configuration.)
4. Run `docker-compose build`
5. Run `docker-compose up`

## Interacting with the bot
The bot supports the following commands (assuming the display name of the twitter bot is `TwitterBot`:
- `@TwitterBot /follow myUser`: instructs the bot to follow a twitter user with the username `myUser` in the current Semaphor channel.
- `@TwitterBot /unfollow myUser`: Stop following `myUser` in the current channel
- `@TwitterBot /following`: List all twitter usernames currently being followed in the channel.


> “TWITTER, TWEET, RETWEET and the Twitter logo are trademarks of Twitter, Inc. or its affiliates.”