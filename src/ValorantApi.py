import requests
from logger import logger
from os import environ
from ratelimit import limits


class ValorantApi:
    def __init__(self):
        token = environ.get('VALORANT_API_KEY')
        if token is None and environ.get("PYTHON_ENV") != 'testing':
            raise Exception(
                "The VALORANT_API_KEY environment variable is missing")
        self.token = token

    @limits(calls=100, period=60)
    def __make_request(self, url):
        logger.debug("Making request to RIOT API: {}".format(url))
        response = requests.get(url, headers={'X-Riot-Token': self.token})
        return response.json()

    def get_puuid(self, game_name, tag_line):
        url = 'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}'.format(
            game_name, tag_line)
        return self.__make_request(url)

    def get_matches_list(self, region, puuid):
        # noinspection SpellCheckingInspection
        url = 'https://{}.api.riotgames.com/val/match/v1/matchlists/by-puuid/{}'.format(
            region, puuid)
        return self.__make_request(url)

    def get_match_data(self, region, match_id):
        # noinspection SpellCheckingInspection
        url = 'https://{}.api.riotgames.com/val/match/v1/matches/{}'.format(
            region, match_id)
        return self.__make_request(url)
