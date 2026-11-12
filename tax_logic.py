"""Deterministic implementations used by tools and by the offline fallback."""
from __future__ import annotations

from models import CalculationOutput, ChecklistOutput, ClassificationOutput, ComplianceOutput, Profile
from tax_db import TAX_DB


def classify(profile: Profile) -> ClassificationOutput:
    flags: list[str] = []
    if profile.income < 0:
        flags.append("Invalid input: income cannot be negative.")
    if profile.investment < 0:
        flags.append("Invalid input: investment cannot be negative.")
    if profile.investment > profile.income and profile.income >= 0:
        flags.append("Investment exceeds income, please verify.")
    if profile.age < 18 and profile.wants_to_file_independently:
        flags.append("Minor cannot file independently.")

    if profile.freedom_fighter:
        category = "Freedom Fighter"
        key = "freedom_fighter"
    elif profile.disabled:
        category = "Disabled"
        key = "disabled"
    elif profile.age >= 65:
        category = "Senior 65+"
        key = "senior_65_plus"
    elif profile.gender == "female":
        category = "Female"
        key = "female"
    else:
        category = "General"
        key = "general"

    threshold = TAX_DB["thresholds"][key]
    minimum = TAX_DB["minimum_tax"][profile.location.value]
    mandatory = profile.age >= 18 and profile.income > threshold
    if profile.claims_required_to_file and not mandatory:
        flags.append("Filing is not mandatory at this income under the simulated DB; review the minimum-tax rule if filing voluntarily.")
    return ClassificationOutput(
        taxpayer_category=category,
        tax_free_threshold=threshold,
        minimum_tax=minimum,
        filing_mandatory=mandatory,
        flags=flags,
    )


def calculate(profile: Profile, classification: ClassificationOutput) -> CalculationOutput:
    income = max(profile.income, 0)
    taxable = max(0, income - classification.tax_free_threshold)
    remaining = taxable
    gross = 0.0
    for slab in TAX_DB["slabs_after_threshold"]:
        portion = remaining if slab["limit"] is None else min(remaining, slab["limit"])
        gross += portion * slab["rate"]
        remaining -= portion
        if remaining <= 0:
            break
    allowed = min(max(profile.investment, 0), income * TAX_DB["investment_rebate"]["max_investment_percent_of_income"])
    rebate = allowed * TAX_DB["investment_rebate"]["rate"]
    # The assignment explicitly applies minimum tax only above the threshold.
    net = max(gross - rebate, classification.minimum_tax) if income > classification.tax_free_threshold else 0.0
    return CalculationOutput(
        total_income=income, taxable_income_after_threshold=taxable, gross_tax=gross,
        allowable_investment=allowed, investment_rebate=rebate, net_payable_tax=net,
    )


def checklist(profile: Profile) -> ChecklistOutput:
    docs = list(TAX_DB["required_docs"]["common"])
    if not profile.has_tin:
        docs.insert(0, "TIN Registration")
    profession = profile.profession.strip().lower()
    sources = {source.strip().lower() for source in profile.income_sources}
    mapping = {
        "salaried": "salaried", "software engineer": "salaried", "employee": "salaried",
        "business": "business", "business owner": "business", "freelancer": "freelancer",
        "landlord": "landlord",
    }
    matched = mapping.get(profession)
    if matched:
        docs.extend(TAX_DB["required_docs"][matched])
    if "salary" in sources and matched != "salaried":
        docs.extend(TAX_DB["required_docs"]["salaried"])
    if "freelance" in sources and matched != "freelancer":
        docs.extend(TAX_DB["required_docs"]["freelancer"])
    if profile.investment > 0:
        docs.extend(TAX_DB["required_docs"]["investor"])
    # Preserve order while removing duplicated documents.
    return ChecklistOutput(documents=list(dict.fromkeys(docs)), used_general_fallback=matched is None)


def review(profile: Profile, c: ClassificationOutput, calc: CalculationOutput, docs: ChecklistOutput) -> ComplianceOutput:
    findings = list(c.flags)
    if calc.gross_tax < 0 or calc.net_payable_tax < 0:
        findings.append("Invalid negative tax result.")
    if profile.income > c.tax_free_threshold and calc.net_payable_tax < c.minimum_tax:
        findings.append("Net tax is below the location minimum tax.")
    if not profile.has_tin and (not docs.documents or docs.documents[0] != "TIN Registration"):
        findings.append("TIN Registration must be first in the checklist.")
    if docs.used_general_fallback:
        findings.append("Profession not in DB: general checklist used.")
    return ComplianceOutput(status="✅ Passed" if not findings else "⚠️ Flagged", findings=findings)
