import json
from os import environ

import boto3

from src.types.session_data import Session

SESSIONS_TABLE = environ['SESSIONS_TABLE']
PUUID_TABLE = environ['PUUID_TABLE']
PYTHON_ENV = environ.get('PYTHON_ENV')

if PYTHON_ENV == 'development':
    client = boto3.client('dynamodb', region_name='localhost', endpoint_url='http://localhost:8000')
else:
    client = boto3.client('dynamodb')


def get_session_data(session_id: str):
    response = client.get_item(
        TableName=SESSIONS_TABLE,
        Key={
            'sessionId': {'S': session_id},
        },
    )
    return response


def set_session_data(session_id: str, session_data: Session):
    return client.put_item(
        TableName=SESSIONS_TABLE,
        Item={
            'sessionId': {'S': session_id},
            'gameData': {'S': json.dumps(session_data)},
        },
    )


def get_puuid_data(player_identity: str):
    response = client.get_item(
        TableName=PUUID_TABLE,
        Key={
            'playerIdentity': {'S': player_identity},
        },
    )
    return response


def set_puuid_data(player_identity: str, puuid: str):
    return client.put_item(
        TableName=PUUID_TABLE,
        Item={
            'playerIdentity': {'S': player_identity},
            'puuid': {'S': puuid},
        },
    )
