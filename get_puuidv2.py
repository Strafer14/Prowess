import json
import requests
from os import environ


def main(event, context):
    path_params = event.get('pathParameters', {})
    region = path_params.get("region")
    game_name_with_tagline = path_params.get("game_name_with_tagline")
    if not game_name_with_tagline or game_name_with_tagline == "undefined":
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            }
        }
    [game_name, tag_line] = game_name_with_tagline.split("_$_")
    payload = {"game_name": game_name, "tag_line": tag_line, "region": region}
    request_result = requests.get("{}/api/v2/prowess/puuid".format(environ.get(
        "CONSUMER_API_URL")), params=payload)
    if request_result.status_code != requests.codes.ok:
        return {
            "statusCode": request_result.status_code,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps({"error": "An error has occurred"})
        }
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        "body": request_result.text
    }


if __name__ == "__main__":
    main('', '')
