import json
import requests
import os
import datetime
import time
#from PullRequest import PullRequest
from Issue import Issue

class Repo:


    def __init__(self,org_name, issue_name, USER, AUTH_TOKEN, org_members):
        self.USER = USER
        self.AUTH_TOKEN = AUTH_TOKEN
        self.org_name = org_name
        self.org_members = org_members

        #get repo comments
        comments_url = "https://api.github.com/repos/"+ org_name + "/" + issue_name +"/issues/comments?state=all&per_page=100&page=1"
        comments_response = requests.get(comments_url, auth=(self.USER, self.AUTH_TOKEN))
        self.raw_comments = json.loads(comments_response.text)
        while 'next' in comments_response.links.keys():
            comments_response = requests.get(comments_response.links['next']['url'], auth=(self.USER, self.AUTH_TOKEN))
            self.raw_comments.extend(json.loads(comments_response.text))

        self.curr_comment_index = 0
        self.raw_comments.reverse()

        #Get lists of pull requests and issues
        issue_url = "https://api.github.com/repos/"+ org_name + "/" + issue_name + "/issues?state=all&per_page=100&page=1"
        issue_response = requests.get(issue_url, auth=(self.USER, self.AUTH_TOKEN))
        raw_issues = json.loads(issue_response.text)
        while 'next' in issue_response.links.keys():
            issue_response = requests.get(issue_response.links['next']['url'], auth=(self.USER, self.AUTH_TOKEN))
            raw_issues.extend(json.loads(issue_response.text))

        self.pr_list = []
        self.issue_list = []
        self.sort_lists(raw_issues)

        now = time.localtime()
        self.six_months = [time.localtime(time.mktime((time.localtime().tm_year, time.localtime().tm_mon - n, 1, 0, 0, 0, 0, 0, 0)))[:2] for n in range(6)]
        self.issue_name = issue_name

#pr
        self.pr_open_states = 0
        self.pr_closed_states = 0
        self.pr_unique_contr = []
        self.pr_unique_contr_count = []
        self.pr_in_org_contr = []
        self.pr_in_org_contr_count = []
        self.pr_out_org_contr = []
        self.pr_out_org_contr_count = []
        self.pr_created_times = []
        self.pr_closed_times = []
        self.pr_first_response_times = []
        self.pr_six_months_count = [0] * 6
#issue
        self.issue_open_states = 0
        self.issue_closed_states = 0
        self.issue_unique_contr = []
        self.issue_unique_contr_count = []
        self.issue_in_org_contr = []
        self.issue_in_org_contr_count = []
        self.issue_out_org_contr = []
        self.issue_out_org_contr_count = []
        self.issue_created_times = []
        self.issue_closed_times = []
        self.issue_first_response_times = []
        self.issue_six_months_count = [0] * 6

        self.get_repo_data(self.pr_list, self.issue_list)

    #sort issue and pr lists
    def sort_lists(self, raw_list):
        for issue in raw_list:
            try:
                flag = issue['pull_request']    ##this will cause an error if the pull_request tag isn't there -> means it's an issue
                self.pr_list.append(Issue(issue, self.USER, self.AUTH_TOKEN))
            except KeyError:
                self.issue_list.append(Issue(issue, self.USER, self.AUTH_TOKEN))

    #Gets all needed data for repo from each pr/issue. Adds them to their lists
    def get_repo_data(self, prlist, issue_list):
        print("Getting data from " + self.issue_name + "...")
        for pr in prlist:
            self.pr_created_times.append(pr.get_creation_time())
            self.pr_closed_times.append(pr.get_closed_time())
            self.pr_first_response_times.append(self.first_comment(pr.get_url()))   ############
            if pr.get_state() == "closed":  #get state
                self.pr_closed_states+=1
            else:
                self.pr_open_states+=1

            author = pr.get_author()
            unique = self.contributors(author, self.pr_unique_contr, self.pr_unique_contr_count )  #add author to total count
            self.pr_unique_contr = unique[0]
            self.pr_unique_contr_count = unique[1]
            if self.author_in_org(author):
                unique = self.contributors(author, self.pr_in_org_contr, self.pr_in_org_contr_count )  #add author to in org count
                self.pr_in_org_contr = unique[0]
                self.pr_in_org_contr_count = unique[1]
            else:
                unique = self.contributors(author, self.pr_out_org_contr, self.pr_out_org_contr_count )  #add author to out of org count
                self.pr_out_org_contr = unique[0]
                self.pr_out_org_contr_count = unique[1]

            #do this dynamically from repo creation date instead of 6 months?
            if pr.within_six_months():
                for date in self.six_months:
                    if pr.get_creation_time().year == date[0] and pr.get_creation_time().month == date[1]:
                        self.pr_six_months_count[self.six_months.index(date)] += 1
                        break
            
        #for issue in issue_list
        for issue in issue_list:
            self.issue_created_times.append(issue.get_creation_time())
            self.issue_closed_times.append(issue.get_closed_time())
            self.issue_first_response_times.append(self.first_comment(issue.get_url())) ##############
            if issue.get_state() == "closed":  #get state
                self.issue_closed_states+=1
            else:
                self.issue_open_states+=1

            author = issue.get_author()
            unique = self.contributors(author, self.issue_unique_contr, self.issue_unique_contr_count )  #add author to total count
            self.issue_unique_contr = unique[0]
            self.issue_unique_contr_count = unique[1]
            if self.author_in_org(author):
                unique = self.contributors(author, self.issue_in_org_contr, self.issue_in_org_contr_count )  #add author to in org count
                self.issue_in_org_contr = unique[0]
                self.issue_in_org_contr_count = unique[1]
            else:
                unique = self.contributors(author, self.issue_out_org_contr, self.issue_out_org_contr_count )  #add author to out of org count
                self.issue_out_org_contr = unique[0]
                self.issue_out_org_contr_count = unique[1]

            #do this dynamically from repo creation date instead of 6 months?
            if issue.within_six_months():
                for date in self.six_months:
                    if issue.get_creation_time().year == date[0] and issue.get_creation_time().month == date[1]:
                        self.issue_six_months_count[self.six_months.index(date)] += 1
                        break

#returns time of first comment
    def first_comment(self, issue_url):
#could speed up by keeping track of where you are in the comment list when you find the match and starting from there next time, instead of
#traversing whole list every time
        for index in range(len(self.raw_comments)):
            issue_id = issue_url.split('/')
            issue_id = issue_id[7]
            curr_comment_url = self.raw_comments[index]['issue_url']
            if  curr_comment_url == issue_url: 
                try:
                    return datetime.datetime.strptime(self.raw_comments[index]["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                except KeyError:
                    return None
        return None

#returns true or false if the author is a member or the current organization
    def author_in_org(self, author):
        return author in self.org_members

#Updates parallel lists of contributors and their # of contributions
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

#find difference in time
    def time_difference(self, first, second):
        dif = second - first
        # hours = (dif.seconds/60)/60

        return dif.seconds

#returns avg time in hours of two lists of times
    def avg_time(self, created_times, stopped_times):
        count = None
        num_of_times = 0
        for x in range(len(created_times)):
            if len(stopped_times) > 0:
                if stopped_times[x] is None:    #does not count open prs
                        continue
            if count is None:
                count = self.time_difference(created_times[x], stopped_times[x])
                num_of_times += 1
            else:
                count += self.time_difference(created_times[x], stopped_times[x])
                num_of_times += 1
        if count == None:
            return None
        return (count / num_of_times)/3600 ##seconds to hours

#format last 6 months of prs
    def format_last_six_months_by_month(self, count):
        to_return = {
            'total': sum(count)
        }
        x = 0
        for date in self.six_months:
            to_return[x] = {
                'year': date[0],
                'month': date[1],
                'count': count[x]
            }
            x+=1
        return to_return

#format contributor data
    def format_contributor_list(self, contr_list, contr_count):
        to_return = {
            'topContributor': self.top_contributor(contr_list, contr_count),
            'size': len(contr_list)
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
            'name': self.issue_name,
            'totalPR': len(self.pr_list),
            'closedPR': self.pr_closed_states,
            'openPR': self.pr_open_states,
            'lastSixMonthPR': self.format_last_six_months_by_month(self.pr_six_months_count),
            'avgTimeToFirstResponsePR': self.avg_time(self.pr_created_times, self.pr_closed_times),
            'avgTimeToResolutionPR': self.avg_time(self.pr_created_times, self.pr_first_response_times),
            'allPRAuthors': self.format_contributor_list(self.pr_unique_contr,self.pr_unique_contr_count),
            'inOrgPRAuthors': self.format_contributor_list(self.pr_in_org_contr, self.pr_in_org_contr_count),
            'outOrgContributorsPR': self.format_contributor_list(self.pr_out_org_contr, self.pr_out_org_contr_count),
            'totalIssue': len(self.issue_list),
            'closedIssue': self.issue_closed_states,
            'openIssue': self.issue_open_states,
            'lastSixMonthIssue': self.format_last_six_months_by_month(self.issue_six_months_count),
            'avgTimeToFirstResponseIssue': self.avg_time(self.issue_created_times, self.issue_closed_times),
            'avgTimeToResolutionIssue': self.avg_time(self.issue_created_times, self.issue_first_response_times),
            'allIssueAuthors': self.format_contributor_list(self.issue_unique_contr,self.issue_unique_contr_count),
            'inOrgIssueAuthors': self.format_contributor_list(self.issue_in_org_contr, self.issue_in_org_contr_count),
            'outOrgIssueAuthors': self.format_contributor_list(self.issue_out_org_contr, self.issue_out_org_contr_count)

        }
        return to_export