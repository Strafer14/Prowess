import json


def main(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    # handle websocket messages
    # messages like connected -> starting session
    # reconnected -> connecting to existing session_id
    # while player is connected he gets a response every 60 seconds (might skip sometimes due to rate limit) that updates his stats
    # on disconnect -> end player session

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """

if __name__ == "__main__":
    main('', '')