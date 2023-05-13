import json
from typing import cast

from aws_lambda_typing import context, events

from src.api_utils import build_error_response, build_response
from src.dynamodb import get_session_data, set_session_data
from src.logger import logger
from src.types.session_data import Session
from src.valorant_data_parsing import update_player_data


def main(event: events.APIGatewayProxyEventV2, context: context.Context):
    try:
        session_id = event.get('pathParameters', {}).get('session_id')
        if not session_id:
            return build_response(400, {'error': 'Bad Request'})
        logger.info(f'Received get session request, {session_id}')
        if existing_session := get_session_data(session_id).get('Item', {}).get('gameData', {}).get('S'):
            session_data: Session = json.loads(existing_session)
        else:
            return build_response(404, {'error': "Couldn't find session data"})
        player_data = update_player_data(session_data)
        set_session_data(player_data['sessionId'], player_data)
        return build_response(200, cast(dict, player_data))
    except Exception as e:
        logger.error(f'Update and Retrieve Data - Received error {e}')
        return build_error_response()


if __name__ == '__main__':
    main('', '')   # type: ignore
