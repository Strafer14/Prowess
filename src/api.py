from api_service import process_message
import uuid
import redis
from os import environ
from sys import exc_info
from flask import Flask, json, request, abort
from RiotHandler import RiotHandler
from logger import logger
import sentry_sdk
from sentry_sdk import capture_exception
from sentry_sdk.integrations.flask import FlaskIntegration

if environ.get("PYTHON_ENV") == "production":
    sentry_sdk.init(
        dsn=environ.get("SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )
r = redis.Redis(
    host=environ.get("REDIS_HOST"),
    port=environ.get(
        "REDIS_PORT"),
    password=environ.get("REDIS_PWD") if environ.get(
        "PYTHON_ENV") == "production" else None,
    db=0)

riot_handler = RiotHandler()
api = Flask(__name__)


@api.route('/api/v1/prowess/puuid', methods=['GET'])
def get_puuid():
    logger.info("Received get puuid request, {}".format(
        json.dumps(request.args)))
    game_name = request.args.get("game_name")
    tag_line = request.args.get("tag_line")
    try:
        redis_puuid = r.get('{}#{}'.format(game_name, tag_line))
        if redis_puuid is not None:
            player_puuid = {"puuid": redis_puuid.decode('utf8')}
        else:
            player_puuid = riot_handler.get_puuid(game_name, tag_line)
            if player_puuid.get("status", {}).get("status_code") is not None:
                abort(player_puuid.get("status", {}).get("status_code"))
            r.set('{}#{}'.format(game_name, tag_line),
                  player_puuid.get('puuid'))
        return json.dumps({"puuid": player_puuid.get('puuid', 'Unknown')})
    except Exception as e:
        capture_exception(e)


@api.route('/api/v1/prowess/session', methods=['GET'])
def get_session():
    logger.info("Received get session request, {}".format(
        json.dumps(request.args)))
    region = request.args.get("region")
    puuid = request.args.get("puuid")
    session_id = request.args.get("session_id")
    if session_id is None:
        session_id = str(uuid.uuid4())
        logger.info("Creating session {} for user {}".format(
            session_id, puuid))
        session_data = {
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
                "legshots": 0,
                "bodyshots": 0,
                "headshots": 0,
                "won": 0,
                "games_played": 0,
            }
        }
    else if region is not None:
        session_data = json.loads(r.get(session_id).decode('utf8'))
    return process_message(session_data, r, riot_handler)


@api.route('/api/v1/prowess/health', methods=['GET'])
def get_health():
    return json.dumps({"health": "ok"})


if __name__ == '__main__':
    api.run()
