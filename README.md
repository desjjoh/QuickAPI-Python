# 🧩 QuickAPI-FastAPI

A lightweight, production-ready FastAPI template focused on clean architecture, observability, and graceful lifecycle management.

---

## 📁 Project Structure

```bash
app/
├─ api/
│  ├─ health/                # Health & metrics endpoints
│  │  ├─ models/
│  │  │  └─ schemas.py
│  │  └─ routes.py
│  ├─ items/                 # CRUD example module
│  │  ├─ models/
│  │  │  ├─ db_models.py
│  │  │  ├─ item.py
│  │  │  └─ schemas.py
│  │  └─ routes.py
│
├─ core/                     # Core infrastructure
│  ├─ config.py              # Application configuration (pydantic settings)
│  ├─ logging.py             # Structlog configuration with colorized output
│  ├─ middleware.py          # Request logging & error handling middleware
│
├─ services/                 # Shared services (DB, caching, etc.)
│  └─ db.py                  # Async SQLAlchemy engine and session manager
│
└─ main.py                   # Application entrypoint with graceful lifespan
```

---

## ⚙️ Features

- **FastAPI** powered async API with modular route architecture
- **SQLite** via async SQLAlchemy for persistence
- **Structured logging** with contextual, colorized output
- **Centralized error handling & middleware**
- **Health & readiness routes** for observability
- **Graceful startup/shutdown** via lifespan context
- **Dockerized** with lightweight Uvicorn runtime and healthcheck

---

## 🚀 Running the Application

### Local Development

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Dockerized Environment

```bash
docker compose up --build
```

The API will be available at  
**<http://localhost:8000>**

Swagger documentation:  
**<http://localhost:8000/docs>**

---

## 🩺 Health & Monitoring

| Endpoint        | Description                            |
| --------------- | -------------------------------------- |
| `/health/alive` | Verifies the service is reachable      |
| `/health/ready` | Confirms DB connectivity and readiness |

---

## 🧰 Environment Variables

| Variable       | Default                        | Description                            |
| -------------- | ------------------------------ | -------------------------------------- |
| `APP_NAME`     | `QuickAPI`                     | Application name for logging context   |
| `DEBUG`        | `false`                        | Enables development logging and reload |
| `DATABASE_URL` | `sqlite+aiosqlite:///./app.db` | Connection string for database         |

---

## 🧩 Docker Compose Overview

```yaml
services:
  api:
    image: quickapi-fastapi:latest
    container_name: quickapi-fastapi
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app.db:/app/app.db
    environment:
      APP_NAME: QuickAPI
      DEBUG: "false"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/ready"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    restart: unless-stopped
```

---

## 🧠 Design Principles

- **Fail-fast validation** using Pydantic schemas
- **Observable behavior** through contextual, structured logs
- **Graceful degradation** — clean startup, shutdown, and error boundaries
- **Portable architecture** — swap SQLite for Postgres, Redis, etc. with minimal effort

---

## 🧾 License

MIT © John Desjardins
