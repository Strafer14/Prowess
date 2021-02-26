import json
import requests
import asyncio
from os import environ
from threading import Thread

from src.logger import logger

loop = asyncio.get_event_loop()


def f(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


t = Thread(target=f, args=(loop,))
t.start()


def main(event, context):
    session_id = event.get('pathParameters', {}).get('session_id')
    if not session_id:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
        }
    payload = {"session_id": session_id}
    logger.debug(payload)
    session_data = requests.get(environ.get(
        "CONSUMER_API_URL") + "/api/v2/prowess/session", params=payload)
    if session_data.status_code != requests.codes.ok:
        return {
            "statusCode": session_data.status_code,
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
        "body": session_data.text
    }


if __name__ == "__main__":
    main('', '')
