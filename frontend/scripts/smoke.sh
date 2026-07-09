#!/usr/bin/env bash
set -euo pipefail

echo "==> Starting frontend (and its deps)"
docker compose up -d db backend frontend

echo "==> Waiting for Vite dev server on :5173"
ok=""
for _ in {1..30}; do
  if curl -sf -o /dev/null http://localhost:5173/; then
    ok="yes"
    break
  fi
  sleep 1
done
if [ -z "$ok" ]; then
  echo "ERROR: frontend did not respond on http://localhost:5173/"
  docker compose logs frontend | tail -30
  exit 1
fi

echo "==> Checking key routes return 200"
for path in "/" "/dashboard" "/planner"; do
  code="$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:5173${path}")"
  echo "    ${path} -> ${code}"
  if [ "$code" != "200" ]; then
    echo "ERROR: ${path} returned ${code}"
    exit 1
  fi
done

echo "==> Type-check + production build"
docker compose exec -T frontend npm run build

echo "Frontend smoke test complete."
