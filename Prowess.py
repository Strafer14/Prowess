from os import environ
import requests
from urllib import request
import json
from pprint import pprint
import time
import operator
from RiotHandler import RiotHandler

## agrregated metrics that shouldn't be restarted on every run
user_kills = 0
user_deaths = 0
user_assists = 0
user_games_won = 0
user_games_played = 0
headshots = 0
legshots = 0
bodyshots = 0
latest_match_ts = 0
last_round_played = -1

## values to be recieved from user
gameName = "SettMyAssOnFire"
tagLine = "EUW"
region = "eu"

#getting API token
riot_handle = RiotHandler()

#getting puuid
get_puuid = RiotHandler.get_puuid(riot_handle,gameName,tagLine) #real values to be recieved from user
get_puuid = get_puuid.json()
puuid = get_puuid['puuid']

#getting a list of the user's latest matches
latest_matches = RiotHandler.get_data(riot_handle,region,puuid)#real values to be recieved from user
latest_matches = latest_matches.json()

## Sorting the latest matches so the oldest match comes first, this is needed for the next step where we filter for older matches that were already proccessed

sorted_latest_matches = dict(latest_matches) 
sorted_latest_matches['history'] = sorted(sorted_latest_matches['history'], key=lambda x : x['gameStartTimeMillis'], reverse=False)

pprint(sorted_latest_matches)

## setting up metrics to be filled later
new_user_kills = 0 
new_user_deaths = 0
new_user_assists = 0 
new_user_games_won = 0 
new_user_games_played = 0
match_won_status = 'null'
new_headshots = 0
new_legshots = 0
new_bodyshots = 0

## looping through latest matches, creating an API call for each, and storing relevant data
for match in sorted_latest_matches['history']:
    if match['gameStartTimeMillis'] > latest_match_ts:
        new_user_games_played += 1
    if match['gameStartTimeMillis'] >= latest_match_ts:
        latest_match_ts = match['gameStartTimeMillis']
        print('latest_match_ts', latest_match_ts)
        matchId = match['matchId']
        print('matchId', matchId)
        time.sleep(5)
#        match_data = requests.get('https://eu.api.riotgames.com/val/match/v1/matches/'+matchId, headers=headers) 
        match_data = match_data.json()
        for player in match_data['players']: ##getting match KDA and team from player section
            if player['puuid'] == puuid:
                user_player_data = player
                user_team = user_player_data['teamId']
                print('user_team', user_team)
                new_user_kills = new_user_kills + user_player_data['stats']['kills']
                new_user_deaths = new_user_deaths + user_player_data['stats']['deaths']
                new_user_assists = new_user_assists + user_player_data['stats']['assists']
                print('teams', match_data['teams'])
                break
        for team in match_data['teams']: ##checking if player's team won in the team section
            if team['teamId'] == user_team:
                user_team_data = team
                print('user_team_data', user_team_data) 
                match_won_status = user_team_data['won']
                print('match_won_status', match_won_status)
                if match_won_status == True:
                    new_user_games_won += 1
                    break
        for match_round in match_data['roundResults']: ##storing last round number to avoid double counting
            print ('last_round_played', last_round_played, 'current round is ',match_round['roundNum'])
            if  match['gameStartTimeMillis'] == latest_match_ts and last_round_played < match_round['roundNum']:
                last_round_played = match_round['roundNum']
                for match_round_player_stats in match_data['roundResults'][0]['playerStats']: ##getting damage to calculate headshot%
                    if match_round_player_stats['puuid'] == puuid:
                        user_round_data = match_round_player_stats
                        user_round_damage = user_round_data['damage']
                        for damage_per_round in user_round_damage:
                            new_headshots = new_headshots + damage_per_round['headshots']
                            new_bodyshots = new_bodyshots + damage_per_round['bodyshots']
                            new_legshots = new_legshots + damage_per_round['legshots']
                            break
    
        print('stats', new_user_kills, new_user_deaths, new_user_assists, new_user_games_won, new_user_games_played)
        print('headshots', new_headshots, 'bodyshots', new_bodyshots, 'legshots', new_legshots)
        print('-----------------------------')
        


user_kills = user_kills + new_user_kills  
user_deaths = new_user_deaths + user_deaths
user_assists = new_user_assists + user_assists
user_games_won = new_user_games_won + user_games_won  
user_games_played = new_user_games_played + user_games_played
headshots = new_headshots + headshots
legshots = new_legshots + legshots
bodyshots = new_bodyshots + bodyshots


## Calculate metrics from data

win_rate = round((user_games_won/user_games_played)*100,2)
print('win rate is', win_rate)

headshot_rate = round(headshots/(headshots+bodyshots+legshots)*100,2)
print('headshot rate is', headshot_rate)

print('K/D/A is', user_kills,'/', user_deaths,'/',user_assists)

kd_ratio = round(user_kills/user_deaths,2)

print('KD ratio is', kd_ratio)

print('KD ratio is', kd_ratio)

