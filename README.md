Gets metrics from a github organization

Requirements:
`python3 -m pip install requests`

Set env variables:
`GITHUB_USERNAME`
`GITHUB_AUTH_TOKEN`

Add the organizations you want to analyze to the `orgs[]` array in `start.py`
Note: If you just want to test it, I suggest only having one organization in the `orgs[]` array to save time.

`python3 start.py`
