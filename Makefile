COMPOSE ?= docker compose

.PHONY: dev-up dev-down dev-restart \
        migrate seed \
        test-backend smoke-backend \
        test-frontend smoke-frontend \
        smoke

# --- environment -----------------------------------------------------------

# Rebuild frontend image when dependencies change; sync node_modules volume.
dev-up:
	$(COMPOSE) up -d --build db backend
	$(COMPOSE) build frontend
	$(COMPOSE) run --rm --no-deps -T frontend npm install
	$(COMPOSE) up -d --force-recreate frontend
	@echo ""
	@echo "Stack ready:"
	@echo "  Frontend  http://localhost:5173"
	@echo "  Backend   http://localhost:8000/api/ping"
	@echo "  Run 'make seed' if course data is missing."

# Stop all compose services.
dev-down:
	$(COMPOSE) down

# Full stop + start (use after package.json or Docker changes).
dev-restart: dev-down dev-up

# --- backend ---------------------------------------------------------------

migrate:
	$(COMPOSE) exec -T backend alembic upgrade head

seed:
	$(COMPOSE) exec -T backend python -m app.seed

test-backend:
	$(COMPOSE) exec -T backend python -m pytest -q

smoke-backend:
	bash backend/scripts/smoke.sh

# --- frontend --------------------------------------------------------------

# Type-check + production build; fails loudly on TS or bundler errors.
test-frontend:
	$(COMPOSE) exec -T frontend npm run build

smoke-frontend:
	bash frontend/scripts/smoke.sh

# --- full stack ------------------------------------------------------------

smoke: smoke-backend smoke-frontend
