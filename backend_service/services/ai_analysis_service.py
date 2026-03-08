from typing import Any, Dict, Optional
import asyncio
import json
import logging
import os
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
        region = os.getenv('AWS_REGION', 'us-east-1')
        cfg = Config(read_timeout=30, connect_timeout=10, retries={'max_attempts': 2})

        aws_key = os.getenv('AWS_ACCESS_KEY_ID', '')
        aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY', '')

        if aws_key and aws_secret:
            # Use explicit IAM credentials from env
            _bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=region,
                config=cfg,
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret,
            )
            logger.info("Bedrock client created with explicit IAM credentials")
        else:
            # Fall back to default credential chain (EC2 instance role, env, etc.)
            _bedrock_client = boto3.client('bedrock-runtime', region_name=region, config=cfg)
            logger.info("Bedrock client created with default credential chain")

    return _bedrock_client


def _build_request_body(prompt_text: str) -> str:
    """Build a Nova-compatible request body (Messages API format)."""
    return json.dumps({
        "messages": [
            {"role": "user", "content": [{"text": prompt_text}]}
        ],
        "inferenceConfig": {
            "maxTokens": 1024,
            "temperature": 0.3,
            "topP": 0.9,
        }
    })


def _parse_model_response(raw_body: str) -> Optional[str]:
    """Parse Nova model response."""
    try:
        data = json.loads(raw_body)
        # Nova Messages API response format
        output = data.get('output', {})
        message = output.get('message', {})
        content = message.get('content', [])
        if content:
            return content[0].get('text', '')
        # Fallback: try Titan format
        results = data.get('results', [])
        if results:
            return results[0].get('outputText', '')
        return raw_body
    except Exception:
        return raw_body


async def _invoke_bedrock(prompt: str, model: str = 'amazon.nova-micro-v1:0', timeout: int = 30) -> Optional[str]:
    """Invoke Bedrock in a thread to avoid blocking the event loop. Includes latency logging."""

    def call():
        client = _get_bedrock_client()
        body = _build_request_body(prompt)
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
        return _parse_model_response(raw) if raw else None
    except asyncio.TimeoutError:
        logger.error('Bedrock call timed out after %ds', timeout)
    except Exception:
        logger.exception('Bedrock invocation failed')
    # Reset cached client so next call retries with fresh credentials
    global _bedrock_client
    _bedrock_client = None
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
    try:
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

        # Persist AI report (non-critical — don't lose the response on DB error)
        try:
            async with async_session() as session:
                ai_report = AiReport(village_id=village_id, farmer_id=None, report_type='village', content=parsed)
                session.add(ai_report)
                await session.commit()
        except Exception:
            logger.exception('Failed to persist village AI report — returning analysis anyway')

        return parsed

    except Exception:
        logger.exception('generate_village_analysis failed — returning fallback')
        return _fallback_response(village_id=village_id)


async def generate_farmer_analysis(farmer_id: UUID) -> Dict[str, Any]:
    """Farmer-level AI analysis with proper context."""
    try:
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

        # Persist AI report (non-critical — don't lose the response on DB error)
        try:
            async with async_session() as session:
                ai_report = AiReport(village_id=village_id, farmer_id=farmer_id, report_type='farmer', content=parsed)
                session.add(ai_report)
                await session.commit()
        except Exception:
            logger.exception('Failed to persist farmer AI report — returning analysis anyway')

        return parsed

    except Exception:
        logger.exception('generate_farmer_analysis failed — returning fallback')
        return _fallback_response(farmer_id=farmer_id)


async def generate_farmland_analysis(farmland, db) -> Dict[str, Any]:
    """Generate AI insight for a specific farmland using farm registry + weather + market data."""
    try:
        return await _generate_farmland_analysis_inner(farmland, db)
    except Exception:
        logger.exception('generate_farmland_analysis failed — returning fallback')
        return _farmland_fallback_insight(farmland, None, [])


async def _generate_farmland_analysis_inner(farmland, db) -> Dict[str, Any]:
    """Inner implementation for farmland analysis."""
    from backend_service.models import WeatherData, MarketPrice, Village
    from sqlalchemy import desc

    # Gather weather context — run sync ORM queries in a thread
    def _gather_context():
        weather_data = None
        market_data = []
        village_name = None
        if farmland.village_id:
            village = db.query(Village).filter(Village.id == farmland.village_id).first()
            village_name = village.name if village else None

            weather_row = (
                db.query(WeatherData)
                .filter(WeatherData.village_id == farmland.village_id)
                .order_by(desc(WeatherData.recorded_at))
                .first()
            )
            if weather_row:
                weather_data = {
                    "temperature": weather_row.temperature,
                    "humidity": weather_row.humidity,
                    "rainfall": weather_row.rainfall,
                    "description": weather_row.description,
                }

            market_rows = (
                db.query(MarketPrice)
                .filter(MarketPrice.village_id == farmland.village_id)
                .order_by(desc(MarketPrice.created_at))
                .limit(7)
                .all()
            )
            market_data = [
                {"commodity": m.commodity, "modal_price": m.modal_price,
                 "arrival_date": str(m.arrival_date) if m.arrival_date else None}
                for m in market_rows
            ]
        return village_name, weather_data, market_data

    village_name, weather_data, market_data = await asyncio.to_thread(_gather_context)

    prompt_data = {
        "farmland": {
            "land_name": farmland.land_name,
            "total_acres": farmland.total_acres,
            "soil_type": farmland.soil_type,
            "irrigation_type": farmland.irrigation_type,
            "crop_type": farmland.crop_type,
            "sowing_date": str(farmland.sowing_date) if farmland.sowing_date else None,
            "harvest_date": str(farmland.harvest_date) if farmland.harvest_date else None,
            "village": village_name,
        },
        "weather": weather_data or {},
        "market": market_data,
    }

    system_prompt = (
        "You are an agricultural intelligence expert AI. "
        "Analyze the following farmland data including weather and market context. "
        "Return ONLY valid JSON with these exact keys: "
        "crop_suitability, weather_risk, price_opportunity, irrigation_recommendation, "
        "harvest_timing, risk_score (0-100 number), risk_level (Low/Moderate/High/Critical), "
        "recommendations (array of strings), summary (string). "
        "Do not include any text outside the JSON object."
    )
    full_prompt = system_prompt + "\n\nInput data:\n" + json.dumps(prompt_data, default=str)

    result_text = await _invoke_bedrock(full_prompt)
    if not result_text:
        # Fallback: generate deterministic insight
        return _farmland_fallback_insight(farmland, weather_data, market_data)

    parsed = None
    try:
        text = result_text.strip()
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        parsed = json.loads(text)
    except (json.JSONDecodeError, IndexError):
        parsed = _farmland_fallback_insight(farmland, weather_data, market_data)

    # Ensure all required keys
    required = ['crop_suitability', 'weather_risk', 'price_opportunity',
                'irrigation_recommendation', 'harvest_timing', 'risk_score',
                'risk_level', 'recommendations', 'summary']
    for k in required:
        if k not in parsed:
            parsed[k] = 'Not available'
    parsed['prompt_version'] = PROMPT_VERSION
    return parsed


def _farmland_fallback_insight(farmland, weather_data, market_data) -> dict:
    """Deterministic fallback when Bedrock is unavailable."""
    crop = farmland.crop_type or 'General'
    temp = weather_data.get('temperature', 28) if weather_data else 28
    humidity = weather_data.get('humidity', 60) if weather_data else 60
    rainfall = weather_data.get('rainfall', 0) if weather_data else 0

    # Simple risk computation
    risk = 25.0
    recs = []

    if temp > 35:
        risk += 15
        recs.append(f'High temperatures ({temp}°C) detected. Consider heat-resistant {crop} varieties.')
    if temp < 10:
        risk += 15
        recs.append(f'Low temperatures ({temp}°C) may affect {crop} growth. Consider frost protection.')
    if humidity > 85:
        risk += 10
        recs.append('High humidity increases fungal disease risk. Apply preventive fungicide.')
    if rainfall > 50:
        risk += 10
        recs.append('Heavy rainfall expected. Ensure proper drainage to prevent waterlogging.')
    elif rainfall < 5:
        risk += 10
        recs.append('Low rainfall forecast. Increase irrigation frequency.')

    if market_data:
        prices = [m.get('modal_price', 0) for m in market_data if m.get('modal_price')]
        if prices and len(prices) >= 2:
            trend = prices[0] - prices[-1]
            if trend > 0:
                recs.append(f'{crop} prices trending up (₹{prices[0]:,.0f}/quintal). Good time to plan harvest.')
            else:
                recs.append(f'{crop} prices declining. Consider storage or alternative markets.')
                risk += 10

    if not recs:
        recs.append(f'Conditions are generally favorable for {crop} cultivation.')
        recs.append('Continue current farming practices and monitor weather updates.')

    irrigation = farmland.irrigation_type or 'Unknown'
    if irrigation.lower() in ('rainfed', 'none', 'unknown'):
        recs.append('Consider installing drip irrigation for water efficiency and yield improvement.')

    risk = max(0, min(100, risk))
    level = 'Low' if risk <= 30 else ('Moderate' if risk <= 60 else ('High' if risk <= 80 else 'Critical'))

    return {
        'crop_suitability': f'{crop} is suitable for the current soil and weather conditions.' if risk < 60 else f'{crop} faces moderate challenges in current conditions.',
        'weather_risk': f'Temperature: {temp}°C, Humidity: {humidity}%, Rainfall: {rainfall}mm',
        'price_opportunity': f'Market data available for {len(market_data)} recent entries.' if market_data else 'No recent market data available.',
        'irrigation_recommendation': f'Current: {irrigation}. Drip irrigation recommended for optimal water usage.' if irrigation.lower() in ('rainfed', 'none', 'unknown') else f'Current {irrigation} system is adequate.',
        'harvest_timing': f'Planned harvest: {farmland.harvest_date.strftime("%B %Y") if farmland.harvest_date else "Not specified"}.',
        'risk_score': round(risk, 1),
        'risk_level': level,
        'recommendations': recs,
        'summary': f'{crop} on {farmland.total_acres} acres — Risk: {level} ({risk:.0f}%). {recs[0]}',
        'prompt_version': PROMPT_VERSION,
        'is_fallback': True,
    }
