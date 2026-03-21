#!/bin/bash

if [ ! -d "alembic" ]; then
    alembic init alembic
    echo "alembic initialized"
else
    echo "alembic already initialized"

fi

python settings.py

if [ $ENV = "DEV" ]; then
    python -m debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
