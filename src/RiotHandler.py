import requests
from os import environ


def make_request(url, token):
    return requests.get(url, headers={'X-Riot-Token': token})


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
        return (make_request(url, self.token)).text

    def get_matches_list(self, region, puuid):
        url = 'https://{}.api.riotgames.com/val/match/v1/matchlists/by-puuid/{}'.format(
            region, puuid)
        return (make_request(url, self.token)).text

    def get_match_data(self, region, match_id):
        url = 'https://{}.api.riotgames.com/val/match/v1/matches/{}'.format(
            region, match_id)
        return (make_request(url, self.token)).text
