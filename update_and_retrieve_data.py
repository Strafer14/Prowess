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
    if puuid is None or region is None:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
        }
    payload = {"region": region, "puuid": puuid, "session_id": session_id}
    logger.debug(payload)
    try:
        session_data = requests.get(environ.get(
            "CONSUMER_API_URL") + "/api/v1/prowess/session", params=payload)
        try:
            session_data = session_data.json()
        except Exception as e:
            logger.error("Could not parse response data {}".format(str(session_data)))
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
