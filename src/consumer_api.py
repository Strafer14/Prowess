from flask import Flask, json, request
from RiotHandler import RiotHandler
from logger import logger

api = Flask(__name__)


@api.route('/api/v1/prowess/puuid', methods=['GET'])
def get_puuid():
    logger.debug("Received get puuid request, {}".format(json.dumps(request.args)))
    riot_handler = RiotHandler()
    player_puuid = riot_handler.get_puuid(request.args.get("game_name"), request.args.get("tag_line"))
    return json.dumps({"puuid": player_puuid.get('puuid', 'Unknown')})

@api.route('/api/v1/prowess/health', methods=['GET'])
def get_health():
    return json.dumps({"health": "ok"})


if __name__ == '__main__':
    api.run()
