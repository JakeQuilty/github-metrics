import json
import requests
import os
from PullRequest import PullRequest
from Issue import Issue

class Repo:


    def __init__(self,org_name, repo_name, USER, AUTH_TOKEN):
        self.USER = USER
        self.AUTH_TOKEN = AUTH_TOKEN

        #Get lists of pull requests and issues
        # self.issue_url = "https://api.github.com/repos/"+ org_name + "/" + repo_name +"/issues?state=all"
        # issue_response = requests.get(self.issue_url)
        # raw_issues = json.loads(issue_response.text)
        # self.issue_list = make_issue_list(raw_issues)

        self.pull_url = "https://api.github.com/repos/"+ org_name + "/" + repo_name +"/pulls?state=all"
        pull_response = requests.get(self.pull_url, auth=(self.USER, self.AUTH_TOKEN))
        raw_prs = json.loads(pull_response.text)
        self.pr_list = self.make_pr_list(raw_prs)

        self.repo_name = repo_name
        self.open_states = 0
        self.closed_states = 0
        self.unique_contr = []
        self.unique_contr_count = []
        self.created_times = []
        self.closed_times = []
        self.first_response_times = []

        self.get_repo_data(self.pr_list)


    ##create pr list
    def make_pr_list(self,raw_pr_list):
        to_return = []
        for pr in raw_pr_list:
            to_return.append(PullRequest(pr,self.USER, self.AUTH_TOKEN))
        return to_return

    def make_issue_list(self,raw_issue_list):
        raise NotImplementedError()

    #Gets all needed data from repo only touching each pr/issue once. Adds them to their lists
    def get_repo_data(self, prlist):
        print("Getting data from " + self.repo_name + "...")
        for pr in prlist:
            self.created_times.append(pr.get_creation_time())
            self.closed_times.append(pr.get_closed_time())
            self.first_response_times.append(pr.get_first_response_time())
            if pr.get_state() == "closed":  #get state
                self.closed_states+=1
            else:
                self.open_states+=1
            self.contributors(pr.get_author())  #add author to contributor count



#Updates parallel lists of unique_contr and their list of contributions(unique_count)
    def contributors(self,curr_contr):
        try:
         self.unique_contr_count[self.unique_contr.index(curr_contr)]+=1
        except ValueError:
         self.unique_contr.append(curr_contr)
         self.unique_contr_count.append(1)

#returns FIRST author in list with most contributions
    def top_contributor(self):
        if len(self.unique_contr) == 0:
            return None

        high = 0
        index = 0
        for x in range(len(self.unique_contr_count)):
            if self.unique_contr_count[x] > high:
                high = self.unique_contr_count[x]
                index = x
        return self.unique_contr[index]

#returns list of ints of the states of the prs in the repo

    def get_closed(self):
        return self.closed_states

    def get_open(self):
        return self.open_states

#return number of prs in this repo
    def get_pr_count(self):
        return len(self.pr_list)

#find difference in time
    def time_difference(self, first, second):
        dif = second - first
        # hours = (dif.seconds/60)/60

        return dif.seconds

#avg time to final resolution
    def avg_time_final_res(self):
        count = None
        for x in range(self.get_pr_count()):
            if len(self.closed_times) > 0:
                if self.closed_times[x] is None:    #does not count open prs
                        continue
            if count is None:
                count = self.time_difference(self.created_times[x], self.closed_times[x])
            else:
                count += self.time_difference(self.created_times[x], self.closed_times[x])
        if count == None:
            return None
        return (count / len(self.pr_list))/3600 ##seconds to hours

#average time to first comment
    def avg_time_first_response(self):
        count = None
        for x in range(self.get_pr_count()):
            if len(self.first_response_times) > 0:
                if self.first_response_times[x] is None:
                        continue
            if count is None:
                count = self.time_difference(self.created_times[x], self.first_response_times[x])
            else:
                count += self.time_difference(self.created_times[x], self.first_response_times[x])
        if count == None:
            return None
        return (count / len(self.pr_list))/3600 ##seconds to hours

#Runs all the methods that fio the data and puts it into a dict
    def export(self):
        to_export = {
            'name': self.repo_name,
            'total_prs': self.get_pr_count(),
            'avgTimeToFirstResponse': self.avg_time_first_response(),
            'avgTimeToResolution': self.avg_time_final_res(),
            'closedPR': self.get_closed(),
            'openPR': self.get_open(),
            'contributors': self.unique_contr,
            'topContributor': self.top_contributor()

        }
        return to_export