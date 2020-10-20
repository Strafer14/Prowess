from os import environ
import requests
from urllib import request
import json
import time
import operator
from RiotHandler import RiotHandler
from functools import reduce

# agrregated metrics that shouldn't be restarted on every run
# user_kills = 0
# user_deaths = 0
# user_assists = 0
# user_games_won = 0
# user_games_played = 0
# headshots = 0
# legshots = 0
# bodyshots = 0
# latest_match_ts = 0
# last_round_played = -1

# ## values to be recieved from user
# gameName = "SettMyAssOnFire"
# tagLine = "EUW"
# region = "eu"

# #getting API token
# riot_handle = RiotHandler()

# #getting puuid
# get_puuid = riot_handle.get_puuid(gameName,tagLine) #real values to be recieved from user
# get_puuid = get_puuid.json()
# puuid = get_puuid['puuid']

# #getting a list of the user's latest matches
# latest_matches = RiotHandler.get_data(riot_handle,region,puuid)#real values to be recieved from user
# latest_matches = latest_matches.json()

# ## Sorting the latest matches so the oldest match comes first, this is needed for the next step where we filter for older matches that were already proccessed
# sorted_latest_matches = dict(latest_matches)
# sorted_latest_matches['history'] = sorted(sorted_latest_matches['history'], key=lambda x : x['gameStartTimeMillis'], reverse=False)

# #imitating api match results with json file
# match_data_open = open('match_info_sample.json')
# match_data = json.load(match_data_open)

# building a class that uses a sample file to save API calls while testing


class Analyzer:
    def __init__(self):
        self.results_dict = {  # seting metrics to be populated when iterating over match rounds
            new_user_kills: 0,
            new_user_deaths: 0,
            new_user_assists: 0,
            new_user_games_won: 0,
            new_user_rounds_won: 0,
            new_user_games_played: 0,
            match_won_status: Null,
            new_headshots: 0,
            new_legshots: 0,
            new_bodyshots: 0,
            match_game_start_time: 0,  # should get actual value as an input
            last_round_played: -1,
        }

    def analyze_match(self, match_data):
        # getting match KDA and team from player section
        for player in match_data['players']:
            if player['puuid'] == puuid:
                user_player_data = player
                user_team = user_player_data['teamId']
                new_user_kills = new_user_kills + \
                    user_player_data['stats']['kills']
                new_user_deaths = new_user_deaths + \
                    user_player_data['stats']['deaths']
                new_user_assists = new_user_assists + \
                    user_player_data['stats']['assists']
                break
        # checking if player's team won in the team section
        for team in match_data['teams']:
            if team['teamId'] == user_team:
                user_team_data = team
                match_won_status = user_team_data['won']
                if match_won_status == True:
                    new_user_games_won = new_user_games_won + 1
                    break
        # storing last round number to avoid double counting
        for match_round in match_data['roundResults']:
            last_round_played = match_round['roundNum']
            if match_round['winningTeam'] == user_team:
                new_user_rounds_won += 1
            # getting damage to calculate headshot%
            for match_round_players_stats in match_round['playerStats']:
                if match_round_players_stats['puuid'] == puuid:
                    user_round_data = match_round_players_stats
                    for damage_dealt_to_victim in user_round_data['damage']:
                        new_headshots = new_headshots + \
                            damage_dealt_to_victim['headshots']
                        new_bodyshots = new_bodyshots + \
                            damage_dealt_to_victim['bodyshots']
                        new_legshots = new_legshots + \
                            damage_dealt_to_victim['legshots']

        user_kills += new_user_kills
        user_deaths += new_user_deaths
        user_assists += new_user_assists
        user_games_won += new_user_games_won
        user_games_played += new_user_games_played
        headshots += new_headshots
        legshots += new_legshots
        bodyshots += new_bodyshots


def __analyze_player_score__(match, puuid):
    players_data = match.get('players', [])
    relevant_player = next(filter(lambda x: x['puuid'] == puuid, players_data))
    return relevant_player.get('stats', {
        "score": 0,
        "roundsPlayed": 0,
        "kills": 0,
        "deaths": 0,
        "assists": 0,
        "playtimeMillis": 0,
        "abilityCasts": None
    })


def __analyze_player_aim__(match, puuid):
    def reduce_results(acc, val):
        players = val['playerStats']
        relevant_player = next(filter(lambda x: x['puuid'] == puuid, players))
        for damage_instance in relevant_player['damage']:
            acc["legshots"] += damage_instance["legshots"]
            acc["bodyshots"] += damage_instance["bodyshots"]
            acc["headshots"] += damage_instance["headshots"]
        return acc
    rounds_data = match.get('roundResults', [])
    return reduce(reduce_results, rounds_data, {
        "legshots": 0,
        "bodyshots": 0,
        "headshots": 0
    })


def __analyze_match_over_score__(match, puuid):
    players_data = match.get('players', [])
    relevant_player = next(filter(lambda x: x['puuid'] == puuid, players_data))
    team_id = relevant_player['teamId']
    players_team = next(
        filter(lambda x: x['teamId'] == team_id), match['teams'])
    return {"won": int(players_team['won'] == True), "games_played": 1}


def get_match_results(match, puuid):
    match_overview_results = __analyze_player_score__(match, puuid)
    match_rounds_results = __analyze_player_aim__(match, puuid)
    return {**match_overview_results, **match_rounds_results}
