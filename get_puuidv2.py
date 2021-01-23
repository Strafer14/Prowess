import json
import requests
from os import environ

from src.logger import logger


def main(event, context):
    path_params = event.get('pathParameters', {})
    region = path_params.get("region")
    game_name_with_tagline = path_params.get("game_name_with_tagline")
    if not game_name_with_tagline or not region:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            }
        }
    [game_name, tag_line] = game_name_with_tagline.split("#")
    payload = {"game_name": game_name, "tag_line": tag_line, "region": region}
    try:
        request_result = requests.get(environ.get(
            "CONSUMER_API_URL") + "/api/v2/prowess/puuid", params=payload)
        if request_result.status_code == requests.codes.not_found:
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True,
                }
            }
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            "body": request_result.text
        }
    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps({"error": "An error has occurred"})
        }


if __name__ == "__main__":
    main('', '')
