import json
import requests
from os import environ

from src.logger import logger


def main(event, context):
    path_params = event.get('pathParameters', {})
    session_id = path_params.get("session_id")
    if not session_id:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            }
        }
    payload = {"session_id": session_id}
    try:
        request_result = requests.put(environ.get(
            "CONSUMER_API_URL") + "/api/v1/prowess/session", params=payload)
        if request_result.status_code == requests.codes.not_found:
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True,
                }
            }
        session_data = request_result.json()
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps({**session_data})
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
