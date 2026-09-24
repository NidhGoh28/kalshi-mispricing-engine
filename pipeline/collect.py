import time
import datetime as dt
from pathlib import Path

import pandas as pd
import requests


BASE = "https://api.elections.kalshi.com/trade-api/v2"
OUT = Path("data/snapshots")
TICKER_FILE = Path("research/tickers.txt")
INTERVAL = 60


def load_tickers():
    """Load tracked tickers from research/tickers.txt."""
    if TICKER_FILE.exists():
        lines = TICKER_FILE.read_text().splitlines()
        tickers = [
            line.strip()
            for line in lines
            if line.strip() and not line.startswith("#")
        ]

        if tickers:
            return tickers

    print("Ticker file is empty or missing. Using 50 open markets.")

    response = requests.get(
        f"{BASE}/markets",
        params={"status": "open", "limit": 200},
        timeout=10,
    )
    response.raise_for_status()

    markets = pd.DataFrame(response.json()["markets"])

    if "volume" in markets.columns:
        markets = markets.sort_values("volume", ascending=False)

    return markets["ticker"].head(50).tolist()


def snapshot(tickers):
    """Collect one order-book snapshot for all tickers."""
    timestamp = dt.datetime.now(dt.timezone.utc)
    rows = []

    for ticker in tickers:
        try:
            response = requests.get(
                f"{BASE}/markets/{ticker}/orderbook",
                timeout=10,
            )
            response.raise_for_status()

            payload = response.json()
            orderbook = payload.get("orderbook_fp") or {}

        except requests.RequestException as error:
            print(f"Skipped {ticker}: {error}")
            continue

        for side in ("yes_dollars", "no_dollars"):
            for level in orderbook.get(side) or []:
                rows.append(
                    {
                        "ts": timestamp,
                        "ticker": ticker,
                        "side": "yes" if side == "yes_dollars" else "no",
                        "price": float(level[0]),
                        "qty": float(level[1]),
                    }
                )

        time.sleep(0.1)

    return timestamp, pd.DataFrame(rows)


def main():
    tickers = load_tickers()
    print(f"Tracking {len(tickers)} markets")

    while True:
        timestamp, data = snapshot(tickers)

        if not data.empty:
            folder = OUT / timestamp.strftime("%Y-%m-%d")
            folder.mkdir(parents=True, exist_ok=True)

            filename = folder / f"{timestamp.strftime('%H%M%S')}.parquet"
            data.to_parquet(filename, index=False)

        print(
            f"{timestamp:%H:%M:%S} "
            f"saved {len(data)} order book levels"
        )

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()