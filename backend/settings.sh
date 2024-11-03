#!/bin/bash

if [ ! -d "alembic" ]; then
    alembic init alembic
    echo "alembic initialized"
else
    echo "alembic already initialized"

fi

python settings.py

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload