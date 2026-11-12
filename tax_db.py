"""Simulated 2026 Bangladesh tax data. This is the application's source of truth."""

TAX_DB = {
    "tax_year": "2026-27",
    "filing_deadline": "2026-11-30",
    "thresholds": {
        "general": 350_000,
        "female": 400_000,
        "senior_65_plus": 400_000,
        "disabled": 475_000,
        "freedom_fighter": 500_000,
    },
    "slabs_after_threshold": [
        {"limit": 100_000, "rate": 0.05},
        {"limit": 400_000, "rate": 0.10},
        {"limit": 500_000, "rate": 0.15},
        {"limit": 500_000, "rate": 0.20},
        {"limit": None, "rate": 0.25},
    ],
    "minimum_tax": {
        "dhaka_chattogram_city": 5_000,
        "other_city_corporation": 4_000,
        "rest_of_country": 3_000,
    },
    "investment_rebate": {"rate": 0.15, "max_investment_percent_of_income": 0.20},
    "required_docs": {
        "common": ["TIN Certificate", "NID Copy", "Bank Statement"],
        "salaried": ["Salary Certificate", "Employer Details"],
        "business": ["Trade License", "Profit & Loss Statement", "Balance Sheet"],
        "freelancer": ["Foreign Remittance Proof", "Client Invoices"],
        "landlord": ["Rent Agreement", "Municipal Tax Receipt"],
        "investor": ["Investment Certificates (DPS/Sanchaypatra)", "Bank Interest Certificate"],
    },
}
