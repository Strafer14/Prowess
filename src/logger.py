import logging
from discord_handler import DiscordHandler
from os import environ

webhook_url = environ.get("DISCORD_WEBHOOK")
agent = "Prowess"

logger = logging.getLogger("Prowess")
logger.setLevel(logging.DEBUG)

# Create formatter
FORMAT = logging.Formatter(
"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
if environ.get("PYTHON_ENV") != "development" and environ.get("PYTHON_ENV") != "testing":
    discord_handler = DiscordHandler(webhook_url, agent)
    stream_handler = logging.StreamHandler()
    discord_handler.setLevel(logging.INFO)
    stream_handler.setLevel(logging.DEBUG)
    discord_handler.setFormatter(FORMAT)
    stream_handler.setFormatter(FORMAT)
    logger.addHandler(discord_handler)
    logger.addHandler(stream_handler)

logger.debug("Logger created")