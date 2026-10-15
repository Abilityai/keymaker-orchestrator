---
name: map
description: Read the routing map back - who you route to and how you decide - and with --check verify every owner is a running agent you are permitted to call, and report what changed in the canon since the last pull.
automation: autonomous
version: 1.0
---

# /map [--check]

## 1. Pull and read
```
python3 scripts/canon.py refresh
python3 scripts/canon.py owners
python3 scripts/canon.py flows
python3 scripts/canon.py approver ""      # the whole approval map
```

## 2. Say it back, plainly
One line per kind of work: *kind → agent (person)*. Then the gates you will not pass on your own,
from the approval map: sending to a client, a price off the list or above a rep's limit, a change
to the canon, a client's state, publishing, graduating a note, granting an edge. Then the five
flows with their gates, one line each. Cite the canon commit you read.

## 3. --check (the daily canon-watch)
- `git -C canon log --oneline <last-seen>..HEAD` - say what changed since the last check (store the
  SHA in `ledger/open_loops.md` under "canon seen"); "no change" when there is none.
- `mcp__trinity__list_agents` - for every `agent:` in `domains.yaml`: running? in your permitted
  list? Report each owner that is missing, stopped, or not permitted **by name**. Do not route
  around it; an owner you cannot reach is a gap for a person to close (the principal grants edges
  on the Access tab).
- Report asks still pending past their expiry and receipts older than a day with no verified
  result (from `/open-loops`).

## Never
Edit the map. Guess an owner for a kind of work the map does not name.
