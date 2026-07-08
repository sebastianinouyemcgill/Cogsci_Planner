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

Responsibilities: user interface, degree dashboard, course exploration, semester planner, graph visualization.

### Backend
- FastAPI

Responsibilities: API layer, database communication, requirement evaluation engine, course recommendation logic.

### Database
- PostgreSQL
- SQLAlchemy (ORM)

Responsibilities: store academic data, user plans, and requirement relationships.

### Infrastructure
- Docker Compose

**Services:** `frontend`, `backend`, `database`

**Current ports:**

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

**The frontend should never directly access the database.** All data flows through FastAPI APIs.

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
    │   └── requirement.py
    ├── schemas/
    │   ├── course.py
    │   └── requirement.py
    ├── routers/
    │   ├── courses.py
    │   ├── planner.py
    │   └── requirements.py
    ├── services/
    │   ├── degree_evaluator.py
    │   └── allocation_engine.py
    └── seed/
        ├── courses.py
        └── requirements.py
```

---

## Database Design

The database should model the academic domain. Courses are not simply stored as a flat list — they're connected through prerequisites, streams, areas, and requirements.

### Core Tables

#### `courses`

| Field | Notes |
|---|---|
| id | |
| code | e.g., `COMP551` |
| title | e.g., "Applied Machine Learning" |
| description | |
| credits | e.g., 3 |
| level | numeric (see below) |
| faculty | Arts / Science |
| department | |

**Level** is stored numerically (e.g., 200, 300, 400, 500) so upper-level requirements can be queried with `level >= 400`.

**Faculty** (Arts / Science) supports the Arts/Science degree requirement.

#### `streams`

| Field | Notes |
|---|---|
| id | |
| name | Computer Science, Neuroscience, Psychology, Linguistics, Philosophy |

#### `course_streams` (many-to-many)

| Field |
|---|
| course_id |
| stream_id |

A course may belong to multiple streams (e.g., `COMP550` → Computer Science, Linguistics).

#### `course_prerequisites` (self-referencing)

| Field |
|---|
| course_id |
| prerequisite_course_id |

Example: `COMP551` requires `COMP251`.

> **Important:** Prerequisites generate warnings only — they never prevent students from adding a course to their plan.

#### `areas`

| Field | Notes |
|---|---|
| id | |
| name | e.g., Artificial Intelligence, Language, Cognition, Perception |

The first 24 credits of the degree consist of 8 required areas.

#### `area_courses`

| Field |
|---|
| area_id |
| course_id |

Defines which courses satisfy each area (e.g., Artificial Intelligence → `COMP550`, `COMP551`).

#### `requirements`

| Field | Notes |
|---|---|
| id | |
| name | e.g., Stream Requirement, Complementary Requirement, 400-Level Requirement, Arts Requirement, Science Requirement, Honours Research Requirement |
| type | |
| credits_required | |

Requirements are **rules**, not simple course lists. Examples:

- **Stream Requirement:** need 18 credits from one stream
- **Advanced Requirement:** need 15 credits where `course.level >= 400`
- **Arts Requirement:** need 21 Arts credits

---

## Requirement Allocation Engine

The most important backend component. Given a student's selected courses, it determines the best allocation of those courses across requirements.

**Input:** completed/planned courses (e.g., `COMP551`, `COMP550`, `COMP558`)

**Example output:**

| Course | Allocated To |
|---|---|
| COMP551 | Computer Science Stream, 400+ Requirement |
| COMP550 | Artificial Intelligence Area |
| COMP558 | Computer Science Stream |

### Allocation Rules

1. **Mutual exclusivity:** A course cannot satisfy multiple mutually exclusive requirements (e.g., cannot count as both Stream credits and Complementary credits).
2. **Independent constraints:** The 400+ requirement is independent — a course can satisfy both a Stream requirement *and* the 400+ requirement simultaneously.
3. **Optimization:** The system should optimize for overall completion. Candidate approaches: constraint satisfaction, integer programming, graph optimization.

---

## User Data Model

Authentication is a future milestone (OAuth, possibly McGill login).

#### `users`

| Field |
|---|
| id |
| email |
| name |

#### `user_courses`

| Field | Notes |
|---|---|
| user_id | |
| course_id | |
| status | completed / planned |

#### `plans`

| Field |
|---|
| id |
| user_id |
| name |

#### `planned_courses`

| Field |
|---|
| plan_id |
| course_id |
| semester |
| year |

---

## Frontend Structure

```
frontend/src/
├── components/
│   ├── CourseCard
│   ├── CourseList
│   ├── RequirementProgress
│   ├── SemesterColumn
│   └── GraphViewer
├── pages/
│   ├── Dashboard
│   ├── CourseExplorer
│   └── Planner
├── api/
│   ├── courses.ts
│   ├── requirements.ts
│   └── planner.ts
└── types/
    ├── course.ts
    └── requirement.ts
```

### State Management

- **Short term:** React Context
- **Long term:** possibly React Query or Zustand for server state

### Main Pages

- **Dashboard** — degree completion, stream progress, missing requirements, recommendations
- **Course Explorer** — course information, prerequisites, streams, requirements satisfied
- **Planner** — semester organization, selected courses, warnings
- **Graph Explorer** — prerequisite graph, course pathways, stream relationships (candidate libraries: React Flow, D3.js, Cytoscape)

---

## API Design

### Courses

```
GET /api/courses
```
Returns all courses.

```
GET /api/courses/{course_id}
```
Returns course details, prerequisites, streams, and satisfiable requirements.

### Requirements

```
GET /api/requirements/progress
```
Returns stream progress, area completion, Arts/Science completion, and 400+ completion.

### Planner

```
POST /api/planner/course
```
Adds a course to the plan.

```
DELETE /api/planner/course/{id}
```
Removes a course from the plan.

---

## Development Principles

1. **Model the academic domain first.** Don't build UI before the database accurately represents courses, requirements, and relationships.
2. **Keep business logic separate.** Requirement evaluation lives in `services/`, not `routers/`.
3. **Avoid hard-coded degree logic in the frontend.** The frontend displays results; the backend determines completion, missing requirements, and allocations.
4. **Build incrementally**, in this order:
   1. Database model
   2. Seed academic data
   3. Backend APIs
   4. Requirement engine
   5. Frontend dashboard
   6. Visualization
   7. AI features

---

## Current Status

- ✓ Docker Compose setup
- ✓ React frontend
- ✓ FastAPI backend
- ✓ PostgreSQL database
- ✓ SQLAlchemy ORM
- ✓ Course CRUD
- ✓ Frontend-backend communication
- ✓ Basic course seeding

**Next milestone:** Implement the academic data model — streams, prerequisites, Cogsci areas, and requirements.
