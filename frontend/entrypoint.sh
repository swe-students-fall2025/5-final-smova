#!/bin/sh
set -e

python scripts/ml_client.py || echo "Seed script failed, continuing..."

exec python app.py
