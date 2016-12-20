import tweepy
import logging
import time


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
        self.user_ids = None

    def auto_restart(self, interval=60):
        """Auto restart the twitter stream every [interval] seconds if down."""
        while True:
            try:
                if self.stream and self.stream.running is False:
                    self._restart()
                time.sleep(interval)
            except (SystemExit, KeyboardInterrupt):
                self.twitterbot.cleanup()
                self.stream.disconnect()
                break

    def follow(self, user_ids):
        """Disconnext the existing stream then follow the new users."""
        if user_ids:
            self.user_ids = user_ids
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

    def on_exception(self, exception):
        """Attempt to restart the stream using the last known user_ids."""
        return False

    def on_timeout(self):
        """Attempt to restart the stream using the last known user_ids."""
        return False

    def _restart(self):
        """Try restarting based on last known user_ids."""
        self.stream.disconnect()
        if self.user_ids:
            self.follow(self.user_ids)
        return True

    def on_status(self, status):
        """Handle new status message."""
        try:
            self.twitterbot.handle_tweet(status)
        except Exception as e:
            print(e)
        return True

    def on_error(self, status_code):
        logging.error('Got an error with status code: ' + str(status_code))
        if status_code == 401:
            print("Check your Twitter tokens in 'local_settings'.")
            raise SystemExit
        print(status_code)
        return True  # To continue listening
