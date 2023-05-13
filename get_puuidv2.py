import uuid

from aws_lambda_typing import context, events

from src.api_utils import build_error_response, build_response
from src.dynamodb import get_puuid_data, set_puuid_data, set_session_data
from src.logger import logger
from src.valorant_data_parsing import (create_initial_session_data,
                                       extract_puuid, find_region)

UNKNOWN_REGION = 'undefined'


def main(event: events.APIGatewayProxyEventV2, context: context.Context):
    try:
        path_params = event.get('pathParameters', {})
        logger.info(f'Received request, {path_params}')
        # available regions are: "NA", "AP", "BR", "EU", "KR", "LATAM"
        region = path_params.get('region')
        game_name_with_tagline = path_params.get('game_name_with_tagline')
        if not game_name_with_tagline or game_name_with_tagline == 'undefined':
            return build_response(400, {'error': 'Bad Request'})
        [game_name, tag_line] = game_name_with_tagline.split('_$_')
        lowercase_game_name = str(game_name).lower()
        lowercase_tag_line = str(tag_line).lower()
        key = f'{lowercase_game_name}#{lowercase_tag_line}'
        if not tag_line or len(tag_line) <= 1:
            return build_response(400, {'error': 'Bad Request'})
        payload = {'game_name': game_name, 'tag_line': tag_line, 'region': region}
        logger.info(f'Received get puuid request, {payload}')

        dynamo_saved_puuid_payload = get_puuid_data(key)
        if saved_puuid := dynamo_saved_puuid_payload.get('Item', {}).get('puuid', {}).get('S'):
            puuid = saved_puuid
        else:
            puuid = extract_puuid(game_name, tag_line)['puuid']

        # search for region
        if not region or region == UNKNOWN_REGION:
            region = find_region(puuid)

        session_id = str(uuid.uuid4())
        session_data = create_initial_session_data(session_id, puuid, region)
        set_session_data(session_id, session_data)
        set_puuid_data(key, puuid)
        return build_response(200,
                              {
                                  'sessionId': session_id,
                                  'region': region,
                                  'puuid': puuid,
                              },
                              )
    except Exception as e:
        logger.error(f'Get PUUID - Received error {e}')
        return build_error_response()


if __name__ == '__main__':
    main('', '')   # type: ignore
