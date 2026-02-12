# Design Document: GramSight AI

## Overview

GramSight AI is a cloud-native, microservices-based AI platform designed to provide predictive agricultural risk intelligence at scale. The system ingests multi-source data (satellite imagery, weather, soil, market prices), processes it through ML pipelines, generates risk scores, and delivers actionable alerts to 1M+ farmers and institutional users.

### Design Principles

1. **API-First**: All functionality exposed via RESTful APIs for maximum integration flexibility
2. **Event-Driven**: Asynchronous processing using message queues for scalability and fault tolerance
3. **Microservices**: Loosely coupled services that can scale independently
4. **Multi-Tenant**: Secure data isolation for different organizations
5. **Cloud-Native**: Designed for AWS with horizontal scaling, auto-recovery, and cost optimization
6. **Observability**: Comprehensive logging, monitoring, and tracing built-in
7. **Data-Driven**: ML models continuously retrained with new data

### Technology Stack

**Backend Services**: Python (FastAPI), Node.js (for real-time services)
**ML/AI**: PyTorch, Scikit-learn, TensorFlow, Hugging Face
**Databases**: PostgreSQL (OLTP), TimescaleDB (time-series), Amazon Redshift (analytics)
**Cache**: Redis Cluster (distributed caching)
**Message Queue**: Amazon SQS + Amazon SNS (for simplicity) or Apache Kafka (for high throughput)
**Object Storage**: Amazon S3 (satellite imagery, model artifacts)
**Container Orchestration**: Amazon ECS with Fargate (serverless containers)
**API Gateway**: Amazon API Gateway + AWS Lambda (for edge functions)
**Monitoring**: Amazon CloudWatch, Prometheus, Grafana, AWS X-Ray (distributed tracing)
**CI/CD**: GitHub Actions, AWS CodePipeline, AWS CodeDeploy


## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           External Data Sources                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  Sentinel-2  │  │ Weather APIs │  │  Soil Data   │  │ Market APIs │ │
│  │   Imagery    │  │   (IMD/OW)   │  │   (ICAR)     │  │ (AGMARKNET) │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
└─────────┼──────────────────┼──────────────────┼──────────────────┼──────┘
          │                  │                  │                  │
          └──────────────────┴──────────────────┴──────────────────┘
                                      │
                                      ▼
          ┌───────────────────────────────────────────────────────┐
          │              Data Ingestion Layer                     │
          │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │
          │  │  Satellite  │  │   Weather   │  │ Market/Soil  │  │
          │  │  Ingestion  │  │  Ingestion  │  │  Ingestion   │  │
          │  │   Service   │  │   Service   │  │   Service    │  │
          │  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘  │
          └─────────┼─────────────────┼─────────────────┼─────────┘
                    │                 │                 │
                    └─────────────────┴─────────────────┘
                                      │
                                      ▼
          ┌───────────────────────────────────────────────────────┐
          │              Message Queue (SQS/Kafka)                │
          └───────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
          ┌──────────────────┐              ┌──────────────────────┐
          │   ML Processing  │              │   Data Processing    │
          │      Layer       │              │       Layer          │
          │  ┌────────────┐  │              │  ┌────────────────┐  │
          │  │   Crop     │  │              │  │  Feature       │  │
          │  │  Stress    │  │              │  │  Engineering   │  │
          │  │  Detection │  │              │  │  Service       │  │
          │  └─────┬──────┘  │              │  └────────┬───────┘  │
          │  ┌─────┴──────┐  │              │  ┌────────┴───────┐  │
          │  │   Risk     │  │              │  │  Data          │  │
          │  │  Scoring   │  │              │  │  Validation    │  │
          │  │  Engine    │  │              │  │  Service       │  │
          │  └─────┬──────┘  │              │  └────────┬───────┘  │
          └────────┼─────────┘              └───────────┼──────────┘
                   │                                    │
                   └────────────────┬───────────────────┘
                                    ▼
          ┌───────────────────────────────────────────────────────┐
          │              Storage Layer                            │
          │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
          │  │PostgreSQL│  │TimescaleDB│ │  Redshift│            │
          │  │  (OLTP)  │  │(Time-Series)│(Analytics)│            │
          │  └────┬─────┘  └─────┬─────┘  └─────┬────┘            │
          │  ┌────┴──────────────┴─────────────┴────┐             │
          │  │         S3 (Imagery & Models)        │             │
          │  └──────────────────────────────────────┘             │
          └───────────────────────────────────────────────────────┘
                                    │
                                    ▼
          ┌───────────────────────────────────────────────────────┐
          │              Application Layer                        │
          │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │
          │  │    Risk     │  │   Alert     │  │   Farmer     │  │
          │  │    API      │  │  Service    │  │   Profile    │  │
          │  │   Service   │  │             │  │   Service    │  │
          │  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘  │
          └─────────┼─────────────────┼─────────────────┼─────────┘
                    │                 │                 │
                    └─────────────────┴─────────────────┘
                                      │
                                      ▼
          ┌───────────────────────────────────────────────────────┐
          │              Cache Layer (Redis Cluster)              │
          └───────────────────────────────────────────────────────┘
                                      │
                                      ▼
          ┌───────────────────────────────────────────────────────┐
          │              API Gateway + Load Balancer              │
          └───────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
          ┌──────────────────┐              ┌──────────────────────┐
          │   Mobile App     │              │   Web Dashboard      │
          │   (Farmers)      │              │   (Institutions)     │
          └──────────────────┘              └──────────────────────┘
```

### Architecture Layers

1. **Data Ingestion Layer**: Fetches data from external sources, validates, and queues for processing
2. **Message Queue Layer**: Decouples ingestion from processing, ensures fault tolerance
3. **Processing Layer**: ML models and data transformation services
4. **Storage Layer**: Multi-database strategy for different data types and access patterns
5. **Application Layer**: Business logic services exposing APIs
6. **Cache Layer**: Reduces database load and improves response times
7. **API Gateway**: Entry point with authentication, rate limiting, and routing
8. **Client Layer**: Mobile apps and web dashboards


## Components and Interfaces

### 1. Data Ingestion Services

#### Satellite Ingestion Service

**Responsibilities**:
- Poll Sentinel-2 API for new imagery covering monitored regions
- Download multi-spectral imagery (10 bands)
- Validate image quality (cloud cover, completeness)
- Store raw imagery in S3 with metadata
- Publish ingestion events to message queue

**Interfaces**:
```python
class SatelliteIngestionService:
    def fetch_available_imagery(region: BoundingBox, date_range: DateRange) -> List[ImageryMetadata]
    def download_imagery(imagery_id: str) -> ImageryFile
    def validate_imagery(imagery: ImageryFile) -> ValidationResult
    def store_imagery(imagery: ImageryFile, metadata: ImageryMetadata) -> S3Location
    def publish_ingestion_event(s3_location: S3Location, metadata: ImageryMetadata) -> EventId
```

**Configuration**:
- Polling interval: 6 hours
- Supported sources: Sentinel-2 (primary), Landsat-8 (fallback)
- Quality threshold: <40% cloud cover
- Retry policy: 3 attempts with exponential backoff

#### Weather Ingestion Service

**Responsibilities**:
- Fetch weather forecasts and historical data
- Validate data completeness
- Interpolate missing values from nearby stations
- Store in TimescaleDB for time-series queries
- Trigger alerts for extreme weather events

**Interfaces**:
```python
class WeatherIngestionService:
    def fetch_forecast(village_ids: List[str], horizon_days: int) -> List[WeatherForecast]
    def fetch_historical(village_ids: List[str], date_range: DateRange) -> List[WeatherRecord]
    def validate_weather_data(data: WeatherData) -> ValidationResult
    def interpolate_missing_values(data: WeatherData, nearby_stations: List[Station]) -> WeatherData
    def store_weather_data(data: WeatherData) -> bool
    def detect_extreme_events(forecast: WeatherForecast) -> List[ExtremeEvent]
```

**Configuration**:
- Polling interval: 6 hours for forecasts, daily for historical
- Data sources: IMD (primary), OpenWeather (fallback)
- Required fields: temperature, rainfall, humidity, wind_speed
- Extreme event thresholds: rainfall >100mm, temperature >40°C

#### Market & Soil Ingestion Service

**Responsibilities**:
- Fetch daily market prices from commodity exchanges
- Import soil health data from government datasets
- Validate and clean data
- Store in PostgreSQL with versioning
- Detect price anomalies and volatility

**Interfaces**:
```python
class MarketSoilIngestionService:
    def fetch_market_prices(crops: List[str], markets: List[str]) -> List[PriceRecord]
    def import_soil_data(source: DataSource, region: Region) -> List[SoilRecord]
    def validate_price_data(prices: List[PriceRecord]) -> ValidationResult
    def detect_price_anomalies(prices: List[PriceRecord]) -> List[Anomaly]
    def store_market_data(prices: List[PriceRecord]) -> bool
    def store_soil_data(soil_data: List[SoilRecord], version: str) -> bool
```

**Configuration**:
- Market data polling: Daily at 6 PM IST
- Soil data updates: Quarterly or as available
- Price anomaly threshold: >15% change in 7 days
- Data retention: 2 years for prices, indefinite for soil

### 2. ML Processing Services

#### Crop Stress Detection Service

**Responsibilities**:
- Process satellite imagery to compute vegetation indices (NDVI, EVI, NDWI)
- Run computer vision models to detect stress patterns
- Compare against historical baselines
- Generate stress classifications with confidence scores
- Store results and trigger alerts for high-confidence detections

**Interfaces**:
```python
class CropStressDetectionService:
    def compute_vegetation_indices(imagery: SatelliteImage) -> VegetationIndices
    def detect_stress_patterns(imagery: SatelliteImage, indices: VegetationIndices) -> StressDetection
    def compare_to_baseline(current: VegetationIndices, historical: List[VegetationIndices]) -> DeviationScore
    def classify_stress_type(detection: StressDetection) -> StressClassification
    def generate_confidence_score(detection: StressDetection) -> float
    def store_detection_results(farm_id: str, detection: StressDetection) -> bool
```

**ML Model Details**:
- Architecture: ResNet-50 backbone + custom classification head
- Input: 10-band multi-spectral imagery (224x224 patches)
- Output: 4 classes (healthy, water_stress, nutrient_deficiency, pest_damage) + confidence
- Training data: 100K labeled images with ground-truth validation
- Inference time: <100ms per farm on GPU
- Model storage: S3 with versioning

#### Risk Scoring Engine

**Responsibilities**:
- Aggregate features from satellite, weather, soil, and market data
- Run ensemble ML models to generate risk scores
- Compute risk scores for multiple time horizons (7-day, 30-day, 90-day)
- Generate explainability data (SHAP values)
- Store risk scores with historical tracking
- Trigger alerts when risk exceeds thresholds

**Interfaces**:
```python
class RiskScoringEngine:
    def aggregate_features(farm_id: str, date: Date) -> FeatureVector
    def compute_risk_score(features: FeatureVector, horizon: int) -> RiskScore
    def generate_explainability(features: FeatureVector, score: RiskScore) -> ExplainabilityData
    def store_risk_score(farm_id: str, score: RiskScore, explainability: ExplainabilityData) -> bool
    def check_alert_thresholds(score: RiskScore) -> Optional[Alert]
    def get_historical_scores(farm_id: str, date_range: DateRange) -> List[RiskScore]
```

**ML Model Details**:
- Architecture: Ensemble (Random Forest + XGBoost + Neural Network)
- Input: 50+ engineered features
- Output: Risk score (0-100) + confidence interval + SHAP values
- Training data: 2 years historical with actual crop outcomes
- Retraining: Monthly with rolling window
- Feature importance: Top 10 features tracked for model monitoring

### 3. Application Services

#### Risk API Service

**Responsibilities**:
- Expose RESTful APIs for querying risk scores
- Implement caching for frequently accessed data
- Support batch queries for institutional users
- Provide filtering and aggregation capabilities
- Return results with pagination

**Interfaces**:
```python
class RiskAPIService:
    def get_risk_score(farm_id: str, date: Optional[Date] = None) -> RiskScoreResponse
    def get_risk_scores_batch(farm_ids: List[str], date: Optional[Date] = None) -> List[RiskScoreResponse]
    def get_risk_trend(farm_id: str, date_range: DateRange) -> RiskTrendResponse
    def get_portfolio_risk(tenant_id: str, filters: RiskFilters) -> PortfolioRiskResponse
    def get_explainability(farm_id: str, date: Date) -> ExplainabilityResponse
```

**API Endpoints**:
```
GET  /api/v1/risk/{farm_id}                    # Get current risk score
GET  /api/v1/risk/{farm_id}/trend              # Get risk trend over time
POST /api/v1/risk/batch                        # Batch query for multiple farms
GET  /api/v1/risk/portfolio                    # Portfolio-level aggregation
GET  /api/v1/risk/{farm_id}/explainability     # Get SHAP values and feature importance
```

**Caching Strategy**:
- Cache current risk scores for 1 hour (Redis)
- Cache historical trends for 24 hours
- Invalidate cache when new risk scores computed
- Use cache-aside pattern with automatic refresh

#### Alert Service

**Responsibilities**:
- Receive alert triggers from risk engine and weather service
- Prioritize alerts based on severity and user preferences
- Format alerts for different channels (SMS, push notification, email)
- Deliver alerts via appropriate channels
- Track delivery status and retry failures
- Implement rate limiting to prevent alert fatigue
- Store alert history

**Interfaces**:
```python
class AlertService:
    def create_alert(alert_type: AlertType, farm_id: str, severity: Severity, message: str) -> Alert
    def prioritize_alert(alert: Alert, user_preferences: UserPreferences) -> Priority
    def format_alert(alert: Alert, channel: Channel, language: str) -> FormattedMessage
    def deliver_alert(alert: Alert, channel: Channel, recipient: str) -> DeliveryStatus
    def retry_failed_delivery(alert_id: str) -> DeliveryStatus
    def check_rate_limits(user_id: str, alert_type: AlertType) -> bool
    def get_alert_history(user_id: str, date_range: DateRange) -> List[Alert]
```

**Alert Types**:
- CROP_STRESS: Detected via satellite imagery
- EXTREME_WEATHER: Heavy rain, heatwave, frost
- PRICE_SPIKE: Significant market price change
- RISK_THRESHOLD: Risk score exceeds configured threshold

**Delivery Channels**:
- SMS: Via AWS SNS or Twilio (primary for farmers)
- Push Notification: Via Firebase Cloud Messaging (mobile app)
- Email: Via AWS SES (institutional users)
- Dashboard: Real-time updates via WebSocket

**Rate Limiting**:
- Max 3 SMS per day per farmer
- Max 10 push notifications per day
- No limit on dashboard alerts
- Critical alerts bypass rate limits

#### Farmer Profile Service

**Responsibilities**:
- Manage farmer registration and profiles
- Store farm location, crop type, land size
- Manage user preferences (language, alert settings)
- Handle authentication and authorization
- Support multi-tenancy for institutional users

**Interfaces**:
```python
class FarmerProfileService:
    def register_farmer(farmer_data: FarmerRegistration) -> FarmerId
    def update_profile(farmer_id: str, updates: ProfileUpdates) -> bool
    def get_profile(farmer_id: str) -> FarmerProfile
    def register_farm(farmer_id: str, farm_data: FarmRegistration) -> FarmId
    def update_farm(farm_id: str, updates: FarmUpdates) -> bool
    def get_farms(farmer_id: str) -> List[Farm]
    def set_preferences(farmer_id: str, preferences: UserPreferences) -> bool
    def authenticate(credentials: Credentials) -> AuthToken
```

**Data Model**:
```python
FarmerProfile:
    farmer_id: str
    name: str
    phone: str
    language: str (ISO 639-1 code)
    tenant_id: str (for institutional users)
    created_at: datetime
    
Farm:
    farm_id: str
    farmer_id: str
    location: GeoPoint (lat, lon)
    boundary: GeoPolygon (optional)
    crop_type: str
    land_size_acres: float
    soil_type: str
    created_at: datetime
    
UserPreferences:
    alert_types: List[AlertType]
    alert_channels: List[Channel]
    quiet_hours: TimeRange
    language: str
```

### 4. Infrastructure Services

#### API Gateway

**Responsibilities**:
- Route requests to appropriate backend services
- Authenticate API requests (API keys, OAuth 2.0)
- Implement rate limiting per API key
- Log all requests for audit and analytics
- Handle CORS for web clients
- Transform responses (compression, format conversion)

**Configuration**:
- Rate limits: 1000 requests/hour per API key (configurable per tenant)
- Authentication: JWT tokens with 1-hour expiry
- Timeout: 30 seconds for API requests
- CORS: Allow configured origins only
- Compression: gzip for responses >1KB

#### Cache Service (Redis Cluster)

**Responsibilities**:
- Cache frequently accessed risk scores
- Cache farmer profiles and farm data
- Cache weather forecasts
- Implement cache invalidation strategies
- Provide pub/sub for real-time updates

**Caching Patterns**:
- **Cache-Aside**: Application checks cache first, loads from DB on miss
- **Write-Through**: Updates written to cache and DB simultaneously
- **TTL-Based Expiry**: Risk scores (1 hour), profiles (24 hours), weather (6 hours)
- **Event-Based Invalidation**: Invalidate when new data computed

**Redis Data Structures**:
- Strings: Individual risk scores, farmer profiles
- Hashes: Farm metadata, weather data
- Sorted Sets: Leaderboards (highest risk farms)
- Pub/Sub: Real-time dashboard updates

#### Message Queue (SQS/Kafka)

**Responsibilities**:
- Decouple data ingestion from processing
- Ensure at-least-once delivery semantics
- Support dead-letter queues for failed messages
- Enable parallel processing of messages
- Provide message ordering where needed

**Queue Design**:
```
satellite-ingestion-queue:
    - Messages: New satellite imagery available
    - Consumers: Crop Stress Detection Service
    - Throughput: ~1000 messages/day
    - Retention: 7 days

weather-ingestion-queue:
    - Messages: New weather data available
    - Consumers: Risk Scoring Engine, Alert Service
    - Throughput: ~10,000 messages/day
    - Retention: 3 days

risk-computation-queue:
    - Messages: Trigger risk score computation
    - Consumers: Risk Scoring Engine
    - Throughput: ~100,000 messages/day
    - Retention: 3 days

alert-delivery-queue:
    - Messages: Alert to be delivered
    - Consumers: Alert Service
    - Throughput: ~1,000,000 messages/day (peak)
    - Retention: 1 day
```

**Dead Letter Queues**:
- Failed messages moved to DLQ after 3 retry attempts
- DLQ monitored with CloudWatch alarms
- Manual intervention required for DLQ processing


## Data Models

### Database Selection Strategy

**PostgreSQL (OLTP)**:
- Use case: Transactional data (farmer profiles, farms, alerts, audit logs)
- Rationale: ACID compliance, strong consistency, rich query capabilities
- Scaling: Read replicas for read-heavy workloads, sharding by tenant_id for write scaling
- Instance: Amazon RDS PostgreSQL with Multi-AZ deployment

**TimescaleDB (Time-Series)**:
- Use case: Weather data, risk score history, vegetation indices over time
- Rationale: Optimized for time-series queries, automatic partitioning, compression
- Scaling: Horizontal scaling via distributed hypertables
- Instance: Self-managed on EC2 or TimescaleDB Cloud

**Amazon Redshift (Analytics)**:
- Use case: Historical analytics, business intelligence, ML training data
- Rationale: Columnar storage, fast aggregations, integration with ML tools
- Scaling: Add nodes to cluster as data grows
- Data pipeline: Daily ETL from PostgreSQL/TimescaleDB to Redshift

**Amazon S3 (Object Storage)**:
- Use case: Satellite imagery, ML model artifacts, data lake for raw data
- Rationale: Unlimited scalability, cost-effective, integration with ML services
- Lifecycle policies: Move infrequently accessed data to S3 Glacier after 90 days

### Core Data Models

#### Farmer and Farm Models (PostgreSQL)

```python
# Farmers table
CREATE TABLE farmers (
    farmer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,  -- For multi-tenancy
    phone VARCHAR(15) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    language VARCHAR(5) NOT NULL DEFAULT 'hi',  -- ISO 639-1
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_phone (phone)
);

# Farms table
CREATE TABLE farms (
    farm_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_id UUID NOT NULL REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    location GEOGRAPHY(POINT, 4326) NOT NULL,  -- PostGIS for geospatial
    boundary GEOGRAPHY(POLYGON, 4326),  -- Optional farm boundary
    crop_type VARCHAR(50) NOT NULL,
    land_size_acres DECIMAL(10, 2) NOT NULL,
    soil_type VARCHAR(50),
    village_id VARCHAR(50) NOT NULL,  -- For aggregation
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_farmer_id (farmer_id),
    INDEX idx_village_id (village_id),
    INDEX idx_location USING GIST (location)  -- Spatial index
);

# User preferences table
CREATE TABLE user_preferences (
    farmer_id UUID PRIMARY KEY REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    alert_types JSONB NOT NULL DEFAULT '["CROP_STRESS", "EXTREME_WEATHER", "PRICE_SPIKE"]',
    alert_channels JSONB NOT NULL DEFAULT '["SMS"]',
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    max_alerts_per_day INT NOT NULL DEFAULT 3,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

#### Alert Models (PostgreSQL)

```python
# Alerts table
CREATE TABLE alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_id UUID NOT NULL REFERENCES farms(farm_id) ON DELETE CASCADE,
    farmer_id UUID NOT NULL REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,  -- CROP_STRESS, EXTREME_WEATHER, etc.
    severity VARCHAR(20) NOT NULL,  -- CRITICAL, HIGH, MEDIUM, LOW
    message TEXT NOT NULL,
    message_localized JSONB,  -- Translations for different languages
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,
    INDEX idx_farm_id (farm_id),
    INDEX idx_farmer_id (farmer_id),
    INDEX idx_created_at (created_at),
    INDEX idx_alert_type (alert_type)
);

# Alert delivery tracking
CREATE TABLE alert_deliveries (
    delivery_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID NOT NULL REFERENCES alerts(alert_id) ON DELETE CASCADE,
    channel VARCHAR(20) NOT NULL,  -- SMS, PUSH, EMAIL
    recipient VARCHAR(100) NOT NULL,  -- Phone number, email, device token
    status VARCHAR(20) NOT NULL,  -- PENDING, SENT, DELIVERED, FAILED
    attempts INT NOT NULL DEFAULT 0,
    delivered_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_alert_id (alert_id),
    INDEX idx_status (status)
);
```

#### Time-Series Models (TimescaleDB)

```python
# Weather data (hypertable)
CREATE TABLE weather_data (
    time TIMESTAMP NOT NULL,
    village_id VARCHAR(50) NOT NULL,
    temperature_celsius DECIMAL(5, 2),
    rainfall_mm DECIMAL(6, 2),
    humidity_percent DECIMAL(5, 2),
    wind_speed_kmh DECIMAL(5, 2),
    is_forecast BOOLEAN NOT NULL DEFAULT FALSE,
    data_source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

SELECT create_hypertable('weather_data', 'time');
CREATE INDEX idx_weather_village_time ON weather_data (village_id, time DESC);

# Risk scores (hypertable)
CREATE TABLE risk_scores (
    time TIMESTAMP NOT NULL,
    farm_id UUID NOT NULL,
    risk_score DECIMAL(5, 2) NOT NULL,  -- 0-100
    confidence_score DECIMAL(5, 2) NOT NULL,  -- 0-100
    horizon_days INT NOT NULL,  -- 7, 30, or 90
    contributing_factors JSONB,  -- SHAP values and feature importance
    model_version VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

SELECT create_hypertable('risk_scores', 'time');
CREATE INDEX idx_risk_farm_time ON risk_scores (farm_id, time DESC);
CREATE INDEX idx_risk_score ON risk_scores (risk_score DESC);

# Vegetation indices (hypertable)
CREATE TABLE vegetation_indices (
    time TIMESTAMP NOT NULL,
    farm_id UUID NOT NULL,
    ndvi DECIMAL(5, 4),  -- -1 to 1
    evi DECIMAL(5, 4),
    ndwi DECIMAL(5, 4),
    lai DECIMAL(5, 2),  -- Leaf Area Index
    imagery_source VARCHAR(50) NOT NULL,
    cloud_cover_percent DECIMAL(5, 2),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

SELECT create_hypertable('vegetation_indices', 'time');
CREATE INDEX idx_veg_farm_time ON vegetation_indices (farm_id, time DESC);

# Market prices (hypertable)
CREATE TABLE market_prices (
    time TIMESTAMP NOT NULL,
    crop_type VARCHAR(50) NOT NULL,
    market_location VARCHAR(100) NOT NULL,
    price_per_quintal DECIMAL(10, 2) NOT NULL,
    volume_quintals DECIMAL(12, 2),
    data_source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

SELECT create_hypertable('market_prices', 'time');
CREATE INDEX idx_price_crop_time ON market_prices (crop_type, time DESC);
```

#### Satellite Imagery Metadata (PostgreSQL)

```python
# Satellite imagery metadata
CREATE TABLE satellite_imagery (
    imagery_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capture_date TIMESTAMP NOT NULL,
    satellite_source VARCHAR(50) NOT NULL,  -- SENTINEL2, LANDSAT8
    bounding_box GEOGRAPHY(POLYGON, 4326) NOT NULL,
    cloud_cover_percent DECIMAL(5, 2) NOT NULL,
    quality_score DECIMAL(5, 2) NOT NULL,
    s3_bucket VARCHAR(100) NOT NULL,
    s3_key VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    processing_status VARCHAR(20) NOT NULL,  -- PENDING, PROCESSING, COMPLETED, FAILED
    processed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_capture_date (capture_date),
    INDEX idx_processing_status (processing_status),
    INDEX idx_bounding_box USING GIST (bounding_box)
);
```

#### Soil Health Data (PostgreSQL)

```python
# Soil health data
CREATE TABLE soil_health (
    soil_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    village_id VARCHAR(50) NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    ph DECIMAL(4, 2),
    organic_carbon_percent DECIMAL(5, 2),
    nitrogen_kg_per_ha DECIMAL(8, 2),
    phosphorus_kg_per_ha DECIMAL(8, 2),
    potassium_kg_per_ha DECIMAL(8, 2),
    soil_type VARCHAR(50),
    data_source VARCHAR(100) NOT NULL,
    measurement_date DATE NOT NULL,
    version VARCHAR(20) NOT NULL,  -- For tracking updates
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_village_id (village_id),
    INDEX idx_location USING GIST (location),
    INDEX idx_measurement_date (measurement_date)
);
```

#### Audit and Monitoring (PostgreSQL)

```python
# API audit logs
CREATE TABLE api_audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    api_key_id UUID NOT NULL,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_params JSONB,
    response_status INT NOT NULL,
    response_time_ms INT NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_created_at (created_at),
    INDEX idx_endpoint (endpoint)
);

# System metrics (for custom monitoring)
CREATE TABLE system_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15, 4) NOT NULL,
    metric_unit VARCHAR(20),
    tags JSONB,  -- For dimensions like service_name, region, etc.
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_metric_name (metric_name),
    INDEX idx_timestamp (timestamp)
);
```

### Data Partitioning Strategy

**Geographic Partitioning**:
- Partition farms table by region (North, South, East, West, Central India)
- Enables regional scaling and data locality
- Partition key: `region_id` derived from `village_id`

**Time-Based Partitioning**:
- TimescaleDB automatically partitions hypertables by time
- Chunk interval: 7 days for high-frequency data (weather, risk scores)
- Chunk interval: 30 days for lower-frequency data (market prices)

**Tenant-Based Partitioning**:
- Partition audit logs by `tenant_id` for multi-tenant isolation
- Consider separate databases for large institutional tenants

### Data Retention and Archival

**Hot Data (Frequent Access)**:
- Risk scores: Last 30 days in TimescaleDB
- Weather data: Last 90 days in TimescaleDB
- Alerts: Last 90 days in PostgreSQL

**Warm Data (Occasional Access)**:
- Risk scores: 30-365 days in TimescaleDB with compression
- Weather data: 90 days - 2 years in TimescaleDB with compression
- Satellite imagery: 90 days - 1 year in S3 Standard

**Cold Data (Archival)**:
- Risk scores: >1 year aggregated monthly, moved to Redshift
- Weather data: >2 years aggregated daily, moved to Redshift
- Satellite imagery: >1 year moved to S3 Glacier
- Audit logs: >1 year moved to S3 Glacier (7-year retention for compliance)

### Data Consistency and Integrity

**Consistency Model**:
- Strong consistency for transactional data (farmers, farms, alerts)
- Eventual consistency acceptable for analytics data (risk scores, weather)
- Use database transactions for multi-table updates

**Data Validation**:
- Application-level validation before database writes
- Database constraints (NOT NULL, CHECK, FOREIGN KEY)
- Unique constraints on natural keys (phone numbers, farm locations)

**Referential Integrity**:
- Foreign key constraints for critical relationships
- Cascade deletes for dependent data (alerts when farm deleted)
- Soft deletes for audit trail (add `deleted_at` column)

