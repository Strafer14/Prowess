import unittest
from Analyzer import Analyzer
import json

class AnalyticsTests(unittest.TestCase):
    def test_stats_are_accurate(self):

        #Assume
        user_kills = 0
        user_deaths = 0
        user_assists = 0
        user_games_won = 0
        user_rounds_won = 0
        user_games_played = 0
        headshots = 0
        legshots = 0
        bodyshots = 0
        latest_match_ts = 0
        last_round_played = 0
        new_user_kills = 0 
        new_user_deaths = 0
        new_user_assists = 0 
        new_user_games_won = 0 
        new_user_rounds_won = 0
        new_user_games_played = 0
        match_won_status = 'null'
        new_headshots = 0
        new_legshots = 0
        new_bodyshots = 0
        match_game_start_time = 0 #should get actual value as an input
        last_round_played = -1 
        match_data_open = open('match_info_sample.json') #mock json file imitating api result
        match_data = json.load(match_data_open)
        puuid = 'EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ'


        #Action
        test = Analyzer()
        result = Analyzer.analyze_match(test, match_data)

        #Assert
        assert new_user_rounds_won == 3
        assert new_user_kills == 1 
        assert new_user_deaths == 6 
        assert new_user_assists == 3
        assert new_headshots == 0
        assert new_legshots == 2
        assert new_bodyshots == 6
      

