# McGill Cognitive Science Degree Planner — Project Summary

## Overview

A degree-aware academic planning application designed specifically for McGill Cognitive Science students.

The application models the Cognitive Science program as a graph of courses, prerequisites, streams, and degree requirements. It helps students build course plans while automatically evaluating whether their selections satisfy degree constraints.

The goal is not simply to store a list of courses, but to answer:

- Does my course selection satisfy my degree requirements?
- Which requirements can this course satisfy?
- How should my courses be allocated to maximize degree completion?
- What courses should I take next?
- Which streams am I progressing toward?
- What pathways exist based on my interests?

---

## Product Vision

McGill Cognitive Science is flexible but difficult to plan because requirements overlap. Students must reason about:

- 8 required Cognitive Science areas
- 5 possible streams
- Stream credit requirements
- Complementary credits
- 400-level course requirements
- Arts and Science credit balance
- Electives
- Honours requirements
- Course prerequisites

Existing university tools usually show requirements but don't explain relationships between courses or optimize course allocation. This application provides a visual, intelligent planning assistant.

---

## Target User

McGill Cognitive Science undergraduate students.

**Initial scope:**
- McGill Cognitive Science Major only
- McGill course catalog only

**Future possibility:**
- Expand to other McGill programs
- Expand to other universities

---

## Core Design Philosophy

Courses are not simply labeled as "required," "stream," or "elective." Instead, **a course is a resource that can potentially satisfy different requirements**, and the system should optimize how courses are allocated across them.

### Example: COMP551

| Attribute | Value |
|---|---|
| Credits | 3 |
| Level | 500 |
| Faculty | Science |

**Possible contributions:**
- ✓ Computer Science Stream
- ✓ 400+ level requirement
- ✓ Science credit requirement

### Allocation Rules

- A course **cannot** be double-counted for mutually exclusive requirements. For example, a 3-credit course cannot simultaneously count as both Stream credits and Complementary credits.
- **Exception:** a course *can* satisfy both a program area requirement and the 400+ requirement, since the 400+ requirement is an additional, independent constraint rather than a competing bucket.

---

## Cognitive Science Degree Model

### Total Credits

| Program | Credits |
|---|---|
| Standard Cognitive Science Major | 54 |
| Honours Cognitive Science | 60 |

### 1. Required Cognitive Science Areas — 24 credits

Students must complete 8 required areas. Each area has 1–3 possible course options.

**Example:**
- Area: Artificial Intelligence
- Possible courses: `COMP551`, `COMP550`

The system tracks area completion (e.g., "Artificial Intelligence ✓ Completed").

### 2. Stream Requirement — 18 credits

Students complete coursework from one or more Cognitive Science streams:

- Computer Science
- Neuroscience
- Psychology
- Linguistics
- Philosophy

Students do **not** officially declare a stream — it's determined by the courses they complete. The app should show progress toward *every* stream simultaneously, and a student may satisfy multiple streams.

**Example:**

| Stream | Progress |
|---|---|
| Computer Science | 15 / 18 credits |
| Neuroscience | 9 / 18 credits |
| Psychology | 6 / 18 credits |
| Linguistics | 3 / 18 credits |
| Philosophy | 0 / 18 credits |

### 3. Complementary Requirement — 12 credits

Complementary credits come from approved Cognitive Science coursework and must be tracked **separately** from stream credits. A course allocated to complementary cannot also be allocated to a stream.

### 4. Advanced Course Requirement — 15 credits

15 credits at the 400-level or above. This overlaps with other requirements and is tracked independently.

**Example:** COMP551 counts as both ✓ Computer Science Stream and ✓ 400+ level requirement.

### 5. Arts and Science Requirement

| Faculty | Minimum Credits |
|---|---|
| Arts | 21 |
| Science | 21 |

Every course has faculty metadata (Arts / Science). Importantly, Arts and Science credits are **not limited to Cognitive Science courses** — users should be able to manually enter completed non-major courses (e.g., `PHIL210`, `HIST200`).

### 6. Honours Cognitive Science (optional)

Adds a 6-credit research requirement, completed either:
- In one semester (6 credits), or
- Across two semesters (3 + 3 credits)

---

## Main Features

### 1. Degree Dashboard (Main Interface)

The primary user experience — shows overall progress, required area completion, stream progress, advanced course progress, and Arts/Science completion at a glance.

### 2. Course Explorer

Search and explore courses, viewing prerequisites, faculty, level, streams, and which requirements a course can satisfy.

### 3. Semester Planner

Organize courses by semester. The system provides **non-blocking** warnings — e.g., flagging an unmet prerequisite — while still showing requirement impact. Students may take courses without prerequisites; warnings never block course selection.

### 4. Requirement Allocation Engine

The core technical challenge: given a student's completed and planned courses, produce an **optimized allocation** of courses toward degree requirements, maximizing:

- Completed requirements
- Stream progress
- Overall degree completion percentage

Potential approaches: constraint satisfaction, optimization algorithms, graph algorithms.

---

## Data Model (Conceptual)

- **Course** — id, code, title, description, credits, level, faculty, department
- **Stream** — id, name (Computer Science, Neuroscience, Psychology, Linguistics, Philosophy)
- **Course–Stream Relationship** — many-to-many (course_id, stream_id)
- **Course Prerequisite Relationship** — self-referencing (course_id, required_course_id); warnings only, not restrictions
- **Cognitive Science Area** — id, name (e.g., Artificial Intelligence, Language, Cognition, Perception)
- **Area Courses** — (area_id, course_id) — defines which courses satisfy which required areas
- **Requirement** — id, name, type, credits_required
- **UserCourse** — user_id, course_id, status (completed / planned)

---

## Technical Architecture (Summary)

| Layer | Technology | Responsibilities |
|---|---|---|
| Frontend | React + TypeScript + Vite | Dashboard, course explorer, semester planner, graph visualization |
| Backend | FastAPI | Course APIs, degree evaluation, allocation engine, optimization logic |
| Database | PostgreSQL + SQLAlchemy ORM | Academic data storage |

*(See `PROJECT_ARCHITECTURE.md` for full technical details.)*

---

## Current Progress

- ✓ Docker development environment
- ✓ React frontend
- ✓ FastAPI backend
- ✓ PostgreSQL database
- ✓ SQLAlchemy models
- ✓ Course CRUD
- ✓ Frontend-backend communication
- ✓ Database seeding

---

## Development Roadmap

### Phase 1: Academic Data Model
Course metadata, streams, course-stream relationships, prerequisites, Cognitive Science areas, degree requirements. Seed McGill Cognitive Science courses and requirement rules.

### Phase 2: Requirement Evaluation Engine
Credit counting, stream progress calculation, Arts/Science tracking, 400-level tracking, Honours tracking, course allocation optimization.

### Phase 3: Semester Planner
Add/remove courses, semester organization, requirement impact preview, prerequisite warnings.

### Phase 4: Graph Visualization
Prerequisite graph, stream graph, degree pathway visualization. Possible tech: React Flow, D3.js, Cytoscape.

### Phase 5: Authentication
OAuth login, user accounts, saved degree plans.

### Phase 6: AI Features
Course recommendations, degree planning assistant, natural language queries.

> Example: *"I want an AI/ML pathway while keeping neuroscience options open. What courses should I take?"*

---

## Long-Term Goal

Create an intelligent academic planning system combining relational databases, graph modeling, constraint optimization, visualization, and AI reasoning to help students navigate complex degree structures.
