import json
import redis
from os import environ
from src.api_service import update_player_data
from src.logger import logger


def main(event, context):
    try:
        redis_host = 'localhost' if environ.get('PYTHON_ENV') == 'development' else environ.get('REDIS_HOST')
        redis_port = environ.get('REDIS_PORT', 6379)
        redis_password = environ.get('REDIS_PWD')
        redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=0)

        session_id = event.get('pathParameters', {}).get('session_id')
        if not session_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True,
                },
            }
        logger.info(f'Received get session request, {session_id}')
        if redis_client.get(session_id):
            session_data = json.loads(redis_client.get(session_id).decode('utf8'))
        else:
            raise Exception("Couldn't find session data")
        player_data = update_player_data(session_data)
        redis_client.set(player_data['sessionId'], json.dumps(player_data))
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps(player_data),
        }
    except Exception as e:
        logger.error(f'Update and Retrieve Data - Received error {e.with_traceback()}')
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps({'error': 'An error has occurred'}),
        }


if __name__ == '__main__':
    main('', '')
