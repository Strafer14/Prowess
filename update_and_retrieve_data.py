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
    session_id = event.get('queryStringParameters').get('session_id')
    puuid = event.get('pathParameters', {}).get('puuid')
    region = event.get('queryStringParameters').get('region')
    payload = {"region": region, "puuid": puuid, "session_id": session_id}
    try:
        session_data = requests.get(environ.get(
            "CONSUMER_API_URL") + "/api/v1/prowess/session", params=payload).json()
        return {
            "statusCode": 200,
            "body": json.dumps({**session_data})
        }
    except RuntimeError as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "An error has occurred"})
        }


if __name__ == "__main__":
    main('', '')
