# Amar Tax — CrewAI Virtual Tax Advisor

A Bangladesh individual-tax readiness demonstration. It uses the supplied simulated 2026–27 database as the only tax-rule source; it is **not** production tax advice.

## Architecture

```text
Profile → Classifier → Slab Calculator → Document Organizer → Compliance Reviewer → Markdown report
                         ↑ context passed between every downstream CrewAI task ↑
```

`crew.py` declares the four CrewAI agents, their role/goal/backstory, sequential task delegation, `context=[...]`, `verbose=True`, a custom tool, and a Pydantic task output. `offline.py` is a deterministic local fallback, so the project remains demonstrable without API credentials or if an LLM/API request fails. Both paths use the same local data and calculator. `--live-crew` wraps provider execution in `try/except`, logs failure, and falls back to the local DB.

## Install and run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py --profile example_profile.json --output reports/example.md
python -m unittest discover -s tests -v
python run_examples.py
```

The CLI deliberately uses the offline fallback runner to ensure reproducible tax results. To exercise a configured CrewAI provider, run `python main.py --live-crew`; its LLM must be configured through CrewAI's normal environment settings.

## Required scenarios verified

| Scenario | Result |
|---|---|
| 34-year-old woman, income 1,500,000, investment 200,000, Dhaka | Gross 140,000; rebate 30,000; net 110,000; Passed |
| 16-year-old, income 500,000 | Minor flag; Flagged |
| 45-year-old male, income 300,000, Rangpur | Not mandatory; zero tax |
| Income 800,000, investment 1,000,000 | Investment-exceeds-income flag; allowed investment capped at 160,000 |

`run_examples.py` creates four ready-to-open report artifacts in `reports/`, which can be used as the assignment screenshot evidence.
