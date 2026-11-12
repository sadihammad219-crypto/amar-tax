from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from models import Profile
from offline import run_offline
from reporter import render_report

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Amar Tax virtual tax advisor")
    parser.add_argument("--profile", default="example_profile.json", help="Path to a profile JSON file")
    parser.add_argument("--output", help="Optional Markdown report path")
    parser.add_argument("--live-crew", action="store_true", help="Run a configured CrewAI provider before falling back locally")
    args = parser.parse_args()
    profile = Profile.model_validate(json.loads(Path(args.profile).read_text(encoding="utf-8")))
    # The local DB is authoritative and keeps the assignment runnable when a
    # configured API/LLM provider, web lookup, or package dependency fails.
    if args.live_crew:
        try:
            from crew import run_with_crew
            report = "# Amar Tax — CrewAI output\n\n" + run_with_crew(profile)
        except Exception as exc:  # provider/network/configuration errors are non-fatal
            logging.warning("CrewAI/API lookup failed (%s); falling back to Local DB", exc)
            report = render_report(run_offline(profile))
    else:
        logging.info("Using Local DB fallback runner (no external API configured)")
        report = render_report(run_offline(profile))
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        logging.info("Wrote report to %s", args.output)
    print(report)


if __name__ == "__main__":
    main()
