import datetime
class PullRequest:
    def __init__(self,raw_json):
        self.raw_json = raw_json

##del self.raw_json ??????/

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

    def get_time_difference(self, first, second):
        dif = second - first
        hours = (dif/60)/60

        return hours



###FIND OUT WHAT OTHER DATA YOU NEED
    