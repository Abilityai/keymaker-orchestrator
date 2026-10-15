#!/usr/bin/env python3
"""Read the agency's canon from canon/. stdlib only.

  python3 scripts/canon.py refresh            pull the canon; print the commit it is at
  python3 scripts/canon.py owner <kind>       who owns a kind of work (leads, deals, pricing, ...)
  python3 scripts/canon.py owners             the whole routing map, one line each
  python3 scripts/canon.py approver <action>  who approves an action, and the limit
  python3 scripts/canon.py people             the operators
  python3 scripts/canon.py price <offer>      a price from pricing.md
  python3 scripts/canon.py flows              the flows and their gates
  python3 scripts/canon.py check              every owner in owners.yaml, with the agent named
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(ROOT, "canon")


def die(msg):
    print(f"canon: {msg}", file=sys.stderr)
    sys.exit(2)


def _yaml(path):
    """A small YAML reader for the canon's restricted grammar (scalars, lists, one level of
    list-of-maps, inline [a, b] lists, full-line and trailing comments). No PyYAML needed."""
    try:
        import yaml  # type: ignore
        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        pass
    data, stack = {}, [(-1, {}, None)]
    root = stack[0][1]
    with open(path) as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            body = re.sub(r"\s+#.*$", "", line.strip())
            while stack and indent <= stack[-1][0]:
                stack.pop()
            parent = stack[-1][1]
            if body.startswith("- "):
                item = body[2:]
                if ":" in item and not item.startswith(("'", '"', "[")):
                    k, v = item.split(":", 1)
                    d = {k.strip(): _scalar(v.strip())}
                    parent.setdefault("_list", []).append(d)
                    stack.append((indent, d, None))
                else:
                    parent.setdefault("_list", []).append(_scalar(item))
            elif ":" in body:
                k, v = body.split(":", 1)
                k, v = k.strip(), v.strip()
                if v == "":
                    d = {}
                    parent[k] = d
                    stack.append((indent, d, k))
                else:
                    parent[k] = _scalar(v)
    return _fold(root)


def _scalar(v):
    if v in ("null", "~", ""):
        return None
    if v in ("true", "false"):
        return v == "true"
    if v.startswith("[") and v.endswith("]"):
        return [_scalar(x.strip()) for x in v[1:-1].split(",") if x.strip()]
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    try:
        return int(v)
    except ValueError:
        return v


def _fold(d):
    if isinstance(d, dict):
        if list(d.keys()) == ["_list"]:
            return [_fold(x) for x in d["_list"]]
        return {k: _fold(v) for k, v in d.items()}
    return d


def load(name):
    path = os.path.join(CANON, name)
    if not os.path.exists(path):
        die(f"{name} not found - is canon/ cloned? run .trinity/setup.sh")
    return _yaml(path) if name.endswith(".yaml") else open(path).read()


def cmd_refresh():
    if not os.path.isdir(os.path.join(CANON, ".git")):
        die("canon/ is not a clone - run .trinity/setup.sh")
    r = subprocess.run(["git", "-C", CANON, "pull", "--ff-only", "--quiet"], capture_output=True, text=True)
    sha = subprocess.run(["git", "-C", CANON, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    print(f"canon at {sha}" + ("" if r.returncode == 0 else f" (pull failed: {r.stderr.strip()[:120]}; reading the local copy)"))


def cmd_owners():
    for w in load("owners.yaml")["work"]:
        print(f"{w['kind']:<24} agent={w.get('agent')!s:<20} person={w.get('person')}")
    print(f"unmatched -> {load('owners.yaml').get('unmatched')}")


def cmd_owner(kind):
    work = load("owners.yaml")["work"]
    for w in work:
        if w["kind"] == kind or kind in (w.get("description") or "").lower():
            print(json.dumps(w, indent=2)); return
    print(json.dumps({"kind": kind, "agent": None, "note": load("owners.yaml").get("unmatched")}, indent=2))


def cmd_approver(action):
    ops = load("operators.yaml")
    hits = [a for a in ops["approvals"] if action.lower() in a["action"].lower()]
    print(json.dumps(hits or {"action": action, "approver": "not in the map - ask the principal"}, indent=2))


def cmd_people():
    for p in load("operators.yaml")["people"]:
        print(f"{p['id']:<10} {p['name']:<18} {p['role']:<18} {p['email']}  operates={p.get('operates')}")


def cmd_price(offer):
    for line in load("pricing.md").splitlines():
        if line.startswith("|") and offer.lower() in line.lower():
            cells = [c.strip() for c in line.strip("|").split("|")]
            print(json.dumps({"offer": cells[0], "price": cells[2], "notes": cells[3] if len(cells) > 3 else ""}, indent=2)); return
    print(json.dumps({"offer": offer, "price": "[NEEDS-PRICE-LIST]"}, indent=2))


def cmd_flows():
    for f in load("flows.yaml")["flows"]:
        print(f"{f['id']:<28} gate={f['gate']:<16} {f['from']} -> {f['to']}")


def cmd_check():
    for w in load("owners.yaml")["work"]:
        print(json.dumps({"kind": w["kind"], "agent": w.get("agent")}))
    print("# verify each agent above with mcp__trinity__list_agents (running + permitted); report any that is not")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(0)
    c, rest = args[0], args[1:]
    {"refresh": cmd_refresh, "owners": cmd_owners, "people": cmd_people, "flows": cmd_flows, "check": cmd_check}.get(c, lambda: None)() if c in ("refresh", "owners", "people", "flows", "check") else \
        {"owner": cmd_owner, "approver": cmd_approver, "price": cmd_price}.get(c, lambda *_: print(__doc__))(" ".join(rest))
