import json
import redis
from src.RiotHandler import RiotHandler
from os import environ


def main(event, context):
    path_params = event.get('pathParameters', {})
    game_name = path_params.get("gameName")
    tag_line = path_params.get("tagLine")
    r = redis.Redis(host=environ.get('REDIS_URL'), db=0)
    redis_puuid = r.get('{}#{}'.format(game_name, tag_line))
    if redis_puuid is not None:
        player_puuid = {"puuid": redis_puuid.decode('utf8')}
    else:
        riot_handler = RiotHandler()
        player_puuid = riot_handler.get_puuid(game_name, tag_line)
        r.set('{}#{}'.format(game_name, tag_line),
              player_puuid.get('puuid', 'Unknown'))
    return {
        "statusCode": 200,
        "body": json.dumps(player_puuid)
    }


if __name__ == "__main__":
    main('', '')
