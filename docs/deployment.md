# Deployment

## Development

```bash
# Install
uv sync
mkdir -p storage

# Run with auto-reload
PYTHONPATH=src uvicorn root.entrypoints.api:create_app \
    --factory --reload --reload-dir src

# Or via the installed script
PYTHONPATH=src notification-system
```

Access at `http://127.0.0.1:8000`.

---

## Docker Compose (recommended for production)

```bash
# Copy and edit env file
cp .env.example .env

# Build + start
docker compose up -d --build

# View logs
docker compose logs -f app

# Stop
docker compose down
```

The compose file uses a named volume (`app_data`) for persistent SQLite storage.

---

## Environment Variables Reference

| Variable | Default | Notes |
|---|---|---|
| `LOG_LEVEL` | `INFO` | `DEBUG` for verbose output |
| `CORE_DB_URL` | `sqlite+aiosqlite:///storage/app.sqlite` | SQLite path (absolute inside container: `/app/storage/app.sqlite`) |
| `NOTIFICATIONS_API_TIMEOUT_SECONDS` | `10` | Telegram HTTP timeout |
| `PORT` | `8000` | Docker host port (compose only) |

---

## Production Notes

### SQLite WAL mode

The shared provider enables WAL journal mode (`PRAGMA journal_mode=WAL`) automatically.
This allows one writer and multiple readers simultaneously, which is sufficient for most monitoring workloads.

For high-write scenarios, migrate to PostgreSQL by:
1. Changing `CORE_DB_URL` to `postgresql+asyncpg://...`
2. Adding `asyncpg` to `pyproject.toml`
3. Removing the SQLite `PRAGMA` block in `SharedProvider`

### Scaling

This template is designed for a **single-process** deployment.

The background worker (detector + Telegram polling) runs as asyncio tasks within the same process as the web server.
This works well because:
- SQLite WAL handles concurrent reads + a single writer safely
- asyncio event loop handles I/O concurrency without threads

If you need horizontal scaling:
- Switch to PostgreSQL
- Move the worker to a separate process (`python -m root.entrypoints.worker`)
- Use Redis or a message broker for cross-process event dispatch

### Reverse Proxy (Nginx example)

```nginx
server {
    listen 80;
    server_name monitor.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service

```ini
[Unit]
Description=Notification System
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/notification-system
Environment=PYTHONPATH=/opt/notification-system/src
ExecStart=/opt/notification-system/.venv/bin/uvicorn \
    root.entrypoints.api:create_app \
    --factory --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Note: use `--workers 1`. Multiple uvicorn workers would each start their own background worker and Telegram polling — conflicting on the same SQLite database and Telegram session.

---

## Database Migrations

This template uses SQLAlchemy's `create_all()` on startup, which is sufficient for new tables.

For schema changes on an existing database, either:

1. **Delete and recreate** (simplest — only for development):
   ```bash
   rm storage/app.sqlite
   ```

2. **Alembic** (for production):
   ```bash
   uv pip install alembic
   alembic init alembic
   # Edit alembic/env.py to import your Base metadata
   alembic revision --autogenerate -m "describe change"
   alembic upgrade head
   ```

---

## Health Check

`GET /health` returns `{"status": "ok"}` with HTTP 200.
Used by Docker compose healthcheck and load balancers.
