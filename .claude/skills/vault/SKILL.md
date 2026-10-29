---
name: vault
description: The agency's one credential store - the 1Password vault "Keymaker Agency", read with a vault-scoped service account held by this orchestrator alone, and applied to the desk that needs each secret (write its ~/.env through the platform). Never prints a secret. Use for "give finance the Stripe key", "what credentials exist", "/vault apply finance", and after any desk is recreated.
argument-hint: "list | get <item> <field> | apply <finance|sales|website|all> [--dry-run]"
allowed-tools: [Bash, Read, mcp__trinity__inject_credentials, mcp__trinity__get_credential_status]
user-invocable: true
metadata:
  version: "0.1"
  created: 2026-10-29
  author: keymaker
---

# Vault

Credentials never travel through chat. A person puts them in the 1Password vault **Keymaker
Agency**; this orchestrator holds the one secret that unlocks it (`OP_SERVICE_ACCOUNT_TOKEN`,
read-only on that vault, injected once by the principal) and hands each desk exactly the keys it
needs. The desks hold no 1Password access. The same shape Ability AI's lab runs on.

## Auth

`OP_SERVICE_ACCOUNT_TOKEN` in `~/.env`. `.trinity/setup.sh` installs the `op` CLI at every start.

```bash
set -a; [ -f ~/.env ] && . ~/.env; set +a
command -v op >/dev/null || sh .trinity/setup.sh
op vault get "Keymaker Agency" >/dev/null 2>&1 || { echo "vault not readable - token missing or wrong scope; the principal's move"; exit 1; }
```

## Items (titles are the contract)

| Item | Field | Goes to | As |
|---|---|---|---|
| `Stripe API Key` | `credential` | `finance` | `STRIPE_API_KEY` |
| `Resend API Key` | `credential` | `finance`, `sales` | `RESEND_API_KEY` |
| `Github PAT for keymaker-website-intake issues` | `credential` | `website` | `GITHUB_TOKEN_REQUESTS` |
| `Vercel Personal Access Token` | `credential` | `website` | `VERCEL_TOKEN` |
| `1Password Service Account Keymaker` | `notesPlain` | this orchestrator only | `OP_SERVICE_ACCOUNT_TOKEN` (never applied by this skill) |

## Commands

- **`list`** - `op item list --vault "Keymaker Agency" --format json | python3 -c 'import sys,json;[print(i["title"]) for i in json.load(sys.stdin)]'`, then one line per expected item: `present` / `MISSING`.
- **`get <item> <field>`** - `op read "op://Keymaker Agency/<item>/<field>" | wc -c` → print `ok <item>/<field> (N chars)`. The value is never printed, logged or put in a message.
- **`apply <desk>`** - for each row above that targets the desk: read the field with `op read` into a shell variable, build the `.env` text (`KEY=value` lines, keep nothing else), and call
  `mcp__trinity__inject_credentials(name: <desk>, files: {".env": <text>})`. Then
  `mcp__trinity__get_credential_status(<desk>)` and report `applied <desk>: KEY1, KEY2`. A missing item: `skipped <desk>: <item> MISSING` - name it, do not invent it. `--dry-run`: report what would be written, write nothing. **Never put the orchestrator's own token on a desk.**
  The injected `.env` replaces the desk's `.env`; include every key the desk needs in one call (a desk that also needs `TRINITY_*` gets those from the platform, not from this file).
- **`apply all`** - `finance`, `sales`, `website` in that order; stop at the first failure and name it.

## Gates

- Refuses to print, log or commit a secret. The token value is never in a message, a ledger row, or the canon.
- A desk's `.env` is written only through `inject_credentials`; never with a shell redirect into another agent, never by pasting into chat.
- A credential the agency creates for itself (a new key, a new login) is recorded in the vault by a person in the same turn it is minted - the service account is read-only, so the orchestrator asks the principal with `ask_operator` and names the item title it expects.
