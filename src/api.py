import uuid
from os import environ

import sentry_sdk
from flask import Flask, abort, json, request
from sentry_sdk.integrations.flask import FlaskIntegration

from api_service import (create_initial_session_data, extract_puuid,
                         find_region, update_player_data)
from logger import logger

if environ.get("PYTHON_ENV") == "production":
    import redis

    sentry_sdk.init(
        dsn=environ.get("SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )

    redis_client = redis.Redis(
        host=environ.get("REDIS_HOST"),
        port=environ.get(
            "REDIS_PORT"),
        password=environ.get("REDIS_PWD") if environ.get(
            "PYTHON_ENV") == "production" else None,
        db=0)
else:
    import fakeredis

    server = fakeredis.FakeServer()
    redis_client = fakeredis.FakeStrictRedis(server=server)
api = Flask(__name__)


@api.route('/api/v2/prowess/puuid', methods=['GET'])
def get_puuid():
    logger.info("Received get puuid request, {}".format(
        json.dumps(request.args)))
    game_name = request.args.get("game_name")
    tag_line = request.args.get("tag_line")
    region = request.args.get("region")
    redis_puuid = redis_client.get('{}#{}'.format(game_name, tag_line))
    puuid = redis_puuid.decode('utf8') if redis_puuid else extract_puuid(
        game_name, tag_line, abort)['puuid']
    if not region or region == "undefined":
        region = find_region(puuid, abort)
    session_id = str(uuid.uuid4())
    session_data = create_initial_session_data(session_id, puuid, region)
    redis_client.set(session_id, json.dumps(session_data))
    redis_client.set('{}#{}'.format(
        str(game_name).lower(), str(tag_line).lower()), puuid)
    return json.dumps({"sessionId": session_id, "region": region, "puuid": puuid})


@api.route('/api/v2/prowess/session', methods=['GET'])
def get_session():
    logger.info("Received get session request, {}".format(
        json.dumps(request.args)))
    session_id = request.args.get("session_id")
    if redis_client.get(session_id):
        session_data = json.loads(redis_client.get(session_id).decode('utf8'))
    else:
        abort(404)
    player_data = update_player_data(session_data, abort)
    redis_client.set(player_data['sessionId'], json.dumps(player_data))
    return player_data


@api.route('/api/v1/prowess/health', methods=['GET'])
def get_health():
    return json.dumps({"health": "ok"})


if __name__ == '__main__':
    api.run(host='0.0.0.0', port=8000)
