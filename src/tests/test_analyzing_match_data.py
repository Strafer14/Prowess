import unittest
from .Analyze import Analyzer
import json

class AnalyticsTests(unittest.TestCase):
    def test_stats_are_accurate(self):
        #Assume
        match_data_open = open('match_info_sample.json') #mock json file imitating api result
        match_data = json.load(match_data_open)
        puuid = 'EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ'

        #Action
        test = Analyzer()
        result = test.analyze_match(match_data)

        #Assert
        assert new_user_rounds_won == 3
        assert new_user_kills == 1 
        assert new_user_deaths == 6 
        assert new_user_assists == 3
        assert new_headshots == 0
        assert new_legshots == 2
        assert new_bodyshots == 6
      

