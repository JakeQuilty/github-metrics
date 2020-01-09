import json
import requests
from PullRequest import PullRequest
from Issue import Issue

class Repo:

    unique_contr = []
    unique_contr_count = []

    def __init__(self,org_name, repo_name):
        #Get lists of pull requests and issues
        # self.issue_url = "https://api.github.com/repos/"+ org_name + "/" + repo_name +"/issues?state=all"
        # issue_response = requests.get(self.issue_url)
        # raw_issues = json.loads(issue_response.text)
        # self.issue_list = make_issue_list(raw_issues)

        self.pull_url = "https://api.github.com/repos/"+ org_name + "/" + repo_name +"/pulls?state=all"
        pull_response = requests.get(self.pull_url)
        raw_prs = json.loads(pull_response.text)
        self.pr_list = self.make_pr_list(raw_prs)
        self.open_states = 0
        self.closed_states = 0
        self.find_states()

#Updates parallel lists of unique_contr and their list of contributions(unique_count)
#this is expensive af
    def contributors(self,curr_contr):
        try:
         unique_contr_count[unique_contr.index(curr_contr)]+=1
        except ValueError:
         unique_contr.append(curr_contr)
         unique_contr_count.append(1)

##make this later
    def top_contributor():
        #get author with most # of contrs
        raise NotImplementedError()

##create pr list
    def make_pr_list(self,raw_pr_list):
        to_return = []
        for pr in raw_pr_list:
            to_return.append(PullRequest(pr))
        
        return to_return

    def make_issue_list(self,raw_issue_list):
        raise NotImplementedError()

#returns list of ints of the states of the prs in the repo
    def find_states(self):
        open_states = 0
        closed_states = 0
        for pr in self.pr_list:
            if pr.get_state() == "closed":
                self.closed_states+=1
            else:
                self.open_states+=1

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

    def avg_time_final_res(self):
        count = None
        for pr in self.pr_list:
            if pr.get_closed_time() is None:
                continue
            if count is None:
                count = self.time_difference(pr.get_creation_time(), pr.get_closed_time())
            else:
                count+=self.time_difference(pr.get_creation_time(), pr.get_closed_time())
        return (count / len(self.pr_list))/3600