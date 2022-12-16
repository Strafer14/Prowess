from src.logger import logger
import json
import uuid
import redis
from os import environ
from src.api_service import create_initial_session_data, extract_puuid, find_region


def main(event, context):
    redis_client = redis.Redis(
        host=environ.get("REDIS_HOST") or "localhost",
        port=environ.get("REDIS_PORT") or 6379,
        password=environ.get("REDIS_PWD") if environ.get(
            "PYTHON_ENV") == "production" else None,
        db=0)

    path_params = event.get('pathParameters', {})
    logger.info(f"Received request, {path_params}")
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
    if not tag_line or len(tag_line) <= 1:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            }
        }
    payload = {"game_name": game_name, "tag_line": tag_line, "region": region}
    logger.info(f"Received get puuid request, {payload}")
    try:
        redis_puuid = redis_client.get(f"{game_name}#{tag_line}")
        puuid = redis_puuid.decode('utf8') if redis_puuid else extract_puuid(
            game_name, tag_line)['puuid']
        # search for region
        if not region or region == "undefined":
            region = find_region(puuid)

        session_id = str(uuid.uuid4())
        session_data = create_initial_session_data(session_id, puuid, region)
        redis_client.set(session_id, json.dumps(session_data))
        redis_client.set('{}#{}'.format(
            str(game_name).lower(), str(tag_line).lower()), puuid)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps(
                {
                    "sessionId": session_id,
                    "region": region,
                    "puuid": puuid
                }
            )
        }
    except Exception as e:
        logger.error(f"Received error {e}")
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
