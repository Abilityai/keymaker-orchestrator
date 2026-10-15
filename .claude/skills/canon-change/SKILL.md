---
name: canon-change
description: A request to change the canon (a price, an owner, a limit, an operator) - refuse to edit it, prepare the exact change as a proposal, and raise an approval to the person the canon names. People change the canon by pull request.
automation: autonomous
version: 1.0
---

# /canon-change <what should change>

## 1. Say the rule first
One sentence: you never write the canon; a person does, by pull request. Then do the useful part.

## 2. Find the file and the approver
```
python3 scripts/canon.py refresh
python3 scripts/canon.py approver "<the action: a new price / an owner / a limit / an operator>"
```
Prices → `canon/pricing.md`, principal. Owners → `canon/owners.yaml`, principal. Limits and people →
`canon/operators.yaml`, principal. Read the current value from the file; quote it exactly.

## 3. Write the proposal
`proposals/<YYYY-MM-DD>-<slug>.md`:
```
# Proposal: <one line>
File: canon/<file>
Before: <the exact current line(s)>
After:  <the exact proposed line(s)>
Why (as given): <the request, verbatim>
Touches: <what else reads this value - from owners.yaml reads/ and flows.yaml>
Approver: <name, role> (canon/operators.yaml)
Ask: <request_id> · expires <date>
How to apply: edit the file on a branch, open a PR to the canon repo, merge; add decisions/NNNN-<slug>.md
```

## 4. Raise the approval, once
`mcp__trinity__ask_operator(request_id="canon-<slug>-<date>", type="approval", to="primary",
title="Canon change: <one line>", question=<before/after + why + what it touches>,
options=["Approve - I will open the PR", "Decline"], proposal={...}, expires_at=<3 business days>)`.
Record it in `ledger/open_loops.md`.

## 5. Tell the person
Where the proposal is, who must approve it, when the ask expires, and that nothing in the agency
changes until the PR is merged - desks read the canon, not proposals.

## Never
Edit anything under `canon/`. Commit to the canon repo. Tell a desk the new value.
