---
name: status
description: Ask every desk what needs a person today, in parallel, and return one summary - with a line for every desk that did not answer. The morning brief is this with --brief.
automation: autonomous
version: 1.0
---

# /status [--brief]

## 1. Read the map
`python3 scripts/canon.py refresh && python3 scripts/canon.py owners` - the desks to ask are the
agents in `owners.yaml` with a playbook that reports (sales-agent, delivery-agent, marketing-agent,
meeting-notes-bot). The brain is asked only if a desk's answer needs judgment.

## 2. Ask all of them in one turn, in parallel
Issue the four calls **in the same message** so they run together, each
`mcp__trinity__chat_with_agent(agent_name=<desk>, message=<one line>, parallel=true)`:
- `sales-agent`: `/deal --review`
- `delivery-agent`: `/clients --stalled`
- `marketing-agent`: `/weekly-report`
- `meeting-notes-bot`: `/process-inbox`

Record each receipt in `ledger/receipts.jsonl` (`kind: status`). A call that returns a receipt
instead of an answer (`accepted`, `queued`, timed out) is **running, not failed**: note the
execution id and read it with `mcp__trinity__get_execution_result` before you write the summary;
if it is still running when you must answer, say "running, not yet answered".

## 3. One summary, same shape every time
```
What needs a person today - <date>
Sales      <one line: what needs the deal owner / the principal, or "nothing">   [exec <id>]
Delivery   <one line>                                                            [exec <id>]
Marketing  <one line>                                                            [exec <id>]
Notes      <one line>                                                            [exec <id>]
Did not answer: <desk, reason - unreachable / running / not permitted> or "none"
Waiting on a person: <open asks from ledger/open_loops.md, with expiries>
```
A desk you could not reach, were not permitted to call, or that is still running is **named on
the "Did not answer" line with the reason**. Its status is unknown, not fine. Never let an empty
answer read as "nothing to report".

## 4. --brief (the scheduled morning run)
Same summary, then: pull anything in `ledger/open_loops.md` that expires today to the top as
"Decide today". Record `desks_silent_last_brief` with `mcp__trinity__record_metrics`. Raise
nothing new unless a desk reported money above a limit, a client at risk, or something
irreversible - then `/escalate` for that one item.
