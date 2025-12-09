#!/bin/sh
set -e

python scripts/seed_db.py || echo "Seed script failed, continuing..."

exec python app.py
