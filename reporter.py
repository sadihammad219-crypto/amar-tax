from __future__ import annotations

from models import TaxReadinessResult


def bdt(value: float) -> str:
    return f"{value:,.0f} BDT"


def render_report(result: TaxReadinessResult) -> str:
    c, calc, checklist, review = result.classification, result.calculation, result.checklist, result.compliance
    documents = ", ".join(checklist.documents)
    findings = "; ".join(review.findings) if review.findings else "No inconsistencies found."
    mandatory = "Yes" if c.filing_mandatory else "No"
    return f"""# Amar Tax — Tax Readiness Report

| Field | Result |
|---|---|
| Taxpayer Category | {c.taxpayer_category} |
| Filing Mandatory | {mandatory} |
| Total Income | {bdt(calc.total_income)} |
| Tax-free Threshold | {bdt(c.tax_free_threshold)} |
| Gross Tax (Slab-based) | {bdt(calc.gross_tax)} |
| Allowable Investment | {bdt(calc.allowable_investment)} |
| Investment Rebate (15%) | {bdt(calc.investment_rebate)} |
| Minimum Tax | {bdt(c.minimum_tax)} |
| Net Payable Tax | {bdt(calc.net_payable_tax)} |
| Documents Needed | {documents} |
| Compliance Status | {review.status} |
| Review Notes | {findings} |

## বাংলা সারসংক্ষেপ

আপনার মোট আয় ও প্রযোজ্য করসীমা অনুযায়ী এই হিসাবটি তৈরি করা হয়েছে।
প্রদেয় করের পরিমাণ হলো **{bdt(calc.net_payable_tax)}**।
প্রয়োজনীয় কাগজপত্র সংগ্রহ করে রিটার্ন জমা দেওয়ার আগে তথ্যগুলো যাচাই করুন।
অনিশ্চয়তা বা সতর্কবার্তা থাকলে একজন নিবন্ধিত কর-পরামর্শকের সঙ্গে কথা বলুন।
"""
