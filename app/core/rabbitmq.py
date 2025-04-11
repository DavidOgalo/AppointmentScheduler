import aio_pika
from aio_pika.abc import AbstractConnection, AbstractChannel
from app.core.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RabbitMQ:
    _connection: Optional[AbstractConnection] = None
    _channel: Optional[AbstractChannel] = None

    @classmethod
    async def get_connection(cls) -> AbstractConnection:
        if cls._connection is None or cls._connection.is_closed:
            cls._connection = await aio_pika.connect_robust(
                f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@"
                f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
            )
            logger.info("RabbitMQ connection established")
        return cls._connection

    @classmethod
    async def get_channel(cls) -> AbstractChannel:
        if cls._channel is None or cls._channel.is_closed:
            connection = await cls.get_connection()
            cls._channel = await connection.channel()
            logger.info("RabbitMQ channel established")
        return cls._channel

    @classmethod
    async def close(cls):
        if cls._channel and not cls._channel.is_closed:
            await cls._channel.close()
            logger.info("RabbitMQ channel closed")
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()
            logger.info("RabbitMQ connection closed")

    @classmethod
    async def declare_queue(cls, queue_name: str, durable: bool = True):
        channel = await cls.get_channel()
        queue = await channel.declare_queue(
            queue_name,
            durable=durable,
            arguments={
                "x-message-ttl": 60000,  # 1 minute
                "x-dead-letter-exchange": f"{queue_name}.dlx",
                "x-dead-letter-routing-key": queue_name,
            }
        )
        return queue

    @classmethod
    async def publish_message(cls, queue_name: str, message: str):
        channel = await cls.get_channel()
        queue = await cls.declare_queue(queue_name)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message.encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue_name,
        )
        logger.info(f"Message published to queue {queue_name}")

    @classmethod
    async def consume_messages(cls, queue_name: str, callback):
        channel = await cls.get_channel()
        queue = await cls.declare_queue(queue_name)
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        await callback(message.body.decode())
                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
                        # Message will be requeued if not acknowledged
                        await message.nack(requeue=True) 