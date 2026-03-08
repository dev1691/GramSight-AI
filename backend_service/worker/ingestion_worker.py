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
    logger.info('Weather ingestion complete — %d new records', len(results))
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
    logger.info('Market ingestion complete — %d new records', len(results))
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
    scheduler = AsyncIOScheduler()
    # Schedule coroutine functions directly — AsyncIOScheduler handles the event loop
    scheduler.add_job(run_weather_job, IntervalTrigger(minutes=15), id='weather', max_instances=1)
    scheduler.add_job(run_market_job, IntervalTrigger(minutes=60), id='market', max_instances=1)
    scheduler.start()
    logger.info('Scheduler started')


async def _main():
    start_scheduler()
    # Keep the event loop alive forever
    while True:
        await asyncio.sleep(3600)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(_main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('Worker stopped')
