import json
import RiotHandler

def main(event, context):
    game_name = event.get("gameName")
    tag_line = event.get("tagLine")
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
