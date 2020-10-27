import json
from src.RiotHandler import RiotHandler
from src.Analyze import get_match_results

def main(event, context):
    puuid = event.get('pathParameters', {}).get('puuid')
    region = 'EU'
    riot = RiotHandler()
    matches = json.loads(riot.get_matches_list(region, puuid))
    first_match_id = matches['history'][0]['matchId']
    match_data = json.loads(riot.get_match_data(region, first_match_id))
    return {
        "statusCode": 200,
        "body": json.dumps(get_match_results(match_data, puuid))
    }


if __name__ == "__main__":
    main('', '')
