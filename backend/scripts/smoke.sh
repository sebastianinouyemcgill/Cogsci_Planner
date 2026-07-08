#!/usr/bin/env bash
set -euo pipefail

echo "==> Starting db + backend"
docker compose up -d db backend

echo "==> Waiting for backend health endpoint"
for _ in {1..30}; do
  if docker compose exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/ping').read(); print('ok')" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
docker compose exec -T backend python -c "import urllib.request, json; print(json.load(urllib.request.urlopen('http://localhost:8000/api/ping')))"

echo "==> Running migrations"
docker compose exec -T backend alembic upgrade head

echo "==> Running seed"
docker compose exec -T backend python -m app.seed

echo "==> Running backend tests"
docker compose exec -T backend python -m pytest -q

echo "==> Smoke check API payload"
docker compose exec -T backend python -c "import urllib.request, json; payload=json.load(urllib.request.urlopen('http://localhost:8000/api/courses/?search=COMP%20551')); c=payload[0]; print({'code': c['code'], 'faculty': c['faculty'], 'level': c['level'], 'credits': c['credits']})"

echo "Smoke test complete."
