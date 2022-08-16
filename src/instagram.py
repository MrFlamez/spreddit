# -*- coding: utf-8 -*-

from re import T
from typing import BinaryIO
from datetime import datetime
from time import sleep
import json
import requests
import logging
import io
from PIL import Image
from .errors import ProcessingError, InstagramLoginError
import random

#TODO: Exceptions und Rückgabewerte definieren

class Instagram:

    __ratio_min = 0.91
    __ratio_max = 1.89

    def __init__(self):
        self.session = {"csrf_token": "CSRF_TOKEN",
                        "session_id": "SESSION_ID"}
        self.csrf_tmp = "pMygFRYh9wukUTHfQTrXBNLOss1l9KnU"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                           AppleWebKit/537.36 (KHTML, like Gecko) \
                           Chrome/97.0.4692.71 \
                           Safari/537.36 \
                           Edg/97.0.1072.55"
        self.hashtags = ''
        self.sleeptime_min = 30
        self.sleeptime_max = 120
        self.logger = logging.getLogger(__name__)

    @classmethod
    def isAspectRatioSuitable(cls, width, height):

        ratio = round(width/height, 4)
        
        if cls.__ratio_min < ratio < cls.__ratio_max: return True
        else: return False


    def __getResizedPicture(self, pic):
        
        box = self.__getSuitablePictureSize(pic.width, pic.height)
        resized_pic = pic.crop(box)
        
        buffer = io.BytesIO()
        resized_pic.save(buffer, format='JPEG', quality = 100)

        obj = buffer.getvalue()
        width = box[2]
        height = box[3]

        return obj, width, height

    def __getSuitablePictureSize(self, width, height):

        ratio = round(width/height, 4)
        self.logger.debug(f'B: {width}   H: {height}   ratio: {ratio}')

        if ratio < self.__ratio_min:
            # hochkant --> Breite muss vergrößert werden
            tmp_width = int(height * self.__ratio_min)
            tmp_width_half = int((tmp_width-width)/2)
            box = (-tmp_width_half, 0, tmp_width - tmp_width_half, height)
        elif ratio > self.__ratio_max:
            # quer --> Höhe muss vergrößert werden
            tmp_height = int(width / self.__ratio_max)
            tmp_height_half = int((tmp_height-height)/2)
            box = (0, -tmp_height_half, width, tmp_height - tmp_height_half)
        else:
            box = (0, 0, width, height)
        
        self.logger.debug('new image size')
        self.logger.debug(f'B: {box[2]}   H: {box[3]}   ratio: {round(box[2]/box[3], 4)}')

        return box

    def login(self, username: str, password: str) -> dict:

        self.logger.debug(f'login user {username}')

        login_url = 'https://www.instagram.com/accounts/login/ajax/'

        time = int(datetime.now().timestamp())

        payload = {
            'username': username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{password}',
            'queryParams': {},
            'optIntoOneTap': 'false'
        }

        login_header = {
            "User-Agent": self.user_agent,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken": self.csrf_tmp
        }

        login_response = requests.post(login_url, data=payload, headers=login_header)
        json_data = json.loads(login_response.text)

        #if json_data['message'] == 'checkpoint_required':
            ##ret = requests.get('https://www.instagram.com' + json_data['checkpoint_url'])
            #print(ret)

        """

        choice: 0
        next: /qp/batch_fetch_web/"""

        if 'authenticated' in json_data:
            cookies = login_response.cookies
            cookie_jar = cookies.get_dict()

            self.session = {
                "csrf_token": cookie_jar['csrftoken'],
                "session_id": cookie_jar['sessionid']
            }
            self.logger.debug('authenticated')
            sleep(random.randint(self.sleeptime_min, self.sleeptime_max))
            return self.session

        elif 'spam' in json_data:
            if json_data['spam'] == True:
                raise InstagramLoginError('spam detected')

        elif 'status' in json_data:
            self.logger.debug(f'status: {json_data["status"]} - {json_data["message"]}')
        else:
            raise InstagramLoginError(login_response.text)

    def upload_photo(self, photo: BinaryIO, width, height):
        micro_time = int(datetime.now().timestamp())

        headers = {
            "content-type": "image / jpg",
            "content-length": "1",
            "X-Entity-Name": f"fb_uploader_{micro_time}",
            "Offset": "0",
            "User-Agent": self.user_agent,
            "x-entity-length": "1",
            "X-Instagram-Rupload-Params": f'{{"media_type": 1, "upload_id": {micro_time}, "upload_media_height": {height},'
                                          f' "upload_media_width": {width}}}',
            "x-csrftoken": self.session['csrf_token'],
            "x-ig-app-id": "1217981644879628",
        }
        cookies = {
            "sessionid": self.session['session_id'],
            "csrftoken": self.session['csrf_token']
        }

        upload_response = requests.post(f'https://www.instagram.com/rupload_igphoto/fb_uploader_{micro_time}',
                                        data=photo, headers=headers, cookies=cookies)

        json_data = json.loads(upload_response.text)
        if 'upload_id' in json_data:
            upload_id = json_data['upload_id']
        else:
            self.logger.debug(upload_response)
            self.logger.debug(json_data)

        if 'status' in json_data:
            if json_data['status'] == 'ok':
                sleep(random.randint(self.sleeptime_min, self.sleeptime_max))
                return upload_id

        if 'type' in json_data['debug_info']:
            if json_data['debug_info']['type'] == 'ProcessingFailedError':
                raise ProcessingError(json_data['debug_info']['message'])

        raise Exception(json_data)

    def post(self, photo: BinaryIO, caption=""):

        new_photo, width, height = self.__getResizedPicture(photo)

        try:
            upload_id = Instagram.upload_photo(self, new_photo, width, height)
        except:
            raise

        url = "https://www.instagram.com/create/configure/"

        payload = f'upload_id={upload_id}&caption={caption}&usertags=&custom_accessibility_caption=&retry_timeout='
        headers = {
            'authority': 'www.instagram.com',
            'x-ig-www-claim': 'hmac.AR2-43UfYbG2ZZLxh-BQ8N0rqGa-hESkcmxat2RqMAXejXE3',
            'x-instagram-ajax': 'adb961e446b7-hot',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'user-agent': self.user_agent,
            'x-requested-with': 'XMLHttpRequest',
            'x-csrftoken': self.session['csrf_token'],
            'x-ig-app-id': '1217981644879628',
            'origin': 'https://www.instagram.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.instagram.com/create/details/',
            'accept-language': 'en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7',
        }

        cookies = {
            "sessionid": self.session['session_id'],
            "csrftoken": self.session['csrf_token']
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload, cookies=cookies)
        except UnicodeEncodeError:
            raise

        json_data = json.loads(response.text)

        self.logger.debug(f'state: {json_data["status"]}')

        if json_data["status"] == "ok":
            response = {
                "message": 'photo was shared successfully!',
                'data': json_data}
            sleep(random.randint(self.sleeptime_min, self.sleeptime_max))
            return response['message']

        if json_data['type'] == 'ProcessingFailedError':
            raise ProcessingError(json_data['message'])
        
        raise Exception(json_data)


    def story(self, photo, caption=""):

        upload_id = Instagram.upload_photo(self, photo)

        url = "https://www.instagram.com/create/configure_to_story/"

        payload = f'upload_id={upload_id}&caption={caption}'
        headers = {
            'authority': 'www.instagram.com',
            'x-ig-www-claim': 'hmac.AR3ZEXbtmat2-n-xCNYMcmuUO3wQxV_TwIkcccquQjq_2h-O',
            'x-instagram-ajax': '894dd5337020',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/'
                          '537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'x-csrftoken': self.session['csrf_token'],
            'x-ig-app-id': '1217981644879628',
            'origin': 'https://www.instagram.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.instagram.com/create/story/',
            'accept-language': 'en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7',
        }

        cookies = {
            "sessionid": self.session['session_id'],
            "csrftoken": self.session['csrf_token']
        }

        story_response = requests.request("POST", url, headers=headers, data=payload, cookies=cookies)
        json_data = json.loads(story_response.text)

        if json_data["status"] == "ok":
            response = {
                "message": 'story was shared successfully!',
                'data': json_data}
            sleep(random.randint(self.sleeptime_min, self.sleeptime_max))
            return response

        raise Exception(json_data)

    def setHashtags(self, hashtags):
        self.hashtags = hashtags

    def getHashtags(self, maxNr = None):

        if maxNr == None:
            iRange = len(self.hashtags)
        else:
            iRange = maxNr

        hashtags = ''
        for i in range(iRange):
            if i == 0:
                hashtags = hashtags + f'#{random.choice(self.hashtags)}'
            else:
                hashtags = hashtags + f' #{random.choice(self.hashtags)}'