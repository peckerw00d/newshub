from contextlib import asynccontextmanager
from dotenv import load_dotenv

from dishka.integrations import faststream as faststream_integration
from dishka.integrations import fastapi as fastapi_integration

from fastapi import FastAPI
from faststream import FastStream

import uvicorn

from src.app.common.scheduler import start_scheduler
from src.app.common.broker import (
    new_broker,
)
from src.app.common.di.setup import setup_ioc_container
from src.app.common.config import Config, load_config
from src.app.api.routers import router
from app.services.amqp.handlers import AMQPRouter

load_dotenv()


config: Config = load_config()
broker = new_broker(config=config)
container = setup_ioc_container(config=config, broker=broker)


@asynccontextmanager
async def lifespan(app: FastAPI):
    faststream_app = get_faststream_app()
    print("Попытка запустить FastStream брокер...")
    try:
        await faststream_app.broker.start()
        print("FastStream брокер успешно запущен!")
    except Exception as e:
        print(f"Ошибка подключения к брокеру: {e}")
    yield
    print("Остановка FastStream брокера...")
    await faststream_app.broker.close()


def get_faststream_app() -> FastStream:
    faststream_app = FastStream(broker)
    faststream_integration.setup_dishka(container, faststream_app, auto_inject=True)
    broker.include_router(AMQPRouter)

    start_scheduler(broker)

    return faststream_app


def get_fastapi_app():
    fastapi_app = FastAPI(lifespan=lifespan)
    fastapi_app.include_router(router=router)

    fastapi_integration.setup_dishka(container, fastapi_app)

    return fastapi_app


app = get_fastapi_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
