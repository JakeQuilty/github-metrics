#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##----------------------------------------------
## GITHUB HAS A 5000 API CALL LIMIT PER **HOUR**
##----------------------------------------------

from Org import Org

orgs = ["conjurinc", "cyberark", "conjurdemos"]

def main():
    for org_name in orgs:
        print("\nORGANIZATION: "+ org_name)
        org = Org(org_name)
        org.export_json()
        print("Finished exporting: "+ org_name+".json")

if __name__ == '__main__':
    main()
