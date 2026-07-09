# Architecture Notes — McGill Cognitive Science Degree Planner

## Purpose

This document describes the technical architecture and implementation decisions for the McGill Cognitive Science Degree Planner.

The goal is to maintain a clean separation between:

1. **Product logic** — degree requirements, course relationships, requirement evaluation
2. **Application logic** — API endpoints, database operations, frontend state
3. **Infrastructure** — Docker, PostgreSQL, development environment

---

## Current Tech Stack

### Frontend
- React
- TypeScript
- Vite

Responsibilities: degree dashboard, course status tracking, stream exploration, bucket overrides, honours toggle.

### Backend
- FastAPI

Responsibilities: API layer, database communication, requirement evaluation engine.

### Database
- PostgreSQL (production / Docker)
- SQLite (unit tests via in-memory DB)
- SQLAlchemy (ORM)

### Infrastructure
- Docker Compose

**Services:** `frontend`, `backend`, `database`

| Service | Port |
|---|---|
| Frontend | localhost:5173 |
| Backend | localhost:8000 |
| Database | localhost:5432 |

---

## High-Level Architecture

```
React Frontend
      ↓
FastAPI Backend
      ↓
SQLAlchemy ORM
      ↓
PostgreSQL Database
```

The frontend never accesses the database directly. All data flows through FastAPI.

---

## Backend Structure

```
backend/
└── app/
    ├── main.py
    ├── database.py
    ├── models/
    │   ├── course.py
    │   ├── stream.py
    │   ├── area.py
    │   └── requirement.py
    ├── schemas/
    │   ├── course.py
    │   ├── stream.py
    │   ├── area.py
    │   ├── requirement.py
    │   └── requirement_progress.py
    ├── routers/
    │   ├── courses.py
    │   └── requirements.py
    ├── services/
    │   └── degree_evaluator.py      # pure allocation logic (no ORM)
    └── seed/
        ├── cogsci_seed_data.py      # source of truth for McGill CogSci data
        ├── data.py                  # re-exports cogsci_seed_data
        └── seeder.py                # idempotent DB seeding
```

**Academic catalogue reference:** `cogsci_course_catalogue.md` (repo root) — McGill 2026–2027 Honours Cognitive Science (B.A. & Sc., 60 credits). The seed file mirrors this structure; expand course lists from the catalogue as needed.

---

## Database Design

Courses are connected through prerequisites, streams, areas, and requirements.

### Core Tables

#### `courses`

| Field | Notes |
|---|---|
| id | |
| code | e.g. `COMP 551` |
| title | |
| description | |
| credits | |
| level | numeric (200, 300, 400, 500, …) |
| faculty | Arts / Science |
| department | |

**Level** is stored numerically so upper-level requirements can be queried with `level >= 400`.

**Faculty** supports the Arts/Science degree requirement.

#### `streams`

Five Cognitive Science streams: Computer Science, Neuroscience, Psychology, Linguistics, Philosophy.

#### `course_streams` (many-to-many)

Links a course to the stream(s) whose **Complementary Courses** list it appears on in the official catalogue.

**Important:** A course may satisfy a Core Complementary **area** without being on any stream list. Stream tags come only from stream complementary lists, not from area eligibility.

#### `course_prerequisites` (self-referencing)

Prerequisites generate warnings only — they never block course selection.

#### `areas`

Eight planner areas mapping McGill's Core Complementary categories (24 credits total):

1. Neuroscience (Required) — `NSCI 201`
2. Logic
3. Statistics
4. Computer Science Foundations
5. Linguistics Foundations
6. Philosophy Foundations
7. Neuroscience Foundations
8. Psychology Foundations

"Area" is planner vocabulary; McGill calls this Core Complementary (18 credits in Honours, one course per category).

#### `area_courses`

Defines which courses can satisfy each area. Multiple courses per area are allowed; only one is consumed per area during allocation.

#### `requirements`

Degree-level rules (not course lists):

| Name | Type | Credits |
|---|---|---|
| Required Areas | area_completion | 24 |
| Stream Requirement | stream | 18 |
| Complementary Requirement | complementary | 12 |
| 400-Level Requirement | level_threshold | 15 |
| Arts Requirement | faculty | 21 |
| Science Requirement | faculty | 21 |
| Honours Research Requirement | honours | 6 |

---

## Seed Data Model (`cogsci_seed_data.py`)

Three parallel course classifications drive the evaluator:

1. **`AREA_COURSES`** — courses eligible for one of the 8 area slots.
2. **`COURSE_STREAMS`** — courses on a stream's Complementary list (can be multi-tagged).
3. **`ELECTIVES_ONLY_COURSES`** — area-eligible courses with **no** stream mapping.

Additional constants:

- **`ELECTIVES_BUCKET_COURSES`** — electives-only + research courses (`COGS 401`, `COGS 444`).
- **`FLEXIBLE_FACULTY_COURSES`** — e.g. `COGS 444` may count toward Arts or Science (whichever helps).

**Area overflow rule:** If a student takes more than one course eligible for the same area, one course fills the area slot; additional credits from that area overflow to the **Electives** bucket (visible, not dropped).

**Example:** `COMP 202` satisfies Computer Science Foundations but is not on the CS stream list. `COMP 250` satisfies the same area and is on the CS stream list. With both completed, one fills the area and the other can count toward the stream; if both would only satisfy area, the second goes to Electives.

The seed currently includes **82 courses** — a representative subset of each stream list, not the full catalogue.

---

## Requirement Allocation Engine (`degree_evaluator.py`)

Pure Python service (no SQLAlchemy). Input is a list of `CompletedCourse` dataclass instances with eligibility metadata.

### API entry point

```
POST /api/requirements/progress
```

Request body includes:

- `courses: [{ course_id, status, bucket_override? }]` — `completed` or `planned`
- `declared_stream?` — optional official stream for complementary allocation
- `honours_enabled?` — toggles honours research tracking
- `manual_completed_courses?` — non-catalogue courses for Arts/Science totals

Response includes **dual progress**: `completed` and `projected` (completed + planned).

### Allocation phases (v1 greedy)

For each progress snapshot:

1. **Areas** — one course per area (tie-break: lowest course code); area overflow → Electives.
2. **Explore streams** — `stream_complementary`: independent progress bars for all 5 streams (what-if exploration).
3. **Official stream + complementary** — `official_stream_complementary`: uses `declared_stream` or provisional best-fit stream; 18 cr stream + 12 cr complementary cap; overflow → Electives.
4. **Electives** — explicit electives-bucket courses + official stream-pool overflow.
5. **Independent tallies** — 400-level (15 cr), Arts (21 cr), Science (21 cr), honours research (6 cr when enabled).

### Bucket overrides

Per-course `bucket_override` lets the user force allocation to a specific bucket (area name, stream name, `Complementary`, or `Electives`). Invalid overrides return HTTP 422.

### Design constraints

- A course cannot satisfy mutually exclusive buckets (e.g. stream vs complementary in the official allocation).
- 400-level and Arts/Science requirements are **independent** — the same course credit can count toward a program bucket and toward 400+/faculty totals.
- `COGS 444` satisfies honours research when `honours_enabled` is true; `COGS 401` tracks in the Electives bucket.

Future work may replace the greedy allocator with constraint optimization; the `CompletedCourse` interface and response schema are designed to stay stable.

---

## User Data Model

Authentication and persistent user plans are future milestones.

Planned tables: `users`, `user_courses`, `plans`, `planned_courses`.

Current dashboard state (course status, overrides, declared stream) lives in frontend context and is sent to the progress API on each evaluation.

---

## Frontend Structure

```
frontend/src/
├── pages/
│   └── Dashboard.tsx
├── context/
│   └── CourseStatusContext.tsx
├── api/
│   ├── courses.ts
│   └── requirements.ts
└── types/
    ├── course.ts
    └── requirement.ts
```

### State management

React Context for course status, bucket overrides, declared stream, and honours toggle. Server state fetched via the progress API.

### Dashboard (implemented)

- Required areas progress
- Explore stream bars (all 5 streams)
- Official stream + complementary (declared or provisional)
- Electives bucket
- 400-level, Arts/Science, honours research
- Per-course bucket override controls with 422 error display

---

## API Design

### Courses

```
GET /api/courses
GET /api/courses/{course_id}
```

### Requirements

```
POST /api/requirements/progress
```

Evaluates degree progress from the request payload against seeded catalogue data.

---

## Development Principles

1. **Model the academic domain first.** Seed data and relationships must match the official catalogue structure.
2. **Keep business logic in services.** Routers load ORM rows and call `degree_evaluator.py`.
3. **No hard-coded degree logic in the frontend.** The backend determines allocations; the UI displays and overrides.
4. **Seed idempotently.** `seed_all()` can run multiple times without duplicating rows.
5. **Test the evaluator in isolation.** Unit tests use `CompletedCourse` fixtures, not the database.

---

## Current Status

- ✓ Docker Compose setup
- ✓ React + FastAPI + PostgreSQL
- ✓ SQLAlchemy models (courses, streams, areas, requirements, prerequisites)
- ✓ Catalogue-aligned seed data (`cogsci_seed_data.py`, 82 courses)
- ✓ Idempotent seeder
- ✓ Degree evaluation engine with dual completed/projected progress
- ✓ Progress API with bucket overrides, declared stream, honours
- ✓ Dashboard UI wired to progress API

**Next milestones:** semester planner, prerequisite warnings, graph visualization, user accounts / saved plans.
