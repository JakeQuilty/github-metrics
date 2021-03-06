# -*- coding: utf-8 -*-

import datetime
import json
import os
import requests
import time

from Issue import Issue

class Repo:
    COMMENTS_URL = "https://api.github.com/repos/{org_name}/{issue_name}/issues/comments?state=all&per_page=100&page=1"

    def __init__(self,org_name, issue_name, user, auth_token, org_members):
        self.USER = user
        self.AUTH_TOKEN = auth_token
        self.org_name = org_name
        self.org_members = org_members

        # Get repo comments
        comments_response = requests.get(Repo.COMMENTS_URL.format(org_name=org_name, issue_name=issue_name), auth=(self.USER, self.AUTH_TOKEN))

        # Raise errors if the request failed
        comments_response.raise_for_status()

        self.raw_comments = json.loads(comments_response.text)

        while 'next' in comments_response.links.keys():
            comments_response = requests.get(comments_response.links['next']['url'], auth=(self.USER, self.AUTH_TOKEN))
            comments_response.raise_for_status()

            self.raw_comments.extend(json.loads(comments_response.text))

        self.curr_comment_index = 0
        self.raw_comments.reverse()

        # Get lists of pull requests and issues
        # TODO: Use the issue URL from Issue module
        issue_url = "https://api.github.com/repos/"+ org_name + "/" + issue_name + "/issues?state=all&per_page=100&page=1"
        issue_response = requests.get(issue_url, auth=(self.USER, self.AUTH_TOKEN))
        raw_issues = json.loads(issue_response.text)
        while 'next' in issue_response.links.keys():
            issue_response = requests.get(issue_response.links['next']['url'], auth=(self.USER, self.AUTH_TOKEN))
            issue_response.raise_for_status()

            raw_issues.extend(json.loads(issue_response.text))

        self.pr_list = []
        self.issue_list = []
        self.sort_lists(raw_issues)

        self.six_months = [time.localtime(time.mktime((time.localtime().tm_year, time.localtime().tm_mon - n, 1, 0, 0, 0, 0, 0, 0)))[:2] for n in range(6)]
        self.issue_name = issue_name

        # PR
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

        # Issue
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

    # Sort issue and PR lists
    def sort_lists(self, raw_list):
        for issue in raw_list:
            try:
                # This will cause an error if the pull_request tag isn't there -> means it's an issue
                flag = issue['pull_request']
                self.pr_list.append(Issue(issue, self.USER, self.AUTH_TOKEN))
            except KeyError:
                self.issue_list.append(Issue(issue, self.USER, self.AUTH_TOKEN))

    # Gets all needed data for repo from each pr/issue. Adds them to their lists
    def get_repo_data(self, prlist, issue_list):
        print("Getting data from " + self.issue_name + "...")
        for pr in prlist:
            self.pr_created_times.append(pr.get_creation_time())
            self.pr_closed_times.append(pr.get_closed_time())
            self.pr_first_response_times.append(self.first_comment(pr.get_url()))

            # Get state
            if pr.get_state() == "closed":
                self.pr_closed_states += 1
            else:
                self.pr_open_states += 1

            author = pr.get_author()

            # Add author to total count
            unique = self.contributors(author, self.pr_unique_contr, self.pr_unique_contr_count)
            self.pr_unique_contr = unique[0]
            self.pr_unique_contr_count = unique[1]
            if self.author_in_org(author):
                # Add author to in org count
                unique = self.contributors(author, self.pr_in_org_contr, self.pr_in_org_contr_count)
                self.pr_in_org_contr = unique[0]
                self.pr_in_org_contr_count = unique[1]
            else:
                # Add author to out of org count
                unique = self.contributors(author, self.pr_out_org_contr, self.pr_out_org_contr_count)
                self.pr_out_org_contr = unique[0]
                self.pr_out_org_contr_count = unique[1]

            # Do this dynamically from repo creation date instead of 6 months?
            if pr.within_six_months():
                for date in self.six_months:
                    if pr.get_creation_time().year == date[0] and pr.get_creation_time().month == date[1]:
                        self.pr_six_months_count[self.six_months.index(date)] += 1
                        break

        #for issue in issue_list
        for issue in issue_list:
            self.issue_created_times.append(issue.get_creation_time())
            self.issue_closed_times.append(issue.get_closed_time())
            self.issue_first_response_times.append(self.first_comment(issue.get_url()))

            # Get state
            if issue.get_state() == "closed":
                self.issue_closed_states += 1
            else:
                self.issue_open_states += 1

            author = issue.get_author()

            # Add author to total count
            unique = self.contributors(author, self.issue_unique_contr, self.issue_unique_contr_count)
            self.issue_unique_contr = unique[0]
            self.issue_unique_contr_count = unique[1]
            if self.author_in_org(author):
                # Add author to in-org total count
                unique = self.contributors(author, self.issue_in_org_contr, self.issue_in_org_contr_count)
                self.issue_in_org_contr = unique[0]
                self.issue_in_org_contr_count = unique[1]
            else:
                # Add author to out-of-org total count
                unique = self.contributors(author, self.issue_out_org_contr, self.issue_out_org_contr_count)
                self.issue_out_org_contr = unique[0]
                self.issue_out_org_contr_count = unique[1]

            # Do this dynamically from repo creation date instead of 6 months?
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
            curr_comment_url = self.raw_comments[index]['issue_url']
            if  curr_comment_url == issue_url:
                try:
                    return datetime.datetime.strptime(self.raw_comments[index]["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                except KeyError:
                    return None
        return None

    # Returns true or false if the author is a member or the current organization
    def author_in_org(self, author):
        # Uncomment to print log output listing the authors that are
        # marked as "not in org"
        #if author not in self.org_members:
        #    print(author + " not in org...")
        return author in self.org_members

    # Updates parallel lists of contributors and their # of contributions
    def contributors(self, curr_contr, contr_list, contr_count):
        try:
            contr_count[contr_list.index(curr_contr)] += 1
        except ValueError:
            contr_list.append(curr_contr)
            contr_count.append(1)

        return [contr_list, contr_count]

    # Returns FIRST author in list with most contributions
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

    # Find difference in time
    def time_difference(self, first, second):
        dif = second - first

        return dif.seconds

    # Returns avg time in hours of two lists of times
    def avg_time(self, created_times, stopped_times):
        count = None
        num_of_times = 0
        for x in range(len(created_times)):
            if len(stopped_times) > 0:
                # XXX: Does not count open PRs
                if stopped_times[x] is None:
                    continue
            if count is None:
                count = self.time_difference(created_times[x], stopped_times[x])
                num_of_times += 1
            else:
                count += self.time_difference(created_times[x], stopped_times[x])
                num_of_times += 1
        if count == None:
            return None

        # Seconds -> hours
        return (count / num_of_times)/3600

    # Format last 6 months of prs
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
            x += 1
        return to_return

    # Format contributor data
    def format_contributor_list(self, contr_list, contr_count):
        contributions = {}
        for  x in range(len(contr_list)):
            contributions[x] = {
                'user': contr_list[x],
                'number': contr_count[x]
            }
        to_return = {
            'topContributor': self.top_contributor(contr_list, contr_count),
            'size': len(contr_list),
            'contributions': contributions
        }

        return to_return

    # Runs all the methods that fio the data and puts it into a dict
    def export(self):

        to_export = {
            'name': self.issue_name,
            'totalPR': len(self.pr_list),
            'closedPR': self.pr_closed_states,
            'openPR': self.pr_open_states,
            'lastSixMonthPR': self.format_last_six_months_by_month(self.pr_six_months_count),
            'avgTimeToFirstResponsePR': self.avg_time(self.pr_created_times, self.pr_first_response_times),
            'avgTimeToResolutionPR': self.avg_time(self.pr_created_times, self.pr_closed_times),
            'allPRAuthors': self.format_contributor_list(self.pr_unique_contr, self.pr_unique_contr_count),
            'inOrgPRAuthors': self.format_contributor_list(self.pr_in_org_contr, self.pr_in_org_contr_count),
            'outOrgContributorsPR': self.format_contributor_list(self.pr_out_org_contr, self.pr_out_org_contr_count),
            'totalIssue': len(self.issue_list),
            'closedIssue': self.issue_closed_states,
            'openIssue': self.issue_open_states,
            'lastSixMonthIssue': self.format_last_six_months_by_month(self.issue_six_months_count),
            'avgTimeToFirstResponseIssue': self.avg_time(self.issue_created_times, self.issue_first_response_times),
            'avgTimeToResolutionIssue': self.avg_time(self.issue_created_times, self.issue_closed_times),
            'allIssueAuthors': self.format_contributor_list(self.issue_unique_contr, self.issue_unique_contr_count),
            'inOrgIssueAuthors': self.format_contributor_list(self.issue_in_org_contr, self.issue_in_org_contr_count),
            'outOrgIssueAuthors': self.format_contributor_list(self.issue_out_org_contr, self.issue_out_org_contr_count)

        }

        return to_export
