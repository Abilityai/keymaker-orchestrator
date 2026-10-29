---
name: vault
description: The agency's one credential store - the 1Password vault "Keymaker Agency", read with a vault-scoped service account held by this orchestrator alone. Lists what exists, tells a person exactly which item goes on which desk's Credentials page, and verifies it landed. Never prints a secret, never writes one - the platform makes a credential a human-only act. Use for "what keys does finance need", "did the Stripe key land", "/vault brief finance", after any desk is created or recreated.
argument-hint: "list | get <item> <field> | brief <finance|sales|website|prospector|all> | check <desk|all>"
allowed-tools: [Bash, Read, mcp__trinity__get_credential_status]
user-invocable: true
metadata:
  version: "0.2"
  created: 2026-10-29
  author: keymaker
  changelog:
    - "0.2 (2026-10-29): `apply` removed - Trinity 1.0 answers 403 'This operation is human-only; agent-scoped keys cannot perform it' to inject_credentials from any agent, for any target. The person applies, this skill briefs and verifies."
---

# Vault

Credentials never travel through chat. A person puts them in the 1Password vault **Keymaker
Agency**; this orchestrator holds the one secret that unlocks it (`OP_SERVICE_ACCOUNT_TOKEN`,
read-only on that vault, pasted once by the principal) and knows which desk needs which key. **It
cannot put a key on a desk**: on Trinity 1.0 writing another agent's credentials is a human-only
operation (`inject_credentials` -> 403 from an agent key, verified 2026-10-29). So the division of
labour is fixed by the platform: the vault remembers, this orchestrator briefs and verifies, a
person applies. The desks hold no 1Password access.

## Auth

`OP_SERVICE_ACCOUNT_TOKEN` in `~/.env`. `.trinity/setup.sh` installs the `op` CLI at every start.

```bash
set -a; [ -f ~/.env ] && . ~/.env; set +a
export PATH="$HOME/.local/bin:$PATH" OP_CACHE=false   # OP_CACHE=false: no `op daemon` - the platform's orphan sweeper kills it and op stalls
command -v op >/dev/null || bash .trinity/setup.sh   # bash, not sh: the hook uses BASH_SOURCE
timeout 30 op vault get "Keymaker Agency" >/dev/null 2>&1 || { echo "vault not readable - token missing or wrong scope; the principal's move"; exit 1; }
```

## Items (titles are the contract - exactly as the vault spells them)

| Item | Field | Goes to | As |
|---|---|---|---|
| `Stripe API Key` | `credential` | `finance` | `STRIPE_API_KEY` |
| `Resend API Key Keymaker` | `credential` | `finance`, `sales` | `RESEND_API_KEY` |
| `Github PAT for keymaker-website-intake issues ` (trailing space in the title - quote it) | `credential` | `website` | `GITHUB_TOKEN_REQUESTS` |
| `Vercel Personal Access Token` | `credential` | `website` | `VERCEL_TOKEN` |
| `1Password Service Account Keymaker` | `notesPlain` | this orchestrator only | `OP_SERVICE_ACCOUNT_TOKEN` (never briefed for a desk) |

`prospector` needs nothing - say so when asked.

## Commands

- **`list`** - `timeout 30 op item list --vault "Keymaker Agency" --format json | python3 -c 'import sys,json;[print(i["title"]) for i in json.load(sys.stdin)]'`, then one line per expected item: `present` / `MISSING`.
- **`get <item> <field>`** - `timeout 30 op read "op://Keymaker Agency/<item>/<field>" | wc -c` -> print `ok <item>/<field>`. The value is never printed, logged or put in a message - not even its length beyond "ok".
- **`brief <desk>`** - for each row above that targets the desk, first `get` it (so the brief never names an item that is not there), then print the instruction a person follows, one line per key:
  `<desk> -> Settings -> Credentials: STRIPE_API_KEY  <-  1Password / Keymaker Agency / "Stripe API Key" / credential`
  A missing item: `MISSING in the vault: <item> - add it there first; nothing to paste yet`. End with `then: /vault check <desk>`.
  **This is the whole of "applying" a key on this platform: a person reads the brief, copies from 1Password, pastes on the desk's Credentials page.** No shortcut exists and none is to be built.
- **`check <desk>`** - `mcp__trinity__get_credential_status(name=<desk>)`: `.env` present and `credential_count` >= the number of keys the desk expects -> `ok <desk>: N credential(s) on the desk`; otherwise `missing <desk>: expected KEY1, KEY2 - run /vault brief <desk>`. Names only; the platform never returns values and neither do you.
- **`brief all` / `check all`** - `finance`, `sales`, `website` in that order, one block each.

## Gates

- `inject_credentials` is **not** in this skill's tools and is never called from this agent for any target: the platform answers 403 (human-only). A request to "just inject it" is answered with the brief and the reason, never with a workaround (no shell into another container, no value in a chat message, no file in a shared folder).
- Every `op` call runs with `OP_CACHE=false` and `timeout 30`; an `op` that hangs is the daemon being swept, not a wrong token.
- Refuses to print, log or commit a secret. The token value is never in a message, a ledger row, or the canon.
- A credential the agency creates for itself (a new key, a new login) is recorded in the vault by a person in the same turn it is minted - the service account is read-only, so the orchestrator asks the principal with `ask_operator` and names the item title it expects.
- After `/hire` creates or a person recreates a desk, `check <desk>` is part of the orchestrator's receipt: a desk that reads as `missing` is reported in the morning brief until it reads `ok`.
