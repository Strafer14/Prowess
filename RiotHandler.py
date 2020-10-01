import requests
from os import environ


class RiotHandler:
    def __init__(self):
        token = environ.get('VALORANT_API_KEY')
        if token is None:
            raise Exception(
                "The VALORANT_API_KEY environment variable is missing")
        self.token = token

    def get_puuid(self, game_name, tag_line):
        url = 'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}'.format(
            game_name, tag_line)
        return requests.get(url, headers={'X-Riot-Token': self.token})

    def get_data(self, region, puuid)
    url = 'https://{}.api.riotgames.com/val/match/v1/matchlists/by-puuid/{}'.format(
        region, puuid)
    return requests.get(url, headers={'X-Riot-Token': self.token})

# {
#     "puuid": "EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ",
#     "gameName": "SettMyAssOnFire",
#     "tagLine": "EUW"
# }
