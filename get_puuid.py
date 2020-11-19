import json
import redis
from os import environ

from src.logger import logger


def main(event, context):
    path_params = event.get('pathParameters', {})
    game_name = path_params.get("gameName")
    tag_line = path_params.get("tagLine")
    r = redis.Redis(host=environ.get("REDIS_URL"), port=environ.get(
        "REDIS_PORT"), password=environ.get("REDIS_PWD"), db=0)
    redis_puuid = r.get('{}#{}'.format(game_name, tag_line))
    try:
        if redis_puuid is not None:
            player_puuid = {"puuid": redis_puuid.decode('utf8')}
        else:
            payload = {"game_name": game_name, "tag_line": tag_line}
            player_puuid = requests.get(environ.get(
                "CONSUMER_API_URL"), params=payload).json()
            r.set('{}#{}'.format(game_name, tag_line),
                  player_puuid.get('puuid'))
        return {
            "statusCode": 200,
            "body": json.dumps(player_puuid)
        }
    except RuntimeError as e:
        logger.error(e)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "session id does not exist"})
        }


if __name__ == "__main__":
    main('', '')
