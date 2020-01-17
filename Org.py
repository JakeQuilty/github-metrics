import json
import requests
import os
from Repo import Repo
class Org:
    def __init__(self, org_name):
        self.name = org_name
        self.USER = os.getenv('GITHUB_USERNAME')         #Have to auth to increase api limit from 60 -> 5000
        self.AUTH_TOKEN = os.getenv('GITHUB_AUTH_TOKEN')
        self.url = "https://api.github.com/search/repositories?q=org:" + org_name + "+archived:false+is:public&per_page=100&page=1"
        response = requests.get(self.url, auth=(self.USER, self.AUTH_TOKEN))
        self.raw_repos = json.loads(response.text)
        while 'next' in response.links.keys():
            response = requests.get(response.links['next']['url'], auth=(self.USER, self.AUTH_TOKEN))   ##this stuff is incase there are more than 100 repos
            self.raw_repos.extend(json.loads(response.text))
        self.repo_list = self.make_repo_list()

        self.open_states = 0
        self.closed_states = 0
        self.find_states()

    #Make list of repo objects
    def make_repo_list(self):
        to_return = []
        for x in range(self.raw_repos['total_count']):
            to_return.append(Repo(self.name, self.raw_repos['items'][x]['name'], self.USER, self.AUTH_TOKEN))
        return to_return
#return list of repo objects
    def get_repos(self):
        return self.repo_list
#return number of repos
    def get_num_repos(self):
        return len(self.repo_list)
#finds states
    def find_states(self):
        self.open_states = 0
        self.closed_states = 0

        for repo in self.repo_list:
            self.open_states += repo.get_open()
            self.closed_states += repo.get_closed()

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
        org_data = {
            'totalRepos': self.get_num_repos(),
            'closedPR': self.get_closed(),
            'openPR': self.get_open()
        }
        x = 0
        for repo in self.repo_list:
            org_data[x] = repo.export()
            x+=1

    
        file_name = self.name + ".json"
        with open(file_name, 'w') as outfile:
            json.dump(org_data, outfile)


            