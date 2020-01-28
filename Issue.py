# -*- coding: utf-8 -*-

import datetime
import json
import requests

class Issue:
    TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, raw_json, USER, AUTH_TOKEN):
        self.raw_json = raw_json
        self.USER = USER
        self.AUTH_TOKEN = AUTH_TOKEN

    def get_author(self):
        return self.raw_json['user']['login']
#returns datetime object of the time
    def get_creation_time(self):
        return datetime.datetime.strptime(self.raw_json['created_at'], Issue.TIME_FORMAT)
#
    def get_updated_time(self):
        if self.raw_json['updated_at'] == None:
            return None
        else:
            return datetime.datetime.strptime(self.raw_json['updated_at'], Issue.TIME_FORMAT)
#
    def get_closed_time(self):
        if self.raw_json['closed_at'] == None:
            return None
        else:
            return datetime.datetime.strptime(self.raw_json['closed_at'], Issue.TIME_FORMAT)

    def get_state(self):
        return self.raw_json['state']

    def within_six_months(self):
        curr_date = datetime.datetime.strptime(self.raw_json['created_at'], Issue.TIME_FORMAT).date()
        today = datetime.datetime.today().date()
        six_months = (datetime.datetime.today() - datetime.timedelta(6*365/12)).date()

        if six_months <= curr_date <= today:
            return True
        else:
            return False

    def get_url(self):
        return self.raw_json['url']
