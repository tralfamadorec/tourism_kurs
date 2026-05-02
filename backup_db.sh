version: '3.8'
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
        POSTGRES_PASSWORD: ${DB_PASS}
        POSTGRES_DB: ${DB_NAME}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: always

  web:
    build: .
    command: >
      sh -c "alembic upgrade head &&
             uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    restart: always
    expose:
      - "8000"

volumes:
  pgdata: