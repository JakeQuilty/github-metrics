# Gets metrics from a github organization

## Requirements
`python3 -m pip install requests`

## Generating metrics

To generate metrics, you'll want to prepare by updating the `orgs[]` array in
[`start.py`](start.py) to include the github organizations you want to analyze.

**Note:** The more organizations you add to the array, the longer it will take
to run - so you may want to consider only running with one org at a time.

There are two ways to set up your local environment to run the script, but
either way you'll need a GitHub account and a
[personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).

### Running using environment variables

1. Set the following environment variables:
  `GITHUB_USERNAME`
  `GITHUB_AUTH_TOKEN`

1. To generate metrics, run
   ```
   python3 start.py
   ```

### Running using Summon

1. You can store your GitHub auth token in your OSX keyring and run this script using
   [Summon](https://github.com/cyberark/summon) and the [keyring provider](https://github.com/cyberark/summon-keyring/).

   To do this, add your auth token to your keyring by running:
   ```
   security add-generic-password \
     -s "summon" \
     -a "github/api_token" \
     -w "[ACCESS TOKEN]"
   ```

1. Update [`secrets.yml`](secrets.yml) to include your github username.

1. To generate metrics, run
   ```
   summon -p keyring.py python3 start.py
   ```

## Metrics Output
Running the script produces a `.json` file for each GitHub org you specified in
`start.py`.
