from functools import reduce


def __extract_relevant_player(players_data, puuid):
    relevant_player_list = [x for x in players_data if x.get('puuid') == puuid]
    if len(relevant_player_list) > 0:
        return relevant_player_list[0]
    return {}


def __analyze_player_score(match, puuid):
    players_data = match.get('players', [])
    extracted_player = __extract_relevant_player(players_data, puuid)
    # Removing abilityCasts key as it is always null
    if extracted_player.get('stats') is not None:
        extracted_player['stats'] = {key: extracted_player['stats'][key]
                                     for key in extracted_player['stats'] if key != 'abilityCasts'}
    return extracted_player.get('stats', {
        "score": 0,
        "roundsPlayed": 0,
        "kills": 0,
        "deaths": 0,
        "assists": 0,
        "playtimeMillis": 0,
    })


def __analyze_player_aim(match, puuid):
    def reduce_results(acc, val):
        players = val['playerStats']
        relevant_player = __extract_relevant_player(players, puuid)
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


def __analyze_match_metadata(match, puuid):
    players_data = match.get('players', [])
    relevant_player = __extract_relevant_player(players_data, puuid)
    team_id = relevant_player.get('teamId')
    players_team = [x for x in match.get(
        'teams', []) if x['teamId'] == team_id]
    match_id = match.get("matchInfo", {}).get("matchId")
    is_completed = match.get("matchInfo", {}).get("isCompleted")
    rounds_played = len(match.get("roundResults", []))
    return {
        "won": int((players_team[0] if len(players_team) > 0 else {}).get('won') == True),
        "gamesPlayed": 1,
        "matchId": match_id,
        "isCompleted": is_completed,
        "roundsPlayed": rounds_played
    }


def get_match_results(match, puuid):
    match_overview_results = __analyze_player_score(match, puuid)
    match_rounds_results = __analyze_player_aim(match, puuid)
    match_metadata = __analyze_match_metadata(match, puuid)
    return {
        "data": {**match_overview_results, **match_rounds_results},
        "currentMatchInfo": {**match_metadata}
    }
