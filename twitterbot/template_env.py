"""template_env.py - A wrapper around the Jinja2 Template environment."""

import util
import os
from jinja2 import Environment, FileSystemLoader


_jinja_env = Environment(
    loader=FileSystemLoader('%s/templates/' % os.path.dirname(__file__))
)
_jinja_env.filters['follower_stars'] = util.follower_stars

template = _jinja_env
