from faststream.rabbit import RabbitBroker

from src.app.common.config import Config


def new_broker(config: Config) -> RabbitBroker:
    return RabbitBroker(config.rabbitmq.url)
