import pika
import os
import asyncio
from .logger import logger

RABBIT_HOST = os.environ.get("RABBIT_HOST", "fox.rmq.cloudamqp.com")
RABBIT_USER = os.environ.get("RABBIT_USER", "ortmbosi")
RABBIT_PWD = os.environ.get("RABBIT_PWD", "DsFBo1FcjzKETHKHRmbAd8FUnQcN6fNb")

credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PWD)
parameters = pika.ConnectionParameters(
    credentials=credentials, host=RABBIT_HOST, virtual_host=RABBIT_USER)


async def publish(body):
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    logger.debug("Attempting to publish message: {}".format(body))
    channel.basic_publish(
        exchange='test', routing_key='lambda-riot-api-requests', body=body)
    logger.info("Successfully published message: {}".format(body))
    connection.close()
