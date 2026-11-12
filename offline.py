"""Reliable no-LLM execution path; it applies the exact same source-of-truth logic."""
from models import Profile, TaxReadinessResult
from tax_logic import calculate, checklist, classify, review


def run_offline(profile: Profile) -> TaxReadinessResult:
    classification = classify(profile)
    calculation = calculate(profile, classification)
    documents = checklist(profile)
    compliance = review(profile, classification, calculation, documents)
    return TaxReadinessResult(
        profile=profile, classification=classification, calculation=calculation,
        checklist=documents, compliance=compliance,
    )
