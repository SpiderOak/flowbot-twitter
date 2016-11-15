"""bot.py - A TwitterBot for Semaphor."""

import re

from flowbot import FlowBot
from flowbot.decorators import mentioned

from . import util
from .twitter_stream import TwitterStream
from .template_env import template


class TwitterBot(FlowBot):
    """Twitter Bot."""

    def __init__(self, settings):
        """In addition to setting up the bot, start the twitter stream."""
        super(TwitterBot, self).__init__(settings)
        self.twitter = TwitterStream(self, settings)
        self._update_twitter_stream()

    def commands(self):
        """Respond to these commands with the given methods."""
        return {
            'following': self.following,
            'follow': self.follow,
            'unfollow': self.unfollow,
            'help': self.help,
            'mention stop': self.mention_stop,
            'mention': self.mention_me
        }

    @mentioned
    def help(self, message):
        """Show all the command options."""
        self.render_response(message, 'help.txt', {
            'botname': self.config.display_name
        })

    @mentioned
    def following(self, message):
        """Respond with list of twitter usernames this channel is following."""
        self.render_response(message, 'following.txt', {
            "users": self._get_following(message['channelId'])
        })

    @mentioned
    def follow(self, message):
        """Follow twitter user in the same channel as the original message."""
        match = re.search(' follow (\w+)', message.get('text', ''))
        unfollow_match = re.search(' unfollow (\w+)', message.get('text', ''))

        if match and not unfollow_match:
            username = match.group(1)
            user = self._get_twitter_user(username)

            if user:
                self._follow_user(user, message['channelId'])

            self.render_response(message, 'follow.txt', {
                "user": user
            })

    @mentioned
    def unfollow(self, message):
        """Stop following a twitter user."""
        match = re.search(' unfollow (\w+)', message.get('text', ''))

        if match:
            username = match.group(1)
            self._unfollow_username(username, message['channelId'])
            self.render_response(message, 'unfollow.txt', {
                "username": username
            })

    @mentioned
    def mention_me(self, message):
        """Remember to highlight a user when a tweet is above threshold.

        If no threshold number is given, just show the user the current
        threshold.
        """
        match = re.search('mention (\d+)', message.get('text', ''))
        match_stop = re.search('mention stop', message.get('text', ''))
        user_id = message['senderAccountId']

        if match:
            follower_threshold = match.group(1)
            self._update_mention_threshold(user_id, follower_threshold)
            self.render_response(message, 'new_mention.txt', {
                "follower_threshold": follower_threshold
            }, highlight=[user_id])
        elif not match_stop:
            current_threshold = self._get_mention_thresholds().get(user_id)
            self.render_response(message, 'current_mention_threshold.txt', {
                "current_threshold": current_threshold,
                "botname": self.config.display_name
            }, highlight=[user_id])

    @mentioned
    def mention_stop(self, message):
        """Stop mentioning the user."""
        user_id = message['senderAccountId']
        self._update_mention_threshold(user_id, None)
        self.render_response(
            message, 'mention_stop.txt', {}, highlight=[user_id])

    def render_response(self, orig_message, template_name, context, highlight=None):  # NOQA
        """Render the context to the message template and respond."""
        response = template.get_template(template_name)
        self.reply(
            orig_message, response.render(**context), highlight=highlight)

    def render_to_channel(self, channel_id, template_name, context, highlight=None):  # NOQA
        """Render the context to a message in the given channel."""
        msg = template.get_template(template_name).render(**context)
        self.message_channel(channel_id, msg, highlight=highlight)

    def handle_tweet(self, tweet):
        """Handle a tweet from the twitter steam."""
        target_usernames = util.get_target_usernames_from_tweet(tweet)
        highlight = self._get_account_ids_to_highlight(tweet)

        for channel_id, users in self._get_all_following().iteritems():
            for user in users:
                if user['username'] in target_usernames:
                    self.render_to_channel(channel_id, 'tweet.txt', {
                        'tweet': tweet
                    }, highlight=highlight)

    def _get_twitter_user(self, username):
        """Return a user object if the username is valid.

        A 'user object' is a dict with a username and id keys.
        """
        twitter_user_id = self.twitter.get_twitter_id(username)
        if not twitter_user_id:
            return None

        return {
            'username': username,
            'id': twitter_user_id
        }

    def _follow_user(self, user, channel_id):
        """Remember to follow the twitter user in this channel."""
        users = self._get_following(channel_id)

        if user not in users:
            users.append(user)

        self._update_following(channel_id, users)

    def _unfollow_username(self, username, channel_id):
        """If the username is in the channel, unfollow them in that channel."""
        users = self._get_following(channel_id)

        for user in users:
            if user['username'].lower() == username.lower():
                users.remove(user)

        self._update_following(channel_id, users)

    def _get_following(self, channel_id):
        """Get this list of user objects followed in this channel."""
        db_key = 'follow_%s' % (channel_id, )
        users = self.channel_db.get_last(db_key)
        return users if users else []

    def _update_following(self, channel_id, users):
        """Update list of users followed in this channel."""
        db_key = 'follow_%s' % (channel_id, )
        self.channel_db.new(db_key, users)

    def _get_mention_thresholds(self):
        """Get the list of mention thresholds."""
        mentions = self.channel_db.get_last('mentions')
        return mentions if mentions else {}

    def _get_account_ids_to_highlight(self, tweet):
        """Get account_ids to highlight given tweet's follower count."""
        account_ids = []
        follower_count = tweet['user']['followers_count']
        for account_id, threshold in self._get_mention_thresholds().items():
            if follower_count and threshold.isdigit():
                if follower_count > int(threshold):
                    account_ids.append(account_id)
        return account_ids

    def _update_mention_threshold(self, user_id, follower_threshold):
        """Save a user_id :: follower_threshold record."""
        mentions = self._get_mention_thresholds()
        mentions[user_id] = follower_threshold
        self.channel_db.new('mentions', mentions)

    def _usernames_followed(self, channel_id):
        """Return a list of usernames followed in the channel."""
        users = self._get_following(channel_id)
        return [u.username for u in users]

    def _update_twitter_stream(self):
        """Update the list of following user_ids in the twitter steam."""
        users = self._get_all_following()
        user_ids = self._get_user_ids(users)
        self.twitter.follow(user_ids)

    def _get_user_ids(self, following):
        """Get the ids of all twitter users this bot is listening to."""
        ids = []
        for channel_id, users in following.iteritems():
            for user in users:
                if user['id'] not in ids:
                    ids.append(user['id'])
        return ids

    def _get_all_following(self):
        """Get list of all users followed in all channels."""
        following = {}

        for channel_id in self.channels():
            following[channel_id] = self._get_following(channel_id)
        return following
