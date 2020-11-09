from functools import reduce


def __extract_relevant_player__(players_data, puuid):
    relevant_player_list = [x for x in players_data if x.get('puuid') == puuid]
    if len(relevant_player_list) > 0:
        return relevant_player_list[0]
    return {}


def __analyze_player_score__(match, puuid):
    players_data = match.get('players', [])
    relevant_player = __extract_relevant_player__(players_data, puuid)
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
        relevant_player = __extract_relevant_player__(players, puuid)
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


def __analyze_match_metadata__(match, puuid):
    players_data = match.get('players', [])
    relevant_player = __extract_relevant_player__(players_data, puuid)
    team_id = relevant_player['teamId']
    players_team = next(
        filter(lambda x: x['teamId'] == team_id, match['teams']))
    match_id = match.get("matchInfo", {}).get("matchId")
    is_completed = match.get("matchInfo", {}).get("isCompleted")
    rounds_played = len(match.get("roundResults", []))
    return {
        "won": int(players_team['won'] == True),
        "gamesPlayed": 1,
        "matchId": match_id,
        "isCompleted": is_completed,
        "roundsPlayed": rounds_played
    }


def get_match_results(match, puuid):
    match_overview_results = __analyze_player_score__(match, puuid)
    match_rounds_results = __analyze_player_aim__(match, puuid)
    match_metadata = __analyze_match_metadata__(match, puuid)
    return {
        "data": {**match_overview_results, **match_rounds_results},
        "currentMatchInfo": {**match_metadata}
    }
