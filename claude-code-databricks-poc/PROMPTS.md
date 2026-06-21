# PROMPTS.md — the demo script for the call

This is what you run/read during the call. Each scenario is one of the client's
exact daily failures, the Claude Code prompt to fix it, and the test that proves
the fix is safe. Keep `pytest` visible in a terminal the whole time.

> Framing line for the client: *"Coding and docs are the easy 3-minute part. The
> hard part is amending an existing shared codebase and proving I didn't break the
> other pipelines. That's what this shows — every fix is gated by the other
> pipelines' tests."*

---

## Setup (once, before the call)
```bash
pip install -r requirements-dev.txt
python scripts/generate_data.py      # 100-row orders.csv + customers + payments
python scripts/break_input.py        # orders_broken.csv with the 5 failure modes
pytest -q                            # all green — your baseline
```

---

## Scenario 1 — Funny characters in the data
**Symptom:** silver/gold fails on a control char inside a value.
**Claude Code prompt:**
> "`orders_broken.csv` has control characters inside the `product` field that
> break silver. Add a failing test in `tests/` that reproduces it, then make it
> pass. Run the full suite afterwards."
**Proof:** `strip_control_chars` handles it; `pytest` stays green everywhere.

## Scenario 2 — Renamed / weird column header
**Symptom:** header is `Unit Price!!` instead of `unit_price`; downstream can't find the column.
**Prompt:**
> "The source renamed `unit_price` to `Unit Price!!`. Show me where header
> normalisation happens and prove `clean_column_names` already maps it to
> `unit_price` with a test."
**Proof:** `test_common_cleansing.py` asserts the mapping.

## Scenario 3 — Data-type drift (1 vs 1.0)
**Symptom:** a column was float, source now sends `1` not `1.00`.
**Prompt:**
> "Confirm silver normalises `unit_price` to double regardless of whether the
> source sends `1` or `1.00`, and add a test for the integer case."
**Proof:** `test_common_casting.py::test_int_is_normalised_to_double`.

## Scenario 4 — Extra column the contract never asked for
**Prompt:**
> "The source added a `notes` column. Make sure it does NOT flow into silver and
> add a test."
**Proof:** `align_to_contract` selects only contract columns; covered by
`test_orders_silver.py`.

## Scenario 5 — Dropped column + adding a new table/column
**Prompt (drop):**
> "The source dropped `status`. Silver must still produce the column as NULL, not
> fail. Verify with a test."
**Prompt (add a new column for real):**
> "We need to start ingesting a new `currency` column (string) on orders. Update
> the contract in `src/common/schema.py`, thread it through silver, add a test,
> and run the full suite."
**Proof:** contract-driven; `align_to_contract` backfills the drop.

---

## THE money demo — blast radius (do this one slowly)
This is the client's #1 fear: *"fix one pipeline, break the other 20–30."*

1. Ask Claude Code to make a **naive** shared-function change, e.g.:
   > "In `strip_control_chars`, also drop any column whose name contains `email`
   > (treat it as PII we shouldn't keep)."
2. Run `pytest`. **`test_customers_silver.py` goes RED — and only that one** —
   because customers' silver calls `strip_control_chars` and relies on the `email`
   column; orders and payments have no `email`, so they stay green. The shared
   change broke exactly one other pipeline, and the suite tells you which.
3. Say to the client: *"This is the regression net. I didn't have to know customers
   used email — its own test caught it, and the green tests told me orders and
   payments were untouched. With ~30 pipelines, each one's test suite guards the
   shared code."*

> Note: target `strip_control_chars` (not `clean_column_names`) — it's the shared
> function every silver pipeline actually calls. `clean_column_names` only runs in
> orders *bronze*, so editing it would leave the whole suite green and the demo flat.
4. Ask Claude Code to revert / narrow the change; `pytest` goes green again.

That loop — change → full suite → red catches collateral damage → narrow the fix —
is the practical answer to every question he asked about testing and not breaking
other pipelines.

---

## If he asks "how does Claude Code TEST it, not just write code?"
Answer with the actual mechanism, not "I run it manually":
- Logic lives in pure functions, so Claude Code writes + runs `pytest` locally in
  seconds — no cluster, no Azure round-trip.
- chispa asserts the exact DataFrame output, so behaviour changes are caught.
- The other pipelines' tests are the regression guard for shared code.
- CI (`azure-pipelines.yml`) re-runs the whole suite and blocks `bundle deploy`
  unless it's green — so a bad change can't reach Databricks.
- Test data is just small CSV/inline DataFrames; for a real fix you copy one ~100-row
  file (exactly what he suggested) into `data/` and point a test at it.
