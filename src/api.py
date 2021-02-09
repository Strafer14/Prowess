from api_service import update_player_data, \
    create_initial_session_data, \
    extract_puuid
import uuid
from os import environ
from flask import Flask, json, request, abort
from logger import logger
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

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


@api.route('/api/v1/prowess/puuid', methods=['GET'])
def get_puuid():
    logger.info("Received get puuid request, {}".format(
        json.dumps(request.args)))
    game_name = request.args.get("game_name")
    tag_line = request.args.get("tag_line")
    redis_puuid = redis_client.get('{}#{}'.format(game_name, tag_line))
    if redis_puuid:
        return json.dumps({"puuid": redis_puuid.decode('utf8')})
    player_puuid = extract_puuid(game_name, tag_line, abort)
    puuid = player_puuid['puuid']
    redis_client.set('{}#{}'.format(str(game_name).lower(), str(tag_line).lower()), puuid)
    return json.dumps({"puuid": puuid})


@api.route('/api/v2/prowess/puuid', methods=['GET'])
def get_puuid_v2():
    logger.info("Received get puuid request, {}".format(
        json.dumps(request.args)))
    game_name = request.args.get("game_name")
    tag_line = request.args.get("tag_line")
    region = request.args.get("region")
    redis_puuid = redis_client.get('{}#{}'.format(game_name, tag_line))
    puuid = redis_puuid.decode('utf8') if redis_puuid else extract_puuid(game_name, tag_line, abort)['puuid']
    session_id = str(uuid.uuid4())
    session_data = create_initial_session_data(session_id, puuid, region)
    redis_client.set(session_id, json.dumps(session_data))
    redis_client.set('{}#{}'.format(str(game_name).lower(), str(tag_line).lower()), puuid)
    return json.dumps({"sessionId": session_id})


@api.route('/api/v1/prowess/session', methods=['GET'])
def get_session():
    logger.info("Received get session request, {}".format(
        json.dumps(request.args)))
    region = request.args.get("region")
    puuid = request.args.get("puuid")
    session_id = request.args.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        session_data = create_initial_session_data(session_id, puuid, region)
    else:
        session_data = json.loads(redis_client.get(session_id).decode('utf8'))
    player_data = update_player_data(session_data, abort)
    redis_client.set(player_data['sessionId'], json.dumps(player_data))
    return player_data


@api.route('/api/v2/prowess/session', methods=['GET'])
def get_session_v2():
    logger.info("Received get session request, {}".format(
        json.dumps(request.args)))
    session_id = request.args.get("session_id")
    session_data = json.loads(redis_client.get(session_id).decode('utf8'))
    player_data = update_player_data(session_data, abort)
    redis_client.set(player_data['sessionId'], json.dumps(player_data))
    return player_data


@api.route('/api/v1/prowess/session', methods=['PUT'])
def reset_session():
    logger.info("Received reset session request, {}".format(
        json.dumps(request.args)))
    session_id = request.args.get("session_id")
    session_data = json.loads(redis_client.get(session_id).decode('utf8'))
    initial_session_data = create_initial_session_data(session_id, session_data['puuid'], session_data['region'])
    initial_session_data['currentMatchInfo'] = {
        "won": 0,
        "gamesPlayed": 0,
        "matchId": session_data['currentMatchInfo']['matchId'],
        "isCompleted": False,
        "roundsPlayed": 0
    }
    redis_client.set(session_id, json.dumps(initial_session_data))
    return initial_session_data


@api.route('/api/v1/prowess/health', methods=['GET'])
def get_health():
    return json.dumps({"health": "ok"})


if __name__ == '__main__':
    api.run(host='0.0.0.0', port=8000)
