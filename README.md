# Cogsci_Planner

## Dev Testing Workflow

Use these commands from the repo root:

- `make dev-up` — start `db`, `backend`, and `frontend` (rebuilds images, syncs frontend deps)
- `make dev-down` — stop the stack
- `make dev-restart` — stop then start (use after `package.json` or Docker changes)
- `make migrate` — apply Alembic migrations
- `make seed` — seed academic data
- `make test-backend` — run backend pytest suite
- `make smoke-backend` — run end-to-end backend smoke script
- `make test-frontend` — type-check + production build (catches TS/bundler errors)
- `make smoke-frontend` — run end-to-end frontend smoke script
- `make smoke` — run both backend and frontend smoke scripts

The backend smoke script (`backend/scripts/smoke.sh`) verifies backend startup,
`/api/ping`, migrations, seed, tests, and one API payload check.

The frontend smoke script (`frontend/scripts/smoke.sh`) verifies the Vite dev
server responds on `:5173`, that `/`, `/courses`, and `/planner` return 200, and
that the app type-checks and builds.

> Note: the app uses client-side routing, so open `http://localhost:5173/`
> or `http://localhost:5173/courses` only after `make dev-up` has started the
> `frontend` container.