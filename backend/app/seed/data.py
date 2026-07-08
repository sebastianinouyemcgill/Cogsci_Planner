"""
McGill Cognitive Science — Seed Data
=====================================

Source: McGill 2024-2025 eCalendar, Interfaculty Program Cognitive Science
(B.A. & Sc.) (54 credits).
https://www.mcgill.ca/study/2024-2025/faculties/basc/undergraduate/programs/
bachelor-arts-and-science-ba-sc-interfaculty-program-cognitive-science

IMPORTANT — read before wiring this into the DB
-------------------------------------------------
The REAL McGill program structure is:

  1. Required Course (3 credits)      -> NSCI 201
  2. Core Complementary (21 credits)  -> 3 credits from EACH of 7 categories:
                                          Logic, Statistics, Computer Science,
                                          Linguistics, Philosophy, Neuroscience,
                                          Psychology
  3. Complementary (30 credits)       -> 18 credits from ONE of the 5 streams
                                          (CS / Linguistics / Neuroscience /
                                          Philosophy / Psychology), plus 12
                                          credits from ANY of the 5 streams.
                                          15 of these 30 credits must be at
                                          the 400-level or higher.

  Total: 3 + 21 + 30 = 54 credits. ✓ matches PROJECT_SUMMARY.md

This maps VERY cleanly onto the "8 required Cognitive Science areas, 24
credits" concept from PROJECT_SUMMARY.md:

  Area 1: Neuroscience (Required)   -> NSCI 201 only               (3 cr)
  Area 2: Logic                     -> COMP230 / MATH318 / PHIL210  (3 cr)
  Area 3: Statistics                -> MATH203 / MATH323 / PSYC204  (3 cr)
  Area 4: Computer Science          -> COMP202 / COMP204 / COMP250  (3 cr)
  Area 5: Linguistics               -> LING201 / LING210 / LING260  (3 cr)
  Area 6: Philosophy                -> PHIL200 / PHIL201 / PHIL221  (3 cr)
  Area 7: Neuroscience (Intro)      -> NSCI200 / PSYC211            (3 cr)
  Area 8: Psychology                -> PSYC212 / PSYC213            (3 cr)
                                                          TOTAL = 24 credits

This is NOT an invented mapping — it falls directly out of the official
program's "Required Course" + "Core Complementary" sections (7 categories
of 3 credits + 1 required 3-credit course = 24 credits). Confirm this
mapping makes sense to you before seeding the `areas` table, since it's an
interpretation of the calendar structure rather than an official McGill
term ("Area" is the planner's vocabulary, not McGill's).

The 5 STREAMS below and their course lists come directly from the
"Complementary Courses" section of the calendar (Computer Science,
Linguistics, Philosophy, Psychology, Neuroscience subsections). Only a
representative subset of each list is included here (not the full
official list) — enough to seed and test Phase 1/2 meaningfully. Expand
freely from the calendar link above.

Faculty mapping: Science = COMP, MATH, NSCI, PSYC, BIOL, ANAT courses.
                  Arts    = LING, PHIL courses.
"""

# ---------------------------------------------------------------------------
# STREAMS
# ---------------------------------------------------------------------------

STREAMS = [
    {"name": "Computer Science"},
    {"name": "Neuroscience"},
    {"name": "Psychology"},
    {"name": "Linguistics"},
    {"name": "Philosophy"},
]

# ---------------------------------------------------------------------------
# COGNITIVE SCIENCE AREAS (see mapping note above)
# ---------------------------------------------------------------------------

AREAS = [
    {"name": "Neuroscience (Required)"},
    {"name": "Logic"},
    {"name": "Statistics"},
    {"name": "Computer Science Foundations"},
    {"name": "Linguistics Foundations"},
    {"name": "Philosophy Foundations"},
    {"name": "Neuroscience Foundations"},
    {"name": "Psychology Foundations"},
]

# ---------------------------------------------------------------------------
# COURSES
# faculty: "Arts" | "Science"
# level: numeric course level (200, 300, 400, 500)
# ---------------------------------------------------------------------------

COURSES = [
    # --- Required course -----------------------------------------------
    {
        "code": "NSCI 201", "title": "Introduction to Neuroscience 2",
        "credits": 3, "level": 200, "faculty": "Science",
        "department": "Psychology",
        "description": "An introduction to how the nervous system acquires "
                        "and integrates information and uses it to produce "
                        "behaviour.",
    },

    # --- Logic category ---------------------------------------------------
    {
        "code": "COMP 230", "title": "Logic and Computability",
        "credits": 3, "level": 230, "faculty": "Science",
        "department": "Computer Science",
        "description": "Propositional logic, predicate calculus, proof "
                        "systems, computability, Turing machines, "
                        "Church-Turing thesis, unsolvable problems.",
    },
    {
        "code": "MATH 318", "title": "Mathematical Logic",
        "credits": 3, "level": 318, "faculty": "Science",
        "department": "Mathematics and Statistics",
        "description": "Propositional logic, first-order logic, Gödel's "
                        "completeness theorem, axiomatic theories, set "
                        "theory, Gödel's incompleteness theorem.",
    },
    {
        "code": "PHIL 210", "title": "Introduction to Deductive Logic 1",
        "credits": 3, "level": 210, "faculty": "Arts",
        "department": "Philosophy",
        "description": "An introduction to propositional and predicate "
                        "logic; formalization of arguments, truth tables, "
                        "systems of deduction.",
    },

    # --- Statistics category ----------------------------------------------
    {
        "code": "MATH 203", "title": "Principles of Statistics 1",
        "credits": 3, "level": 203, "faculty": "Science",
        "department": "Mathematics and Statistics",
        "description": "Examples of statistical data and graphical "
                        "summaries. Basic distributions, tests of "
                        "significance, confidence intervals.",
    },
    {
        "code": "MATH 323", "title": "Probability",
        "credits": 3, "level": 323, "faculty": "Science",
        "department": "Mathematics and Statistics",
        "description": "Sample space, conditional probability, Bayes' "
                        "Theorem, random variables, distributions, central "
                        "limit theorem.",
    },
    {
        "code": "PSYC 204", "title": "Introduction to Psychological Statistics",
        "credits": 3, "level": 204, "faculty": "Science",
        "department": "Psychology",
        "description": "The statistical analysis of research data; "
                        "frequency distributions; measures of central "
                        "tendency and variability.",
    },

    # --- Computer Science category -----------------------------------------
    {
        "code": "COMP 202", "title": "Foundations of Programming",
        "credits": 3, "level": 202, "faculty": "Science",
        "department": "Computer Science",
        "description": "Introduction to computer programming: variables, "
                        "expressions, conditionals, loops, algorithms, "
                        "basic data structures.",
    },
    {
        "code": "COMP 250", "title": "Introduction to Computer Science",
        "credits": 3, "level": 250, "faculty": "Science",
        "department": "Computer Science",
        "description": "Mathematical tools, data structures, recursive and "
                        "non-recursive algorithms, object-oriented "
                        "programming in Java.",
    },

    # --- Linguistics category ----------------------------------------------
    {
        "code": "LING 201", "title": "Introduction to Linguistics",
        "credits": 3, "level": 201, "faculty": "Arts",
        "department": "Linguistics",
        "description": "General introduction to linguistics: phonetics, "
                        "phonology, morphology, syntax, and semantics.",
    },
    {
        "code": "LING 210", "title": "Introduction to Speech Science",
        "credits": 3, "level": 210, "faculty": "Arts",
        "department": "Linguistics",
        "description": "Key concepts of speech science: phonetics, "
                        "speech perception and production, speech "
                        "development and disorders.",
    },
    {
        "code": "LING 260", "title": "Meaning in Language",
        "credits": 3, "level": 260, "faculty": "Arts",
        "department": "Linguistics",
        "description": "Fundamental properties of word and sentence "
                        "meaning and their interdependence with context.",
    },

    # --- Philosophy category ------------------------------------------------
    {
        "code": "PHIL 200", "title": "Introduction to Philosophy 1",
        "credits": 3, "level": 200, "faculty": "Arts",
        "department": "Philosophy",
        "description": "The mind-body problem, freedom, scepticism and "
                        "certainty, fate, time, and the existence of God.",
    },
    {
        "code": "PHIL 221", "title": "Introduction to History and Philosophy "
                                     "of Science 2",
        "credits": 3, "level": 221, "faculty": "Arts",
        "department": "Philosophy",
        "description": "A survey of the development of modern science "
                        "since the eighteenth century.",
    },

    # --- Neuroscience (intro) category --------------------------------------
    {
        "code": "NSCI 200", "title": "Introduction to Neuroscience 1",
        "credits": 3, "level": 200, "faculty": "Science",
        "department": "Physiology",
        "description": "How nerve cells generate action potentials, "
                        "communicate at synapses, and develop synaptic "
                        "connections.",
    },
    {
        "code": "PSYC 211", "title": "Introductory Behavioural Neuroscience",
        "credits": 3, "level": 211, "faculty": "Science",
        "department": "Psychology",
        "description": "The relationship between brain and behaviour: "
                        "learning, memory, brain damage and neuroplasticity, "
                        "emotion and motivation.",
    },

    # --- Psychology category -------------------------------------------------
    {
        "code": "PSYC 212", "title": "Perception",
        "credits": 3, "level": 212, "faculty": "Science",
        "department": "Psychology",
        "description": "The organization of sensory input into a "
                        "representation of the environment: sensory coding, "
                        "object recognition, spatial localization.",
    },
    {
        "code": "PSYC 213", "title": "Cognition",
        "credits": 3, "level": 213, "faculty": "Science",
        "department": "Psychology",
        "description": "The study of human information processing: memory, "
                        "attention, categorization, decision making, "
                        "intelligence, philosophy of mind.",
    },

    # --- Computer Science stream (representative subset, incl. 400/500) -----
    {
        "code": "COMP 206", "title": "Introduction to Software Systems",
        "credits": 3, "level": 206, "faculty": "Science",
        "department": "Computer Science",
        "description": "Overview of programming in C, system calls and "
                        "libraries, debugging and testing, developmental "
                        "tools.",
    },
    {
        "code": "COMP 251", "title": "Algorithms and Data Structures",
        "credits": 3, "level": 251, "faculty": "Science",
        "department": "Computer Science",
        "description": "Algorithm design and analysis. Graph algorithms, "
                        "greedy algorithms, data structures, dynamic "
                        "programming, maximum flows.",
    },
    {
        "code": "COMP 302", "title": "Programming Languages and Paradigms",
        "credits": 3, "level": 302, "faculty": "Science",
        "department": "Computer Science",
        "description": "Programming language design issues and paradigms: "
                        "binding, scoping, lambda abstraction, functional "
                        "and logic programming.",
    },
    {
        "code": "COMP 330", "title": "Theory of Computation",
        "credits": 3, "level": 330, "faculty": "Science",
        "department": "Computer Science",
        "description": "Finite automata, regular languages, context-free "
                        "languages, computability theory, undecidability.",
    },
    {
        "code": "COMP 421", "title": "Database Systems",
        "credits": 3, "level": 421, "faculty": "Science",
        "department": "Computer Science",
        "description": "Database design, relational data model, SQL, "
                        "transactions, concurrency control, query "
                        "optimization.",
    },
    {
        "code": "COMP 424", "title": "Artificial Intelligence",
        "credits": 3, "level": 424, "faculty": "Science",
        "department": "Computer Science",
        "description": "Search methods, knowledge representation using "
                        "logic and probability, planning and decision "
                        "making under uncertainty, intro to machine "
                        "learning.",
    },
    {
        "code": "COMP 445", "title": "Computational Linguistics",
        "credits": 3, "level": 445, "faculty": "Science",
        "department": "Computer Science",
        "description": "Foundational ideas in computational linguistics "
                        "and NLP: formal language theory, probability "
                        "theory, models of language structure.",
    },
    {
        "code": "COMP 451", "title": "Fundamentals of Machine Learning",
        "credits": 3, "level": 451, "faculty": "Science",
        "department": "Computer Science",
        "description": "Computational, statistical, and mathematical "
                        "foundations of machine learning: supervised and "
                        "unsupervised learning, neural networks.",
    },
    {
        "code": "COMP 550", "title": "Natural Language Processing",
        "credits": 3, "level": 550, "faculty": "Science",
        "department": "Computer Science",
        "description": "Computational modelling of natural language: "
                        "morphology, language modelling, parsing, "
                        "semantics, discourse analysis, machine learning "
                        "for NLP.",
    },
    {
        "code": "COMP 551", "title": "Applied Machine Learning",
        "credits": 4, "level": 551, "faculty": "Science",
        "department": "Computer Science",
        "description": "Selected topics in machine learning and data "
                        "mining: clustering, neural networks, support "
                        "vector machines, decision trees.",
    },
    {
        "code": "COMP 558", "title": "Fundamentals of Computer Vision",
        "credits": 4, "level": 558, "faculty": "Science",
        "department": "Computer Science",
        "description": "Image filtering, edge detection, segmentation, "
                        "image motion and tracking, projective geometry, "
                        "stereo, 3D registration.",
    },
    {
        "code": "COMP 549", "title": "Brain-Inspired Artificial Intelligence",
        "credits": 3, "level": 549, "faculty": "Science",
        "department": "Computer Science",
        "description": "The influence of neuroscience and psychology on "
                        "AI: perceptrons, PDP framework, deep learning, "
                        "attention, memory and consciousness.",
    },

    # --- Linguistics stream (300/400/500-level) -----------------------------
    {
        "code": "LING 445", "title": "Computational Linguistics",
        "credits": 3, "level": 445, "faculty": "Arts",
        "department": "Linguistics",
        "description": "Identical in content to COMP 445 (double-prefix "
                        "course): formal language theory, probability "
                        "theory, models of language structure.",
    },

    # --- Philosophy stream (300/400-level) ----------------------------------
    {
        "code": "PHIL 306", "title": "Philosophy of Mind",
        "credits": 3, "level": 306, "faculty": "Arts",
        "department": "Philosophy",
        "description": "A survey of major positions on the mind-body "
                        "problem: minds and bodies, mind-body identity, "
                        "consciousness.",
    },
    {
        "code": "PHIL 310", "title": "Intermediate Logic",
        "credits": 3, "level": 310, "faculty": "Arts",
        "department": "Philosophy",
        "description": "A second course in logic: completeness of "
                        "first-order logic, Tarski's and Gödel's limitative "
                        "theorems.",
    },
    {
        "code": "PHIL 415", "title": "Philosophy of Language",
        "credits": 3, "level": 415, "faculty": "Arts",
        "department": "Philosophy",
        "description": "Central notions in the philosophy of language: "
                        "reference, meaning, truth, communication, "
                        "understanding.",
    },
    {
        "code": "PHIL 419", "title": "Epistemology",
        "credits": 3, "level": 419, "faculty": "Arts",
        "department": "Philosophy",
        "description": "Central topics in the theory of knowledge: what "
                        "is knowledge, justified belief, conscious "
                        "knowledge.",
    },

    # --- Neuroscience stream (300/400/500-level) ----------------------------
    {
        "code": "BIOL 306", "title": "Neural Basis of Behaviour",
        "credits": 3, "level": 306, "faculty": "Science",
        "department": "Biology",
        "description": "Neural mechanisms of animal behaviour, "
                        "neuroethology, cellular neurophysiology, neural "
                        "control of movement.",
    },
    {
        "code": "BIOL 320", "title": "Evolution of Brain and Behaviour",
        "credits": 3, "level": 320, "faculty": "Science",
        "department": "Biology",
        "description": "Functional and comparative approach to "
                        "neuroanatomy: how species changes in brain "
                        "organization contribute to evolutionary behaviour "
                        "changes.",
    },
    {
        "code": "ANAT 321", "title": "Circuitry of the Human Brain",
        "credits": 3, "level": 321, "faculty": "Science",
        "department": "Anatomy and Cell Biology",
        "description": "The functional organization of the human brain "
                        "and spinal cord; neuronal systems for motor, "
                        "sensory, and cognitive operations.",
    },
    {
        "code": "NSCI 300", "title": "Neuroethics",
        "credits": 3, "level": 300, "faculty": "Science",
        "department": "Physiology",
        "description": "Ethical issues arising from basic and clinical "
                        "neuroscience; therapeutic, diagnostic, and "
                        "research interventions.",
    },

    # --- Psychology stream (300/400/500-level) ------------------------------
    {
        "code": "PSYC 304", "title": "Child Development",
        "credits": 3, "level": 304, "faculty": "Science",
        "department": "Psychology",
        "description": "Critical issues, theories, and findings in "
                        "perceptual, cognitive, language, emotional, and "
                        "social development.",
    },
    {
        "code": "PSYC 305", "title": "Statistics for Experimental Design",
        "credits": 3, "level": 305, "faculty": "Science",
        "department": "Psychology",
        "description": "The design and analysis of experiments, including "
                        "analysis of variance, planned and post hoc tests.",
    },
    {
        "code": "PSYC 311", "title": "Human Cognition and the Brain",
        "credits": 3, "level": 311, "faculty": "Science",
        "department": "Psychology",
        "description": "How human cognitive processes (perception, "
                        "attention, language, memory) relate to brain "
                        "processes.",
    },
    {
        "code": "PSYC 315", "title": "Computational Psychology",
        "credits": 3, "level": 315, "faculty": "Science",
        "department": "Psychology",
        "description": "Application of computational methods to "
                        "simulating psychological phenomena; symbolic and "
                        "neural network techniques.",
    },
    {
        "code": "PSYC 340", "title": "Psychology of Language",
        "credits": 3, "level": 340, "faculty": "Science",
        "department": "Psychology",
        "description": "Psycholinguistics: how we understand speech "
                        "sounds, words, sentences, discourse; language and "
                        "thought; language acquisition.",
    },
    {
        "code": "PSYC 413", "title": "Cognitive Development",
        "credits": 3, "level": 413, "faculty": "Science",
        "department": "Psychology",
        "description": "Cognitive development in infants and children: "
                        "knowledge representation, conceptual and language "
                        "development.",
    },
    {
        "code": "PSYC 433", "title": "Cognitive Science",
        "credits": 3, "level": 433, "faculty": "Science",
        "department": "Psychology",
        "description": "The multidisciplinary study of cognitive science: "
                        "the computer metaphor of mind, symbolic modeling, "
                        "Turing machines, neural networks.",
    },
    {
        "code": "PSYC 506", "title": "Cognitive Neuroscience of Attention",
        "credits": 3, "level": 506, "faculty": "Science",
        "department": "Psychology",
        "description": "Cognitive properties and neural mechanisms of "
                        "human attention: theories, methods, links to "
                        "memory and consciousness.",
    },
    {
        "code": "PSYC 513", "title": "Human Decision-Making",
        "credits": 3, "level": 513, "faculty": "Science",
        "department": "Psychology",
        "description": "How humans compute values and make choices: risk "
                        "and uncertainty, reinforcement learning, "
                        "heuristics and biases.",
    },
]

# ---------------------------------------------------------------------------
# COURSE -> STREAM relationships (many-to-many)
# Only includes the "Complementary" stream-eligible courses, matching the
# calendar's Computer Science / Linguistics / Philosophy / Neuroscience /
# Psychology subsections. Area/required/core-complementary courses are NOT
# stream courses.
# ---------------------------------------------------------------------------

COURSE_STREAMS = [
    # Computer Science stream
    ("COMP 206", "Computer Science"),
    ("COMP 251", "Computer Science"),
    ("COMP 302", "Computer Science"),
    ("COMP 330", "Computer Science"),
    ("COMP 421", "Computer Science"),
    ("COMP 424", "Computer Science"),
    ("COMP 445", "Computer Science"),
    ("COMP 451", "Computer Science"),
    ("COMP 550", "Computer Science"),
    ("COMP 551", "Computer Science"),
    ("COMP 558", "Computer Science"),
    ("COMP 549", "Computer Science"),

    # Linguistics stream ("any 300/400/500-level LING course, or the list")
    ("LING 445", "Linguistics"),

    # Philosophy stream
    ("PHIL 306", "Philosophy"),
    ("PHIL 310", "Philosophy"),
    ("PHIL 415", "Philosophy"),
    ("PHIL 419", "Philosophy"),

    # Neuroscience stream
    ("BIOL 306", "Neuroscience"),
    ("BIOL 320", "Neuroscience"),
    ("ANAT 321", "Neuroscience"),
    ("NSCI 300", "Neuroscience"),

    # Psychology stream
    ("PSYC 304", "Psychology"),
    ("PSYC 305", "Psychology"),
    ("PSYC 311", "Psychology"),
    ("PSYC 315", "Psychology"),
    ("PSYC 340", "Psychology"),
    ("PSYC 413", "Psychology"),
    ("PSYC 433", "Psychology"),
    ("PSYC 506", "Psychology"),
    ("PSYC 513", "Psychology"),

    # A course can belong to multiple streams — e.g. COMP 445 / LING 445 are
    # a double-prefix course (identical content), so it's reasonable to also
    # tag COMP 445 under Linguistics if your allocation engine should treat
    # them as interchangeable. Left as a single stream here; adjust as needed.
]

# ---------------------------------------------------------------------------
# COURSE -> AREA relationships (many-to-many)
# Maps each course to the Area(s) it satisfies, per the mapping documented
# at the top of this file.
# ---------------------------------------------------------------------------

AREA_COURSES = [
    ("Neuroscience (Required)", "NSCI 201"),

    ("Logic", "COMP 230"),
    ("Logic", "MATH 318"),
    ("Logic", "PHIL 210"),

    ("Statistics", "MATH 203"),
    ("Statistics", "MATH 323"),
    ("Statistics", "PSYC 204"),

    ("Computer Science Foundations", "COMP 202"),
    ("Computer Science Foundations", "COMP 250"),

    ("Linguistics Foundations", "LING 201"),
    ("Linguistics Foundations", "LING 210"),
    ("Linguistics Foundations", "LING 260"),

    ("Philosophy Foundations", "PHIL 200"),
    ("Philosophy Foundations", "PHIL 221"),

    ("Neuroscience Foundations", "NSCI 200"),
    ("Neuroscience Foundations", "PSYC 211"),

    ("Psychology Foundations", "PSYC 212"),
    ("Psychology Foundations", "PSYC 213"),
]

# ---------------------------------------------------------------------------
# PREREQUISITES (self-referencing course -> course)
# Only a representative, VERIFIED subset from the calendar is included.
# Format: (course_code, prerequisite_course_code)
# Where a prerequisite is a boolean OR of options in the calendar, each
# valid option is listed as a separate row (the allocation/warning engine
# should treat multiple rows for the same course as OR, not AND — confirm
# this convention with your CoursePrerequisite model design).
# ---------------------------------------------------------------------------

PREREQUISITES = [
    # COMP 250 requires MATH 140 (not seeded) and one of COMP 202/204/208
    ("COMP 250", "COMP 202"),

    # COMP 251 requires COMP 250 and (MATH 235 or MATH 240 — not seeded)
    ("COMP 251", "COMP 250"),

    # COMP 302 requires COMP 250 and one of MATH240/235/318/COMP230/PHIL210
    ("COMP 302", "COMP 250"),
    ("COMP 302", "MATH 318"),

    # COMP 330 requires COMP 251
    ("COMP 330", "COMP 251"),

    # COMP 421 requires COMP 206, COMP 251, COMP 302
    ("COMP 421", "COMP 206"),
    ("COMP 421", "COMP 251"),
    ("COMP 421", "COMP 302"),

    # COMP 424 requires (COMP 206) + MATH 323 + COMP 251
    ("COMP 424", "COMP 206"),
    ("COMP 424", "MATH 323"),
    ("COMP 424", "COMP 251"),

    # COMP 445 / LING 445 require COMP 250 and MATH 240 (not seeded)
    ("COMP 445", "COMP 250"),

    # COMP 451 requires COMP 251 + MATH 222/223/323 (only 323 seeded)
    ("COMP 451", "COMP 251"),
    ("COMP 451", "MATH 323"),

    # COMP 550 requires MATH 323 and COMP 251
    ("COMP 550", "MATH 323"),
    ("COMP 550", "COMP 251"),

    # COMP 551 requires MATH 323, COMP 202
    ("COMP 551", "MATH 323"),
    ("COMP 551", "COMP 202"),

    # COMP 558 requires COMP 251
    ("COMP 558", "COMP 251"),

    # COMP 549 requires MATH 323
    ("COMP 549", "MATH 323"),

    # PHIL 310 requires PHIL 210
    ("PHIL 310", "PHIL 210"),

    # PHIL 415 requires PHIL 210
    ("PHIL 415", "PHIL 210"),

    # PHIL 419 requires PHIL 210
    ("PHIL 419", "PHIL 210"),

    # PSYC 305 requires PSYC 204
    ("PSYC 305", "PSYC 204"),

    # PSYC 311 has no hard prerequisite listed beyond intro psych (omitted)

    # PSYC 340 requires PSYC 212 or PSYC 213
    ("PSYC 340", "PSYC 212"),
    ("PSYC 340", "PSYC 213"),

    # PSYC 413 requires PSYC 304 or PSYC 213
    ("PSYC 413", "PSYC 304"),
    ("PSYC 413", "PSYC 213"),

    # PSYC 433 requires PSYC 212 or PSYC 213
    ("PSYC 433", "PSYC 212"),
    ("PSYC 433", "PSYC 213"),

    # PSYC 506 requires PSYC 213 and PSYC 311, and (PSYC 305 or BIOL 373)
    ("PSYC 506", "PSYC 213"),
    ("PSYC 506", "PSYC 311"),
    ("PSYC 506", "PSYC 305"),

    # PSYC 513 requires PSYC 212 or PSYC 213
    ("PSYC 513", "PSYC 212"),
    ("PSYC 513", "PSYC 213"),

    # BIOL 320 requires NSCI 201 or BIOL 306
    ("BIOL 320", "NSCI 201"),
    ("BIOL 320", "BIOL 306"),

    # NSCI 201 requires NSCI 200 or PSYC 211
    ("NSCI 201", "NSCI 200"),
    ("NSCI 201", "PSYC 211"),
]

# ---------------------------------------------------------------------------
# REQUIREMENTS (degree-level rules, per PROJECT_ARCHITECTURE.md)
# ---------------------------------------------------------------------------

REQUIREMENTS = [
    {"name": "Required Areas", "type": "area_completion", "credits_required": 24},
    {"name": "Stream Requirement", "type": "stream", "credits_required": 18},
    {"name": "Complementary Requirement", "type": "complementary", "credits_required": 12},
    {"name": "400-Level Requirement", "type": "level_threshold", "credits_required": 15},
    {"name": "Arts Requirement", "type": "faculty", "credits_required": 21},
    {"name": "Science Requirement", "type": "faculty", "credits_required": 21},
    {"name": "Honours Research Requirement", "type": "honours", "credits_required": 6},
]
