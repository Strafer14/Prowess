from api_service import update_player_data, \
    create_initial_session_data, \
    get_puuid
import uuid
import redis
from os import environ
from flask import Flask, json, request, abort
from logger import logger
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

if environ.get("PYTHON_ENV") == "production":
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

api = Flask(__name__)


@api.route('/api/v1/prowess/puuid', methods=['GET'])
def get_puuid():
    logger.info("Received get puuid request, {}".format(
        json.dumps(request.args)))
    game_name = request.args.get("game_name")
    tag_line = request.args.get("tag_line")
    redis_puuid = redis_client.get('{}#{}'.format(game_name, tag_line))
    if redis_puuid is not None:
        return json.dumps({"puuid": redis_puuid.decode('utf8')})
    player_puuid = get_puuid(game_name, tag_line, abort)
    puuid = player_puuid['puuid']
    redis_client.set('{}#{}'.format(game_name, tag_line), puuid)
    return json.dumps({"puuid": puuid})


@api.route('/api/v1/prowess/session', methods=['GET'])
def get_session():
    logger.info("Received get session request, {}".format(
        json.dumps(request.args)))
    region = request.args.get("region")
    puuid = request.args.get("puuid")
    session_id = request.args.get("session_id")
    if session_id is None:
        session_id = str(uuid.uuid4())
        session_data = create_initial_session_data(session_id, puuid, region)
    else:
        session_data = json.loads(redis_client.get(session_id).decode('utf8'))
    player_data = update_player_data(session_data)
    redis_client.set(json.loads(player_data)['sessionId'], player_data)
    return player_data


@api.route('/api/v1/prowess/health', methods=['GET'])
def get_health():
    return json.dumps({"health": "ok"})


if __name__ == '__main__':
    api.run()
