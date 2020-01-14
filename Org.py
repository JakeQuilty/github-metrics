import json
import requests
import csv
from Repo import Repo
class Org:
    def __init__(self, org_name):
        self.name = org_name
        self.url = "https://api.github.com/search/repositories?q=org:" + org_name + "+archived:false+is:public&per_page=100"
        response = requests.get(self.url)
        self.raw_repos = json.loads(response.text)
        self.repo_list = self.make_repo_list()
        self.open_states = 0
        self.closed_states = 0
        self.find_states()

    #Make list of repo objects
    def make_repo_list(self):
        to_return = []
        for x in range(self.raw_repos['total_count']):
            to_return.append(Repo(self.name, self.raw_repos['items'][x]['name']))
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

    def export_csv(self):
        print(self.get_repos())
        print(self.get_num_repos())
        print(self.get_closed())
        print(self.get_open())
        print(self.repo_list[0].export())

        #####MAKE ANOTHER DICT WITH ALL THE EXPORTED REPOS


       # print(self.repo_list[0].avg_time_sub_approval())
            