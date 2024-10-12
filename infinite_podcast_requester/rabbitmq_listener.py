import asyncio
import logging

from aio_pika import ExchangeType, connect
from aio_pika.abc import AbstractIncomingMessage
from config import configuration
from enums.v1 import (
    script_generation_status_pb2
)
from events.v1 import script_generation_status_event_pb2
from discord_bot import send_status_message

async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        event = script_generation_status_event_pb2.ScriptGenerationStatusEvent()
        event.ParseFromString(message.body)
        message = f"Reported status id={event.id} topic={event.topic} status={script_generation_status_pb2.ScriptGenerationStatus.Name(event.status)}"
        logging.info(message)
        await send_status_message(event)


async def listener_init() -> None:
    # Perform connection
    username = configuration["rabbitmq"]["username"]
    password = configuration["rabbitmq"]["password"]
    host = configuration["rabbitmq"]["host"]

    connection = await connect(f"amqp://{username}:{password}@{host}/")

    async with connection:
        # Creating a channel
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(
            configuration["rabbitmq"]["username"], ExchangeType.FANOUT,
        )

        # Declaring queue
        queue = await channel.declare_queue(
            name=configuration["rabbitmq"]["job_status_queue"],
            arguments={"x-message-ttl": 60000},
            durable=True
        )

        # Binding the queue to the exchange
        await queue.bind(exchange)

        # Start listening the queue
        await queue.consume(on_message)
        logging.info("rabbitmq listener started")

        await asyncio.Future()
