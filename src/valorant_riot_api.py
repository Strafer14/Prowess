import requests
from os import environ
from ratelimit import limits  # type: ignore
from src.logger import logger


class ValorantApi:
    def __init__(self):
        token = environ.get('VALORANT_API_KEY')
        if token is None and environ.get('PYTHON_ENV') != 'testing':
            raise Exception('The VALORANT_API_KEY environment variable is missing')
        self.token = token

    @limits(calls=100, period=60)
    def __make_request(self, url):
        logger.debug(f'Making request to RIOT API: {url}')
        response = requests.get(url, headers={'X-Riot-Token': self.token})
        return response.json()

    def get_puuid(self, game_name, tag_line):
        url = f'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}'
        return self.__make_request(url)

    def get_matches_list(self, region, puuid):
        # noinspection SpellCheckingInspection
        url = f'https://{region}.api.riotgames.com/val/match/v1/matchlists/by-puuid/{puuid}'
        return self.__make_request(url)

    def get_match_data(self, region, match_id):
        # noinspection SpellCheckingInspection
        url = f'https://{region}.api.riotgames.com/val/match/v1/matches/{match_id}'
        return self.__make_request(url)
