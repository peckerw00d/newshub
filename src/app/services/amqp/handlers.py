import logging
from datetime import datetime

from dishka.integrations.faststream import FromDishka
from faststream.rabbit import RabbitBroker, RabbitRouter

from src.app.db.models.news import News
from src.app.db.repositories.news import NewsRepository
from src.app.services.news_pipeline.collector import NewsCollector
from src.app.services.news_pipeline.deduplicator import Deduplicator

AMQPRouter = RabbitRouter()

logger = logging.getLogger(__name__)


@AMQPRouter.subscriber("collect_queue")
async def fetch_news(
    msg: dict, collector: FromDishka[NewsCollector], broker: FromDishka[RabbitBroker]
):
    logger.info("Начало обработки сообщения из очереди collect_queue")
    try:
        news_items = await collector.collect_news()
        logger.info(f"Собрано {len(news_items)} новостей")
        for news_item in news_items:
            await broker.publish(news_item, "dedup_queue")
    except Exception as err:
        logger.error(f"Ошибка в task_fetch_news: {err}")


@AMQPRouter.subscriber("dedup_queue")
async def deduplicate_news(
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
