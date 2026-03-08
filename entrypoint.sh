#!/bin/bash
set -e

echo "=== GramSight-AI entrypoint ==="

# Bootstrap: decide how to initialise the database.
#   Case 1 — Fresh / corrupted DB (core tables missing):
#            Run create_all from models, then stamp Alembic at head.
#   Case 2 — DB created via create_all but never tracked by Alembic:
#            Stamp baseline (0001_initial) so future migrations apply.
#   Case 3 — Alembic already tracking & core tables present:
#            Just run upgrade.
python -c "
from backend_service.database import engine, Base
from sqlalchemy import inspect, text
import subprocess, sys

insp = inspect(engine)
tables = insp.get_table_names()
has_alembic = 'alembic_version' in tables
has_core_tables = 'users' in tables and 'villages' in tables

if not has_core_tables:
    # Core tables missing — could be fresh DB or corrupted state where
    # alembic_version was stamped but migrations never actually ran.
    if has_alembic:
        print('Corrupted state: alembic_version exists but core tables missing.')
        print('Dropping alembic_version to reset...')
        with engine.connect() as conn:
            conn.execute(text('DROP TABLE alembic_version'))
            conn.commit()
    print('Creating all tables from models...')
    Base.metadata.create_all(bind=engine)
    print('Tables created. Stamping Alembic at head...')
    subprocess.check_call([sys.executable, '-m', 'alembic', 'stamp', 'head'])
    print('Stamped at head — all migrations marked as applied.')
elif not has_alembic and has_core_tables:
    print('DB was initialized via create_all — stamping baseline (0001_initial)...')
    subprocess.check_call([sys.executable, '-m', 'alembic', 'stamp', '0001_initial'])
    print('Baseline stamped.')
else:
    print('alembic_version table exists with core tables — will run pending migrations.')
"

echo "Running Alembic migrations..."
alembic upgrade head
echo "Migrations complete."

# Execute the CMD passed to the container
exec "$@"
