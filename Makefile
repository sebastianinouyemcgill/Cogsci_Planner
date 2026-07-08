COMPOSE ?= docker compose

.PHONY: dev-up dev-down migrate seed \
        test-backend smoke-backend \
        test-frontend smoke-frontend \
        smoke

# --- environment -----------------------------------------------------------

dev-up:
	$(COMPOSE) up -d db backend frontend

dev-down:
	$(COMPOSE) down

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
