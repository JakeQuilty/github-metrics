from Org import Org
##----------------------------------------------
## GITHUB HAS A 5000 API CALL LIMIT PER **HOUR**
##----------------------------------------------

orgs = ["conjurinc", "cyberark", "conjurdemos"]

def main():
    for org_name in orgs:
        org = Org(org_name)
        org.export_json()

if __name__ == '__main__':
    main()
