"""Compatibility module for the current Cognitive Science seed data.

The hand-maintained source of truth now lives in `cogsci_seed_data.py`. Import
and re-export it here so the existing seeder/tests keep using `app.seed.data`
without maintaining two divergent copies.
"""

from app.seed.cogsci_seed_data import *  # noqa: F401,F403
