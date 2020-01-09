import time
from Org import Org
##----------------------------------------------
## GITHUB HAS A 5000 API CALL LIMIT PER **HOUR**
##----------------------------------------------

#GET REPOSS => FOR ALL PRS => annalizePR(rip all important data and tack on to running counts);
# **UPDATE FUNCTION to run after ever repo/pr is hit??*

orgs = ["conjurinc"]       #cyberark,conjurdemos




def main():
    org = Org(orgs[0])
    org.export_csv()

    # for repo in repoList:
    #     #print("Current Repository: " + repoList[x])
    #     time.sleep(.2)  #To avoid API rate limit

    #SORT UNIQUE_COUNT AND DO SAME MOVEMENTS TO UNIQUE_CONTR 

if __name__ == '__main__':
    main()
