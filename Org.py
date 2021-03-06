# -*- coding: utf-8 -*-

import json
import requests
import os

from Repo import Repo

class Org:
    REPO_URL = "https://api.github.com/search/repositories?q=org:{org_name}+archived:false+is:public&per_page=100&page=1"

    def __init__(self, org_name):
        self.name = org_name

        # Have to auth to increase api limit from 60 -> 5000
        self.USER = os.getenv('GITHUB_USERNAME')
        self.AUTH_TOKEN = os.getenv('GITHUB_AUTH_TOKEN')

        if not self.USER or not self.AUTH_TOKEN:
            raise Exception("ERROR: GITHUB_USERNAME or GITHUB_AUTH_TOKEN not provided!")


        response = requests.get(Org.REPO_URL.format(org_name=self.name), auth=(self.USER, self.AUTH_TOKEN))

        # Raise errors if the request for repos failed
        response.raise_for_status()

        self.raw_repos = json.loads(response.text)

        while 'next' in response.links.keys():
            response = requests.get(response.links['next']['url'], auth=(self.USER, self.AUTH_TOKEN))
            self.raw_repos.extend(json.loads(response.text))

        members_url = "https://api.github.com/orgs/"+ org_name +"/members?per_page=100&page=1"
        response = requests.get(members_url, auth=(self.USER, self.AUTH_TOKEN))
        org_members = json.loads(response.text)

        while 'next' in response.links.keys():
            response = requests.get(response.links['next']['url'], auth=(self.USER, self.AUTH_TOKEN))
            org_members.extend(json.loads(response.text))

        self.members = self.make_member_list(org_members)
        self.repo_list = self.make_repo_list()

        self.open_states = 0
        self.closed_states = 0
        self.find_states()

    # Make list of repo objects
    def make_repo_list(self):
        to_return = []
        for x in range(self.raw_repos['total_count']):
            to_return.append(Repo(self.name, self.raw_repos['items'][x]['name'], self.USER, self.AUTH_TOKEN, self.members))
        return to_return

    # Make string list of org members
    def make_member_list(self, members):
        to_return = []
        for member in members:
            to_return.append(member['login'])

        return to_return

    # Return list of repo objects
    def get_repos(self):
        return self.repo_list

    # Return number of repos
    def get_num_repos(self):
        return len(self.repo_list)

    # Finds states
    def find_states(self):
        self.open_states = 0
        self.closed_states = 0

        for repo in self.repo_list:
            self.open_states += repo.pr_open_states
            self.closed_states += repo.pr_closed_states

    def get_open(self):
        return self.open_states

    def get_closed(self):
        return self.closed_states

    ##################
    #methods to make:
    #repos with smallest and greatest avgTimes, open, closed
    #total # of prs in last 6 months
    # # of prs in each of the last 6 months
    #call them in export_json and feed in the org_data dict
    ##################

    def export_json(self):
        # TODO: Simplify this - lots of unnecessary work here
        repos = {}
        x = 0
        for repo in self.repo_list:
            repos[x] = repo.export()
            x+=1
        org_data = {
            'repos': repos,
            'totalRepos': self.get_num_repos(),
            'closedPR': self.get_closed(),
            'openPR': self.get_open()
        }

        file_name = self.name + ".json"
        with open(file_name, 'w') as outfile:
            json.dump(org_data, outfile)
