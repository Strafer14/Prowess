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
        self.requests_made = 0

    def __update_requests_amount__(self):
        self.requests_made += 1

    def get_puuid(self, game_name, tag_line):
        self.__update_requests_amount__()
        url = 'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}'.format(
            game_name, tag_line)
        if self.requests_made >= 100: return
        return (make_request(url, self.token)).text

    def get_matches_list(self, region, puuid):
        self.__update_requests_amount__()
        url = 'https://{}.api.riotgames.com/val/match/v1/matchlists/by-puuid/{}'.format(
            region, puuid)
        if self.requests_made >= 100: return
        return (make_request(url, self.token)).text

    def get_match_data(self, region, match_id):
        self.__update_requests_amount__()
        url = 'https://{}.api.riotgames.com/val/match/v1/matches/{}'.format(
            region, match_id)
        if self.requests_made >= 100: return
        return (make_request(url, self.token)).text
