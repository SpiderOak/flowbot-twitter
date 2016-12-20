"""util.py - Standalone utility functions for TwitterBot."""

import emoji


def follower_stars(tweet):
    """Return a set of emoji stars based on the tweeter's follower count."""
    star_levels = [1000, 10000, 100000, 1000000]
    star_emoji = emoji.emojize(':star:', use_aliases=True)
    stars = ' '
    for level in star_levels:
        if tweet.user.followers_count >= level:
            stars += star_emoji
    return stars if stars != ' ' else ''


def get_target_usernames_from_tweet(tweet):
    """Return target usernames (owners or reply-targets) from a tweet."""
    usernames = []
    if tweet.user:
        usernames.append(tweet.user.screen_name)
    if tweet.in_reply_to_screen_name:
        usernames.append(tweet.in_reply_to_screen_name)

    return usernames


def comma_delimited_number(number):
    """Return a comma-delimited version of the number.

    e.g. 12345 -> 12,345
    """
    return format(int(number), ",d")
