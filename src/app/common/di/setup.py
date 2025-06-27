from dishka import make_async_container

from faststream.rabbit import RabbitBroker

from src.app.common.config import Config
from src.app.common.di.providers import (
    DBProvider,
    RepositoryProvider,
    ServiceProvider,
)


def setup_ioc_container(config: Config, broker: RabbitBroker):
    container = make_async_container(
        DBProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        context={Config: config, RabbitBroker: broker},
    )
    return container
