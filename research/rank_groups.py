"""
Rank the groups in research/groups.json to find the best ones to track.

Good candidates are:
  - liquid: at least a few markets with a real bid AND ask, with tight spreads
  - settling soon-ish: so prices actually move during the project, but the
    markets don't disappear after a few days

If nothing passes the filters, it explains why and shows the closest matches
anyway, so you can decide for yourself.

Run from the project's top folder (after find_groups.py):
    python research/rank_groups.py
"""
import json
import datetime as dt
from pathlib import Path
from statistics import median

GROUPS = Path("research/groups.json")
MIN_DAYS, MAX_DAYS = 3, 120
MIN_LIVE = 3          # markets with both a bid and an ask
MAX_SPREAD = 10       # cents; wider than this means nobody is really trading


def days_until(iso_time):
    if not iso_time:
        return None
    try:
        closes = dt.datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (closes - dt.datetime.now(dt.timezone.utc)).days


def score(group):
    spreads, live = [], 0
    for m in group["markets"]:
        bid, ask = m["yes_bid"], m["yes_ask"]
        if bid and ask and 0 < bid < ask < 100:
            spreads.append(ask - bid)
            live += 1
    closes = [d for d in (days_until(m["close_time"]) for m in group["markets"])
              if d is not None]
    return {
        "event": group["event_ticker"],
        "type": group["type"],
        "title": (group["title"] or "")[:45],
        "markets": len(group["markets"]),
        "live": live,
        "spread": median(spreads) if spreads else None,
        "days": min(closes) if closes else None,
    }


def show(rows, n=30):
    print(f"{'type':<16}{'event':<28}{'live':>5}{'spread':>8}{'days':>7}  title")
    for r in rows[:n]:
        spread = f"{r['spread']:.0f}c" if r["spread"] is not None else "   -"
        days = r["days"] if r["days"] is not None else "-"
        print(f"{r['type']:<16}{r['event'][:27]:<28}{r['live']:>5}"
              f"{spread:>8}{str(days):>7}  {r['title']}")


def main():
    rows = [score(g) for g in json.loads(GROUPS.read_text())]

    # Why groups get dropped, so a zero result is explainable
    thin = [r for r in rows if r["live"] < MIN_LIVE]
    no_close = [r for r in rows if r["days"] is None]
    too_soon = [r for r in rows if r["days"] is not None and r["days"] < MIN_DAYS]
    too_far = [r for r in rows if r["days"] is not None and r["days"] > MAX_DAYS]
    wide = [r for r in rows if r["spread"] is not None and r["spread"] > MAX_SPREAD]
    print(f"{len(rows)} groups total")
    print(f"  {len(thin)} have fewer than {MIN_LIVE} markets with both a bid and an ask")
    print(f"  {len(no_close)} have no close time")
    print(f"  {len(too_soon)} close in under {MIN_DAYS} days")
    print(f"  {len(too_far)} close in over {MAX_DAYS} days")
    print(f"  {len(wide)} have a median spread wider than {MAX_SPREAD}c\n")

    good = [r for r in rows
            if r["live"] >= MIN_LIVE and r["spread"] is not None
            and r["spread"] <= MAX_SPREAD and r["days"] is not None
            and MIN_DAYS <= r["days"] <= MAX_DAYS]
    good.sort(key=lambda r: (r["spread"], r["days"], -r["live"]))

    if good:
        print(f"{len(good)} groups pass every filter. Best {min(30, len(good))}:\n")
        show(good)
        return

    print("Nothing passed every filter. Closest matches: groups with at least "
          "2 live markets, soonest close first.\n")
    fallback = [r for r in rows if r["live"] >= 2 and r["days"] is not None]
    fallback.sort(key=lambda r: (r["days"], r["spread"] or 99))
    show(fallback, 20)


if __name__ == "__main__":
    main()
