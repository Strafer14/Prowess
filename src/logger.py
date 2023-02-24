import logging
from os import environ

from discord_handler import DiscordHandler  # type: ignore

WEBHOOK_URL = environ.get('DISCORD_WEBHOOK')
AGENT = 'Prowess'
SUB_SYSTEM = 'api'

logger = logging.getLogger(AGENT)
logger.setLevel(logging.DEBUG)

# Create formatter
# noinspection SpellCheckingInspection
FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if WEBHOOK_URL:
    discord_handler = DiscordHandler(WEBHOOK_URL, AGENT)
    discord_handler.setLevel(logging.INFO)
    discord_handler.setFormatter(FORMAT)
    logger.addHandler(discord_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(FORMAT)
logger.addHandler(stream_handler)
logger.debug('Logger created')
