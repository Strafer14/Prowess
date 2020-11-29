import json
import requests
from os import environ

from src.logger import logger


def main(event, context):
    path_params = event.get('pathParameters', {})
    game_name = path_params.get("gameName")
    tag_line = path_params.get("tagLine")
    payload = {"game_name": game_name, "tag_line": tag_line}
    try:
        request_result = requests.get(environ.get(
            "CONSUMER_API_URL") + "/api/v1/prowess/puuid", params=payload)
        if request_result.status_code == requests.codes.not_found:
            return {
                "statusCode": 404
            }
        player_puuid = request_result.text
        return {
            "statusCode": 200,
            "body": player_puuid
        }
    except RuntimeError as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "An error has occurred"})
        }


if __name__ == "__main__":
    main('', '')
