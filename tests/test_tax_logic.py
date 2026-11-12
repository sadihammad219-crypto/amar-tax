import unittest

from models import Profile
from offline import run_offline


class TaxLogicTests(unittest.TestCase):
    def test_example_scenario_matches_assignment(self):
        result = run_offline(Profile(
            age=34, gender="female", profession="software engineer", income_sources=["salary", "freelance"], income=1_500_000,
            investment=200_000, location="dhaka_chattogram_city", has_tin=True,
        ))
        self.assertEqual(result.classification.taxpayer_category, "Female")
        self.assertEqual(result.calculation.gross_tax, 140_000)
        self.assertEqual(result.calculation.investment_rebate, 30_000)
        self.assertEqual(result.calculation.net_payable_tax, 110_000)
        self.assertEqual(result.compliance.status, "✅ Passed")

    def test_minor_is_flagged(self):
        result = run_offline(Profile(
            age=16, gender="male", profession="student", income=500_000,
            location="rest_of_country", has_tin=False,
        ))
        self.assertIn("Minor cannot file independently.", result.classification.flags)
        self.assertEqual(result.compliance.status, "⚠️ Flagged")
        self.assertEqual(result.checklist.documents[0], "TIN Registration")

    def test_income_below_threshold_is_not_mandatory(self):
        result = run_offline(Profile(
            age=45, gender="male", profession="teacher", income=300_000,
            location="rest_of_country", claims_required_to_file=True, has_tin=True,
        ))
        self.assertFalse(result.classification.filing_mandatory)
        self.assertEqual(result.calculation.net_payable_tax, 0)
        self.assertTrue(any("not mandatory" in flag for flag in result.classification.flags))

    def test_investment_exceeding_income_is_flagged_and_capped(self):
        result = run_offline(Profile(
            age=35, gender="male", profession="business", income=800_000,
            investment=1_000_000, location="rest_of_country", has_tin=True,
        ))
        self.assertIn("Investment exceeds income, please verify.", result.classification.flags)
        self.assertEqual(result.calculation.allowable_investment, 160_000)
        self.assertEqual(result.compliance.status, "⚠️ Flagged")


if __name__ == "__main__":
    unittest.main()
