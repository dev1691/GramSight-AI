# GramSight-AI

Rural Infrastructure Intelligence Platform: GramSight AI converts satellite imagery into actionable rural intelligence using computer vision, geo-projection, risk scoring, and executive summarization.

---

## Quick Start (Docker)

### Prerequisites

- **Docker** &ge; 20.10 and **Docker Compose** (v2 plugin)
- Ports **8080**, **8000**, **8001**, **5432**, **6379**, **5050** available

### 1. Clone & configure

```bash
git clone <repo-url> && cd GramSight-AI
cp .env.example .env          # then edit .env with your API keys
```

### 2. Build & run

```bash
docker compose up --build -d
```

### 3. Access the services

| Service   | URL                          |
| --------- | ---------------------------- |
| Frontend  | http://localhost:8080         |
| Backend   | http://localhost:8000/health  |
| Admin     | http://localhost:8001         |
| pgAdmin   | http://localhost:5050         |

pgAdmin default login: `pgadmin@example.com` / `admin`

### Rebuild a single service

```bash
docker compose build --no-cache frontend   # or backend, admin_service, etc.
docker compose up -d frontend
```

---

## Project Structure

```
GramSight-AI/
├── backend_service/   # FastAPI backend (uvicorn)
├── admin_service/     # FastAPI admin dashboard
├── frontend/          # React + Vite SPA (served by nginx)
├── alembic/           # Database migrations
├── scripts/           # Utility scripts (e.g. create_admin.py)
├── Dockerfile         # Backend & worker image
├── docker-compose.yml # Full stack orchestration
├── requirements.txt   # Python dependencies (backend)
└── .env.example       # Template environment variables
```

## Environment Variables

Copy `.env.example` to `.env` and fill in the values. Key variables:

| Variable              | Description                                    |
| --------------------- | ---------------------------------------------- |
| `POSTGRES_USER`       | Postgres user (shared between compose & code)  |
| `POSTGRES_PASSWORD`   | Postgres password                              |
| `POSTGRES_DB`         | Database name                                  |
| `DB_USER` / `DB_PASSWORD` / `DB_NAME` | Must match `POSTGRES_*` vars  |
| `SECRET_KEY`          | JWT signing key (change for production!)       |
| `OPENWEATHER_API_KEY` | OpenWeather API key                            |
| `MARKET_API_KEY`      | Market data API key                            |
| `ADMIN_API_KEY`       | Admin dashboard API key                        |

## Local Frontend Development

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev                   # Vite dev server on http://localhost:5173
```

## Notes

- The frontend Docker build uses `node node_modules/vite/bin/vite.js build` instead of `npm run build` to avoid Alpine Linux shebang issues with npm shell wrappers.
- If `npm ci` fails inside Docker due to a lockfile mismatch, the Dockerfile falls back to `npm install` automatically. For reproducible CI builds, run `npm install --legacy-peer-deps` locally and commit the updated `package-lock.json`.

