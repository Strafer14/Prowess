from functools import reduce
from typing import List, Union, cast

from src.logger import logger
from src.types.riot import (MatchResponse, PlayerInfo, PlayerStats,
                            RoundPlayerStats, RoundResult)
from src.types.session_data import (ExtractedMatchMetaData,
                                    GeneratedMatchResults, MergedResults,
                                    ParsedPlayerAim, ParsedPlayerInfo)

default_stats: PlayerStats = {
    'score': 0,
    'roundsPlayed': 0,
    'kills': 0,
    'deaths': 0,
    'assists': 0,
    'playtimeMillis': 0,
}


def _extract_relevant_player(players_data: Union[List[RoundPlayerStats], List[PlayerInfo]], puuid: str) -> Union[
        RoundPlayerStats, PlayerInfo]:
    relevant_player_list = [x for x in players_data if x.get('puuid') == puuid]
    if len(relevant_player_list) > 0:
        return relevant_player_list[0]
    raise Exception('Could not find player in the match')


def _analyze_player_score(match: MatchResponse, puuid: str) -> PlayerStats:
    players_data = match.get('players', [])
    extracted_player = cast(PlayerInfo, _extract_relevant_player(players_data, puuid))
    stats = extracted_player.get('stats')
    if stats is not None:
        try:
            stats.pop('abilityCasts')  # type: ignore
        except Exception:
            logger.warn('No abilitycasts')
        return stats
    return default_stats


def _get_player_info(match: MatchResponse, puuid: str) -> ParsedPlayerInfo:
    players_data = match.get('players', [])
    extracted_player = cast(PlayerInfo, _extract_relevant_player(players_data, puuid))
    rank = extracted_player.get('competitiveTier')
    return {'rank': rank, 'characterId': extracted_player.get('characterId')}


def _analyze_player_aim(match: MatchResponse, puuid: str) -> ParsedPlayerAim:
    def reduce_results(acc: ParsedPlayerAim, val: RoundResult):
        players = val['playerStats']
        relevant_player = cast(RoundPlayerStats, _extract_relevant_player(players, puuid))
        for damage_instance in relevant_player['damage']:
            acc['legshots'] += damage_instance['legshots']
            acc['bodyshots'] += damage_instance['bodyshots']
            acc['headshots'] += damage_instance['headshots']
        return acc
    rounds_data = match.get('roundResults', [])
    return reduce(reduce_results, rounds_data, cast(ParsedPlayerAim, {
        'legshots': 0,
        'bodyshots': 0,
        'headshots': 0,
    }))


def _analyze_match_metadata(match: MatchResponse, puuid: str) -> ExtractedMatchMetaData:
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
    did_player_win = int(players_team[0].get('won') is True if len(players_team) > 0 else False)
    return {
        'won': did_player_win,
        'gamesPlayed': 1,
        'matchId': match_id,
        'queueId': queue_id,
        'isCompleted': is_completed,
        'roundsPlayed': rounds_played,
    }


def get_match_results(match: MatchResponse, puuid: str) -> GeneratedMatchResults:
    match_overview_results = _analyze_player_score(match, puuid)
    match_rounds_results = _analyze_player_aim(match, puuid)
    match_metadata = _analyze_match_metadata(match, puuid)
    player_metadata = _get_player_info(match, puuid)
    return {
        'data': cast(MergedResults, {**match_overview_results, **match_rounds_results}),
        'currentMatchInfo': cast(ExtractedMatchMetaData, {**match_metadata}),
        'playerInfo': cast(ParsedPlayerInfo, {**player_metadata}),
    }
