# TEMP

1. Security Middleware

   Add HTTP security headers

   Strict-Transport-Security

   X-Content-Type-Options

   X-Frame-Options

   X-XSS-Protection (legacy but harmless)

   Referrer-Policy

   Permissions-Policy

   Content-Security-Policy (basic, no inline script execution)

2. Rate Limiting

   Per-IP request throttling

   Burst + sustained window

   No connection-killing, just clean 429 responses with our custom error formatting

3. Request Size Limits

   Restrict JSON bodies (5MB or similar)

   Restrict headers length

   FastAPI can enforce this at ASGI or via middleware

4. Process Safety / Lifecycle Hardening

   Make sure services stop cleanly

   Ensure DB connections close sanely

   Prevent silent failure on startup/shutdown
   (This is already nearly perfect in our template.)

5. CORS (strict & simple)

   Explicit allowed origins array

   No wildcard unless development

   Limit methods to GET,POST,PUT,PATCH,DELETE

6. Suppress internal errors

   Our custom error handler already does this

   Hide Python tracebacks

   Always return our safe error envelope
   This is done — we just need to be sure errors never leak stack traces.

7. Hide server fingerprint

   Override FastAPI’s default OpenAPI exposed metadata (done)

   Disable default Server: uvicorn header

   Add stripped or custom header

8. Log sanitization

   Ensure we redacted sensitive inputs (we already do not log body by default)

   Avoid logging stack traces in production

9. Basic input-level protections

   Path parameter regex validation for HexId

   Null/Unset rules for PATCH/PUT (we finished this)

## ⭐ Why it's not an 8–10 yet (and that’s okay!)

These missing pieces are what separate production-ready from battle-tested enterprise.

- 7 → 8 requires:

  CORS policies

  Rate limiting

  API authentication (JWT, API keys)

  Role/permission examples

  Exception-safe database disposal

  Environment-based feature toggles

  Response caching hooks

- 8 → 9 requires:

  Multi-environment config (dev/stage/prod)

  Metrics + tracing (Prometheus, OpenTelemetry)

  Health endpoints that check subsystems

  Request logging redaction logic

  Background job framework integration (RQ/BullMQ/Celery)

  Configurable CORS, CSP, and Permissions-Policy

.

## More

4. Process Safety / Lifecycle Hardening

   You're already strong here, but we can refine:

   graceful shutdown

   worker shutdown hooks

   DB cleanup

   background task draining

   start/stop verifiers
