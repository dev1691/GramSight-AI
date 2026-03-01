from typing import Any, Dict, Optional
import asyncio
import json
import logging
from uuid import UUID

import boto3
from botocore.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend_service.models import AiReport, WeatherData, MarketPrice
from backend_service.database_async import AsyncSessionLocal as async_session

logger = logging.getLogger(__name__)

# Bedrock client configuration - keep small timeout and retries
_bedrock_client = None


def _get_bedrock_client():
    global _bedrock_client
    if _bedrock_client is None:
        cfg = Config(read_timeout=20, connect_timeout=10, retries={'max_attempts': 2})
        _bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1', config=cfg)
    return _bedrock_client


async def _invoke_bedrock(prompt: str, model: str = 'amazon.titan-text-lite-v1', timeout: int = 20) -> Optional[str]:
    """Invoke Bedrock synchronously in a thread to avoid blocking the event loop."""

    def call():
        client = _get_bedrock_client()
        response = client.invoke_model(body=prompt.encode('utf-8'), modelId=model)
        # response shape may vary; attempt to read 'body' or 'response' keys
        body = response.get('body') if isinstance(response, dict) else None
        if hasattr(body, 'read'):
            return body.read().decode('utf-8')
        return body

    try:
        return await asyncio.wait_for(asyncio.to_thread(call), timeout=timeout)
    except asyncio.TimeoutError:
        logger.exception('Bedrock call timed out')
    except Exception:
        logger.exception('Bedrock invocation failed')
    return None


async def generate_village_analysis(village_id: UUID) -> Dict[str, Any]:
    """Fetch latest weather, recent market prices, risk score and soil summary,
    build a structured prompt and call Bedrock. Store the parsed JSON response
    in `ai_reports` table with report_type='village'.
    """
    # Compose data from DB (async)
    async with async_session() as session:  # type: AsyncSession
        # latest weather
        q = select(WeatherData).where(WeatherData.village_id == village_id).order_by(WeatherData.recorded_at.desc()).limit(1)
        res = await session.execute(q)
        latest_weather = res.scalars().first()

        # recent market prices (last 7 entries)
        q2 = select(MarketPrice).where(MarketPrice.village_id == village_id).order_by(MarketPrice.created_at.desc()).limit(7)
        res2 = await session.execute(q2)
        recent_market = [r for r in res2.scalars().all()]

        # TODO: fetch risk score table

    prompt = {
        "system": "You are an agricultural intelligence expert AI. Produce a JSON structured response with weather_analysis, market_analysis, risk_assessment, recommendations, summary.",
        "village_id": str(village_id),
        "weather": {
            "temperature": getattr(latest_weather, 'temperature', None),
            "humidity": getattr(latest_weather, 'humidity', None),
            "rainfall": getattr(latest_weather, 'rainfall', None),
            "description": getattr(latest_weather, 'description', None),
        },
        "market": [
            {"commodity": m.commodity, "modal_price": m.modal_price, "arrival_date": str(getattr(m, 'arrival_date', None))} for m in recent_market
        ]
    }

    system_prompt = (
        "System prompt: You are an agricultural intelligence expert AI. "
        "Return only JSON with keys: weather_analysis, market_analysis, risk_assessment, recommendations, summary."
    )

    full_prompt = system_prompt + "\n\nInput data:\n" + json.dumps(prompt, default=str)

    # call bedrock
    result_text = await _invoke_bedrock(full_prompt)
    if not result_text:
        return {"error": "AI analysis temporarily unavailable"}

    # Try to parse JSON from response
    parsed = None
    try:
        parsed = json.loads(result_text)
    except Exception:
        # best-effort: wrap raw text into summary field
        parsed = {"summary": result_text}

    # store in DB
    async with async_session() as session:
        ai_report = AiReport(village_id=village_id, farmer_id=None, report_type='village', content=parsed)
        session.add(ai_report)
        await session.commit()

    return parsed


async def generate_farmer_analysis(farmer_id: UUID) -> Dict[str, Any]:
    """Fetch farmer's farmland, crops, village weather and market data, then
    craft crop-aware prompt and invoke Bedrock. Store with report_type='farmer'.
    """
    # Minimal placeholder implementation; fetch necessary data and then call Bedrock
    # TODO: implement crop-aware prompt composition
    prompt = {"farmer_id": str(farmer_id)}
    result_text = await _invoke_bedrock(json.dumps(prompt))
    if not result_text:
        return {"error": "AI analysis temporarily unavailable"}

    try:
        parsed = json.loads(result_text)
    except Exception:
        parsed = {"summary": result_text}

    async with async_session() as session:
        ai_report = AiReport(village_id=None, farmer_id=farmer_id, report_type='farmer', content=parsed)
        session.add(ai_report)
        await session.commit()

    return parsed
