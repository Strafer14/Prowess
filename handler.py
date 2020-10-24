import json
from src.RiotHandler import RiotHandler


def main(event, context):
    query_params = event.get("multiValueQueryStringParameters")
    game_name = query_params.get("gameName", [''])[0]
    tag_line = query_params.get("tagLine", [''])[0]
    # check if puuid exists in redis, if not >>>
    riot_handler = RiotHandler()
    player_puuid = riot_handler.get_puuid(game_name, tag_line)
    # save puuid to redis
    return {
        "statusCode": 200,
        "body": json.dumps(player_puuid)
    }


if __name__ == "__main__":
    main('', '')
