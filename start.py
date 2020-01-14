from Org import Org
##----------------------------------------------
## GITHUB HAS A 5000 API CALL LIMIT PER **HOUR**
##----------------------------------------------

orgs = ["conjurinc", "cyberark", "conjurdemos"]

def main():
    for org_name in orgs:
        print("\nORGANIZATION: "+ org_name)
        org = Org(org_name)
        org.export_json()
        print("Finished exporting: "+ org_name)

if __name__ == '__main__':
    main()
