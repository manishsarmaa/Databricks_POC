# CLAUDE.md

Project context for Claude Code. Read this before changing anything.

## What this is
A medallion (bronze → silver → gold) ETL POC on Azure Data Factory + Databricks,
deployed with Databricks Asset Bundles. It exists to show how Claude Code
maintains an EXISTING pipeline safely: amend code, test it, and prove the change
did not break other pipelines.

## Architecture
- `src/common/` — shared functions (`cleansing`, `casting`, `schema`). **Reused by
  every pipeline.** Treat them as high-blast-radius.
- `src/pipelines/<name>/` — bronze/silver/gold for each source. These call the
  common functions; they hold almost no logic of their own.
- `notebooks/` — thin Databricks wrappers. No business logic here.
- `tests/` — pytest + chispa. Runs locally, no cluster.
- `resources/` + `databricks.yml` — the Asset Bundle (deploy).

## The one rule that matters
`src/common/*` is shared by orders, customers and payments. **After editing ANY
file in `src/common/`, run the FULL test suite (`pytest`), not just the test for
the pipeline you were fixing.** The other pipelines' tests are the regression net
— they are how we know a shared-code change didn't break the other 20–30 pipelines.

## How to make a change safely (always follow this loop)
1. Reproduce the failure with a failing test first (add it to `tests/`).
2. Make the smallest change. Prefer fixing it inside `src/common/` ONLY if the
   behaviour is genuinely shared; otherwise fix it in the one pipeline.
3. Run `pytest`. All tests — including customers/payments — must stay green.
4. If a common-function change turns another pipeline's test red, that change is
   wrong: narrow it (parameterise, or move it into the single pipeline) instead.
5. Update the contract in `src/common/schema.py` if columns/types changed.
6. Only then deploy (`databricks bundle deploy -t dev`). CI also blocks deploy
   unless `pytest` is green.

## Conventions
- Read bronze as strings; never trust source-inferred types. Cast in silver
  against the contract in `schema.py`.
- New column from source → add to the contract. Dropped column → `align_to_contract`
  already backfills NULL. Funny characters → `strip_control_chars` /
  `clean_column_names` already handle them.
- Don't widen a shared function's behaviour to fix one source. Keep it narrow.

## Commands
- Tests: `pytest -q`
- Generate sample data: `python scripts/generate_data.py`
- Inject the failure modes: `python scripts/break_input.py`
- Deploy: `databricks bundle deploy -t dev`
