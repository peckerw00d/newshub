from dishka import make_async_container
from taskiq_aio_pika import AioPikaBroker

from src.app.common.config import Config
from src.app.common.di.providers import (
    DBProvider,
    RepositoryProvider,
    ServiceProvider,
    RabbitProvider,
)


def setup_ioc_container(config: Config, broker: AioPikaBroker):
    container = make_async_container(
        DBProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        RabbitProvider(),
        context={Config: config, AioPikaBroker: broker},
    )
    return container
