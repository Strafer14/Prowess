import unittest
from src.Analyze import get_match_results
import json


class AnalyticsTests(unittest.TestCase):
    def test_stats_are_accurate(self):
        # Assume
        # mock json file imitating api result
        match_data_open = open('match_info_sample.json')
        match_data = json.load(match_data_open)
        puuid = 'EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ'

        # Action
        result = get_match_results(match_data, puuid)
        # Assert
        assert result['roundsPlayed'] == 7
        assert result['kills'] == 1
        assert result['deaths'] == 6
        assert result['assists'] == 3
        assert result['playtimeMillis'] == 671396
        assert result['legshots'] == 2
        assert result['bodyshots'] == 6
        assert result['headshots'] == 0
