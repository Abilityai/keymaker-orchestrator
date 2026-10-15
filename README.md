# Keymaker Orchestrator

The one agent you talk to in **Keymaker**, a fictional automation agency built in public during
the [Agent-Native Agency workshop](https://www.ability.ai/trinity/workshops/agent-native-agency-workshop).
It holds the map, not the work: it reads the agency's **canon**, hands each request to the one
desk that owns it, keeps a receipt for every hand-off, checks "done" against evidence, and brings
decisions to a person - once, with options and a deadline.

## Install

1. On a Trinity instance running the 1.0 release candidate or later: **Create Agent → from GitHub → `Abilityai/keymaker-orchestrator`**
   (or Library → Agents → Keymaker Orchestrator). Name it `orchestrator`. No credentials.
2. On its **Access** tab, grant it the desks it may call: `sales-agent`, `delivery-agent`,
   `marketing-agent`, `meeting-notes-bot`, `cornelius`. Only a person can grant an edge.
3. Tag each desk `reports-to-orchestrator`; the Network view draws the org chart.
4. Ask it: *"Who do you route to, and how do you decide?"* It reads `canon/domains.yaml` back.

Or rebuild the whole agency from one file on a **fresh** instance: `deploy/system.yaml` (in this repo) in
[`Abilityai/keymaker-canon`](https://github.com/Abilityai/keymaker-canon) with `deploy_system`
(it creates `keymaker-*` agents; on an instance that already runs the desks, use the Access tab
instead or you get a second set).

## The canon

The orchestrator reads what the agency decided from a clone of
[`Abilityai/keymaker-canon`](https://github.com/Abilityai/keymaker-canon) at `canon/`
(`.trinity/setup.sh` clones it on every container start; `scripts/canon.py refresh` pulls it).
Make your own from that template and change `CANON_REPO` in `.trinity/setup.sh`.

| File | What the orchestrator takes from it |
|---|---|
| `domains.yaml` | which agent owns each kind of work; the role behind it |
| `roles/` + `domains/org-context/ORGANISATION.md` | the seats, and who fills them today |
| `domains/approvals/approvals.yaml` | who may decide what alone, up to which limit; who decides above |
| `domains/pricing/pricing.md` | the price, when a request mentions one |
| `protocols/information-routing.md` | the five flows and the gate on each |

It never writes the canon. `/canon-change` prepares a proposal and raises an approval.

## Playbooks

- `/route <request>` - the loop: read the canon, hand off to the one owner, keep the receipt
- `/status [--brief]` - ask every desk in parallel; one summary; name who did not answer
- `/escalate <decision>` - one ask to the named person, with options and an expiry
- `/canon-change <what>` - a proposal file and an approval; never a commit
- `/map [--check]` - the routing map read back; with `--check`, every owner verified live
- `/open-loops` - receipts verified, expired asks chased (runs every two hours)

## Schedules (all enabled)

| Schedule | When | Does |
|---|---|---|
| `[morning-brief]` | weekdays 07:30 ET | `/status --brief` - one line per desk, silence named |
| `[open-loops]` | every 2 h | `/open-loops` |
| `[canon-watch]` | daily 06:00 ET | `/map --check` - pulls the canon, reports drift |

Schedules fire only while the agent's autonomy toggle is on.

## Licence

Apache 2.0. Fictional company; no real people, clients or money.
