"""
Print every market inside a group, so you can see the buckets and check
whether they cover every possible outcome.

Run from the project's top folder:
    python research/show_group.py                    # all tracked groups
    python research/show_group.py KXHEISMAN-27       # just one
"""
import json
import sys
from pathlib import Path

from make_tickers import CHOSEN

GROUPS = Path("research/groups.json")


def show(g):
    print(f"\n{'=' * 70}")
    print(f"{g['title']}   [{g['type']}]   {g['event_ticker']}")
    print(f"{'=' * 70}")
    print(f"{'subtitle':<32}{'floor':>10}{'cap':>10}{'bid':>6}{'ask':>6}")
    for m in g["markets"]:
        floor = m["floor_strike"] if m["floor_strike"] is not None else ""
        cap = m["cap_strike"] if m["cap_strike"] is not None else ""
        bid = f"{m['yes_bid']:.0f}" if m["yes_bid"] else "-"
        ask = f"{m['yes_ask']:.0f}" if m["yes_ask"] else "-"
        print(f"{(m['subtitle'] or m['ticker'])[:31]:<32}"
              f"{str(floor):>10}{str(cap):>10}{bid:>6}{ask:>6}")
    asks = [m["yes_ask"] for m in g["markets"] if m["yes_ask"]]
    bids = [m["yes_bid"] for m in g["markets"] if m["yes_bid"]]
    if g["type"] in ("range_partition", "exclusive_set"):
        print(f"\nSum of YES asks: {sum(asks):.0f}c   Sum of YES bids: {sum(bids):.0f}c")
        print("(Exhaustive sets should sum to roughly 100c.)")


def main():
    groups = {g["event_ticker"]: g for g in json.loads(GROUPS.read_text())}
    wanted = sys.argv[1:] or CHOSEN
    for event in wanted:
        g = groups.get(event)
        if g:
            show(g)
        else:
            print(f"Not found: {event}")


if __name__ == "__main__":
    main()