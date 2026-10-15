---
name: open-loops
description: The two-hourly check - every receipt in the ledger verified against evidence, every pending ask read, expired asks noted, queued requests re-tried once the owner is idle. Keeps the ledger true; routes nothing new.
automation: autonomous
version: 1.0
---

# /open-loops

## 1. Receipts
For every row in `ledger/receipts.jsonl` with `status` in `sent | running | claimed`:
`mcp__trinity__get_execution_result(<owner>, <execution_id>)`.
- `running` / `queued`: leave it; it is not stuck.
- `success`: open the evidence the result names (the deal file, the client record, the note). Found →
  `verified` with the evidence path. Not found or cannot open → `claimed`, and say so in the report.
- `failed` / `cancelled`: `failed`; re-send the identical message **once** only if the result says it
  never started; otherwise it needs a person.

## 2. Asks
For every ask in `ledger/open_loops.md`: `mcp__trinity__get_my_ask(<request_id>)`.
- answered → route what the chosen option said (`/route`), close the loop.
- expired → mark it "denied by timeout"; do not re-ask without new information.
- pending and expiring within 24 h → list it under "Decide today" for the morning brief.

## 3. Queued requests
For every `queued` row: `mcp__trinity__list_recent_executions(<owner>, status="running")`; if idle,
hand it off now (`/route` step 3) and update the row.

## 4. Report and record
A short report: verified N · claimed N (named) · failed N (named) · asks pending N (with expiries) ·
expired N · re-sent N. Record `open_loops` and `asks_pending` with `mcp__trinity__record_metrics`.
Rewrite `ledger/open_loops.md` so it holds only what is still open. Nothing new is routed here
unless a queued request's owner became idle.
