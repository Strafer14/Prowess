import pika
import os
import redis
import json
import threading
import time
from RiotHandler import RiotHandler
from match_analyzer import get_match_results

RABBIT_HOST = os.environ.get("RABBIT_HOST")
RABBIT_USER = os.environ.get("RABBIT_USER")
RABBIT_PWD = os.environ.get("RABBIT_PWD")

credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PWD)
parameters = pika.ConnectionParameters(
    credentials=credentials, host=RABBIT_HOST, virtual_host=RABBIT_USER)


def process_message(body):
    start_time = time.time()
    parsed_body = json.loads(body.decode('utf8'))
    current_match_info = parsed_body.get("currentMatchInfo", {})
    riot = RiotHandler()

    match_id = current_match_info.get("matchId")
    game_over = current_match_info.get("isCompleted")
    round_count = current_match_info.get("roundsPlayed")
    games_played = current_match_info.get('gamesPlayed')
    games_won = current_match_info.get('won')
    if match_id is not None and game_over is False:
        first_match_id = current_match_info.get("matchId")
    else:
        matches = json.loads(riot.get_matches_list(
            parsed_body.get('region'), parsed_body.get('puuid')))
        first_match_id = matches['history'][0]['matchId']
    match_data = json.loads(riot.get_match_data(
        parsed_body.get('region'), first_match_id))
    results = get_match_results(match_data, parsed_body['puuid'])

    current_match_id = results['currentMatchInfo']['matchId']
    current_round_count = results['currentMatchInfo']['roundsPlayed']
    is_current_match_over = results['currentMatchInfo']['isCompleted']

    did_match_progress = current_match_id != match_id or current_round_count != round_count
    if did_match_progress is True:
        for key in results['data']:
            if results['data'][key] is not None and parsed_body['data'][key] is not None:
                results['data'][key] += parsed_body['data'][key]
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
