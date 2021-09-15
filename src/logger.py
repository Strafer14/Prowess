import logging
from os import environ

from coralogix.handlers import CoralogixLogger
from discord_handler import DiscordHandler

CORALOGIX_PRIVATE_KEY = environ.get("CORALOGIX_KEY")
WEBHOOK_URL = environ.get("DISCORD_WEBHOOK")
AGENT = "Prowess"
SUB_SYSTEM = "api"

logger = logging.getLogger(AGENT)
logger.setLevel(logging.DEBUG)

# Create formatter
# noinspection SpellCheckingInspection
FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

if WEBHOOK_URL is not None:
    discord_handler = DiscordHandler(WEBHOOK_URL, AGENT)
    discord_handler.setLevel(logging.INFO)
    discord_handler.setFormatter(FORMAT)
    logger.addHandler(discord_handler)
if CORALOGIX_PRIVATE_KEY:
    coralogix_handler = CoralogixLogger(CORALOGIX_PRIVATE_KEY, AGENT, SUB_SYSTEM)
    logger.addHandler(coralogix_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(FORMAT)
logger.addHandler(stream_handler)
logger.debug("Logger created")
