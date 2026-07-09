# McGill Cognitive Science Degree Planner — Project Summary

## Overview

A degree-aware academic planning application for McGill Cognitive Science students.

The application models the program as courses linked to areas, streams, prerequisites, and degree requirements. It helps students track progress and understand how their course selections allocate across competing buckets.

The goal is not simply to list courses, but to answer:

- Does my course selection satisfy degree requirements?
- Which bucket does each course count toward?
- How do I progress toward each stream?
- What happens when I take two courses from the same core area?
- How do Arts/Science and 400-level credits add up?

---

## Product Vision

McGill Cognitive Science is flexible but difficult to plan because requirements overlap. Students must reason about:

- 8 required Cognitive Science areas (Core Complementary)
- 5 streams (Computer Science, Neuroscience, Psychology, Linguistics, Philosophy)
- Stream credits (18) and complementary credits (12) from stream-eligible courses
- 400-level credits (15)
- Arts and Science balance (21 each)
- Electives (overflow from areas and official stream pool)
- Honours research (optional, 6 credits)

Existing university tools show requirements but rarely explain **allocation** — which bucket each course actually fills when credits cannot double-count.

---

## Target User

McGill Cognitive Science undergraduate students.

**Initial scope:**
- McGill Cognitive Science Major / Honours
- McGill course catalog (seeded subset; full lists in `cogsci_course_catalogue.md`)

---

## Core Design Philosophy

Courses are **resources** that may satisfy different requirements. The system allocates each course to at most one program bucket per allocation pass, then reports independent totals (400-level, Arts/Science).

### Three-way classification (from official catalogue)

| Classification | Meaning |
|---|---|
| **Area-eligible** | Can fill one of the 8 Core Complementary slots |
| **Stream-eligible** | Appears on a stream's Complementary Courses list |
| **Electives-only** | Area-eligible but **not** on any stream list |

Stream tags are **not** inferred from area membership. Many core courses (e.g. `COMP 202`, `PSYC 211`) satisfy an area only.

### Area overflow

Only **one** course per area counts toward the 24-credit area requirement. If a student takes a second course from the same area, that credit overflows to the **Electives** bucket instead of silently disappearing or auto-filling a stream.

**Example:** `COMP 202` + `COMP 250` — both are Computer Science Foundations options. `COMP 250` is also on the CS stream list. One fills the area; the other can count toward the CS stream. If only area-eligible courses are taken, extras go to Electives.

### Mutual exclusivity vs independence

- **Mutually exclusive:** Official stream credits vs complementary credits; each course goes to one program bucket.
- **Independent:** 400-level and Arts/Science totals — the same course can contribute to a program bucket and to these global tallies.

---

## Cognitive Science Degree Model

Reference: `cogsci_course_catalogue.md` (McGill 2026–2027 Honours, 60 credits). Standard 54-credit major follows the same structural ideas with slightly different credit splits.

### Program size

| Program | Credits |
|---|---|
| Standard Major | 54 |
| Honours | 60 |

### 1. Required Cognitive Science Areas — 24 credits (planner view)

Eight areas, one course each (3 credits × 8):

| Area | Example options |
|---|---|
| Neuroscience (Required) | `NSCI 201` |
| Logic | `COMP 230`, `MATH 318`, `PHIL 210` |
| Statistics | `MATH 203`, `MATH 323`, `PSYC 204` |
| Computer Science Foundations | `COMP 202`, `COMP 204`, `COMP 250` |
| Linguistics Foundations | `LING 201`, `LING 210`, `LING 260` |
| Philosophy Foundations | `PHIL 200`, `PHIL 201`, `PHIL 203`, `PHIL 221` |
| Neuroscience Foundations | `NSCI 200`, `PHGY 209`, `PSYC 211` |
| Psychology Foundations | `PSYC 212`, `PSYC 213` |

### 2. Stream requirement — 18 credits

Credits from courses on **one** stream's complementary list. The dashboard shows:

- **Explore bars** — progress toward all 5 streams simultaneously (what-if).
- **Official allocation** — uses a declared stream (or provisional best-fit) for the 18 + 12 split.

Students may optionally declare a stream in the app; McGill does not require formal stream declaration.

### 3. Complementary requirement — 12 credits

Additional credits from stream-eligible courses, tracked separately from the 18-credit stream bucket in the official allocation.

### 4. Advanced courses — 15 credits at 400+

Tracked independently; overlaps with stream/area allocations.

### 5. Arts and Science — 21 credits each

Faculty metadata on each course. Manual entry of non-major courses is supported for faculty totals.

### 6. Electives bucket

Visible credit pool for:

- Area overflow (second+ course from same area)
- Official stream-pool overflow (after stream + complementary caps)
- Explicit electives-only and research courses (`COGS 401`, etc.)

### 7. Honours (optional)

6-credit research requirement (`COGS 444` when honours is enabled). Toggle in dashboard.

---

## Main Features

### 1. Degree Dashboard (implemented)

- Dual **completed** vs **projected** progress
- Area completion
- Stream exploration (all 5) + official stream/complementary
- Electives, 400-level, Arts/Science, honours research
- Per-course status (completed / planned)
- Bucket override controls with validation errors

### 2. Course Explorer (planned)

Search courses with prerequisites, streams, areas, and satisfiable requirements.

### 3. Semester Planner (planned)

Organize courses by term; non-blocking prerequisite warnings.

### 4. Graph Visualization (planned)

Prerequisite and stream pathway graphs.

---

## Data Model (Conceptual)

- **Course** — code, title, credits, level, faculty, department, prerequisites
- **Stream** — 5 Cognitive Science streams
- **Area** — 8 Core Complementary categories
- **Requirement** — degree rules (areas, stream, complementary, 400+, Arts, Science, honours)
- **Relationships** — course↔stream, course↔area, course↔prerequisite (many-to-many where applicable)

Seed source of truth: `backend/app/seed/cogsci_seed_data.py` (82 courses, expandable from catalogue).

---

## Technical Architecture (Summary)

| Layer | Technology | Responsibilities |
|---|---|---|
| Frontend | React + TypeScript + Vite | Dashboard, course status, overrides |
| Backend | FastAPI | Course API, `degree_evaluator`, progress API |
| Database | PostgreSQL + SQLAlchemy | Academic data storage |

See `PROJECT_ARCHITECTURE.md` for file layout, allocation phases, and API contracts.

---

## Current Progress

- ✓ Docker development environment
- ✓ Academic data model (courses, streams, areas, requirements, prerequisites)
- ✓ Catalogue-aligned seed data with three-way course classification
- ✓ Degree evaluation engine (greedy v1)
- ✓ `POST /api/requirements/progress` with overrides, declared stream, honours
- ✓ Dashboard UI
- ✓ 38 backend unit/integration tests

---

## Development Roadmap

### Phase 1: Academic Data Model — largely complete
Expand seeded course lists from `cogsci_course_catalogue.md` as needed.

### Phase 2: Requirement Evaluation — largely complete
Refinements possible (smarter optimization, standard vs honours program profiles).

### Phase 3: Semester Planner
Term organization, prerequisite warnings, impact preview.

### Phase 4: Graph Visualization
Prerequisite and stream graphs.

### Phase 5: Authentication
User accounts, saved plans.

### Phase 6: AI Features
Recommendations, natural-language planning assistance.

---

## Long-Term Goal

An intelligent planning system combining relational data, graph relationships, constraint-aware allocation, and visualization so students can navigate McGill Cognitive Science without manually reconciling overlapping requirements.
