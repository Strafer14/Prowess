from match_analyzer import get_match_results
from RiotHandler import RiotHandler

import pika
import os
import redis
import json
import threading
import time
import logging
from operator import itemgetter
from dotenv import load_dotenv
load_dotenv()

RABBIT_HOST = os.environ.get("RABBIT_HOST")
RABBIT_USER = os.environ.get("RABBIT_USER")
RABBIT_PWD = os.environ.get("RABBIT_PWD")


def extract_first_match(matches):
    return matches.get('history', [{}])[0].get('matchId')


def distil_data(parsed_body):
    logging.debug("Parsing body received from consumer: " +
                  json.dumps(parsed_body))
    current_match_info = parsed_body.get("currentMatchInfo", {})
    (region, puuid) = itemgetter("region", "puuid")(parsed_body)
    try:
        (match_id, game_over, round_count, games_played, games_won) = itemgetter(
            "matchId", "isCompleted", "roundsPlayed", "gamesPlayed", "won")(current_match_info)
    except:
        (match_id, game_over, round_count, games_played,
         games_won) = (None, False, 0, 0, 0)

    riot = RiotHandler()
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


def update_session_in_db(data):
    r = redis.Redis(host=localhost, port=os.environ.get(
        "REDIS_PORT"), password=os.environ.get("REDIS_PWD"), db=0)
    r.set(data['sessionId'], json.dumps(data))


def process_message(body):
    start_time = time.time()
    try:
        parsed_body = json.loads(body.decode('utf8'))
        update_session_in_db(distil_data(parsed_body))
        logging.info("Successfully processed consumed message, took: " +
                     str(round(time.time() - start_time, 2)) + " seconds")
    except RuntimeError as e:
        logging.error(
            "An error occured when parsing consumed message {}: {}".format(body, e))


def on_message(channel, method_frame, header_frame, body):
    t = threading.Thread(process_message(body))
    t.start()
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


def main():
    logging.info("Starting service")
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PWD)
    parameters = pika.ConnectionParameters(
        credentials=credentials, host=RABBIT_HOST, virtual_host=RABBIT_USER)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.basic_consume('lambda-riot-api-requests', on_message)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == '__main__':
    main()
