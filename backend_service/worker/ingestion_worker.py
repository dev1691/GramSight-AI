import asyncio
import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend_service.services import weather_ingestion_service, market_ingestion_service
from backend_service.cache import set_cached

logger = logging.getLogger('ingestion.worker')


async def run_weather_job():
    logger.info('Starting scheduled weather ingestion')
    results = await weather_ingestion_service.ingest_weather_for_all_villages()
    # Optionally cache latest weather per village
    for r in results:
        try:
            key = f"weather:latest:{r.village_id}"
            await set_cached(key, {
                'temperature': r.temperature,
                'humidity': r.humidity,
                'rainfall': r.rainfall,
                'recorded_at': str(r.recorded_at)
            }, ttl=60 * 60)
        except Exception:
            logger.exception('Failed to cache weather')


async def run_market_job():
    logger.info('Starting scheduled market ingestion')
    results = await market_ingestion_service.ingest_market_for_all_villages()
    # Optionally cache summary per village
    for r in results:
        try:
            key = f"market:latest:{r.village_id}"
            await set_cached(key, {
                'commodity': r.commodity,
                'modal_price': r.modal_price,
                'arrival_date': str(r.arrival_date)
            }, ttl=60 * 60)
        except Exception:
            logger.exception('Failed to cache market')


def start_scheduler():
    loop = asyncio.get_event_loop()
    scheduler = AsyncIOScheduler(event_loop=loop)
    # run every 15 minutes
    scheduler.add_job(lambda: asyncio.ensure_future(run_weather_job()), IntervalTrigger(minutes=15), id='weather')
    scheduler.add_job(lambda: asyncio.ensure_future(run_market_job()), IntervalTrigger(minutes=60), id='market')
    scheduler.start()
    logger.info('Scheduler started')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_scheduler()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Worker stopped')
