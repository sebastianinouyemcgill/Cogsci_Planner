"""
McGill Cognitive Science — Seed Data
=====================================

Source: McGill 2026-2027 Honours Cognitive Science (B.A. & Sc.) (60 credits).
Local catalogue: cogsci_course_catalogue.md (repo root).

IMPORTANT — read before wiring this into the DB
-------------------------------------------------
The REAL McGill Honours program structure is:

  1. Required Courses (9 credits)       -> COGS 444 (6 cr) + PSYC 213 (3 cr)
  2. Core Complementary (18 credits)    -> 3 credits from EACH of 6 categories:
                                          Logic, Statistics, Computer Science,
                                          Linguistics, Philosophy, Neuroscience
  3. Complementary (33 credits)         -> 18 credits from ONE of the 5 streams
                                          (CS / Linguistics / Neuroscience /
                                          Philosophy / Psychology), plus 15
                                          credits from ANY of the 5 streams.
                                          15 of these 33 credits must be at
                                          the 400-level or higher.

This maps onto the planner's "8 required Cognitive Science areas, 24 credits"
vocabulary (PROJECT_SUMMARY.md):

  Area 1: Neuroscience (Required)   -> NSCI 201 only               (3 cr)
  Area 2: Logic                     -> COMP 230 / MATH 318 / PHIL 210 (3 cr)
  Area 3: Statistics                -> MATH 203 / MATH 323 / PSYC 204 (3 cr)
  Area 4: Computer Science          -> COMP 202 / COMP 204 / COMP 250 (3 cr)
  Area 5: Linguistics               -> LING 201 / LING 210 / LING 260 (3 cr)
  Area 6: Philosophy                -> PHIL 200 / PHIL 201 / PHIL 203 / PHIL 221 (3 cr)
  Area 7: Neuroscience (Intro)      -> NSCI 200 / PHGY 209 / PSYC 211 (3 cr)
  Area 8: Psychology                -> PSYC 212 / PSYC 213            (3 cr)
                                                          TOTAL = 24 credits

"Area" is the planner's vocabulary, not McGill's official term.

THREE-WAY COURSE ALLOCATION (critical for progress engine)
-----------------------------------------------------------
  1. AREA_COURSES — satisfies one of the 8 Core Complementary area slots.
  2. COURSE_STREAMS — ONLY courses that appear on a stream's Complementary
     Courses list in cogsci_course_catalogue.md. A course can satisfy an Area
     AND count toward a stream only when it is explicitly on that stream's list.
  3. ELECTIVES_ONLY_COURSES — area-eligible courses with NO stream mapping.
     When a student takes a second course from the same Area, the overflow
     credit is tracked in the Electives bucket (not silently dropped).

Example: COMP 202 satisfies "Computer Science Foundations" but is NOT on the
CS stream complementary list, so it has no COURSE_STREAMS entry. A student who
takes both COMP 202 and COMP 250 uses COMP 250 for the Area and the stream;
COMP 202's extra credit overflows to Electives.

Only a representative subset of each official stream list is seeded here —
enough to exercise Phase 1/2 meaningfully. Expand from cogsci_course_catalogue.md.

Faculty mapping: Science = COMP, MATH, NSCI, PSYC, BIOL, ANAT, NEUR, PHGY courses.
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
    # --- Required / area courses -------------------------------------------
    {
        "code": "NSCI 201", "title": "Introduction to Neuroscience 2",
        "credits": 3, "level": 200, "faculty": "Science",
        "department": "Psychology",
        "description": "An introduction to how the nervous system acquires "
                        "and integrates information and uses it to produce "
                        "behaviour.",
    },
    {
        "code": "PSYC 213", "title": "Cognition",
        "credits": 3, "level": 213, "faculty": "Science",
        "department": "Psychology",
        "description": "The study of human information processing: memory, "
                        "attention, categorization, decision making, "
                        "intelligence, philosophy of mind, and the "
                        "mind-as-computer metaphor.",
    },

    # --- Logic category ----------------------------------------------------
    {
        "code": "COMP 230", "title": "Logic and Computability",
        "credits": 3, "level": 230, "faculty": "Science",
        "department": "Computer Science",
        "description": "Propositional logic, predicate calculus, proof "
                        "systems, computability, Turing machines, "
                        "Church-Turing thesis, unsolvable problems, "
                        "completeness, incompleteness, Tarski semantics.",
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
                        "systems of deduction, elementary metaresults.",
    },

    # --- Statistics category -----------------------------------------------
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
        "description": "Introduction to computer programming in a high "
                        "level language: variables, expressions, types, "
                        "methods, conditionals, loops, algorithms, data "
                        "structures, modular software design.",
    },
    {
        "code": "COMP 204", "title": "Computer Programming for Life Sciences",
        "credits": 3, "level": 204, "faculty": "Science",
        "department": "Computer Science",
        "description": "Computer programming in a high level language with "
                        "emphasis on applications in the life sciences: "
                        "variables, functions, conditionals, loops, objects, "
                        "algorithms, and debugging.",
    },
    {
        "code": "COMP 250", "title": "Introduction to Computer Science",
        "credits": 3, "level": 250, "faculty": "Science",
        "department": "Computer Science",
        "description": "Object oriented programming in Java, data structures, "
                        "recursive and non-recursive algorithms and their "
                        "asymptotic complexity, mathematical tools.",
    },

    # --- Linguistics category ----------------------------------------------
    {
        "code": "LING 201", "title": "Introduction to Linguistics",
        "credits": 3, "level": 201, "faculty": "Arts",
        "department": "Linguistics",
        "description": "General introduction to linguistics: phonetics, "
                        "phonology, morphology, syntax, semantics, and "
                        "language acquisition.",
    },
    {
        "code": "LING 210", "title": "Introduction to Speech Science",
        "credits": 3, "level": 210, "faculty": "Arts",
        "department": "Linguistics",
        "description": "Key concepts of speech science: phonetics, speech "
                        "perception and production, speech development and "
                        "disorders.",
    },
    {
        "code": "LING 260", "title": "Meaning in Language",
        "credits": 3, "level": 260, "faculty": "Arts",
        "department": "Linguistics",
        "description": "Fundamental properties of word and sentence meaning "
                        "and their interdependence with context.",
    },

    # --- Philosophy category -----------------------------------------------
    {
        "code": "PHIL 200", "title": "Introduction to Philosophy 1",
        "credits": 3, "level": 200, "faculty": "Arts",
        "department": "Philosophy",
        "description": "Central problems of philosophy: the mind-body problem, "
                        "freedom, scepticism and certainty, fate, time, and "
                        "the existence of God.",
    },
    {
        "code": "PHIL 201", "title": "Introduction to Philosophy 2",
        "credits": 3, "level": 201, "faculty": "Arts",
        "department": "Philosophy",
        "description": "An introduction to some of the major problems of "
                        "philosophy. This course does not duplicate PHIL 200.",
    },
    {
        "code": "PHIL 203", "title": "Introduction to Artificial Intelligence Ethics",
        "credits": 3, "level": 203, "faculty": "Arts",
        "department": "Philosophy",
        "description": "Debates in the ethics of artificial intelligence: "
                        "artificial general intelligence, artificial "
                        "consciousness, existential risk, moral status of "
                        "advanced AI systems, opacity, discrimination, privacy.",
    },
    {
        "code": "PHIL 221", "title": "Introduction to History and Philosophy "
                                     "of Science 2",
        "credits": 3, "level": 221, "faculty": "Arts",
        "department": "Philosophy",
        "description": "A survey of the development of modern science since "
                        "the eighteenth century.",
    },

    # --- Neuroscience (intro) category -------------------------------------
    {
        "code": "NSCI 200", "title": "Introduction to Neuroscience 1",
        "credits": 3, "level": 200, "faculty": "Science",
        "department": "Physiology",
        "description": "How nerve cells generate action potentials, "
                        "communicate at synapses, and develop synaptic "
                        "connections; early brain development.",
    },
    {
        "code": "PHGY 209", "title": "Mammalian Physiology 1",
        "credits": 3, "level": 209, "faculty": "Science",
        "department": "Physiology",
        "description": "Physiology of body fluids, blood, body defense "
                        "mechanisms, muscle, peripheral, central, and "
                        "autonomic nervous systems.",
    },
    {
        "code": "PSYC 211", "title": "Introductory Behavioural Neuroscience",
        "credits": 3, "level": 211, "faculty": "Science",
        "department": "Psychology",
        "description": "Contemporary research on the relationship between "
                        "brain and behaviour: learning, memory, brain damage "
                        "and neuroplasticity, emotion and motivation.",
    },

    # --- Psychology category -----------------------------------------------
    {
        "code": "PSYC 212", "title": "Perception",
        "credits": 3, "level": 212, "faculty": "Science",
        "department": "Psychology",
        "description": "The organization of sensory input into a "
                        "representation of the environment: sensory coding, "
                        "object recognition, spatial localization.",
    },

    # --- Research courses (no stream; repeatable in practice) --------------
    {
        "code": "COGS 401", "title": "Research Cognitive Science 1",
        "credits": 6, "level": 401, "faculty": "Science",
        "department": "Cognitive Science",
        "description": "Research project supervised by a McGill faculty member.",
    },
    {
        "code": "COGS 444", "title": "Honours Research",
        "credits": 6, "level": 444, "faculty": "Science",
        # McGill lists this as Arts & Science Admin (Shared). The progress
        # engine may assign faculty credit to Arts or Science, whichever
        # benefits the student most (often Arts).
        "department": "Cognitive Science",
        "description": "Honours research project.",
        # Displaying the 3+3 split is a future semester-planner concern.
        "splittable_terms": "3+3",
    },

    # --- Computer Science stream (representative subset) -------------------
    {
        "code": "COMP 206", "title": "Introduction to Software Systems",
        "credits": 3, "level": 206, "faculty": "Science",
        "department": "Computer Science",
        "description": "Comprehensive overview of programming in C, use of "
                        "system calls and libraries, debugging and testing "
                        "of code; developmental tools.",
    },
    {
        "code": "COMP 251", "title": "Algorithms and Data Structures",
        "credits": 3, "level": 251, "faculty": "Science",
        "department": "Computer Science",
        "description": "Data structures, graph algorithms, algorithm design "
                        "(greedy, divide and conquer, dynamic programming), "
                        "proofs of asymptotic complexity.",
    },
    {
        "code": "COMP 280", "title": "History and Philosophy of Computing",
        "credits": 3, "level": 280, "faculty": "Science",
        "department": "Computer Science",
        "description": "A history of early mathematical computation, symbolic "
                        "logic and computation, modern computer systems and "
                        "networks, and the rise of the internet.",
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
        "code": "COMP 345", "title": "From Natural Language to Data Science",
        "credits": 3, "level": 345, "faculty": "Science",
        "department": "Computer Science",
        "description": "Introduction to language data science: processing and "
                        "querying text, modelling psycholinguistic data, "
                        "information retrieval, question answering, ethics.",
    },
    {
        "code": "COMP 360", "title": "Algorithm Design",
        "credits": 3, "level": 360, "faculty": "Science",
        "department": "Computer Science",
        "description": "Advanced algorithm design and analysis: linear "
                        "programming, complexity and NP-completeness, "
                        "advanced algorithmic techniques.",
    },
    {
        "code": "COMP 400", "title": "Project in Computer Science",
        "credits": 4, "level": 400, "faculty": "Science",
        "department": "Computer Science",
        "description": "A research project in any area of computer science, "
                        "involving a programming effort and/or theoretical "
                        "investigation, supervised by a faculty member.",
    },
    {
        "code": "COMP 409", "title": "Concurrent Programming",
        "credits": 3, "level": 409, "faculty": "Science",
        "department": "Computer Science",
        "description": "Characteristics and utility of concurrent programs; "
                        "formal methods for specification, verification and "
                        "development; synchronization and resource management.",
    },
    {
        "code": "COMP 417", "title": "Introduction Robotics and Intelligent Systems",
        "credits": 3, "level": 417, "faculty": "Science",
        "department": "Computer Science",
        "description": "Issues relevant to the design of robotic and "
                        "intelligent systems: kinematics, sensors, path "
                        "planning, spatial mapping, multi-agent systems.",
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
    {
        "code": "MATH 222", "title": "Calculus 3",
        "credits": 3, "level": 222, "faculty": "Science",
        "department": "Mathematics and Statistics",
        "description": "Taylor series, partial differentiation, multiple "
                        "integrals, parametric curves, polar and spherical "
                        "coordinates.",
    },
    {
        "code": "MATH 223", "title": "Linear Algebra",
        "credits": 3, "level": 223, "faculty": "Science",
        "department": "Mathematics and Statistics",
        "description": "Matrix algebra, vector spaces, linear operators, "
                        "orthogonality, eigenvalues and eigenvectors, "
                        "applications.",
    },
    {
        "code": "MATH 240", "title": "Discrete Structures",
        "credits": 3, "level": 240, "faculty": "Science",
        "department": "Mathematics and Statistics",
        "description": "Discrete mathematics: logical reasoning, number "
                        "theory, combinatorics, recurrence equations, graph "
                        "theory.",
    },

    # --- Linguistics stream ------------------------------------------------
    {
        "code": "LING 445", "title": "Computational Linguistics",
        "credits": 3, "level": 445, "faculty": "Arts",
        "department": "Linguistics",
        "description": "Identical in content to COMP 445 (double-prefix "
                        "course): formal language theory, probability "
                        "theory, models of language structure.",
    },

    # --- Philosophy stream -------------------------------------------------
    {
        "code": "NSCI 300", "title": "Neuroethics",
        "credits": 3, "level": 300, "faculty": "Science",
        "department": "Physiology",
        "description": "Ethical issues arising from basic and clinical "
                        "neuroscience; therapeutic, diagnostic, and "
                        "research interventions.",
    },
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
        "code": "PHIL 311", "title": "Philosophy of Mathematics",
        "credits": 3, "level": 311, "faculty": "Arts",
        "department": "Philosophy",
        "description": "An historically informed introduction to philosophy "
                        "of mathematics: prominent issues and arguments in "
                        "contemporary research.",
    },
    {
        "code": "PHIL 354", "title": "Plato",
        "credits": 3, "level": 354, "faculty": "Arts",
        "department": "Philosophy",
        "description": "Philosophical problems in logic, epistemology, "
                        "metaphysics, and ethics found in a selection of "
                        "Plato's dialogues.",
    },
    {
        "code": "PHIL 355", "title": "Aristotle",
        "credits": 3, "level": 355, "faculty": "Arts",
        "department": "Philosophy",
        "description": "Selected works by Aristotle: moral philosophy, "
                        "logical treatises, Physics, Metaphysics, and "
                        "philosophy of mind.",
    },
    {
        "code": "PHIL 360", "title": "17th Century Philosophy",
        "credits": 3, "level": 360, "faculty": "Arts",
        "department": "Philosophy",
        "description": "Seventeenth-century philosophers including Descartes, "
                        "Hobbes, Gassendi, Malebranche, Leibniz, and the "
                        "Cambridge Platonists.",
    },
    {
        "code": "PHIL 361", "title": "18th Century Philosophy",
        "credits": 3, "level": 361, "faculty": "Arts",
        "department": "Philosophy",
        "description": "Eighteenth century philosophy, especially British: "
                        "Locke, Berkeley, Hume, Hutcheson, Butler, and Reid.",
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
    {
        "code": "PHIL 441", "title": "Philosophy of Science 2",
        "credits": 3, "level": 441, "faculty": "Arts",
        "department": "Philosophy",
        "description": "Key philosophical ideas in science and technology: "
                        "problem, explanation, forecast, testability and truth.",
    },

    # --- Neuroscience stream -----------------------------------------------
    {
        "code": "ANAT 321", "title": "Circuitry of the Human Brain",
        "credits": 3, "level": 321, "faculty": "Science",
        "department": "Anatomy and Cell Biology",
        "description": "The functional organization of the human brain "
                        "and spinal cord; neuronal systems for motor, "
                        "sensory, and cognitive operations.",
    },
    {
        "code": "BIOL 200", "title": "Molecular Biology",
        "credits": 3, "level": 200, "faculty": "Science",
        "department": "Biology",
        "description": "Physical and chemical properties of the cell: "
                        "protein structure, enzymes, nucleic acid "
                        "replication, transcription, translation, gene "
                        "expression.",
    },
    {
        "code": "BIOL 201", "title": "Cell Biology and Metabolism",
        "credits": 3, "level": 201, "faculty": "Science",
        "department": "Biology",
        "description": "Modern understanding of cells: energy metabolism, "
                        "plasma membrane, cytoskeleton, nervous system, "
                        "hormone signaling, cell cycle.",
    },
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
        "code": "NEUR 310", "title": "Cellular Neurobiology",
        "credits": 3, "level": 310, "faculty": "Science",
        "department": "Neurology and Neurosurgery",
        "description": "Functional organization of nerve cells, signalling "
                        "in the nervous system, and principles of neural "
                        "development at the molecular level.",
    },
    {
        "code": "PHGY 311", "title": "Channels, Synapses and Hormones",
        "credits": 3, "level": 311, "faculty": "Science",
        "department": "Physiology",
        "description": "Experimental results and hypotheses on cellular "
                        "communication in the nervous system and the "
                        "endocrine system.",
    },
    {
        "code": "PHGY 314", "title": "Integrative Neuroscience",
        "credits": 3, "level": 314, "faculty": "Science",
        "department": "Physiology",
        "description": "How neurons and ensembles encode sensory "
                        "information, generate movement, and control "
                        "cognitive functions during voluntary behaviours.",
    },

    # --- Psychology stream (300/400/500-level) ----------------------------
    {
        "code": "PSYC 302", "title": "Pain",
        "credits": 3, "level": 302, "faculty": "Science",
        "department": "Psychology",
        "description": "Pain research and theory: interactions of "
                        "psychological, cultural and physiological factors "
                        "in pain perception and clinical management.",
    },
    {
        "code": "PSYC 303", "title": "Introduction to Human Memory",
        "credits": 3, "level": 303, "faculty": "Science",
        "department": "Psychology",
        "description": "Human memory: major models and taxonomies, memory "
                        "processes, development, autobiographical memory, "
                        "metamemory, disorders of memory.",
    },
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
        "code": "PSYC 306", "title": "Research Methods in Psychology",
        "credits": 3, "level": 306, "faculty": "Science",
        "department": "Psychology",
        "description": "Philosophy of science, methods psychologists use, "
                        "ethical issues, and how to interpret and communicate "
                        "psychological research.",
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
        "code": "PSYC 341", "title": "The Psychology of Bilingualism",
        "credits": 3, "level": 341, "faculty": "Science",
        "department": "Psychology",
        "description": "Issues in bilingualism: second language acquisition, "
                        "critical period hypothesis, cognitive consequences, "
                        "social psychological aspects, bilingual education.",
    },
    {
        "code": "PSYC 342", "title": "Hormones and Behaviour",
        "credits": 3, "level": 342, "faculty": "Science",
        "department": "Psychology",
        "description": "The role of hormones in organization of CNS "
                        "function, as effectors of behaviour, and in mental "
                        "illness.",
    },
    {
        "code": "PSYC 410", "title": "Special Topics in Neuropsychology",
        "credits": 3, "level": 410, "faculty": "Science",
        "department": "Psychology",
        "description": "Developments in cognitive neuroscience and "
                        "cognitive neuropsychiatry via readings from "
                        "primary sources.",
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
        "code": "PSYC 427", "title": "Sensorimotor Neuroscience",
        "credits": 3, "level": 427, "faculty": "Science",
        "department": "Psychology",
        "description": "A systematic examination of the sensorimotor system: "
                        "cortical motor areas, cerebellum, basal ganglia, "
                        "spinal mechanisms, proprioception.",
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
        "code": "PSYC 443", "title": "Affective Neuroscience",
        "credits": 3, "level": 443, "faculty": "Science",
        "department": "Psychology",
        "description": "Neurobiology of emotion, links between emotion and "
                        "cognition, and individual differences in emotional "
                        "states associated with psychopathology.",
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
#
# ONLY courses that appear on a stream's Complementary Courses list in
# cogsci_course_catalogue.md are tagged here. Area/Core-Complementary
# courses that are NOT on any stream list belong in ELECTIVES_ONLY_COURSES
# instead — their overflow credit goes to the Electives bucket.
# ---------------------------------------------------------------------------

COURSE_STREAMS = [
    # Computer Science stream (catalogue complementary list)
    ("COMP 206", "Computer Science"),
    ("COMP 250", "Computer Science"),
    ("COMP 251", "Computer Science"),
    ("COMP 280", "Computer Science"),
    ("COMP 302", "Computer Science"),
    ("COMP 330", "Computer Science"),
    ("COMP 345", "Computer Science"),
    ("COMP 360", "Computer Science"),
    ("COMP 400", "Computer Science"),
    ("COMP 409", "Computer Science"),
    ("COMP 417", "Computer Science"),
    ("COMP 421", "Computer Science"),
    ("COMP 424", "Computer Science"),
    ("COMP 445", "Computer Science"),
    ("COMP 451", "Computer Science"),
    ("COMP 550", "Computer Science"),
    ("COMP 551", "Computer Science"),
    ("COMP 558", "Computer Science"),
    ("COMP 549", "Computer Science"),
    ("MATH 222", "Computer Science"),
    ("MATH 223", "Computer Science"),
    ("MATH 240", "Computer Science"),

    # Linguistics stream
    ("LING 201", "Linguistics"),
    ("LING 210", "Linguistics"),
    ("LING 260", "Linguistics"),
    ("LING 445", "Linguistics"),
    ("COMP 445", "Linguistics"),   # double-prefix; also CS stream above

    # Philosophy stream
    ("NSCI 300", "Philosophy"),
    ("PHIL 306", "Philosophy"),
    ("PHIL 310", "Philosophy"),
    ("PHIL 311", "Philosophy"),
    ("PHIL 354", "Philosophy"),
    ("PHIL 355", "Philosophy"),
    ("PHIL 360", "Philosophy"),
    ("PHIL 361", "Philosophy"),
    ("PHIL 415", "Philosophy"),
    ("PHIL 419", "Philosophy"),
    ("PHIL 441", "Philosophy"),

    # Psychology stream
    ("PSYC 204", "Psychology"),
    ("PSYC 302", "Psychology"),
    ("PSYC 303", "Psychology"),
    ("PSYC 304", "Psychology"),
    ("PSYC 305", "Psychology"),
    ("PSYC 306", "Psychology"),
    ("PSYC 311", "Psychology"),
    ("PSYC 315", "Psychology"),
    ("PSYC 340", "Psychology"),
    ("PSYC 341", "Psychology"),
    ("PSYC 342", "Psychology"),
    ("PSYC 410", "Psychology"),
    ("PSYC 413", "Psychology"),
    ("PSYC 427", "Psychology"),
    ("PSYC 433", "Psychology"),
    ("PSYC 443", "Psychology"),
    ("PSYC 506", "Psychology"),
    ("PSYC 513", "Psychology"),

    # Neuroscience stream
    ("NSCI 201", "Neuroscience"),
    ("NSCI 300", "Neuroscience"),
    ("ANAT 321", "Neuroscience"),
    ("BIOL 200", "Neuroscience"),
    ("BIOL 201", "Neuroscience"),
    ("BIOL 306", "Neuroscience"),
    ("BIOL 320", "Neuroscience"),
    ("NEUR 310", "Neuroscience"),
    ("PHGY 311", "Neuroscience"),
    ("PHGY 314", "Neuroscience"),
    # PSYC courses also on the Neuroscience complementary list
    ("PSYC 302", "Neuroscience"),
    ("PSYC 303", "Neuroscience"),
    ("PSYC 306", "Neuroscience"),
    ("PSYC 311", "Neuroscience"),
    ("PSYC 342", "Neuroscience"),
    ("PSYC 410", "Neuroscience"),
    ("PSYC 427", "Neuroscience"),
    ("PSYC 433", "Neuroscience"),
    ("PSYC 443", "Neuroscience"),
    ("PSYC 506", "Neuroscience"),
]

# ---------------------------------------------------------------------------
# ELECTIVES BUCKET (not a Stream, not a Requirement row)
#
# Area-eligible courses with NO stream mapping. If a student completes/plans
# two courses eligible for the same Area, one satisfies the Area and the
# other overflows here (visible Elective credit, not silently dropped).
# ---------------------------------------------------------------------------

ELECTIVES_ONLY_COURSES = [
    "COMP 202", "COMP 204", "COMP 230",
    "MATH 203", "MATH 318", "MATH 323",
    "PHIL 200", "PHIL 201", "PHIL 203", "PHIL 210", "PHIL 221",
    "NSCI 200", "PHGY 209",
    "PSYC 211", "PSYC 212", "PSYC 213",
]

# Research courses with no stream mapping — tracked in the Electives bucket
# when not consumed elsewhere. COGS 444 also satisfies the honours research
# requirement when honours is enabled.
RESEARCH_ELECTIVE_COURSES = ["COGS 401", "COGS 444"]

# Courses whose Arts/Science credit may be assigned to either faculty bucket
# during progress evaluation (whichever benefits the student most).
FLEXIBLE_FACULTY_COURSES = ["COGS 444"]

# All courses that should surface in the Electives bucket when not consumed
# by an Area requirement.
ELECTIVES_BUCKET_COURSES = ELECTIVES_ONLY_COURSES + RESEARCH_ELECTIVE_COURSES

# ---------------------------------------------------------------------------
# COURSE -> AREA relationships (many-to-many)
# Maps each course to the Area(s) it satisfies, per the mapping documented
# at the top of this file and cogsci_course_catalogue.md Core Complementary.
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
    ("Computer Science Foundations", "COMP 204"),
    ("Computer Science Foundations", "COMP 250"),

    ("Linguistics Foundations", "LING 201"),
    ("Linguistics Foundations", "LING 210"),
    ("Linguistics Foundations", "LING 260"),

    ("Philosophy Foundations", "PHIL 200"),
    ("Philosophy Foundations", "PHIL 201"),
    ("Philosophy Foundations", "PHIL 203"),
    ("Philosophy Foundations", "PHIL 221"),

    ("Neuroscience Foundations", "NSCI 200"),
    ("Neuroscience Foundations", "PHGY 209"),
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
    ("COMP 250", "COMP 204"),

    # COMP 251 requires COMP 250 and (MATH 235 or MATH 240 — not seeded)
    ("COMP 251", "COMP 250"),
    ("COMP 251", "MATH 240"),

    # COMP 302 requires COMP 250 and one of MATH240/235/318/COMP230/PHIL210
    ("COMP 302", "COMP 250"),
    ("COMP 302", "MATH 240"),
    ("COMP 302", "MATH 318"),
    ("COMP 302", "COMP 230"),
    ("COMP 302", "PHIL 210"),

    # COMP 330 requires COMP 251
    ("COMP 330", "COMP 251"),

    # COMP 345 requires COMP 250
    ("COMP 345", "COMP 250"),

    # COMP 360 requires COMP 251
    ("COMP 360", "COMP 251"),

    # COMP 421 requires COMP 206, COMP 251, COMP 302
    ("COMP 421", "COMP 206"),
    ("COMP 421", "COMP 251"),
    ("COMP 421", "COMP 302"),

    # COMP 424 requires (COMP 206) + MATH 323 + COMP 251
    ("COMP 424", "COMP 206"),
    ("COMP 424", "MATH 323"),
    ("COMP 424", "COMP 251"),

    # COMP 445 / LING 445 require COMP 250 and MATH 240
    ("COMP 445", "COMP 250"),
    ("COMP 445", "MATH 240"),
    ("LING 445", "COMP 250"),
    ("LING 445", "MATH 240"),

    # COMP 451 requires COMP 251 + MATH 222/223/323
    ("COMP 451", "COMP 251"),
    ("COMP 451", "MATH 223"),
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

    # PSYC 306 requires PSYC 204
    ("PSYC 306", "PSYC 204"),

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

    # NEUR 310 requires NSCI 201
    ("NEUR 310", "NSCI 201"),

    # PHGY 311 requires PHGY 209
    ("PHGY 311", "PHGY 209"),

    # PHGY 314 requires NSCI 201
    ("PHGY 314", "NSCI 201"),

    # BIOL 201 requires BIOL 200
    ("BIOL 201", "BIOL 200"),

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
