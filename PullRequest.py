import datetime
import json
import requests
class PullRequest:
    def __init__(self,raw_json, USER, AUTH_TOKEN, ORG_NAME):
        self.raw_json = raw_json
        self.USER = USER
        self.AUTH_TOKEN = AUTH_TOKEN
        self.ORG_NAME = ORG_NAME

    def get_author(self):
        return self.raw_json['user']['login']
#returns datetime object of the time
    def get_creation_time(self):
        return datetime.datetime.strptime(self.raw_json['created_at'], "%Y-%m-%dT%H:%M:%SZ")
#
    def get_updated_time(self):
        if self.raw_json['updated_at'] == None:
            return None
        else:
            return datetime.datetime.strptime(self.raw_json['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
#
    def get_closed_time(self):
        if self.raw_json['closed_at'] == None:
            return None
        else:
            return datetime.datetime.strptime(self.raw_json['closed_at'], "%Y-%m-%dT%H:%M:%SZ")
#
    def get_merged_time(self):
        if self.raw_json['merged_at'] == None:
            return None
        else:
            return datetime.datetime.strptime(self.raw_json['merged_at'], "%Y-%m-%dT%H:%M:%SZ")
    
    def get_state(self):
        return self.raw_json['state']

    def is_member(self):
        if self.raw_json['author_association'] == "MEMBER":
            return True
        else:
            return False
    def get_pr_number(self):
        return self.raw_json['number']
    
    def get_url(self):
        return self.raw_json['url']

#has to make another api call to get first response time
    def get_first_response_time(self):
        url = self.raw_json['comments_url']
        if url == None:
            return None
        response = requests.get(url, auth=(self.USER, self.AUTH_TOKEN))
        raw_comments = json.loads(response.text)
        try:
            return datetime.datetime.strptime(raw_comments[0]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        except IndexError:
            return None

#returns true or false if author of PR is in the organization
#if authed user is not in the orgs, this will return None
    def author_in_org(self):
        ##get api
        ##return true or false
        url = "https://api.github.com/orgs/" + self.ORG_NAME + "/members/" + self.get_author()
        response = requests.get(url, auth=(self.USER, self.AUTH_TOKEN))
        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            return False
        else:
            return None


    def within_six_months(self):
        curr_date = datetime.datetime.strptime(self.raw_json['created_at'], "%Y-%m-%dT%H:%M:%SZ").date()
        today = datetime.datetime.today().date()
        six_months = (datetime.datetime.today() - datetime.timedelta(6*365/12)).date()

        if six_months <= curr_date <= today:
            return True
        else:
            return False



###FIND OUT WHAT OTHER DATA YOU NEED
    