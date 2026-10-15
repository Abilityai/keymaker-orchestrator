---
name: escalate
description: Bring one decision to the person the canon names - with the options the canon allows, the consequence of waiting, and an expiry. Then end the turn. Never decide; never ask twice.
automation: autonomous
version: 1.0
---

# /escalate <the decision> [--now]

## 1. Who decides, and what are the options
```
python3 scripts/canon.py refresh
python3 scripts/canon.py approver "<the action>"
python3 scripts/canon.py roles
```
`decides_alone` + `limit` say which **role** may decide alone; `above_limit` names the role past it.
A role, never a person: `python3 scripts/canon.py roles` shows who fills each seat today
(`domains/org-context/ORGANISATION.md`); the `principal` is the instance owner, so `to: primary`.
`expires_after_hours` is the ask's lifetime. If the action is not in the map, the approver is the principal and the ask
says "not in the approval map - add it?".

If the decision needs judgment (a discount, a scope change, a risk), ask the brain first in the
same turn: `mcp__trinity__chat_with_agent("cornelius", "/advise <situation and question>", parallel=true)`,
and put its answer, labelled, in the ask's context.

## 2. One ask, atomic
`mcp__trinity__ask_operator` with:
- `request_id`: `<kind>-<slug>-<YYYY-MM-DD>-<first 8 chars of your execution id>` (a retry in the
  same run replays; a second decision on the same slug the same day is a new ask, never swallowed)
- `type`: `approval` when there are options; `question` when there are not
- `to`: `primary` (the principal) unless the canon names another role that exists on the instance
- `title`: one line, under 100 characters
- `question`: the situation, the limit it crosses, what the brain said (labelled), what waiting costs
- `options`: at most 4, each the choice only (e.g. `Hold the list price`, `10% as an invoice credit`,
  `Pilot first, credited`) - never "something else", the platform adds it
- `proposal`: what you will route if each option is chosen (the one-line playbook call per option)
- `expires_at`: now + `expires_after_hours` from the approval entry (default 72 h), ISO with timezone
- `priority`: `high` for the `escalate_now` classes in `domains/approvals/approvals.yaml` (`--now`), else `medium`

## 3. Record and stop
Append the ask to `ledger/open_loops.md`: request id, who, expires, what each option routes.
Tell the person: who was asked, where it landed (their Inbox / the Operating Room), when it
expires, and that nothing moves until they answer. **End the turn.** Do not poll. The answer
arrives as a wake or is read by `/open-loops` with `mcp__trinity__get_my_ask`.

## Never
Decide. Ask the same thing twice (an expired ask is re-raised only with new information, with
`supersedes_expired`). Ask "someone". Ask without an expiry. Bury two decisions in one ask.
