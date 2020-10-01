import requests
from urllib import request
import json
from pprint import pprint
import time
import os
import operator

token = os.environ.get('ENV_VAR')

##actual values to be recieved from client
puuid = "EE8A-dek_wW2K9vwp7SrtdVq8GZ7glvOtKnLEL5gcO6HsOpQoFnlr2F7UMS4Nk7rO1cz-JkvaZ36YQ"
region = "eu"

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

## Get Latest Matches
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    "Accept-Language": "en,en-US;q=0.9,ru;q=0.8,he;q=0.7,es;q=0.6",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com/",
    "X-Riot-Token": token
        }

latest_matches = requests.get('https://'+region+'.api.riotgames.com/val/match/v1/matchlists/by-puuid/'+puuid, headers=headers)
latest_matches = latest_matches.json()
pprint(latest_matches)

## Sorting the latest matches so the oldest match comes first, this is needed for the next step where we filter for older matches that were already proccessed

sorted_latest_matches = dict(latest_matches) 
sorted_latest_matches['history'] = sorted(sorted_latest_matches['history'], key=lambda x : x['gameStartTimeMillis'], reverse=False)

pprint(sorted_latest_matches)

## Get Matches Data

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
        match_data = requests.get('https://eu.api.riotgames.com/val/match/v1/matches/'+matchId, headers=headers) 
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