import json
import requests
import os
import datetime
import time
from PullRequest import PullRequest
from Issue import Issue

class Repo:


    def __init__(self,org_name, repo_name, USER, AUTH_TOKEN):
        self.USER = USER
        self.AUTH_TOKEN = AUTH_TOKEN
        self.org_name = org_name

        #Get lists of pull requests and issues
        # self.issue_url = "https://api.github.com/repos/"+ org_name + "/" + repo_name +"/issues?state=all&page=1"
        # issue_response = requests.get(self.issue_url)
        # raw_issues = json.loads(issue_response.text)
        # while 'next' in issue_response.links.keys():
        #     issue_response = requests.get(issue_response.links['next']['url'], auth=(self.USER, self.AUTH_TOKEN))
        #     raw_issues.extend(json.loads(issue_response.text))
        # self.issue_list = make_issue_list(raw_issues)

        self.pull_url = "https://api.github.com/repos/"+ org_name + "/" + repo_name +"/pulls?state=all&per_page=100&page=1"
        pull_response = requests.get(self.pull_url, auth=(self.USER, self.AUTH_TOKEN))
        raw_prs = json.loads(pull_response.text)
        while 'next' in pull_response.links.keys():
            pull_response = requests.get(pull_response.links['next']['url'], auth=(self.USER, self.AUTH_TOKEN))
            raw_prs.extend(json.loads(pull_response.text))
        self.pr_list = self.make_pr_list(raw_prs)

        print(self.pr_list)

        self.repo_name = repo_name
        self.open_states = 0
        self.closed_states = 0
        self.unique_contr = []
        self.unique_contr_count = []
        self.in_org_contr = []
        self.in_org_contr_count = []
        self.out_org_contr = []
        self.out_org_contr_count = []
        self.created_times = []
        self.closed_times = []
        self.first_response_times = []
        now = time.localtime()
        self.six_months = [time.localtime(time.mktime((time.localtime().tm_year, time.localtime().tm_mon - n, 1, 0, 0, 0, 0, 0, 0)))[:2] for n in range(6)]
        self.six_months_count = [0] * 6

        self.get_repo_data(self.pr_list)


    ##create list of PR objects
    def make_pr_list(self,raw_pr_list):
        to_return = []
        for pr in raw_pr_list:
            to_return.append(PullRequest(pr,self.USER, self.AUTH_TOKEN, self.org_name))
        return to_return

    #create list of Issue objects
    def make_issue_list(self,raw_issue_list):
        to_return = []
        for issue in raw_issue_list:
            to_return.append(Issue(pr,self.USER, self.AUTH_TOKEN, self.org_name))
        return to_return

    #Gets all needed data from repo only touching each pr/issue once. Adds them to their lists
    def get_repo_data(self, prlist):
        print("Getting data from " + self.repo_name + "...")
        #x = 1
        for pr in prlist:
            #print(x)
            #x+=1
            self.created_times.append(pr.get_creation_time())
            self.closed_times.append(pr.get_closed_time())
            self.first_response_times.append(pr.get_first_response_time())
            if pr.get_state() == "closed":  #get state
                self.closed_states+=1
            else:
                self.open_states+=1

            author = pr.get_author()
            unique = self.contributors(author, self.unique_contr, self.unique_contr_count )  #add author to total count
            self.unique_contr = unique[0]
            self.unique_contr_count = unique[1]
            if pr.author_in_org():
                unique = self.contributors(author, self.in_org_contr, self.in_org_contr_count )  #add author to in org count
                self.in_org_contr = unique[0]
                self.in_org_contr_count = unique[1]
            else:
                unique = self.contributors(author, self.out_org_contr, self.out_org_contr_count )  #add author to out of org count
                self.out_org_contr = unique[0]
                self.out_org_contr_count = unique[1]

            #do this dynamically from repo creation date instead of 6 months?
            if pr.within_six_months():
                for date in self.six_months:
                    if pr.get_creation_time().year == date[0] and pr.get_creation_time().month == date[1]:
                        self.six_months_count[self.six_months.index(date)] += 1
                        break
            
                







#Updates parallel lists of unique_contr and their list of contributions(unique_count)
    def contributors(self,curr_contr,contr_list, contr_count):
        try:
         contr_count[contr_list.index(curr_contr)]+=1
        except ValueError:
         contr_list.append(curr_contr)
         contr_count.append(1)

        return [contr_list, contr_count]

#returns FIRST author in list with most contributions
    def top_contributor(self, contr_list, contr_count):
        if len(contr_list) == 0:
            return None

        high = 0
        index = 0
        for x in range(len(contr_count)):
            if contr_count[x] > high:
                high = contr_count[x]
                index = x
        return contr_list[index]

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

#format last 6 months of prs
    def format_last_six_months_by_month(self):
        to_return = {
            'total': sum(self.six_months_count)
        }
        x = 0
        for date in self.six_months:
            to_return[x] = {
                'year': date[0],
                'month': date[1],
                'count': self.six_months_count[x]
            }
            x+=1
        return to_return

#format contributor data
    def format_contributor_list(self, contr_list, contr_count):
        to_return = {
            'topContributor': self.top_contributor(contr_list, contr_count)
        }
        for  x in range(len(contr_list)):
            to_return[x] = {
                'user': contr_list[x],
                'number': contr_count[x]
            }
        return to_return

#Runs all the methods that fio the data and puts it into a dict
    def export(self):

        to_export = {
            'name': self.repo_name,
            'totalPR': self.get_pr_count(),
            'closedPR': self.get_closed(),
            'openPR': self.get_open(),
            'lastSixMonthPR': self.format_last_six_months_by_month(),
            'avgTimeToFirstResponsePR': self.avg_time_first_response(),
            'avgTimeToResolutionPR': self.avg_time_final_res(),
            'allContributors': self.format_contributor_list(self.unique_contr,self.unique_contr_count),
            'inOrgContributors': self.format_contributor_list(self.in_org_contr, self.in_org_contr_count),
            'outOrgContributors': self.format_contributor_list(self.out_org_contr, self.out_org_contr_count)



            # 'contributors': self.unique_contr,
            # 'topContributorOverall': self.top_contributor(self.unique_contr, self.unique_contr_count),  ##add number of prs to contributors lists??
            # 'inOrgContributors': self.in_org_contr,
            # 'topInOrgContributor': self.top_contributor(self.in_org_contr, self.in_org_contr_count),
            # 'outOrgContributors': self.out_org_contr,
            # 'topOutOrgContributor': self.top_contributor(self.out_org_contr, self.out_org_contr_count)
        }
        return to_export