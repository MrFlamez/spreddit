# -*- coding: utf-8 -*-

import praw
import requests
import datetime
from .storage import Post
import logging

class Reddit:

    def __init__(self, app_id, secret, os, app_name, app_vers):
        self.app_id = app_id
        self.os = os
        self.app_name = app_name
        self.app_vers = app_vers
        self.secret = secret
        self.api = None
        self.logger = logging.getLogger(__name__)
        self.limitNrNewPosts = 100

    def login(self, user, password):

        self.logger.debug(f'login user {user}')
        reddit_user_agent = f'{self.os}:{self.app_name}:{self.app_vers} (by /u/{user})'
        self.api = praw.Reddit(client_id = self.app_id,
                                  client_secret = self.secret,
                                  password = password,
                                  user_agent = reddit_user_agent,
                                  username = user)

    def getNewPostsFromSub(self, strSub, time):

        self.logger.debug(f'get all posts since {datetime.datetime.fromtimestamp(time)} limited to {self.limitNrNewPosts} posts')

        sub = self.api.subreddit(strSub).new(limit = self.limitNrNewPosts)
        posts = []

        for element in sub:
            if int(element.created) > time:
                #timestamp = datetime.datetime.fromtimestamp(int(element.created))
                filename = element.name + '.jpg'
                with open(f'.\pictures\{filename}','wb') as f:
                    r = requests.get(element.url)
                    f.write(r.content)
                posts.append(Post(element.name, element.title, element.author.name, int(element.created), filename))
# "F:\Projects\spreddit\Pictures"
        return posts