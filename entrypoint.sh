#!/bin/bash
set -e

echo "=== GramSight-AI entrypoint ==="

# Bootstrap: if alembic_version table doesn't exist, the DB was initialised
# via create_all, not Alembic. Stamp the baseline so Alembic knows where we are.
python -c "
from backend_service.database import engine
from sqlalchemy import inspect
insp = inspect(engine)
if 'alembic_version' not in insp.get_table_names():
    print('No alembic_version table — stamping baseline (0001_initial)...')
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'alembic', 'stamp', '0001_initial'])
    print('Baseline stamped.')
else:
    print('alembic_version table exists — skipping stamp.')
"

echo "Running Alembic migrations..."
alembic upgrade head
echo "Migrations complete."

# Execute the CMD passed to the container
exec "$@"
