"""
Find groups of related Kalshi markets.

Kalshi organizes everything as Series -> Event -> Market.
Markets inside the same event are usually related: either a ladder
("above $90k", "above $95k", ...) or a set of mutually exclusive outcomes
("between 70-75F", "between 75-80F", ...). This script groups them for you.

Run from the project's top folder:
    python research/find_groups.py
"""
import json
from pathlib import Path

import requests

BASE = "https://api.elections.kalshi.com/trade-api/v2"
OUT = Path("research/groups.json")


def fetch_open_events(max_pages=30):
    """Download open events, each with its markets nested inside it."""
    events, cursor = [], None
    for _ in range(max_pages):
        params = {"status": "open", "with_nested_markets": "true", "limit": 200}
        if cursor:
            params["cursor"] = cursor
        r = requests.get(f"{BASE}/events", params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        events.extend(data.get("events", []))
        print(f"  fetched {len(events)} events so far...")
        cursor = data.get("cursor")
        if not cursor:  # no more pages
            break
    return events


def cents(market, field):
    """Read a price in cents, whether Kalshi sends cents or dollars."""
    value = market.get(field)
    if value is not None:
        return float(value)
    dollars = market.get(f"{field}_dollars")
    if dollars not in (None, ""):
        return float(dollars) * 100
    return None


def distinct_strikes(markets, field):
    """True if the markets really are ordered by a number.

    Some ladders share one strike and differ only by DATE, e.g. "S&P above
    8000 by Oct 1 / by Nov 1". Those must be ordered by date instead, so we
    detect them here and classify them as ladder_date.
    """
    values = {m.get(field) for m in markets if m.get(field) is not None}
    return len(values) == len(markets) and len(values) > 1


def classify(event, markets):
    """Decide what kind of logical relationship the markets share."""
    types = {m.get("strike_type") for m in markets}
    if types and types <= {"greater", "greater_or_equal"}:
        return "ladder_above" if distinct_strikes(markets, "floor_strike") else "ladder_date"
    if types and types <= {"less", "less_or_equal"}:
        return "ladder_below" if distinct_strikes(markets, "cap_strike") else "ladder_date"
    if "between" in types:
        return "range_partition"
    if event.get("mutually_exclusive"):
        return "exclusive_set"
    return "other"


def simplify(market):
    """Keep only the fields we need."""
    return {
        "ticker": market.get("ticker"),
        "subtitle": market.get("yes_sub_title") or market.get("subtitle") or "",
        "strike_type": market.get("strike_type"),
        "floor_strike": market.get("floor_strike"),
        "cap_strike": market.get("cap_strike"),
        "yes_bid": cents(market, "yes_bid"),
        "yes_ask": cents(market, "yes_ask"),
        "close_time": market.get("close_time"),
    }


def build_groups(events, min_markets=3):
    groups = []
    for event in events:
        markets = [simplify(m) for m in event.get("markets") or []]
        # Skip tiny groups and markets nobody is bidding on
        live = [m for m in markets if m["yes_bid"] and m["yes_bid"] > 0]
        if len(markets) < min_markets or len(live) < 2:
            continue
        kind = classify(event, event.get("markets") or [])
        if kind == "other":
            continue
        groups.append({
            "event_ticker": event.get("event_ticker"),
            "title": event.get("title"),
            "type": kind,
            "markets": markets,
        })
    return groups


def main():
    events = fetch_open_events()
    print(f"Downloaded {len(events)} open events")
    groups = build_groups(events)
    OUT.write_text(json.dumps(groups, indent=2))
    print(f"Found {len(groups)} related groups, saved to {OUT}\n")
    for g in groups[:40]:
        print(f"[{g['type']:<15}] {g['event_ticker']:<30} "
              f"{len(g['markets']):>3} markets  {g['title']}")


if __name__ == "__main__":
    main()
