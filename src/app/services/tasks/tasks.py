from dishka.integrations.taskiq import FromDishka, inject
from taskiq_aio_pika import AioPikaBroker

from src.app.services.news_collector import NewsCollector


@inject
async def task_fetch_news(collector: FromDishka[NewsCollector]):
    await collector.collect_news()


def register_tasks(broker: AioPikaBroker) -> None:
    broker.register_task(task_fetch_news, task_name="fetch_news")
