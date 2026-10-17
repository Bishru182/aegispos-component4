
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")

files_to_inspect = [
    "pos_transactions.csv",
    "products.csv",
    "pricing_history.csv",
    "promotions.csv",
]

for filename in files_to_inspect:
    file_path = DATA_DIR / filename

    print("\n" + "=" * 60)
    print(f"FILE: {filename}")
    print("=" * 60)

    if not file_path.exists():
        print("File not found. Check the filename and folder.")
        continue

    # Read a small sample first rather than loading everything.
    df = pd.read_csv(file_path, nrows=5)

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nFirst five rows:")
    print(df.to_string(index=False))
