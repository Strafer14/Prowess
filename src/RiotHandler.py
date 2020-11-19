import requests
import json
from logger import logger
from os import environ
from ratelimit import limits, sleep_and_retry


class RiotHandler:
    def __init__(self):
        token = environ.get('VALORANT_API_KEY')
        if token is None:
            raise Exception(
                "The VALORANT_API_KEY environment variable is missing")
        self.token = token

    @sleep_and_retry
    @limits(calls=10, period=60)
    def __make_request(self, url):
        logger.debug("Making request to RIOT API")
        response = requests.get(url, headers={'X-Riot-Token': self.token})
        if response.status_code != 200:
            raise Exception('API response - {}: {}'.format(response.status_code, response.text))
        return response.json()

    def get_puuid(self, game_name, tag_line):
        url = 'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}'.format(
            game_name, tag_line)
        return self.__make_request(url)

    def get_matches_list(self, region, puuid):
        url = 'https://{}.api.riotgames.com/val/match/v1/matchlists/by-puuid/{}'.format(
            region, puuid)
        return self.__make_request(url)

    def get_match_data(self, region, match_id):
        url = 'https://{}.api.riotgames.com/val/match/v1/matches/{}'.format(
            region, match_id)
        return self.__make_request(url)
