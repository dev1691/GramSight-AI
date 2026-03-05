from typing import Any, Dict, Optional
import asyncio
import json
import logging
import time
from uuid import UUID

import boto3
from botocore.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend_service.models import AiReport, WeatherData, MarketPrice
from backend_service.database_async import AsyncSessionLocal as async_session

logger = logging.getLogger(__name__)

PROMPT_VERSION = "1.0"
REQUIRED_AI_KEYS = {'weather_analysis', 'market_analysis', 'risk_assessment', 'recommendations', 'summary'}

# Bedrock client configuration
_bedrock_client = None


def _get_bedrock_client():
    global _bedrock_client
    if _bedrock_client is None:
        cfg = Config(read_timeout=30, connect_timeout=10, retries={'max_attempts': 2})
        _bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1', config=cfg)
    return _bedrock_client


def _build_titan_body(prompt_text: str) -> str:
    """Build a properly structured Titan model request body."""
    return json.dumps({
        "inputText": prompt_text,
        "textGenerationConfig": {
            "maxTokenCount": 1024,
            "temperature": 0.3,
            "topP": 0.9,
        }
    })


def _parse_titan_response(raw_body: str) -> Optional[str]:
    """Parse Titan model response."""
    try:
        data = json.loads(raw_body)
        results = data.get('results', [])
        if results:
            return results[0].get('outputText', '')
        return raw_body
    except Exception:
        return raw_body


async def _invoke_bedrock(prompt: str, model: str = 'amazon.titan-text-lite-v1', timeout: int = 30) -> Optional[str]:
    """Invoke Bedrock in a thread to avoid blocking the event loop. Includes latency logging."""

    def call():
        client = _get_bedrock_client()
        body = _build_titan_body(prompt)
        response = client.invoke_model(body=body, modelId=model, contentType='application/json', accept='application/json')
        resp_body = response.get('body')
        if hasattr(resp_body, 'read'):
            return resp_body.read().decode('utf-8')
        return resp_body

    start = time.perf_counter()
    try:
        raw = await asyncio.wait_for(asyncio.to_thread(call), timeout=timeout)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("bedrock_latency_ms=%.1f model=%s prompt_version=%s", elapsed_ms, model, PROMPT_VERSION)
        return _parse_titan_response(raw) if raw else None
    except asyncio.TimeoutError:
        logger.error('Bedrock call timed out after %ds', timeout)
    except Exception:
        logger.exception('Bedrock invocation failed')
    return None


def _validate_ai_response(parsed: dict) -> dict:
    """Ensure AI response has all required keys; fill defaults for missing ones."""
    for key in REQUIRED_AI_KEYS:
        if key not in parsed:
            parsed[key] = "Not available"
    return parsed


def _fallback_response(village_id=None, farmer_id=None) -> dict:
    return {
        'weather_analysis': 'AI analysis temporarily unavailable',
        'market_analysis': 'AI analysis temporarily unavailable',
        'risk_assessment': 'AI analysis temporarily unavailable',
        'recommendations': ['Please try again later'],
        'summary': 'AI analysis temporarily unavailable. Risk data is still calculated deterministically.',
        'prompt_version': PROMPT_VERSION,
        'is_fallback': True,
    }


async def generate_village_analysis(village_id: UUID) -> Dict[str, Any]:
    """Fetch latest weather + market, build structured prompt, call Bedrock, validate & persist."""
    async with async_session() as session:  # type: AsyncSession
        q = select(WeatherData).where(WeatherData.village_id == village_id).order_by(WeatherData.recorded_at.desc()).limit(1)
        res = await session.execute(q)
        latest_weather = res.scalars().first()

        q2 = select(MarketPrice).where(MarketPrice.village_id == village_id).order_by(MarketPrice.created_at.desc()).limit(7)
        res2 = await session.execute(q2)
        recent_market = [r for r in res2.scalars().all()]

    prompt_data = {
        "village_id": str(village_id),
        "weather": {
            "temperature": getattr(latest_weather, 'temperature', None),
            "humidity": getattr(latest_weather, 'humidity', None),
            "rainfall": getattr(latest_weather, 'rainfall', None),
            "description": getattr(latest_weather, 'description', None),
        },
        "market": [
            {"commodity": m.commodity, "modal_price": m.modal_price, "arrival_date": str(getattr(m, 'arrival_date', None))} for m in recent_market
        ],
    }

    system_prompt = (
        "You are an agricultural intelligence expert AI. "
        "Analyze the following village data and return ONLY valid JSON with these exact keys: "
        "weather_analysis, market_analysis, risk_assessment, recommendations, summary. "
        "Do not include any text outside the JSON object."
    )
    full_prompt = system_prompt + "\n\nInput data:\n" + json.dumps(prompt_data, default=str)

    result_text = await _invoke_bedrock(full_prompt)
    if not result_text:
        return _fallback_response(village_id=village_id)

    # Attempt to extract JSON from response
    parsed = None
    try:
        # Try to find JSON in the response
        text = result_text.strip()
        # Handle markdown code blocks
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        parsed = json.loads(text)
    except (json.JSONDecodeError, IndexError):
        parsed = {"summary": result_text}

    parsed = _validate_ai_response(parsed)
    parsed['prompt_version'] = PROMPT_VERSION

    async with async_session() as session:
        ai_report = AiReport(village_id=village_id, farmer_id=None, report_type='village', content=parsed)
        session.add(ai_report)
        await session.commit()

    return parsed


async def generate_farmer_analysis(farmer_id: UUID) -> Dict[str, Any]:
    """Farmer-level AI analysis with proper context."""
    # Gather farmer context from DB
    async with async_session() as session:
        # Fetch user's village_id
        from backend_service.models import User
        q = select(User).where(User.id == farmer_id).limit(1)
        res = await session.execute(q)
        user = res.scalars().first()
        village_id = getattr(user, 'village_id', None) if user else None

        weather_data = None
        market_data = []
        if village_id:
            q2 = select(WeatherData).where(WeatherData.village_id == village_id).order_by(WeatherData.recorded_at.desc()).limit(1)
            res2 = await session.execute(q2)
            weather_data = res2.scalars().first()

            q3 = select(MarketPrice).where(MarketPrice.village_id == village_id).order_by(MarketPrice.created_at.desc()).limit(7)
            res3 = await session.execute(q3)
            market_data = res3.scalars().all()

    prompt_data = {
        "farmer_id": str(farmer_id),
        "village_id": str(village_id) if village_id else None,
        "weather": {
            "temperature": getattr(weather_data, 'temperature', None),
            "humidity": getattr(weather_data, 'humidity', None),
            "rainfall": getattr(weather_data, 'rainfall', None),
        } if weather_data else {},
        "market": [
            {"commodity": m.commodity, "modal_price": m.modal_price} for m in market_data
        ],
    }

    system_prompt = (
        "You are an agricultural intelligence expert AI. "
        "Analyze the following farmer data and return ONLY valid JSON with these exact keys: "
        "weather_analysis, market_analysis, risk_assessment, recommendations, summary."
    )
    full_prompt = system_prompt + "\n\nInput data:\n" + json.dumps(prompt_data, default=str)

    result_text = await _invoke_bedrock(full_prompt)
    if not result_text:
        return _fallback_response(farmer_id=farmer_id)

    parsed = None
    try:
        text = result_text.strip()
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        parsed = json.loads(text)
    except (json.JSONDecodeError, IndexError):
        parsed = {"summary": result_text}

    parsed = _validate_ai_response(parsed)
    parsed['prompt_version'] = PROMPT_VERSION

    async with async_session() as session:
        ai_report = AiReport(village_id=village_id, farmer_id=farmer_id, report_type='farmer', content=parsed)
        session.add(ai_report)
        await session.commit()

    return parsed
