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
    """Return (superset, subset) pairs of neighbouring rungs in a ladder.

    Which market contains which depends on how the ladder is ordered:
      ladder_above  "above 95k" contains "above 100k"   -> lower strike wins
      ladder_below  "below 100k" contains "below 95k"   -> higher strike wins
      ladder_date   "by November" contains "by October" -> later date wins
    Getting this backwards turns a perfectly normal price ordering into a
    fake arbitrage, so each case is handled explicitly.
    """
    kind = group["type"]

    if kind == "ladder_date":
        rungs = [m for m in group["markets"] if m.get("close_time")]
        rungs.sort(key=lambda m: m["close_time"])          # earliest first
        # the LATER market is the superset, so pair (later, earlier)
        return [(late, early) for early, late in zip(rungs, rungs[1:])]

    if kind == "ladder_above":
        rungs = [m for m in group["markets"] if m["floor_strike"] is not None]
        rungs.sort(key=lambda m: m["floor_strike"])
        return list(zip(rungs, rungs[1:]))

    rungs = [m for m in group["markets"] if m["cap_strike"] is not None]
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
        if g["type"] in ("ladder_above", "ladder_below", "ladder_date"):
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
