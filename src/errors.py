# -*- coding: utf-8 -*-

class RegramError(Exception):

    def __init(self):
        pass

class ProcessingError (RegramError):

    def __init__(self, message):
        self.message = message

class InstagramLoginError (RegramError):

    def __init__(self, message):
        self.message = message