import tweepy
import json
import logging


class TwitterStream(tweepy.StreamListener):
    """Handles data received from the stream."""

    def __init__(self, twitterbot, settings):
        self.twitterbot = twitterbot
        self.auth = tweepy.OAuthHandler(
            settings.get('twitter_consumer_key'),
            settings.get('twitter_consumer_secret')
        )
        self.auth.set_access_token(
            settings.get('twitter_access_token'),
            settings.get('twitter_access_token_secret')
        )
        self.api = tweepy.API(self.auth)
        self.stream = self._new_stream()

    def follow(self, user_ids):
        """Disconnext the existing stream then follow the new users."""
        if user_ids:
            self.stream.disconnect()
            self.stream = self._new_stream()
            self.stream.filter(follow=[str(id) for id in user_ids], async=True)

    def get_twitter_id(self, username):
        """Return the twitter_id of the user with the username, if valid."""
        try:
            user = self.api.get_user(username)
            return user.id if user else None
        except tweepy.error.TweepError:
            return False

    def _new_stream(self):
        return tweepy.Stream(auth=self.api.auth, listener=self)

    def on_data(self, data):
        data = json.loads(data)
        self.twitterbot.handle_tweet(data)
        return True

    def on_error(self, status_code):
        logging.error('Got an error with status code: ' + str(status_code))
        if status_code == 401:
            print("Check your Twitter tokens in 'local_settings'.")
            raise SystemExit
        print(status_code)
        return True  # To continue listening

    def on_timeout(self):
        logging.error('Timeout...')
        return True  # To continue listening
