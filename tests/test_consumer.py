import json
import os
import unittest
from unittest import mock

from src.valorant_data_parsing import increment_player_stats

puuid = 'EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ'
default_session = {
    'sessionId': 'e7710fc8-34d2-4cea-987b-2107c4e135d0',
    'currentMatchInfo': {
        'won': 2,
        'gamesPlayed': 2,
        'matchId': 'a937f53e-5b17-478e-a83b-8342fe242e89',
        'isCompleted': True,
        'roundsPlayed': 2,
    },
    'puuid': puuid,
    'region': 'EU',
    'data': {
        'score': 0,
        'roundsPlayed': 0,
        'kills': 0,
        'deaths': 0,
        'assists': 0,
        'playtimeMillis': 0,
        'legshots': 0,
        'bodyshots': 0,
        'headshots': 0,
    },
}


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        calls_amount = 0

        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == f'https://EU.api.riotgames.com/val/match/v1/matchlists/by-puuid/{puuid}':
        response = [
            {
                'matchId': '4ea732fd-1820-43a0-bddd-f88d912fb2ff',
                'gameStartTimeMillis': 1605124255472,
                'teamId': 'Red',
            },
            {
                'matchId': 'd19f8cc8-9750-4cb0-a5c4-d706e9fb2dog',
                'gameStartTimeMillis': 1605122145653,
                'teamId': 'Blue',
            },
        ]
        return MockResponse({
            'puuid': puuid,
            'history': response,
        }, 200)
    elif args[0] == f'https://EU.api.riotgames.com/val/match/v1/matchlists/by-puuid/{puuid}-2':
        response = [
            {
                'matchId': 'd19f8cc8-9750-4cb0-a5c4-d706e9fb2608',
                'gameStartTimeMillis': 1605124255472,
                'teamId': 'Blue',
            },
            {
                'matchId': '4ea732fd-1820-43a0-bddd-f88d912fb2ff',
                'gameStartTimeMillis': 1605124255472,
                'teamId': 'Red',
            },
            {
                'matchId': 'd19f8cc8-9750-4cb0-a5c4-d706e9fb2dog',
                'gameStartTimeMillis': 1605122145653,
                'teamId': 'Blue',
            },
        ]
        return MockResponse({
            'puuid': puuid,
            'history': response,
        }, 200)
    elif args[0] == 'https://EU.api.riotgames.com/val/match/v1/matches/4ea732fd-1820-43a0-bddd-f88d912fb2ff':
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        filename = os.path.join(fileDir, 'tests/mocks/match_info_sample.json')
        match_data_open = open(filename)
        match_data = json.load(match_data_open)
        return MockResponse(match_data, 200)
    elif args[0] == 'https://EU.api.riotgames.com/val/match/v1/matches/d19f8cc8-9750-4cb0-a5c4-d706e9fb2608':
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        filename = os.path.join(fileDir, 'tests/mocks/match_info_sample2.json')
        match_data_open = open(filename)
        match_data = json.load(match_data_open)
        return MockResponse(match_data, 200)

    return MockResponse(None, 404)


class TestConsumer(unittest.TestCase):
    maxDiff = None

    @mock.patch('src.valorant_riot_api.requests.get', side_effect=mocked_requests_get)
    def test_normal_payload_processed_correctly(self, mocked_requests_get):
        result = increment_player_stats(default_session)
        expected_result = {
            'sessionId': 'e7710fc8-34d2-4cea-987b-2107c4e135d0',
            'currentMatchInfo': {
                'won': 2,
                'gamesPlayed': 3,
                'matchId': '4ea732fd-1820-43a0-bddd-f88d912fb2ff',
                'isCompleted': True,
                'roundsPlayed': 7,
            },
            'puuid': 'EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ',
            'region': 'EU',
            'data': {
                'score': 410,
                'roundsPlayed': 7,
                'kills': 1,
                'deaths': 6,
                'assists': 3,
                'playtimeMillis': 671396,
                'legshots': 2,
                'bodyshots': 6,
                'headshots': 0,
            },
            'playerInfo': {'rank': 0, 'characterId': 'eb93336a-449b-9c1b-0a54-a891f7921d69'},
        }
        expected_result_2 = {
            'sessionId': 'e7710fc8-34d2-4cea-987b-2107c4e135d0',
            'currentMatchInfo': {'won': 2, 'gamesPlayed': 3,
                                 'matchId': 'd19f8cc8-9750-4cb0-a5c4-d706e9fb2608',
                                 'isCompleted': False, 'roundsPlayed': 7},
            'puuid': 'EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ-2',
            'region': 'EU',
            'data': {'score': 820, 'roundsPlayed': 14, 'kills': 2, 'deaths': 12, 'assists': 6,
                     'playtimeMillis': 1342792, 'legshots': 4, 'bodyshots': 12, 'headshots': 0},
            'playerInfo': {'rank': 0, 'characterId': 'eb93336a-449b-9c1b-0a54-a891f7921d69'}}
        # self.assertEqual(result, expected_result)
        # Test progress one match
        expected_result['puuid'] += '-2'
        result = increment_player_stats(expected_result)
        # self.assertEqual(result, expected_result_2)
        # Test checked again but no progress happened, results should stay the same
        result = increment_player_stats(expected_result_2)
        self.assertEqual(result, expected_result_2)

    @mock.patch('src.valorant_riot_api.requests.get', side_effect=mocked_requests_get)
    def test_reset_session_does_not_accumulate_previous_match(self, mocked_requests_get):
        reset_session_data = {
            'sessionId': 'e7710fc8-34d2-4cea-987b-2107c4e135d5',
            'currentMatchInfo': {
                'won': 0,
                'gamesPlayed': 0,
                'matchId': '4ea732fd-1820-43a0-bddd-f88d912fb2ff',
                'isCompleted': False,
                'roundsPlayed': 0,
            },
            'puuid': puuid,
            'region': 'EU',
            'data': {
                'score': 0,
                'roundsPlayed': 0,
                'kills': 0,
                'deaths': 0,
                'assists': 0,
                'playtimeMillis': 0,
                'legshots': 0,
                'bodyshots': 0,
                'headshots': 0,
            }}
        result = increment_player_stats(reset_session_data)
        self.assertEqual(result, reset_session_data)
        # Test progress one match
        reset_session_data['puuid'] += '-2'
        result = increment_player_stats(reset_session_data)
        # self.assertEqual(result, {
        #     'sessionId': 'e7710fc8-34d2-4cea-987b-2107c4e135d5',
        #     'currentMatchInfo': {
        #         'won': 0,
        #         'gamesPlayed': 0,
        #         'matchId': 'd19f8cc8-9750-4cb0-a5c4-d706e9fb2608',
        #         'isCompleted': False,
        #         'roundsPlayed': 7,
        #     },
        #     'puuid': puuid + '-2',
        #     'region': 'EU',
        #     'data': {
        #         'score': 410,
        #         'roundsPlayed': 7,
        #         'kills': 1,
        #         'deaths': 6,
        #         'assists': 3,
        #         'playtimeMillis': 671396,
        #         'legshots': 2,
        #         'bodyshots': 6,
        #         'headshots': 0,
        #     },
        #     'playerInfo': {
        #         'rank': 0,
        #         'characterId': 'eb93336a-449b-9c1b-0a54-a891f7921d69',
        #     }})

    @mock.patch('src.valorant_riot_api.requests.get', side_effect=mocked_requests_get)
    def test_empty_payload_processed_correctly(self, mocked_requests_get):
        self.assertRaises(KeyError, increment_player_stats, {})

    @mock.patch('src.valorant_riot_api.requests.get', side_effect=mocked_requests_get)
    def test_wrong_puuid_handled_correctly(self, mocked_requests_get):
        payload = {
            'sessionId': 'e7710fc8-34d2-4cea-987b-2107c4e135d0',
            'currentMatchInfo': {
                'won': 2,
                'gamesPlayed': 2,
                'matchId': 'a937f53e-5b17-478e-a83b-8342fe242e89',
                'isCompleted': True,
                'roundsPlayed': 24,
            },
            'puuid': 'mKFglzHwrBYFbj1j87AHrNsLNm1SQdpiEbNOLM-QG2Kb_Af2QJb-GKkVDQCg41tL8ACfQJpBbXVfxA',
            'region': 'EU',
            'data': {
                'score': 7668,
                'roundsPlayed': 24,
                'kills': 28,
                'deaths': 16,
                'assists': 3,
                'playtimeMillis': 2413246,
                'legshots': 12,
                'bodyshots': 63,
                'headshots': 10,
            },
        }
        self.assertRaises(AttributeError, increment_player_stats, payload)
