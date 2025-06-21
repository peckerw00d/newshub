from contextlib import asynccontextmanager
from typing import AsyncIterator, AsyncContextManager, Callable
from dotenv import load_dotenv

from dishka.integrations.fastapi import setup_dishka as setup_fastapi_dishka
from fastapi import FastAPI
from taskiq_aio_pika import AioPikaBroker
import uvicorn

from src.app.common.broker import setup_taskiq_broker
from src.app.common.di.setup import setup_ioc_container
from src.app.common.config import Config, load_config
from src.app.api.routers import router

load_dotenv()


def broker_startup_lifespan(
    broker: AioPikaBroker,
) -> Callable[[FastAPI], AsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if not broker.is_worker_process:
            await broker.startup()
        yield
        await broker.shutdown()
        await app.state.dishka_container.close()

    return lifespan


config: Config = load_config()
broker: AioPikaBroker = setup_taskiq_broker(config=config)
container = setup_ioc_container(config=config, broker=broker)

app = FastAPI(lifespan=broker_startup_lifespan(broker=broker))
app.include_router(router=router)

setup_fastapi_dishka(container=container, app=app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
