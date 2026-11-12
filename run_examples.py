"""Generate the assignment's four reproducible scenario reports."""
from pathlib import Path

from models import Profile
from offline import run_offline
from reporter import render_report


SCENARIOS = {
    "01_example_passed": Profile(
        age=34, gender="female", profession="software engineer", income_sources=["salary", "freelance"], income=1_500_000,
        investment=200_000, location="dhaka_chattogram_city", has_tin=True,
    ),
    "02_minor_flagged": Profile(
        age=16, gender="male", profession="student", income=500_000,
        location="rest_of_country", has_tin=False,
    ),
    "03_below_threshold": Profile(
        age=45, gender="male", profession="teacher", income=300_000,
        location="rest_of_country", has_tin=True, claims_required_to_file=True,
    ),
    "04_investment_exceeds_income": Profile(
        age=35, gender="male", profession="business", income=800_000,
        investment=1_000_000, location="rest_of_country", has_tin=True,
    ),
}


def main() -> None:
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    for name, profile in SCENARIOS.items():
        report = render_report(run_offline(profile))
        (reports_dir / f"{name}.md").write_text(report, encoding="utf-8")
        print(f"{name}: written")


if __name__ == "__main__":
    main()
