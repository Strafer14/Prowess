from os import environ
from typing import Optional, cast

import requests
from ratelimit import limits  # type: ignore

from src.logger import logger
from src.types.riot import (ErrorStatus, GetPuuidResponse,
                            MatchHistoryResponse, MatchResponse)


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

    def __validate_response_is_not_error(self, response):
        status = cast(Optional[ErrorStatus], response.get('status'))
        if status:
            raise Exception(f"Request failed, got {status.get('message')} from Riot, status code: {status.get('status_code')}")

    def get_puuid(self, game_name, tag_line) -> GetPuuidResponse:
        url = f'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}'
        response = self.__make_request(url)
        self.__validate_response_is_not_error(response)
        return response

    def get_matches_list(self, region, puuid) -> MatchHistoryResponse:
        url = f'https://{region}.api.riotgames.com/val/match/v1/matchlists/by-puuid/{puuid}'
        response = self.__make_request(url)
        self.__validate_response_is_not_error(response)
        return response

    def get_match_data(self, region, match_id) -> MatchResponse:
        url = f'https://{region}.api.riotgames.com/val/match/v1/matches/{match_id}'
        response = self.__make_request(url)
        self.__validate_response_is_not_error(response)
        return response
