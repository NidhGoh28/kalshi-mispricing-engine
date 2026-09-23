"""
Turn the groups you chose into research/tickers.txt (what Om's collector reads)
and print a starter outline for research/relationships.md.

Edit the CHOSEN list below to change which groups you track.

Run from the project's top folder (after find_groups.py):
    python research/make_tickers.py
"""
import json
from pathlib import Path

GROUPS = Path("research/groups.json")
OUT = Path("research/tickers.txt")

# Event tickers we are tracking. Edit this list.
CHOSEN = [
    "KXBTCY-27JAN0100",          # range partition: Bitcoin price end of 2026
    "KXINXY-26DEC31H1600",       # range partition: S&P close end of 2026
    "KXCPIYOY-26DEC",            # ladder above: CPI YoY December 2026
    "KXRHOUSEWON-26NOV03",       # ladder above: Republican House seats
    "KXINXMINY-01JAN2027",       # ladder below: how low the S&P gets
    "KXHEISMAN-27",              # exclusive set: Heisman winner
    "KXNUMREDISTRICTING-26NOV03",  # range partition: states redistricting
]

RULES = {
    "ladder_above": "P must not increase as the threshold increases",
    "ladder_below": "P must not increase as the threshold decreases",
    "range_partition": "exhaustive: YES prices sum to ~100 (both checks apply)",
    "exclusive_set": "exclusive but maybe not exhaustive (sell-side check only)",
}


def main():
    groups = {g["event_ticker"]: g for g in json.loads(GROUPS.read_text())}
    tickers, missing = [], []

    for event in CHOSEN:
        g = groups.get(event)
        if not g:
            missing.append(event)
            continue
        tickers.append(f"# {g['type']}: {g['title']}")
        for m in g["markets"]:
            tickers.append(m["ticker"])
        tickers.append("")

        # Starter text for relationships.md
        closes = {m["close_time"][:10] for m in g["markets"] if m["close_time"]}
        print(f"## {g['title']}")
        print(f"Event: {event}")
        print(f"Type: {g['type']}")
        print(f"Rule: {RULES.get(g['type'], '?')}")
        print(f"Markets: {len(g['markets'])}   Settles: {sorted(closes)[0]}")
        print("Notes: \n")

    OUT.write_text("\n".join(tickers))
    real = [t for t in tickers if t and not t.startswith("#")]
    print(f"Wrote {len(real)} tickers from {len(CHOSEN) - len(missing)} groups to {OUT}")
    if missing:
        print(f"NOT FOUND (rerun find_groups.py, or check spelling): {missing}")


if __name__ == "__main__":
    main()
