import json
from typing import cast

from ratelimit import RateLimitException  # type: ignore

from src.logger import logger
from src.match_analyzer import get_match_results
from src.types.riot import GetPuuidResponse
from src.types.session_data import Session
from src.valorant_riot_api import ValorantApi

valorant_client = ValorantApi()


def extract_first_match(matches):
    if matches.get('history') and len(matches.get('history')) > 0:
        return matches.get('history', [{}])[0].get('matchId')
    raise RuntimeError('The match list is empty')


def increment_player_stats(parsed_body: Session) -> Session:
    logger.debug('Parsing body received from api: ' +
                 json.dumps(parsed_body))

    current_match_info = parsed_body.get('currentMatchInfo', {})
    region = parsed_body['region']
    puuid = parsed_body['puuid']
    match_id = current_match_info.get('matchId')
    game_over = current_match_info.get('isCompleted', False)
    games_played = current_match_info.get('gamesPlayed', 0)
    games_won = current_match_info.get('won', 0)
    previous_data = parsed_body.get('data', {})

    first_match_id = match_id if match_id and not game_over else extract_first_match(
        valorant_client.get_matches_list(region, puuid))
    match_data = valorant_client.get_match_data(region, first_match_id)
    results = get_match_results(match_data, puuid)
    current_match_id = results['currentMatchInfo'].get('matchId')
    is_current_match_over = results['currentMatchInfo'].get('isCompleted')
    queue_id = results['currentMatchInfo'].get('queueId')
    parsed_body['currentMatchInfo']['isCompleted'] = is_current_match_over
    did_match_progress = current_match_id != match_id
    if did_match_progress and queue_id in ['competitive', 'unrated']:
        for key in results['data']:
            old_value = previous_data.get(key, 0)
            results['data'][key] += old_value  # type: ignore
        if is_current_match_over:
            results['currentMatchInfo']['gamesPlayed'] += games_played
            results['currentMatchInfo']['won'] += games_won
        else:
            results['currentMatchInfo']['gamesPlayed'] = games_played
            results['currentMatchInfo']['won'] = games_won
        return cast(Session, {**parsed_body, **results})
    return parsed_body


def update_player_data(body: Session) -> Session:
    try:
        result = increment_player_stats(body)
        return result
    except RateLimitException as e:
        logger.error(f'We hit the RATE LIMIT when parsing consumed message {body}: {e}')
        return body
    except Exception as e:
        logger.error(f'An error occurred when parsing consumed message {body}: {e}')
        raise e


def create_initial_session_data(session_id, puuid, region) -> Session:
    return {
        'sessionId': session_id,
        'currentMatchInfo': {
            'won': 0,
            'gamesPlayed': 0,
            'matchId': None,
            'queueId': None,
            'isCompleted': None,
            'roundsPlayed': 0,
        },
        'playerInfo': {'rank': 0, 'characterId': ''},
        'puuid': puuid,
        'region': region,
        'data': {
            'score': 0,
            'roundsPlayed': 0,
            'kills': 0,
            'deaths': 0,
            'assists': 0,
            'playtimeMillis': 0,
            'legshots': 0,
            'bodyshots': 0,
            'headshots': 0,
            'won': 0,
            'games_played': 0,
        },
    }


def extract_puuid(game_name, tag_line) -> GetPuuidResponse:
    try:
        valorant_puuid_data = valorant_client.get_puuid(
            game_name, tag_line)
        if valorant_puuid_data.get('puuid'):
            logger.info(
                f"Retrieved puuid { valorant_puuid_data['puuid']} from Valorant",
            )
            return valorant_puuid_data
        raise Exception('Unexpected error when getting puuid from Riot')
    except RateLimitException as e:
        logger.error(f'We hit the RATE LIMIT when parsing request: {e}')
        raise e
    except Exception as e:
        logger.error(f'An error occurred when parsing request: {e}')
        raise e


def find_region(puuid: str) -> str:
    region_list = ['NA', 'EU', 'KR', 'BR', 'AP', 'LATAM']
    try:
        for region in region_list:
            valorant_matches = valorant_client.get_matches_list(region, puuid)
            if len(valorant_matches.get('history', [])) > 0:
                return region
    except RateLimitException as e:
        logger.error(f'We hit the RATE LIMIT when parsing request: {e}')
        raise e
    except Exception as e:
        logger.error(f'An error occurred when parsing request: {e}')
        raise e
    raise Exception('Could not find region')
