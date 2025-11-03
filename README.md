# 🐍 QuickAPI-FastAPI

A lightweight, production-ready REST API built with **FastAPI** and **Async SQLAlchemy**.  
This service is designed to demonstrate clean architecture, modern async Python practices,  
and containerized deployment for small to medium microservices.

---

## 🧭 Overview

QuickAPI includes:

- **FastAPI** — async web framework with automatic OpenAPI docs
- **SQLAlchemy 2.0 (async)** — modern, type-safe ORM
- **Pydantic v2** — data validation and serialization
- **Structlog** — structured JSON logging for observability
- **Middleware & Exception Handling** — consistent request metrics and error formatting
- **SQLite** (default) — simple persistence layer with easy Postgres swap
- **Docker** — production-ready container with CPU/memory limits

---

## 📁 Project Structure

```bash
quickapi/
├─ app/
│  ├─ api/           # Routers and endpoints
│  ├─ core/          # Config, logging, middleware
│  ├─ models/        # Pydantic and ORM models
│  ├─ services/      # Database engine/session management
│  └─ main.py        # Application entry point (lifespan)
├─ requirements.txt
├─ Dockerfile
├─ compose.yaml
└─ README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/quickapi.git
cd quickapi
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # On Windows
# or
source .venv/bin/activate    # On Linux/macOS
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the development server

```bash
python -m uvicorn app.main:app --reload
```

Visit:

- Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Root endpoint → [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 💾 Example API Usage

### Create an item

```bash
curl -X POST http://127.0.0.1:8000/items/      -H "Content-Type: application/json"      -d '{"name": "Widget", "price": 10.99}'
```

### Retrieve all items

```bash
curl http://127.0.0.1:8000/items/
```

Response:

```json
[
  {
    "id": 1,
    "name": "Widget",
    "price": 10.99
  }
]
```

---

## ⚙️ Configuration

Configuration values are read via **Pydantic Settings**.  
Create a `.env` file in the project root to override defaults:

```bash
APP_NAME=QuickAPI
DEBUG=true
DATABASE_URL=sqlite+aiosqlite:///./app.db
```

---

## 🧩 Middleware & Logging

- **Request Logging Middleware**  
  Logs every request’s method, path, status code, and duration (in ms).

- **Global Exception Handlers**  
  Converts unhandled errors into clean JSON responses and logs them with `structlog`.

All logs are structured JSON — ideal for use with tools like Grafana, Loki, or CloudWatch.

---

## 🗄️ Database

Uses **SQLite** by default via `sqlalchemy[asyncio]` and `aiosqlite`.

Switching to Postgres only requires:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname
pip install asyncpg
```

Tables auto-initialize on startup via the app’s lifespan context.

---

## 🐳 Docker Deployment

### Build and run locally

```bash
docker compose up --build
docker run --rm -p 8000:8000 -v ${PWD}/app.db:/app/app.db quickapi:latest
```

### Using Compose

```yaml
services:
  api:
    image: quickapi:latest
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app.db:/app/app.db
    environment:
      APP_NAME: QuickAPI (Docker)
      DEBUG: "false"
    mem_limit: 256m
    cpus: 0.5
    restart: unless-stopped
```

Run:

```bash
docker compose up --build
```

Then open [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🧠 Tech Notes

| Feature    | Library                  | Purpose                           |
| ---------- | ------------------------ | --------------------------------- |
| Framework  | FastAPI                  | Async REST API                    |
| ORM        | SQLAlchemy 2.0           | Async persistence                 |
| Validation | Pydantic v2              | Type-safe request/response models |
| Logging    | Structlog                | JSON structured logs              |
| Database   | SQLite (default)         | Easy local storage                |
| Server     | Gunicorn + UvicornWorker | Production async workers          |

---

## 🧩 Next Steps / Roadmap

- [ ] Swap SQLite → PostgreSQL via `asyncpg`
- [ ] Add health and readiness endpoints
- [ ] Integrate background job queue (Redis + RQ or BullMQ-style)
- [ ] Add unit and integration tests
- [ ] Add GitHub Actions CI/CD

---

## 📄 License

MIT © 2025 John Desjardins  
You’re free to use, modify, and distribute this project with attribution.
