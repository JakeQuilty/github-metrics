# -*- coding: utf-8 -*-

import datetime
import json
import requests

class Issue:
    TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, raw_json, user, auth_token):
        self.raw_json = raw_json
        self.USER = user
        self.AUTH_TOKEN = auth_token

    def get_author(self):
        return self.raw_json['user']['login']

    #returns datetime object of the time
    def get_creation_time(self):
        return datetime.datetime.strptime(self.raw_json['created_at'], Issue.TIME_FORMAT)

    def get_updated_time(self):
        if self.raw_json['updated_at'] is None:
            return None

        return datetime.datetime.strptime(self.raw_json['updated_at'], Issue.TIME_FORMAT)

    def get_closed_time(self):
        if self.raw_json['closed_at'] is None:
            return None

        return datetime.datetime.strptime(self.raw_json['closed_at'], Issue.TIME_FORMAT)

    def get_state(self):
        return self.raw_json['state']

    def within_six_months(self):
        issue_date = datetime.datetime.strptime(self.raw_json['created_at'], Issue.TIME_FORMAT).date()
        current_date = datetime.datetime.today().date()

        # TODO: This can be done simpler
        six_months = (datetime.datetime.today() - datetime.timedelta(6*365/12)).date()

        return six_months <= issue_date <= current_date

    def get_url(self):
        return self.raw_json['url']
