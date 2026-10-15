---
name: route
description: The loop for one request - read the canon, hand it to the one owner as a one-line playbook call, keep the receipt, check the result against evidence, close or escalate. Use for anything that is work for a desk.
automation: autonomous
version: 1.0
---

# /route <the request>

## 1. Read the canon (every time)

```
python3 scripts/canon.py refresh
python3 scripts/canon.py owners
```
Decide which **kind of work** the request is (leads, deals, pricing, client-projects, call-notes,
lessons-and-judgment). If it mentions a price, also `python3 scripts/canon.py price <offer>` and
`python3 scripts/canon.py approver <action>`. One request can touch two kinds (a new lead is
`deals` for Sales **and** `lessons-and-judgment` for the brain). If no kind matches: do not guess
an owner - one question to the principal (`/escalate`), then stop.

## 2. Check the owner is idle

`mcp__trinity__list_recent_executions(<owner>, status="running")`. If something is running, append
a `queued` row to `ledger/receipts.jsonl`, write the loop in `ledger/open_loops.md`, set a reminder
(`mcp__trinity__set_reminder`, 10 minutes, naming the request) and end the turn.

## 3. Hand it off - one line, one owner

Call the owner's **named playbook**, one line, no preamble, with
`mcp__trinity__chat_with_agent(agent_name=<owner>, message="/<playbook> <args>", parallel=true, async=true)`.
Examples:
- a new lead → `sales-agent`: `/deal Copperleaf Veterinary Group --open --source inbound --note "40 people, appointment reminders and intake"`
  and in the same turn → `cornelius`: `/advise a 40-person veterinary group asks for help automating reminders and intake; what have we learned about clinics and intake work before the discovery call?`
  If Sales answers that the deal already exists, say so with its stage - never open it twice.
- "how is Cedar Point" → `delivery-agent`: `/client-status Cedar Point Clinics`
- "write the weekly report" → `marketing-agent`: `/weekly-report`
- "summarise yesterday's call" → `meeting-notes-bot`: `/process-inbox`

Playbooks the owner does not have are not called; read its catalog with `mcp__trinity__get_agent_skills`
if unsure. Never describe the work in prose. Never send the same call twice.

## 4. Record the receipt before anything else

Append to `ledger/receipts.jsonl`:
`{"ts": "<ISO>", "request": "<short>", "kind": "<kind>", "owner": "<agent>", "execution_id": "<id>", "status": "sent", "evidence": null}`
A call that errored without an execution id: look for your exact message in
`mcp__trinity__list_recent_executions(<owner>)` first; one match is your receipt. On `agent_busy`,
nothing ran: queue it (step 2). Never re-send on a timeout.

## 5. Report now, verify later

Tell the person what went where, with each execution id, and what you are waiting on. If the
work is long, the desk's result reports back into this chat when it finishes; add the open loop to
`ledger/open_loops.md` and end the turn. If the result is already in: open the evidence it names
(`/deal --review` output, the client record, the file) before calling it done. Update the row to
`verified` (with the evidence) or `claimed` (could not open it - say so).

## 6. Close or escalate

Done with evidence: say so, with the receipt. Needs a person (a price above a limit, a client
at risk, anything irreversible): `/escalate`, once, then end the turn.

## Never
Do the work yourself. Write a desk's file. Invent an owner. Report "done" on a claim. Move a stage,
change a price, send anything.
