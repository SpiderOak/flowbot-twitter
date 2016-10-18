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
            '/following': self.following,
            '/follow': self.follow,
            '/unfollow': self.unfollow
        }

    @mentioned
    def following(self, message):
        """Respond with list of twitter usernames this channel is following."""
        self.render_response(message, 'following.txt', {
            "users": self._get_following(message['channelId'])
        })

    @mentioned
    def follow(self, message):
        """Follow twitter user in the same channel as the original message."""
        match = re.search('/follow (\w+)', message.get('text', ''))

        if match:
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
        match = re.search('/unfollow (\w+)', message.get('text', ''))

        if match:
            username = match.group(1)
            self._unfollow_username(username, message['channelId'])
            self.render_response(message, 'unfollow.txt', {
                "username": username
            })

    def render_response(self, orig_message, template_name, context):
        """Render the context to the message template and respond."""
        response = template.get_template(template_name)
        self.reply(orig_message, response.render(**context))

    def render_to_channel(self, channel_id, template_name, context):
        """Render the context to a message in the given channel."""
        self.server.flow.send_message(
            cid=channel_id,
            oid=self.config.org_id,
            msg=template.get_template(template_name).render(**context)
        )

    def handle_tweet(self, tweet):
        """Handle a tweet from the twitter steam."""
        target_usernames = util.get_target_usernames_from_tweet(tweet)

        for channel_id, users in self._get_all_following().iteritems():
            for user in users:
                if user['username'] in target_usernames:
                    self.render_to_channel(channel_id, 'tweet.txt', {
                        'tweet': tweet
                    })

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
