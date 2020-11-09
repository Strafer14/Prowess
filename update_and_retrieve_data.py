import json
import uuid
import redis
import asyncio
from os import environ
from threading import Thread
from src.publisher import publish

actions = {
    "session_created": 100,
    "data_updated": 200
}

loop = asyncio.get_event_loop()
def f(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
t = Thread(target=f, args=(loop,))
t.start()  

def create_new_session(puuid, region):
    session_id = str(uuid.uuid4())
    default_full_session_dict = {
        "sessionId": session_id,
        "currentMatchInfo": {},
        "puuid": puuid,
        "region": region,
        "data": {
            "score": 0,
            "roundsPlayed": 0,
            "kills": 0,
            "deaths": 0,
            "assists": 0,
            "playtimeMillis": 0,
            "abilityCasts": None,
            "legshots": 0,
            "bodyshots": 0,
            "headshots": 0,
            "won": 0,
            "games_played": 0,
        },
    }
    async def set_default_dict():
        r = redis.Redis(host=environ.get('REDIS_URL'), db=0)
        r.set(session_id, json.dumps(default_full_session_dict))
    asyncio.run_coroutine_threadsafe(set_default_dict(), loop)
    return {
        "statusCode": 200,
        "body": json.dumps({
            **default_full_session_dict,
            "action": actions["session_created"]
        })
    }


def main(event, context):
    session_id = event.get('queryStringParameters').get('session_id')
    puuid = event.get('pathParameters', {}).get('puuid')
    region = event.get('queryStringParameters').get('region')
    if session_id is None:
        return create_new_session(puuid, region)
    try:
        r = redis.Redis(host=environ.get('REDIS_URL'), db=0)
        session_data = json.loads(r.get(session_id).decode('utf8'))
        asyncio.run_coroutine_threadsafe(publish(json.dumps(session_data)), loop)
        return {
            "statusCode": 200,
            "body": json.dumps({**session_data, "action": actions["data_updated"]})
        }
    except RuntimeError as e:
        print(e)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "session id does not exist"})
        }


if __name__ == "__main__":
    main('', '')
