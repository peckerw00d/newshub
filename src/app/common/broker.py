from dishka.integrations.taskiq import setup_dishka
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker

from src.app.services.tasks.tasks import register_tasks
from src.app.common.di.setup import setup_ioc_container
from src.app.common.config import Config


def create_scheduler(broker: AioPikaBroker):
    return TaskiqScheduler(broker, sources=[LabelScheduleSource(broker)])


def configure_broker(config: Config, broker: AioPikaBroker) -> None:
    register_tasks(broker)

    container = setup_ioc_container(config, broker)
    setup_dishka(container, broker)


def setup_taskiq_broker(config: Config) -> AioPikaBroker:
    broker = AioPikaBroker(config.rabbitmq.url)
    configure_broker(config, broker)

    return broker


def setup_taskiq_scheduler(config: Config) -> TaskiqScheduler:
    broker = AioPikaBroker(config.rabbitmq.url)
    scheduler = create_scheduler(broker)

    return scheduler
