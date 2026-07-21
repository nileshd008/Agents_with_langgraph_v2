#!/bin/bash

set -a
source .env
set +a

if [ "$db_dialect" = "mysql" ]; then
    export SANDBOX_CONNECTION="mysql+pymysql://${SANDBOX_USER}:${SANDBOX_PASSWORD}@sandbox_db:3306/${SANDBOX_DB}"
    COMPOSE_FILE=docker-compose.mysql.yml

elif [ "$db_dialect" = "postgres" ]; then
    export SANDBOX_CONNECTION="postgresql+psycopg://${SANDBOX_USER}:${SANDBOX_PASSWORD}@sandbox_db:5432/${SANDBOX_DB}"
    COMPOSE_FILE=docker-compose.postgres.yml

else
    echo "Unsupported DB_DIALECT: $db_dialect"
    exit 1
fi

docker compose \
    -f docker-compose.yml \
    -f "$COMPOSE_FILE" \
    up --build