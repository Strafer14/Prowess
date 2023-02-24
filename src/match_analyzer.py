from functools import reduce

from src.logger import logger

default_stats = {
    'score': 0,
    'roundsPlayed': 0,
    'kills': 0,
    'deaths': 0,
    'assists': 0,
    'playtimeMillis': 0,
}


def _extract_relevant_player(players_data, puuid):
    relevant_player_list = [x for x in players_data if x.get('puuid') == puuid]
    if len(relevant_player_list) > 0:
        return relevant_player_list[0]
    return {}


def _analyze_player_score(match, puuid):
    players_data = match.get('players', [])
    extracted_player = _extract_relevant_player(players_data, puuid)
    # Removing abilityCasts key as it is always null
    if extracted_player.get('stats') is not None:
        try:
            extracted_player['stats'].pop('abilityCasts')
        except Exception:
            logger.warn('No abilitycasts')
        return extracted_player['stats']
    return default_stats


def _get_player_info(match, puuid):
    players_data = match.get('players', [])
    extracted_player = _extract_relevant_player(players_data, puuid)
    rank = extracted_player.get('competitiveTier')
    return {'rank': rank, 'characterId': extracted_player.get('characterId')}


def _analyze_player_aim(match, puuid):
    def reduce_results(acc, val):
        players = val['playerStats']
        relevant_player = _extract_relevant_player(players, puuid)
        for damage_instance in relevant_player['damage']:
            acc['legshots'] += damage_instance['legshots']
            acc['bodyshots'] += damage_instance['bodyshots']
            acc['headshots'] += damage_instance['headshots']
        return acc
    rounds_data = match.get('roundResults', [])
    return reduce(reduce_results, rounds_data, {
        'legshots': 0,
        'bodyshots': 0,
        'headshots': 0,
    })


def _analyze_match_metadata(match, puuid):
    players_data = match.get('players', [])
    relevant_player = _extract_relevant_player(players_data, puuid)
    team_id = relevant_player.get('teamId')
    players_team = [x for x in match.get(
        'teams', []) if x['teamId'] == team_id]
    match_id = match.get('matchInfo', {}).get('matchId')
    is_completed = match.get('matchInfo', {}).get('isCompleted')
    queue_id = match.get('matchInfo', {}).get('queueId')
    rounds_played = len(match.get('roundResults', []))
    logger.info(players_team)
    return {
        'won': int((players_team[0] if len(players_team) > 0 else {}).get('won') is True),
        'gamesPlayed': 1,
        'matchId': match_id,
        'queueId': queue_id,
        'isCompleted': is_completed,
        'roundsPlayed': rounds_played,
    }


def get_match_results(match, puuid):
    match_overview_results = _analyze_player_score(match, puuid)
    match_rounds_results = _analyze_player_aim(match, puuid)
    match_metadata = _analyze_match_metadata(match, puuid)
    player_metadata = _get_player_info(match, puuid)
    return {
        'data': {**match_overview_results, **match_rounds_results},
        'currentMatchInfo': {**match_metadata},
        'playerInfo': {**player_metadata},
    }
