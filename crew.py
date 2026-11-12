"""CrewAI implementation. The offline runner remains available when no LLM/API is configured."""
from __future__ import annotations

import json
import logging
from crewai import Agent, Crew, Process, Task
from models import ClassificationOutput, Profile
from tools import calculate_slab_tax, lookup_tax_db

logger = logging.getLogger(__name__)


def build_crew(profile: Profile) -> Crew:
    """Create the required Classifier → Calculator → Organizer → Reviewer task chain."""
    profile_json = profile.model_dump_json()
    classifier = Agent(
        role="Senior Taxpayer Classification Officer",
        goal="Classify the taxpayer and identify filing requirement, threshold and minimum tax from the local DB.",
        backstory="You are a meticulous NBR-style classification officer. You never invent tax rules.",
        tools=[lookup_tax_db], verbose=True,
    )
    calculator = Agent(
        role="Chartered Tax Accountant",
        goal="Calculate slab tax, rebate and payable tax using only local database rules.",
        backstory="You independently check every number and use the provided calculator tool.",
        tools=[calculate_slab_tax, lookup_tax_db], verbose=True,
    )
    organizer = Agent(
        role="Return Filing Documentation Officer",
        goal="Provide a customized document checklist and put TIN Registration first if absent.",
        backstory="You turn tax facts into a practical filing checklist without requesting irrelevant documents.",
        verbose=True,
    )
    reviewer = Agent(
        role="Compliance & Audit Reviewer",
        goal="Cross-check all preceding work, expose inconsistencies, and set Passed or Flagged.",
        backstory="You are a skeptical audit reviewer who treats the local simulated DB as authoritative.",
        verbose=True,
    )
    classification_task = Task(
        description=f"Classify this profile: {profile_json}. Use lookup_tax_db. Return the requested fields only.",
        expected_output="Category, threshold, minimum tax, mandatory decision, and warnings.",
        agent=classifier, output_pydantic=ClassificationOutput,
    )
    calculation_task = Task(
        description=f"Use this profile: {profile_json}. Use calculate_slab_tax and report all computed fields.",
        expected_output="Gross tax, allowable investment, rebate, and net payable tax.",
        agent=calculator, context=[classification_task],
    )
    documents_task = Task(
        description=f"Create the checklist for this profile: {profile_json}. Apply the local DB rules.",
        expected_output="Customized document list and any fallback note.",
        agent=organizer, context=[classification_task, calculation_task],
    )
    review_task = Task(
        description="Validate the classifier, calculator, and organizer outputs. End with exactly ✅ Passed or ⚠️ Flagged and concise findings.",
        expected_output="Final compliance status plus cross-check findings.",
        agent=reviewer, context=[classification_task, calculation_task, documents_task],
    )
    return Crew(
        agents=[classifier, calculator, organizer, reviewer],
        tasks=[classification_task, calculation_task, documents_task, review_task],
        process=Process.sequential,
        verbose=True,
    )


def run_with_crew(profile: Profile) -> str:
    """Run live CrewAI; callers should fall back to `offline.run_offline` on provider failure."""
    logger.info("Starting CrewAI chain; local DB remains the only tax-rule source")
    return str(build_crew(profile).kickoff())
