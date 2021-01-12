from src.match_analyzer import get_match_results

from sentry_sdk import capture_exception
import json
from src.ValorantApi import ValorantApi
from operator import itemgetter
from src.logger import logger

valorant_client = ValorantApi()


def extract_first_match(matches):
    return matches.get('history', [{}])[0].get('matchId')


def increment_player_stats(parsed_body):
    logger.debug("Parsing body received from api: " +
                 json.dumps(parsed_body))

    current_match_info = parsed_body.get("currentMatchInfo", {})
    (region, puuid) = itemgetter("region", "puuid")(parsed_body)
    try:
        (match_id, game_over, round_count, games_played, games_won) = itemgetter(
            "matchId", "isCompleted", "roundsPlayed", "gamesPlayed", "won")(current_match_info)
    except KeyError:
        (match_id, game_over, round_count, games_played,
         games_won) = (None, False, 0, 0, 0)
    previous_data = parsed_body.get('data', {})

    first_match_id = match_id if match_id is not None and game_over is False else extract_first_match(
        valorant_client.get_matches_list(region, puuid))
    match_data = valorant_client.get_match_data(region, first_match_id)
    results = get_match_results(match_data, puuid)
    (current_match_id, current_round_count, is_current_match_over) = itemgetter(
        'matchId', 'roundsPlayed', 'isCompleted')(results['currentMatchInfo'])
    did_match_progress = current_match_id != match_id or current_round_count != round_count
    if did_match_progress is True:
        for key in results['data']:
            old_value = previous_data.get(key, 0)
            results['data'][key] += old_value
        if is_current_match_over is True:
            results['currentMatchInfo']['gamesPlayed'] += games_played
            results['currentMatchInfo']['won'] += games_won
        else:
            results['currentMatchInfo']['gamesPlayed'] = games_played
            results['currentMatchInfo']['won'] = games_won
        return {**parsed_body, **results}
    return parsed_body


def update_player_data(body):
    try:
        result = json.dumps(increment_player_stats(body))
        return result
    except Exception as e:
        capture_exception(e)
        logger.error(
            "An error occurred when parsing consumed message {}: {}".format(body, e))


def create_initial_session_data(session_id, puuid, region):
    return {
        "sessionId": session_id,
        "currentMatchInfo": {},
        "playerInfo": {},
        "puuid": puuid,
        "region": region,
        "data": {
            "score": 0,
            "roundsPlayed": 0,
            "kills": 0,
            "deaths": 0,
            "assists": 0,
            "playtimeMillis": 0,
            "legshots": 0,
            "bodyshots": 0,
            "headshots": 0,
            "won": 0,
            "games_played": 0,
        }
    }


def extract_puuid(game_name, tag_line, abort):
    try:
        valorant_puuid_data = valorant_client.get_puuid(game_name, tag_line)
        if valorant_puuid_data.get('puuid') is None:
            logger.warn("Empty puuid, {}".format(valorant_puuid_data))
            status_code = valorant_puuid_data.get("status", {}).get("status_code")
            if status_code is not None:
                abort(status_code)
        else:
            logger.info("Retrieved puuid {} from Valorant".format(valorant_puuid_data['puuid']))
        return valorant_puuid_data
    except Exception as e:
        capture_exception(e)
    return {"status": {"status_code": 500}}
