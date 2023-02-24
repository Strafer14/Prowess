import json

from src.api_service import create_initial_session_data
from src.logger import logger
from src.redis import create_redis_client


def main(event, context):
    try:
        redis_client = create_redis_client()

        session_id = event.get('queryStringParameters').get('session_id')
        if not session_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True,
                },
            }
        if redis_client.get(session_id):
            session_data = json.loads(redis_client.get(session_id).decode('utf8'))
        else:
            raise Exception("Couldn't find session data")
        blank_player_session_data = create_initial_session_data(
            session_data['sessionId'],
            session_data['puuid'],
            session_data['region'])
        redis_client.set(session_data['sessionId'], json.dumps(blank_player_session_data))
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps(blank_player_session_data),
        }
    except Exception as e:
        logger.error(f'Restart Session - Received error {e.with_traceback()}')
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
