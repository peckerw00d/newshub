from apscheduler.schedulers.asyncio import AsyncIOScheduler
from faststream.rabbit import RabbitBroker


async def trigger_first_worker(broker: RabbitBroker):
    await broker.publish({}, queue="collect_queue")


def start_scheduler(broker: RabbitBroker):
    scheduler = AsyncIOScheduler()

    async def scheduled_task():
        await trigger_first_worker(broker)

    scheduler.add_job(scheduled_task, "interval", seconds=60)
    scheduler.start()
