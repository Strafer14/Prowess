from match_analyzer import get_match_results
from RiotHandler import RiotHandler

import pika
import os
import redis
import json
import threading
import time
from operator import itemgetter
from dotenv import load_dotenv
load_dotenv()


RABBIT_HOST = os.environ.get("RABBIT_HOST")
RABBIT_USER = os.environ.get("RABBIT_USER")
RABBIT_PWD = os.environ.get("RABBIT_PWD")

credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PWD)
parameters = pika.ConnectionParameters(
    credentials=credentials, host=RABBIT_HOST, virtual_host=RABBIT_USER)


def extract_first_match(match_stringified):
    return matches['history'][0]['matchId']


def process_message(body):
    start_time = time.time()
    parsed_body = json.loads(body.decode('utf8'))
    current_match_info = parsed_body.get("currentMatchInfo", {})
    riot = RiotHandler()
    (region, puuid) = itemgetter("region", "puuid")(parsed_body)
    (match_id, game_over, round_count, games_played, games_won) = itemgetter(
        "matchId", "isCompleted", "roundsPlayed", "gamesPlayed", "won")(current_match_info)

    first_match_id = match_id if match_id is not None and game_over is False else extract_first_match(
        riot.get_matches_list(region, puuid))
    match_data = riot.get_match_data(region, first_match_id)
    results = get_match_results(match_data, puuid)
    (current_match_id, current_round_count, is_current_match_over) = itemgetter(
        'matchId', 'roundsPlayed', 'isCompleted')(results['currentMatchInfo'])

    did_match_progress = current_match_id != match_id or current_round_count != round_count
    if did_match_progress is True:
        for key in results['data']:
            value = parsed_body['data'][key]
            results_value = results['data'][key]
            results_value += value if value is not None else 0
        if is_current_match_over is True:
            results['currentMatchInfo']['gamesPlayed'] += games_played
            results['currentMatchInfo']['won'] += games_won

    r = redis.Redis(host=os.environ.get('REDIS_URL'), db=0)
    r.set(parsed_body['sessionId'], json.dumps({**parsed_body, **results}))

    print("Successfully consumed one, took: " +
          str(round(time.time() - start_time, 2)) + " seconds")


def on_message(channel, method_frame, header_frame, body):
    t = threading.Thread(process_message(body))
    t.start()
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


def main():
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
