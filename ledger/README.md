# Ledger

The orchestrator's own memory of what is in flight. The only files it writes besides `proposals/`.

- `receipts.jsonl` - one row per hand-off: `{"ts","request","kind","owner","execution_id","status","evidence"}`.
  `status` is `sent | running | claimed | verified | failed | queued`. A row exists the moment a
  receipt comes back, before anything else happens.
- `open_loops.md` - what waits on whom, until when: unverified hand-offs, pending asks with
  their request ids and expiries, requests queued because the owner was busy.

A hand-off without a row here did not happen.
