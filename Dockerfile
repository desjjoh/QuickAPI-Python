# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
 && pip install --no-cache-dir --user -r requirements.txt \
 && rm -rf /var/lib/apt/lists/*

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY app ./app

EXPOSE 8000
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker -w ${WORKERS:-2} -b 0.0.0.0:8000 app.main:app"]

