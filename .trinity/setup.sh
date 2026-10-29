#!/bin/bash
# Trinity persistent setup - runs on every container start (base image convention).
# Clones or refreshes the agency's canon into canon/. Idempotent, fast, never blocks startup.
# To use your own canon: change CANON_REPO (a public repo needs no token; for a private one the
# platform's GitHub token is passed on the command line and never written to disk).
AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CANON_REPO="${CANON_REPO:-https://github.com/Abilityai/keymaker-canon.git}"
CANON_DIR="$AGENT_DIR/canon"

if [ -d "$CANON_DIR/.git" ]; then
  git -C "$CANON_DIR" pull --ff-only --quiet 2>/dev/null \
    && echo "canon: refreshed at $(git -C "$CANON_DIR" rev-parse --short HEAD)" \
    || echo "canon: pull failed - reading the copy at $(git -C "$CANON_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown)"
else
  if git clone --depth 1 --quiet "$CANON_REPO" "$CANON_DIR" 2>/dev/null; then
    echo "canon: cloned at $(git -C "$CANON_DIR" rev-parse --short HEAD)"
  else
    echo "canon: CLONE FAILED from $CANON_REPO - the orchestrator has no map and must say so"
  fi
fi
mkdir -p "$AGENT_DIR/ledger" "$AGENT_DIR/proposals"
touch "$AGENT_DIR/ledger/receipts.jsonl"

# 1Password CLI - the orchestrator is the agency's credential broker (/vault). The desks never get it.
if ! command -v op >/dev/null 2>&1 && [ ! -x "$HOME/.local/bin/op" ]; then
  mkdir -p "$HOME/.local/bin" && curl -sSfo /tmp/op.zip "https://cache.agilebits.com/dist/1P/op2/pkg/v2.32.1/op_linux_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')_v2.32.1.zip" \
    && unzip -oq /tmp/op.zip -d "$HOME/.local/bin" op && rm -f /tmp/op.zip && echo "op: installed $($HOME/.local/bin/op --version)" \
    || echo "op: install FAILED - /vault cannot run until it is present"
fi
export PATH="$HOME/.local/bin:$PATH"
# op spawns a cache daemon on every call; Trinity's orphan sweeper SIGKILLs it and op stalls. No daemon:
export OP_CACHE=false
