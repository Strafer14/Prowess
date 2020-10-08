class Analyzer:
    def analyze_match(self, match_data):
        for player in match_data['players']: ##getting match KDA and team from player section
            if player['puuid'] == puuid:
                user_player_data = player
                user_team = user_player_data['teamId']
                new_user_kills = new_user_kills + user_player_data['stats']['kills']
                new_user_deaths = new_user_deaths + user_player_data['stats']['deaths']
                new_user_assists = new_user_assists + user_player_data['stats']['assists']
                break
        for team in match_data['teams']: ##checking if player's team won in the team section
            if team['teamId'] == user_team:
                user_team_data = team
                match_won_status = user_team_data['won']
                if match_won_status == True:
                    new_user_games_won = new_user_games_won + 1
                    break
        for match_round in match_data['roundResults']: ##storing last round number to avoid double counting
            last_round_played = match_round['roundNum']
            if match_round['winningTeam'] == user_team:
                new_user_rounds_won +=1
        for match_round_players_stats in match_round['playerStats']: ##getting damage to calculate headshot%
            if match_round_players_stats['puuid'] == puuid:
                user_round_data = match_round_players_stats
                for damage_dealt_to_victim in user_round_data['damage']:
                    new_headshots = new_headshots + damage_dealt_to_victim['headshots']
                    new_bodyshots = new_bodyshots + damage_dealt_to_victim['bodyshots']
                    new_legshots = new_legshots + damage_dealt_to_victim['legshots']