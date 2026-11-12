from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field, field_validator


class Location(str, Enum):
    DHAKA_CHATTOGRAM = "dhaka_chattogram_city"
    OTHER_CITY = "other_city_corporation"
    REST = "rest_of_country"


class Profile(BaseModel):
    age: int = Field(ge=0, le=130)
    gender: str = "male"
    profession: str
    income_sources: list[str] = []
    income: float
    investment: float = 0
    location: Location = Location.REST
    has_tin: bool = False
    wants_to_file_independently: bool = True
    claims_required_to_file: bool = False
    disabled: bool = False
    freedom_fighter: bool = False

    @field_validator("gender")
    @classmethod
    def normalize_gender(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("location", mode="before")
    @classmethod
    def normalize_location(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "dhaka": "dhaka_chattogram_city", "chattogram": "dhaka_chattogram_city",
            "chittagong": "dhaka_chattogram_city", "other_city": "other_city_corporation",
            "city_corporation": "other_city_corporation", "rangpur": "rest_of_country",
        }
        return aliases.get(normalized, normalized)


class ClassificationOutput(BaseModel):
    taxpayer_category: str
    tax_free_threshold: float
    minimum_tax: float
    filing_mandatory: bool
    flags: list[str] = []


class CalculationOutput(BaseModel):
    total_income: float
    taxable_income_after_threshold: float
    gross_tax: float
    allowable_investment: float
    investment_rebate: float
    net_payable_tax: float


class ChecklistOutput(BaseModel):
    documents: list[str]
    used_general_fallback: bool = False


class ComplianceOutput(BaseModel):
    status: str
    findings: list[str]


class TaxReadinessResult(BaseModel):
    profile: Profile
    classification: ClassificationOutput
    calculation: CalculationOutput
    checklist: ChecklistOutput
    compliance: ComplianceOutput
