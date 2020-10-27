import json
import redis
from src.RiotHandler import RiotHandler
from os import environ


def main(event, context):
    query_params = event.get("multiValueQueryStringParameters")
    game_name = query_params.get("gameName", [''])[0]
    tag_line = query_params.get("tagLine", [''])[0]
    r = redis.Redis(host=environ.get('REDIS_URL'), db=0)
    redis_puuid = r.get('{}#{}'.format(game_name, tag_line))
    if redis_puuid is not None:
        player_puuid = json.dumps({"puuid": redis_puuid.decode(
            'utf8'), "gameName": game_name, "tagLine": tag_line})
    else:
        riot_handler = RiotHandler()
        player_puuid = riot_handler.get_puuid(game_name, tag_line)
        r.set('{}#{}'.format(game_name, tag_line),
              json.loads(player_puuid)['puuid'])
    return {
        "statusCode": 200,
        "body": player_puuid
    }


if __name__ == "__main__":
    main('', '')
