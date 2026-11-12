from __future__ import annotations

import json
import logging
from crewai.tools import tool
from models import Profile
from tax_db import TAX_DB
from tax_logic import calculate, classify

logger = logging.getLogger(__name__)


@tool("lookup_tax_db")
def lookup_tax_db(section: str) -> str:
    """Look up one source-of-truth tax database section by name."""
    try:
        return json.dumps(TAX_DB[section])
    except KeyError:
        # This is deliberately local: a web/API lookup would be attempted here if enabled.
        logger.warning("External lookup unavailable or unknown section; using local tax DB fallback")
        return json.dumps(TAX_DB)


@tool("calculate_slab_tax")
def calculate_slab_tax(profile_json: str) -> str:
    """Calculate simulated slab tax from a JSON taxpayer profile using only the local DB."""
    profile = Profile.model_validate_json(profile_json)
    return calculate(profile, classify(profile)).model_dump_json()
