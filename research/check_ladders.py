"""
Check live Kalshi prices for logical contradictions inside related groups.

Two checks:
  1. Ladders: "above $100k" can never be more likely than "above $95k".
  2. Exclusive sets: exactly one outcome pays $1, so YES prices must
     add up to about 100 cents.

Run from the project's top folder:
    python research/check_ladders.py
"""
from find_groups import fetch_open_events, build_groups


def superset_subset_pairs(group):
    """Return (superset, subset) pairs of neighbouring rungs in a ladder."""
    rungs = [m for m in group["markets"] if m["floor_strike"] is not None
             or m["cap_strike"] is not None]
    if group["type"] == "ladder_above":
        # "above 95k" contains "above 100k": lower strike is the superset
        rungs.sort(key=lambda m: m["floor_strike"])
        return list(zip(rungs, rungs[1:]))
    # "below 95k" is inside "below 100k": higher strike is the superset
    rungs.sort(key=lambda m: m["cap_strike"], reverse=True)
    return list(zip(rungs, rungs[1:]))


def check_ladder(group):
    findings = []
    for sup, sub in superset_subset_pairs(group):
        ask_sup, bid_sub = sup["yes_ask"], sub["yes_bid"]
        # Tradable: buy YES on the superset, sell YES on the subset
        if ask_sup and bid_sub and bid_sub > ask_sup:
            findings.append(
                f"  ARBITRAGE  buy YES {sup['ticker']} at {ask_sup:.0f}c, "
                f"sell YES {sub['ticker']} at {bid_sub:.0f}c "
                f"-> locked-in edge {bid_sub - ask_sup:.0f}c before fees")
    return findings


def check_exclusive(group):
    asks = [m["yes_ask"] for m in group["markets"]]
    bids = [m["yes_bid"] for m in group["markets"]]
    findings = []
    # Buying every outcome only guarantees $1 if the list covers EVERY
    # possible result. Range partitions do (below / between / above);
    # "who will be next X" lists usually don't, since someone unlisted can win.
    exhaustive = group["type"] == "range_partition"
    if exhaustive and all(a and a < 100 for a in asks):
        total_ask = sum(asks)
        if total_ask < 100:
            findings.append(
                f"  ARBITRAGE  buy YES on every outcome for {total_ask:.0f}c "
                f"-> collect 100c, edge {100 - total_ask:.0f}c before fees")
    # Selling every outcome is safe even if the list isn't exhaustive:
    # at most one listed outcome can pay, so you never pay out more than 100.
    if all(b is not None for b in bids):
        total_bid = sum(bids)
        if total_bid > 100:
            findings.append(
                f"  ARBITRAGE  sell YES on every outcome for {total_bid:.0f}c "
                f"-> pay out 100c, edge {total_bid - 100:.0f}c before fees")
    return findings


def main():
    groups = build_groups(fetch_open_events())
    print(f"Checking {len(groups)} groups\n")
    found = 0
    for g in groups:
        if g["type"] in ("ladder_above", "ladder_below"):
            results = check_ladder(g)
        else:
            results = check_exclusive(g)
        if results:
            found += len(results)
            print(f"{g['event_ticker']}  ({g['title']})")
            print("\n".join(results))
    print(f"\n{found} violations found.")
    if found == 0:
        print("That's normal: market makers close these gaps fast. "
              "The collector's history will show how often they appear.")


if __name__ == "__main__":
    main()
