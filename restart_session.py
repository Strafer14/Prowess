import json
from typing import cast

from aws_lambda_typing import context, events

from src.api_utils import build_error_response, build_response
from src.dynamodb import get_session_data, set_session_data
from src.logger import logger
from src.types.session_data import Session
from src.valorant_data_parsing import create_initial_session_data


def main(event: events.APIGatewayProxyEventV2, context: context.Context):
    try:
        session_id = event.get('queryStringParameters', {}).get('session_id')
        if not session_id:
            return build_response(400, {'error': 'Bad Request'})
        if found_session := get_session_data(session_id).get('Item', {}).get('gameData', {}).get('S'):
            session_data: Session = json.loads(found_session)
        else:
            return build_response(404, {'error': "Couldn't find session data"})
        blank_player_session_data = create_initial_session_data(
            session_data['sessionId'],
            session_data['puuid'],
            session_data['region'])
        set_session_data(session_data['sessionId'], blank_player_session_data)
        return build_response(200, cast(dict, blank_player_session_data))
    except Exception as e:
        logger.error(f'Restart Session - Received error {e}')
        return build_error_response()


if __name__ == '__main__':
    main('', '')   # type: ignore
