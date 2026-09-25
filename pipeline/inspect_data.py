from pathlib import Path

import pandas as pd


SNAPSHOT_DIR = Path("data/snapshots")
EXPECTED_COLUMNS = {"ts", "ticker", "side", "price", "qty"}


def load_snapshot_files():
    files = sorted(SNAPSHOT_DIR.rglob("*.parquet"))

    if not files:
        raise SystemExit("No Parquet snapshot files found.")

    return files


def main():
    files = load_snapshot_files()

    frames = []
    failed_files = []

    for file in files:
        try:
            frame = pd.read_parquet(file)
            frame["source_file"] = str(file)
            frames.append(frame)
        except Exception as error:
            failed_files.append((str(file), str(error)))

    if not frames:
        raise SystemExit("No snapshot files could be read.")

    data = pd.concat(frames, ignore_index=True)

    print("=== Snapshot summary ===")
    print(f"Snapshot files: {len(files):,}")
    print(f"Readable files: {len(frames):,}")
    print(f"Rows: {len(data):,}")

    print("\n=== Columns ===")
    print(sorted(data.columns.tolist()))
    print(
        f"Missing expected columns: "
        f"{sorted(EXPECTED_COLUMNS - set(data.columns))}"
    )

    print("\n=== Time coverage ===")
    data["ts"] = pd.to_datetime(data["ts"], utc=True, errors="coerce")
    print(f"First timestamp: {data['ts'].min()}")
    print(f"Last timestamp:  {data['ts'].max()}")
    print(f"Unique timestamps: {data['ts'].nunique():,}")

    print("\n=== Snapshot timing gaps ===")

    snapshot_times = (
        data[["source_file", "ts"]]
        .drop_duplicates()
        .sort_values("ts")
    )

    snapshot_times["gap_seconds"] = (
        snapshot_times["ts"].diff().dt.total_seconds()
    )

    gaps = snapshot_times["gap_seconds"].dropna()

    if gaps.empty:
        print("Not enough snapshots to calculate timing gaps.")
    else:
        print(f"Minimum gap: {gaps.min():,.1f} seconds")
        print(f"Median gap:  {gaps.median():,.1f} seconds")
        print(f"Maximum gap: {gaps.max():,.1f} seconds")
        print(f"Gaps over 90 seconds: {(gaps > 90).sum():,}")
        print(f"Gaps over 5 minutes: {(gaps > 300).sum():,}")

    print("\n=== Market coverage ===")
    print(f"Unique tickers: {data['ticker'].nunique():,}")
    print(
        f"Unique sides: "
        f"{sorted(data['side'].dropna().unique().tolist())}"
    )

    print("\n=== Data validity ===")
    print(f"Missing timestamps: {data['ts'].isna().sum():,}")
    print(f"Missing tickers: {data['ticker'].isna().sum():,}")
    print(f"Missing prices: {data['price'].isna().sum():,}")
    print(f"Missing quantities: {data['qty'].isna().sum():,}")

    print(f"Prices below 0: {(data['price'] < 0).sum():,}")
    print(f"Prices above 1: {(data['price'] > 1).sum():,}")
    print(f"Quantities below 0: {(data['qty'] < 0).sum():,}")

    print("\n=== Rows by side ===")
    print(data["side"].value_counts(dropna=False).to_string())

    print("\n=== Rows by ticker, first 20 ===")
    print(
        data.groupby("ticker")
        .size()
        .sort_values(ascending=False)
        .head(20)
        .to_string()
    )

    print("\n=== Rows by snapshot, first 20 ===")
    rows_per_snapshot = data.groupby("source_file").size()
    print(rows_per_snapshot.head(20).to_string())

    if failed_files:
        print("\n=== Files that failed to read ===")
        for file, error in failed_files:
            print(f"{file}: {error}")


if __name__ == "__main__":
    main()