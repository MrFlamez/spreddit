# -*- coding: utf-8 -*-

from .instagram import Instagram
from .errors import ProcessingError, InstagramLoginError 
from .reddit import Reddit            
from PIL import Image
from .storage import Storage, Post
import sys
import logging
from logging.config import fileConfig


class Spreddit():

    # Social Media Targets
    SMT_ALL = 0
    SMT_INSTAGRAM = 1
    #SMT_TUMBLR = 2

    def __init__(self):
        self.reddit = None
        self.instagram = None
        self.tumblr = None
        self.data = None

        fileConfig('logging_config.ini')
        self.logger = logging.getLogger(__name__)
    
    def __saveData(self):
        try:
            Storage.saveStorageObject(self.data)
        except Exception as e:
            self.logger.exception('storage object could not be saved on disk', exc_info = e)
            # Wird es toleriert, dass das Zwischenspeichern nicht funktioniert, kann es sein,
            # dass Bilder doppelt aus Reddit geholt und in Instagram gepostet werden
            # --> Daher Abbruch
            #TODO: vielleicht das bestehende laden, dass das programm weitermacht
            sys.exit()

    def initRedditAccount(self, user, pw, app_id, secret, os, app_name, app_vers):
        self.reddit = Reddit(app_id, secret, os, app_name, app_vers)
        try:
            self.reddit.login(user, pw)
        except Exception as e:
            self.logger.exception('reddit login failed', exc_info = e)

    def initInstagramAccount(self, user, pw):
        self.instagram = Instagram()
        try:
            self.instagram.login(user, pw)
        except Exception as e:
            self.logger.exception('instagram login failed', exc_info = e)
            sys.exit()

    def initTumblrAccount(self, user, pw):
        pass

    def initStorage(self):
        try:
            self.data = Storage.getStorageObject()
        except Exception as e:
            self.logger.exception('storage object could not be loaded', exc_info = e)
            sys.exit()

    def saveNewPostsFromReddit(self, subReddit):
        try:
            new_posts = self.reddit.getNewPostsFromSub(subReddit, self.data.getLastUpdate())
        except Exception as e:
            self.logger.exception('error when getting new posts on reddit', exc_info = e)
        else:
            self.logger.info(f'found {len(new_posts)} new posts since last Update.')
            self.data.setLastUpdate()

        #TODO: geht auch ohne for-Schleife [] + []
            self.logger.debug(f'adding new posts to storage')
            for post in new_posts:
                self.data.addPost(post)
            
            self.data.ensureDataIntegrity()
            self.__saveData()

    def spreadPost(self, socialMediaTarget):

        if socialMediaTarget in [self.SMT_ALL, self.SMT_INSTAGRAM]:
            try:
                post = self.data.getPostForInstagram()
            except:
                return

            self.logger.info(f'post image {post.filename} on instagram')

            try:
                img = self.data.loadImageFromPost(post)
            except:
                self.logger.debug(f'cant load image {post.filename} from disk')
                self.data.delPost(post.id)
                return

            caption = f'{post.title}\n\nCredits: u/{post.author}\n\n{self.instagram.getHashtags()}'

            try:
                share_post = self.instagram.post(img, caption=caption)
                self.logger.info(share_post)
            except UnicodeEncodeError:
                self.logger.warning('unicode encode error, discard post')
                self.data.delPost(post.id)
            except ProcessingError as e:
                self.logger.error(e.message)
                self.data.delPost(post.id)
            except InstagramLoginError as e:
                self.logger.error(e.message)
            except Exception as e:
                self.logger.exception('cant post image on instagram', exc_info=e)
                return
            else:
                self.data.delPost(post.id)

            self.logger.debug(f'{len(self.data.posts)} photos remaining in storage')

        #TODO: tumblr implementieren
        # getPostForInstagram muss dann allgemein definiert werden
        # delPost am Ende muss dann auch verlagert werden. Darf erst erfolgen, wenn alle Posts fertig sind.

        else:
            self.logger.info('no suitable social media target chosen')

        self.data.ensureDataIntegrity()

        try:
            Storage.saveStorageObject(self.data)
        except Exception as e:
            self.logger.exception('storage object could not be saved on disk', exc_info = e)
