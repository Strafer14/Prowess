import unittest
import json
import os
from unittest import mock
from src.RiotHandler import RiotHandler
from src.consumer import distil_data

puuid = 'EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ'


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'https://EU.api.riotgames.com/val/match/v1/matchlists/by-puuid/{}'.format(puuid):
        return MockResponse({
            "puuid": puuid,
            "history": [
                {
                    "matchId": "4ea732fd-1820-43a0-bddd-f88d912fb2ff",
                    "gameStartTimeMillis": 1605124255472,
                    "teamId": "Red"
                },
                {
                    "matchId": "d19f8cc8-9750-4cb0-a5c4-d706e9fb2608",
                    "gameStartTimeMillis": 1605122145653,
                    "teamId": "Blue"
                },
            ]
        }, 200)
    elif args[0] == 'https://EU.api.riotgames.com/val/match/v1/matches/4ea732fd-1820-43a0-bddd-f88d912fb2ff':
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        filename = os.path.join(fileDir, 'src/static/match_info_sample.json')
        match_data_open = open(filename)
        match_data = json.load(match_data_open)
        return MockResponse(match_data, 200)

    return MockResponse(None, 404)


class TestConsumer(unittest.TestCase):
    @mock.patch('src.RiotHandler.requests.get', side_effect=mocked_requests_get)
    def test_normal_payload_processed_correctly(self):
        result = distil_data({
            "sessionId": "e7710fc8-34d2-4cea-987b-2107c4e135d0",
            "currentMatchInfo": {
                "won": 2,
                "gamesPlayed": 2,
                "matchId": "a937f53e-5b17-478e-a83b-8342fe242e89",
                "isCompleted": True,
                "roundsPlayed": 2
            },
            "puuid": puuid,
            "region": "EU",
            "data": {
                "score": 0,
                "roundsPlayed": 0,
                "kills": 0,
                "deaths": 0,
                "assists": 0,
                "playtimeMillis": 0,
                "legshots": 0,
                "bodyshots": 0,
                "headshots": 0
            }
        })
        self.assertEqual(result, {
            'sessionId': 'e7710fc8-34d2-4cea-987b-2107c4e135d0',
            'currentMatchInfo': {
                'won': 2,
                'gamesPlayed': 3,
                'matchId': '4ea732fd-1820-43a0-bddd-f88d912fb2ff',
                'isCompleted': True,
                'roundsPlayed': 7
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
                     'headshots': 0
            }
        })

    @mock.patch('src.RiotHandler.requests.get', side_effect=mocked_requests_get)
    def test_empty_payload_processed_correctly(self):
        self.assertRaises(KeyError, distil_data, {})

    @mock.patch('src.RiotHandler.requests.get', side_effect=mocked_requests_get)
    def test_wrong_puuid_handled_correctly(self):
        result = distil_data({
            "sessionId": "e7710fc8-34d2-4cea-987b-2107c4e135d0",
            "currentMatchInfo": {
                "won": 2,
                "gamesPlayed": 2,
                "matchId": "a937f53e-5b17-478e-a83b-8342fe242e89",
                "isCompleted": True,
                "roundsPlayed": 24
            },
            "puuid": "mKFglzHwrBYFbj1j87AHrNsLNm1SQdpiEbNOLM-QG2Kb_Af2QJb-GKkVDQCg41tL8ACfQJpBbXVfxA",
            "region": "EU",
            "data": {
                "score": 7668,
                "roundsPlayed": 24,
                "kills": 28,
                "deaths": 16,
                "assists": 3,
                "playtimeMillis": 2413246,
                "legshots": 12,
                "bodyshots": 63,
                "headshots": 10
            }
        })
        self.assertEqual(result, {
            'sessionId': 'e7710fc8-34d2-4cea-987b-2107c4e135d0',
            'currentMatchInfo': {
                'won': 3,
                'gamesPlayed': 3,
                'matchId': '7afb8f25-54ae-4a8b-b03f-bb8e5cb9de46',
                'isCompleted': True,
                'roundsPlayed': 28
            },
            'puuid': 'mKFglzHwrBYFbj1j87AHrNsLNm1SQdpiEbNOLM-QG2Kb_Af2QJb-GKkVDQCg41tL8ACfQJpBbXVfxA',
            'region': 'EU',
            'data': {
                'score': 5805,
                'roundsPlayed': 28,
                'kills': 21,
                'deaths': 18,
                'assists': 2,
                'playtimeMillis': 2734996,
                'legshots': 6,
                'bodyshots': 56,
                'headshots': 12
            }
        })

    # @mock.patch('src.RiotHandler.requests.get', side_effect=mocked_requests_get)
    # def test_round_number_same_match_num_different(self):
    #     result = distil_data({
    #         "sessionId": "e7710fc8-34d2-4cea-987b-2107c4e135d0",
    #         "currentMatchInfo": {
    #             "won": 2,
    #             "gamesPlayed": 2,
    #             "matchId": "a937f53e-5b17-478e-a83b-8342fe242e89",
    #             "isCompleted": True,
    #             "roundsPlayed": 7
    #         },
    #         "puuid": puuid,
    #         "region": "EU",
    #         "data": {
    #             "score": 0,
    #             "roundsPlayed": 0,
    #             "kills": 0,
    #             "deaths": 0,
    #             "assists": 0,
    #             "playtimeMillis": 0,
    #             "legshots": 0,
    #             "bodyshots": 0,
    #             "headshots": 0
    #         }
    #     })
    #     print(result)
    #     # self.assertEqual(result, {
    #     #     'sessionId': 'e7710fc8-34d2-4cea-987b-2107c4e135d0',
    #     #     'currentMatchInfo': {
    #     #         'won': 2,
    #     #         'gamesPlayed': 3,
    #     #         'matchId': '4ea732fd-1820-43a0-bddd-f88d912fb2ff',
    #     #         'isCompleted': True,
    #     #         'roundsPlayed': 7
    #     #     },
    #     #     'puuid': 'EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ',
    #     #     'region': 'EU',
    #     #     'data': {
    #     #         'score': 410,
    #     #         'roundsPlayed': 7,
    #     #         'kills': 1,
    #     #         'deaths': 6,
    #     #         'assists': 3,
    #     #              'playtimeMillis': 671396,
    #     #              'legshots': 2,
    #     #              'bodyshots': 6,
    #     #              'headshots': 0
    #     #     }
    #     # })