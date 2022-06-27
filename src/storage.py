# -*- coding: utf-8 -*-

from collections import namedtuple
from datetime import datetime
import os
import logging
from PIL import Image
import pickle
from .instagram import Instagram

Post = namedtuple("Post", ['id', 'title', 'author', 'time', 'filename'])


class Storage:

    storageFilename = 'data' #TODO: storage.p

    def __init__(self) -> None:
        self.__lastUpdate = int(datetime.now().timestamp())
        self.posts = []
        self.logger = logging.getLogger(__name__)
        # maximale Anzahl übergebbar machen
        self.maxNumberOfPosts = 10
    
    @classmethod
    def getStorageObject(cls):

        # load existing pickle dump or creat a new file
        if not os.path.isfile(cls.storageFilename):
            storage = Storage()
        else:
            with open(cls.storageFilename, 'rb') as file:
                storage = pickle.load(file)

        return storage

    @classmethod
    def saveStorageObject(cls, obj):
    
            with open(cls.storageFilename, 'wb') as file:
                pickle.dump(obj, file, protocol=pickle.HIGHEST_PROTOCOL)

    def __getAllFilenames(self):
        filenames = []
        for post in self.posts:
            filenames.append(post.filename)
        return filenames

    def setLastUpdate(self):
        now = int(datetime.now().timestamp())
        self.__lastUpdate = now
        self.logger.debug(f'set last update (now) to {datetime.fromtimestamp(now)}')

    def getLastUpdate(self):
        return self.__lastUpdate

    def addPost(self, post):
        self.logger.debug(f'add post {post.id} from {datetime.fromtimestamp(post.time)}')
        self.posts.append(post)

    def getOldestPost(self):

        tmpTime = int(datetime.now().timestamp())
        tmpPost = None

        for post in self.posts:
            if post.time < tmpTime:
                tmpTime = post.time
                tmpPost = post

        self.logger.debug(f'found post {tmpPost.id}')
        return tmpPost

    def delImage(self, filename):

        file = f'.\\pictures\\{filename}'

        if os.path.exists(file):
            os.remove(file)
        
        if os.path.exists(file):
            self.logger.error(f'image {filename} could not be deleted')
        else:
            self.logger.debug(f'image {filename} deleted successfully')

    def delPost(self, id):

        self.logger.debug(f'delete post {id}')

        for i in range(len(self.posts)):
            if self.posts[i].id == id:
                break

        #self.delImage(f'.\pictures\{self.posts[i].filename}')
        self.posts.pop(i)

    def printContent(self):
        for post in self.posts:
            self.logger.info(f'{post.title}')
            #self.logger.info(f'id: {post.id}   filename: {post.filename}   posted: {datetime.fromtimestamp(post.time)}')

    def delObsoletePosts(self):

        self.logger.debug('search obsolete posts in data')
        elementIDsToDelete = []
        for i in range(len(self.posts)):
            if not os.path.exists(f'.\pictures\{self.posts[i].filename}'):
                elementIDsToDelete.append(i)
        
        self.logger.debug(f'found {len(elementIDsToDelete)} obsolete posts')
        elementIDsToDelete.sort(reverse=True)
        for i in elementIDsToDelete:
            self.logger.debug(f'delete obsolete post {self.posts[i].id}')
            self.posts.pop(i)

    def delObsoleteImages(self):

        filenamesOnDisk = os.listdir('.\\pictures\\')
        filenamesInPosts = self.__getAllFilenames()

        for filename in filenamesOnDisk:
            if not filename in filenamesInPosts:
                self.delImage(filename)
        
    def loadImageFromPost(self, post):
        try:
            return Image.open(f'.\pictures\{post.filename}')
        except:
            raise

    def delDuplicates(self):

        uniqueIDs = []
        duplicates = []

        for i in range(len(self.posts)):
            if self.posts[i].id in uniqueIDs:
                duplicates.append(i)
            else:
                uniqueIDs.append(self.posts[i].id)
        duplicates.sort(reverse=True)

        for i in duplicates:
            self.logger.debug(f'delete obsolete post {self.posts[i].id}')
            self.posts.pop(i)

    def ensureDataIntegrity(self):
        try:
            self.delDuplicates()
            self.delObsoletePosts()
            self.delObsoleteImages()
        except:
            self.logger.exception('failed to ensure data integrity in storage')

    def getPostForInstagram(self):

        #TODO: in die Klasse Instagram verlagern als 'preparePost'

        post = None
        while (post is None):

            if len(self.posts) == 0:
                raise Exception('there are no pictures in storage to post on instagram')

            tmpPost = self.getOldestPost()

            if tmpPost is None:
                raise Exception('couldnt find oldest post')

            try:
                img = self.loadImageFromPost(tmpPost)
            except:
                self.logger.error('cant load image from disk')
                self.delPost(tmpPost.id)
                continue
            else:
                if img.format == 'PNG':
                    self.logger.debug('picture format PNG is not suitable')
                    img.close()
                    self.delPost(tmpPost.id)
                    continue
                else:
                    width = img.width
                    height = img.height
                    img.close()

            if not Instagram.isAspectRatioSuitable(width, height):
                self.logger.debug(f'aspect ratio from {tmpPost.filename} is not suitable')
                self.delPost(tmpPost.id)
                continue

            post = tmpPost
            self.logger.debug(f'oldest post {post.id} was created on {post.time}')

            return post

    def delSurplusPosts(self):pass
        # TODO: implementieren
        
