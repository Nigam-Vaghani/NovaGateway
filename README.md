# NovaGateway – Enterprise Reverse Proxy & API Gateway

NovaGateway is a production-ready Reverse Proxy and API Gateway built with FastAPI and PostgreSQL. It sits between clients and backend services, intelligently routing HTTP traffic while providing monitoring, security, caching, load balancing, and operational features comparable to lightweight versions of Nginx or Traefik.

## Key Features

- **Dynamic Routing & Reverse Proxy**: Forward HTTP requests to dynamic backend services with path matching, prefix stripping, and transparent header management.
- **Load Balancing & Health Checks**: Supports Round-Robin and Weighted load balancing across multiple backends with automatic failover and asynchronous health checks.
- **Security & Rate Limiting**: IP-based rate limiting (Redis sliding window), IP Allow/Block filtering, Request Size Limits, API Key authentication, and mandatory security headers.
- **HTTPS & SSL Termination**: Secure client communication with built-in SSL termination, automatic HTTP-to-HTTPS redirection, and HSTS support.
- **Observability**: Comprehensive asynchronous request logging to PostgreSQL (capturing latency, status, path, client IP, errors, etc.).

## System Architecture

```mermaid
graph TD
    Client["Client (Browser / API Consumer)"]
    Gateway["NovaGateway (FastAPI)"]
    Redis["Redis (Cache + Rate Limiting)"]
    DB["PostgreSQL (Routes + Logs + Security)"]
    B1["Backend Service A"]
    B2["Backend Service B"]
    B3["Backend Service N"]

    Client -->|HTTPS Request| Gateway
    Gateway -->|Check Rate Limit| Redis
    Gateway -->|Cache Lookup| Redis
    Gateway -->|Route Lookup| DB
    Gateway -->|Log Request| DB
    Gateway -->|Forward Request| B1
    Gateway -->|Forward Request| B2
    Gateway -->|Forward Request| B3
```

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (via asyncpg + SQLAlchemy)
- **Caching/Rate Limiting**: Redis
- **HTTP Client**: HTTPX (Async)
- **Migrations**: Alembic

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL
- Redis
- Docker (optional, for containerized deployment)

### Local Setup

1. **Clone the repository and install dependencies:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   Create a `.env` file in the root directory based on `.env.example`:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/novagateway
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=supersecret
   ALLOWED_HOSTS=*
   RATE_LIMIT_REQUESTS=100
   RATE_LIMIT_WINDOW=60
   HEALTH_CHECK_INTERVAL=30
   LOG_LEVEL=INFO
   MAX_REQUEST_SIZE_MB=10
   MAX_RETRIES=3
   LOAD_BALANCER_STRATEGY=round_robin
   ```

3. **Database Migrations:**
   Ensure PostgreSQL is running locally and apply the Alembic migrations:
   ```bash
   alembic upgrade head
   ```

4. **SSL Setup (Optional but recommended):**
   Generate self-signed certificates for development to test SSL termination:
   ```bash
   mkdir certs
   cd certs
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes -subj "//CN=localhost"
   ```
   Add to `.env`:
   ```env
   SSL_CERTFILE=../certs/cert.pem
   SSL_KEYFILE=../certs/key.pem
   HTTPS_PORT=443
   HTTP_REDIRECT_PORT=80
   ```

5. **Run the Gateway:**
   ```bash
   python run.py
   ```
   *Note: If SSL is configured, this will automatically start an HTTPS server on `HTTPS_PORT` and an HTTP redirect server on `HTTP_REDIRECT_PORT`.*

### Docker Deployment

To run the entire stack (Gateway, PostgreSQL, Redis) via Docker Compose:
```bash
docker-compose up -d --build
```
*Ensure you have generated the `certs/` folder in the root directory if you want SSL termination enabled in Docker.*

## Core Configuration & API Surface

### 1. Proxy Engine
The gateway exposes a catch-all route `/{path:path}` that intercepts traffic, resolves the appropriate backend using the requested path, applies security/rate-limiting middlewares, and forwards the request via an asynchronous `httpx` connection pool. It manages hop-by-hop headers, `X-Forwarded-For` injection, and handles connection failures gracefully.

### 2. Admin API
NovaGateway provides a set of REST endpoints to manage configuration dynamically without restarting the server:

**Routes & Backends:**
- `GET /admin/routes` - List all routes
- `POST /admin/routes` - Create a route
- `GET /admin/backends` - List backends
- `POST /admin/backends` - Add a backend to a route

**Security:**
- `POST /admin/security/api-keys` - Issue new API Keys
- `POST /admin/security/ip-rules` - Add IP Allow/Block rules

**Observability:**
- `GET /admin/logs` - Retrieve paginated request logs with filters (e.g., latency, status codes).

### 3. Load Balancing Strategies
Configurable via `LOAD_BALANCER_STRATEGY`:
- **Round Robin (`round_robin`)**: Distributes requests evenly across all healthy backends.
- **Weighted Round Robin (`weighted`)**: Distributes requests proportionally based on backend weight settings.

Health checks run asynchronously every `HEALTH_CHECK_INTERVAL` seconds to automatically ping each backend and temporarily remove failing instances from the active rotation.

### 4. Security Measures
- **Rate Limiting**: Configured globally per IP using Redis.
- **Security Headers**: HSTS, `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, etc.
- **Cookies**: Automatically injects `Secure` and `SameSite=Strict` flags to proxied `Set-Cookie` headers when in HTTPS mode.

## CI/CD Pipeline

The project includes a `Makefile` to simplify CI/CD tasks, which are compatible with GitHub Actions or other CI runners.

### Useful Commands
- `make dev` - Start development environment using Docker Compose.
- `make prod` - Start production environment using `docker-compose.prod.yml`.
- `make test` - Run the test suite with `pytest`.
- `make lint` - Run code linting with `ruff`.
- `make migrate` - Apply Alembic migrations.
- `make down` - Tear down Docker containers.

### Example GitHub Actions Workflow

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Lint
        run: make lint
      - name: Test
        run: make test
```