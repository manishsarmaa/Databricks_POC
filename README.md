# Claude Code × Databricks — pipeline maintenance POC

A small, runnable medallion pipeline (bronze → silver → gold) on ADF + Databricks,
deployed with Databricks Asset Bundles, built to demonstrate one thing:
**using Claude Code to safely maintain an existing pipeline** — amend the code,
test it, and prove the change didn't break the other pipelines that share the same
common functions.

This contains **no confidential code**. Everything is generated sample data.

## Why it's shaped this way
The hard part of real data work isn't writing code or docs (Claude Code does docs
in minutes). It's changing a shared codebase without breaking the 20–30 pipelines
that reuse the same functions, and testing that automatically when there's no QA
team. So:

- Business logic is pure-Python PySpark in `src/` → unit-testable locally, **no
  cluster**.
- `src/common/` functions are shared by three pipelines (orders, customers,
  payments). Editing them runs against **all three** test suites.
- Notebooks are thin wrappers → Databricks just calls `src/`.
- CI runs the full test suite and **blocks deploy unless green**.

## Layout
```
src/common/        shared cleansing / casting / schema-contract functions
src/pipelines/     orders (bronze/silver/gold), customers, payments (silver)
tests/             pytest + chispa; data_quality/ for property checks
notebooks/         thin Databricks wrappers (Free Edition serverless + UC)
resources/         Asset Bundle job definition
databricks.yml     Asset Bundle config
azure-pipelines.yml Azure DevOps CI (test -> deploy)
scripts/           generate_data.py, break_input.py
data/              generated CSVs (orders 100 rows, customers, payments, broken)
CLAUDE.md          project memory; the self-guard rule for Claude Code
PROMPTS.md         the live demo script for the call
```

## Run it locally (laptop, no cloud)
```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python scripts/generate_data.py
python scripts/break_input.py
pytest -q
```
Requires Java 8/11/17 on PATH (PySpark needs a JVM). `java -version` to check.

## Run it on Databricks Free Edition
1. Sign in at the Free Edition workspace and create a Git folder pointing at this repo.
2. Install Claude Code and connect it to the repo (see below).
3. Create a Unity Catalog volume and upload `data/orders.csv` to it, e.g.
   `/Volumes/workspace/poc/raw/orders.csv`.
4. Configure the CLI: `databricks configure` (host + token), then
   `databricks bundle validate -t dev` and `databricks bundle deploy -t dev`.
5. Run the `orders_medallion` job. It runs bronze → silver → gold on serverless.

## Claude Code setup (what you'll show on the call)
- Install (recommended, no Node): `curl -fsSL https://claude.ai/install.sh | bash`
  (Windows PowerShell: `irm https://claude.ai/install.ps1 | iex`).
  npm alternative (Node 18+): `npm install -g @anthropic-ai/claude-code`.
- Verify: `claude --version`, health check: `claude doctor`.
- In VS Code, install the Claude Code extension; it runs the CLI in the integrated
  terminal and shows diffs in VS Code's diff viewer. (Requires a paid Claude plan
  or an API/Console account.)
- `CLAUDE.md` in the repo root is read automatically — it's what makes Claude Code
  run the full suite after touching shared code.

## The demo (mirrors exactly what the client asked for)
Follow `PROMPTS.md`. In short:
1. Pipeline runs clean on `orders.csv` (100 rows).
2. `break_input.py` injects the 5 daily failure modes (funny chars, renamed header,
   type drift, extra column, dropped column).
3. Drive Claude Code to fix each with a test; `pytest` proves it.
4. **Blast-radius demo:** make a bad shared-function change → a *different*
   pipeline's test goes red → that's the regression net → narrow the fix.

## Talking points for his three hard questions
- **"How do you change shared code without breaking the other pipelines?"** Each
  pipeline keeps its own tests; the full suite is the regression net. A wrong shared
  change turns another pipeline's test red immediately — you don't need to remember
  who uses what.
- **"How does Claude Code test, not just write code?"** Pure functions + pytest +
  chispa run locally in seconds; CI re-runs them and gates deploy. Test data is one
  ~100-row file, exactly as you suggested.
- **"How do you deploy?"** Asset Bundle via Azure DevOps; deploy only runs if tests
  pass.

## Honest scope
This proves the *workflow and the safety mechanism* on a clean sample. Adapting it
to his real ~70–100 notebooks is the actual engagement — but every moving part
(contract-driven silver, shared-function regression net, test-gated bundle deploy)
is here and runnable.
