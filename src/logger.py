import logging
from os import environ

from discord_handler import DiscordHandler

webhook_url = environ.get("DISCORD_WEBHOOK")
agent = "Prowess"

logger = logging.getLogger(agent)
logger.setLevel(logging.DEBUG)

# Create formatter
# noinspection SpellCheckingInspection
FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

if webhook_url is not None:
    discord_handler = DiscordHandler(webhook_url, agent)
    discord_handler.setLevel(logging.INFO)
    discord_handler.setFormatter(FORMAT)
    logger.addHandler(discord_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(FORMAT)
logger.addHandler(stream_handler)
logger.debug("Logger created")
