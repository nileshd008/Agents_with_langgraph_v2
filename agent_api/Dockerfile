FROM python:3.12-alpine AS builder

WORKDIR /app


RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev


COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


RUN uv venv /opt/venv


COPY requirements.txt .
RUN . /opt/venv/bin/activate && uv pip install --no-cache -r requirements.txt


FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache \
    libpq \
    curl


COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY . .

EXPOSE 8050

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8050"]