from match_analyzer import get_match_results
from RiotHandler import RiotHandler

import os
import json
import time
from operator import itemgetter
from logger import logger


def extract_first_match(matches):
    return matches.get('history', [{}])[0].get('matchId')


def distil_data(parsed_body, riot):
    logger.debug("Parsing body received from consumer: " +
                 json.dumps(parsed_body))
    current_match_info = parsed_body.get("currentMatchInfo", {})
    (region, puuid) = itemgetter("region", "puuid")(parsed_body)
    try:
        (match_id, game_over, round_count, games_played, games_won) = itemgetter(
            "matchId", "isCompleted", "roundsPlayed", "gamesPlayed", "won")(current_match_info)
    except:
        (match_id, game_over, round_count, games_played,
         games_won) = (None, False, 0, 0, 0)

    first_match_id = match_id if match_id is not None and game_over is False else extract_first_match(
        riot.get_matches_list(region, puuid))
    match_data = riot.get_match_data(region, first_match_id)
    results = get_match_results(match_data, puuid)
    (current_match_id, current_round_count, is_current_match_over) = itemgetter(
        'matchId', 'roundsPlayed', 'isCompleted')(results['currentMatchInfo'])

    did_match_progress = current_match_id != match_id or current_round_count != round_count
    results['data'] = {key: results['data'][key]
                       for key in results['data'] if key != 'abilityCasts'}
    if did_match_progress is True:
        for key in results['data']:
            value = parsed_body['data'][key]
            results_value = results['data'][key]
            results_value += value if value is not None else 0
        if is_current_match_over is True:
            results['currentMatchInfo']['gamesPlayed'] += games_played
            results['currentMatchInfo']['won'] += games_won
    return {**parsed_body, **results}


def update_session_in_db(data, redis):
    print(data)
    # redis.set(data['sessionId'], data)


def process_message(body, redis, riot):
    start_time = time.time()
    try:
        parsed_body = body
        result = json.dumps(distil_data(parsed_body, riot))
        update_session_in_db(result, redis)
        print("Successfully processed consumed message, took: " +
              str(round(time.time() - start_time, 2)) + " seconds")
        return result
    except RuntimeError as e:
        logger.error(
            "An error occured when parsing consumed message {}: {}".format(body, e))
