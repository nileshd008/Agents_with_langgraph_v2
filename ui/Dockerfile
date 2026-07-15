FROM python:3.11-alpine AS builder

WORKDIR /app

RUN apk add --no-cache \
    gcc \
    musl-dev

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache curl

COPY --from=builder /install /usr/local
COPY . .

EXPOSE 3000

CMD ["streamlit", "run", "run.py", "--server.port=3000", "--server.address=0.0.0.0"]