import unittest
from src.match_analyzer import get_match_results
import json
import os

class AnalyticsTests(unittest.TestCase):
    def test_stats_are_accurate(self):
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        filename = os.path.join(fileDir, 'src/static/match_info_sample.json')
        match_data_open = open(filename)
        match_data = json.load(match_data_open)
        puuid = 'EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ'
        result = get_match_results(match_data, puuid)
        assert result['data']['roundsPlayed'] == 7
        assert result['data']['kills'] == 1
        assert result['data']['deaths'] == 6
        assert result['data']['assists'] == 3
        assert result['data']['playtimeMillis'] == 671396
        assert result['data']['legshots'] == 2
        assert result['data']['bodyshots'] == 6
        assert result['data']['headshots'] == 0
        assert result['currentMatchInfo']['won'] == 0
        assert result['currentMatchInfo']['gamesPlayed'] == 1
        assert result['currentMatchInfo']['roundsPlayed'] == 7

    def test_stats_dont_throw_when_no_data(self):
        puuid = 'EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ'
        result = get_match_results({}, puuid)
        assert result['data']['roundsPlayed'] == 0
        assert result['data']['kills'] == 0
        assert result['data']['deaths'] == 0
        assert result['data']['assists'] == 0
        assert result['data']['headshots'] == 0

    def test_stats_are_accurate_when_no_round_data(self):
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        filename = os.path.join(fileDir, 'src/static/match_info_no_rounds.json')
        match_data_open = open(filename)
        match_data = json.load(match_data_open)
        puuid = 'EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ'
        result = get_match_results(match_data, puuid)
        assert result['data']['roundsPlayed'] == 7
        assert result['data']['kills'] == 1
        assert result['data']['deaths'] == 6
        assert result['data']['assists'] == 3

    def test_stats_are_accurate_when_no_player_stats(self):
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        filename = os.path.join(fileDir, 'src/static/match_info_no_stats.json')
        match_data_open = open(filename)
        match_data = json.load(match_data_open)
        puuid = 'EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ'
        result = get_match_results(match_data, puuid)
        assert result['data']['legshots'] == 0
        assert result['data']['bodyshots'] == 0
        assert result['data']['headshots'] == 0
        assert result['currentMatchInfo']['won'] == 0
        assert result['currentMatchInfo']['gamesPlayed'] == 1
