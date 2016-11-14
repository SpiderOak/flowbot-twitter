> Please Note: This project has not undergone a security review.


## Download & Install
1. Make sure you've installed [SpiderOak Semaphor](https://spideroak.com/opendownload) on your machine.
2. Clone this repo: `git clone git@github.com:SpiderOak/flowbot-twitter.git`
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `settings.json` file with your settings (see `settings.json.example` for example configuration.)
4. Run bot `python run.py`

## Interacting with the bot
The bot supports the following commands (assuming the display name of the twitter bot is `TwitterBot`:
- `@TwitterBot /follow myUser`: instructs the bot to follow a twitter user with the username `myUser` in the current Semaphor channel.
- `@TwitterBot /unfollow myUser`: Stop following `myUser` in the current channel
- `@TwitterBot /following`: List all twitter usernames currently being followed in the channel.


> “TWITTER, TWEET, RETWEET and the Twitter logo are trademarks of Twitter, Inc. or its affiliates.”