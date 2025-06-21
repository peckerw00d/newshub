from taskiq_aio_pika import AioPikaBroker

from src.app.services.tasks.tasks import task_fetch_news


class RabbitPublisher:
    def __init__(self, rabbit: AioPikaBroker):
        self.rabbit = rabbit

    async def publish_fetch_news_task(self):
        task = self.rabbit.task(task_name="fetch_news")(task_fetch_news)
        await task.kiq()
