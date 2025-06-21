from dishka.integrations.taskiq import setup_dishka
from taskiq_aio_pika import AioPikaBroker

from src.app.services.tasks.tasks import register_tasks
from src.app.common.di.setup import setup_ioc_container
from src.app.common.config import Config


def configure_broker(config: Config, broker: AioPikaBroker) -> None:
    register_tasks(broker=broker)

    container = setup_ioc_container(config=config, broker=broker)
    setup_dishka(container=container, broker=broker)


def setup_taskiq_broker(config: Config) -> AioPikaBroker:
    broker = AioPikaBroker(config.rabbitmq.url)
    configure_broker(config, broker)

    return broker
