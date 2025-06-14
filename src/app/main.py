from contextlib import asynccontextmanager
from dotenv import load_dotenv

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka

from fastapi import FastAPI


import uvicorn

from src.app.ioc import DBProvider, RepositoryProvider, ServiceProvider
from src.app.config import Config
from src.app.api.routers import router


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await app.state.dishka_conteiner.close()


config = Config()
container = make_async_container(
    DBProvider(), RepositoryProvider(), ServiceProvider(), context={Config: config}
)

app = FastAPI()
app.include_router(router=router)

setup_dishka(container=container, app=app)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
