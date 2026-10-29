---
name: hire
description: Add a desk to the agency the standard way - canon first, then the agent from the Library or a repo, then one checklist to the principal for the things only a person can do (edges, autonomy, keys, who a schedule delivers to). Use for "add the finance desk", "hire a prospecting desk", "/hire finance", "/hire github:Owner/repo --as name", "we need an agent that ...".
argument-hint: "<finance|sales|delivery|marketing|prospector|website|github:Owner/repo> [--as <name>] | --brief \"<one paragraph>\" [--as <name>]"
allowed-tools: [Bash, Read, Write, mcp__trinity__list_agents, mcp__trinity__list_templates, mcp__trinity__get_agent, mcp__trinity__get_agent_info, mcp__trinity__create_agent, mcp__trinity__set_agent_tags, mcp__trinity__start_agent, mcp__trinity__get_agent_compatibility_report, mcp__trinity__list_agent_schedules, mcp__trinity__get_credential_status, mcp__trinity__chat_with_agent, mcp__trinity__list_recent_executions, mcp__trinity__ask_operator]
user-invocable: true
metadata:
  version: "0.1"
  created: 2026-10-29
  author: keymaker
---

# Hire

A desk is hired the way a person is: the role exists before the hire, the hire gets a seat and a
badge, and the things only the principal can hand over are handed over in one list. You can create
the agent; you cannot grant an edge, turn autonomy on, or put a key on it - the platform reserves
those for a person, and that is the design, not a gap.

## 0. The canon comes first

```
python3 scripts/canon.py refresh
python3 scripts/canon.py owners
```

The desk you are hiring must already be the `owner` of a domain in `canon/domains.yaml`, with a
`role` that exists in `canon/roles/` and a decision file that opened it. **If it is not: stop and
run `/canon-change`** - propose the domain (id, description, owner = the agent name, role,
consumers, playbooks, hands_to), the approvals row for the one irreversible thing the desk touches,
the ORGANISATION.md line, and the decision file; raise the ask to the principal; end the turn. An
agent nobody's map points at is a desk nobody routes to, so you never create one. When the canon
PR is merged and `canon.py owners` shows the desk, `/hire` runs.

## 1. Resolve the source

| You were given | Source |
|---|---|
| a desk name (`finance`, `sales`, `delivery`, `marketing`, `prospector`, `website`) | the Library card `github:Abilityai/keymaker-<desk>` (`website` is `Keymaker-Agency/keymaker-website`); confirm it is in `mcp__trinity__list_templates` |
| `github:Owner/repo` | that repo, as given - the agency's own agents (a migrated notes bot, a desk built from the wizard) come in this way |
| `--brief "<paragraph>"` | the **Agent Builder**: `agent-builder` must exist on the instance (if not, hire it first - `/hire github:Abilityai/agent-builder --as agent-builder` - and stop; the principal grants `orchestrator -> agent-builder` before you can use it). Then one line: `mcp__trinity__chat_with_agent(agent_name="agent-builder", message="/build-agent <brief> --no-deploy", parallel=true)` and report its repo back. The brief still goes through step 0 first: the builder scaffolds the agent, the canon says why it exists. |

The agent's name is `--as <name>` or, for a desk, the desk name. `mcp__trinity__list_agents`: if
the name exists already, stop - report its status and `/vault check`, create nothing.

## 2. Create, badge, start

```
mcp__trinity__create_agent(name=<name>, template=<source>)
mcp__trinity__set_agent_tags(name=<name>, tags=["keymaker", "reports-to-orchestrator"])
mcp__trinity__start_agent(name=<name>)
```

`create_agent` returns the agent stopped; `start_agent` boots it (the start hook clones the canon).
Poll `mcp__trinity__get_agent(<name>)` until `status: running` (give it three minutes), then
`mcp__trinity__get_agent_compatibility_report(<name>)` - report the HARD count; a HARD finding is
in the receipt, not fixed by you. `mcp__trinity__list_agent_schedules(<name>)` - the template's
schedules materialise at creation; list them with their delivery (none yet - a person sets it).

## 3. The receipt, and the one list for the principal

Append to `ledger/receipts.jsonl`:
`{"ts": "<ISO>", "request": "hire <name>", "kind": "hire", "owner": "<name>", "execution_id": "<this execution>", "status": "created", "evidence": "<template> · compat HARD=<n>"}`

Then build the checklist from the canon and the template - never from memory:

- **Edges** (Access tab; approvals.yaml: only the principal grants one): `orchestrator -> <name>`;
  `<name> -> <owner>` for every domain the desk `consumes` in `domains.yaml` whose owner is an agent;
  `<name> -> cornelius` if its role reads `lessons-and-judgment`; and the reverse edge for any desk
  that `hands_to` it.
- **Keys**: `mcp__trinity__get_agent_info(<name>)` -> `credential_requirements`; for each, the
  `/vault brief` line (item, field, which page). A desk with none: say "no key to paste".
- **Autonomy**: ON, on the agent's page - until then every schedule is held.
- **Delivery**: for each materialised schedule, who should receive it (`domains.yaml` role ->
  ORGANISATION.md person), set by the person on the Schedules tab.
- **Owner**: on open source the approvals of a desk land in its owner's Inbox; the owner is whoever
  created it - you. **Say so**: the principal re-owns it or shares it with the seat-holder, or the
  desk's asks will come to the orchestrator's owner.

Raise it once: `mcp__trinity__ask_operator(type="approval", request_id="hire-<name>-<date>",
question="<name> is created and running. Five things only you can do:", proposal=<the checklist>,
options=["done", "not now"], expires_at=<72h>)`. Then **end the turn**. `/open-loops` reads the
answer; `/map --check` and `/vault check <name>` verify the edges and keys landed; the morning
brief names the desk until they do.

## Never

Grant an edge (you cannot; a person can, on the Access tab). Inject a credential (403, human-only;
`/vault brief` instead). Create an agent the canon does not name as an owner. Create a second agent
for a domain that has one. Delete or stop an agent (a person's move). Use `deploy_system` for a
single desk. Describe the hire as finished before the ask is answered - "created" is the word until
then.
