from datetime import datetime
from typing import AsyncGenerator, List

from dishka.integrations.faststream import FromDishka
from faststream.rabbit import RabbitRouter, RabbitBroker

from src.app.db.models.news import News
from src.app.db.repositories.news import NewsRepository
from src.app.services.news_deduplicator import Deduplicator
from src.app.services.news_collector import NewsCollector


AMQPRouter = RabbitRouter()


@AMQPRouter.subscriber("collect_queue")
async def task_fetch_news(
    msg: dict, collector: FromDishka[NewsCollector], broker: FromDishka[RabbitBroker]
):
    news_items = await collector.collect_news()
    for news_item in news_items:
        await broker.publish(news_item, "dedup_queue")


@AMQPRouter.subscriber("dedup_queue")
async def task_process_news_item(
    news_item: dict,
    deduplicator: FromDishka[Deduplicator],
    news_repo: FromDishka[NewsRepository],
):
    published_at = datetime.fromisoformat(news_item["published_at"])
    if not deduplicator.is_duplicate(news_item):
        obj = News(
            source_id=news_item["source_id"],
            title=news_item["title"],
            description=news_item["description"],
            url=news_item["url"],
            full_text=news_item["full_text"],
            published_at=published_at,
            hash=news_item["hash"],
        )
        await news_repo.create(obj)
