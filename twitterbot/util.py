"""util.py - Standalone utility functions for TwitterBot."""

import emoji


def follower_stars(tweet):
    """Return a set of emoji stars based on the tweeter's follower count."""
    followers_count = tweet['user']['followers_count']
    star_levels = [1000, 10000, 100000, 1000000]
    star_emoji = emoji.emojize(':star:', use_aliases=True)
    stars = ' '
    for level in star_levels:
        if followers_count >= level:
            stars += star_emoji
    return stars if stars != ' ' else ''


def get_target_usernames_from_tweet(tweet):
    """Return target usernames (owners or reply-targets) from a tweet."""
    usernames = []
    owner = tweet['user']['screen_name']
    reply_to_username = tweet['entities'].get('in_reply_to_screen_name')

    if owner:
        usernames.append(owner)
    if reply_to_username:
        usernames.append(reply_to_username)

    return usernames
