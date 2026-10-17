
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")
POS_FILE = DATA_DIR / "pos_transactions.csv"

if not POS_FILE.exists():
    raise FileNotFoundError(
        f"Cannot find {POS_FILE}. Check your project folder."
    )

# Load the real POS dataset.
df = pd.read_csv(POS_FILE)

print("=" * 60)
print("POS DATASET OVERVIEW")
print("=" * 60)

print(f"Total rows: {len(df):,}")
print(f"Unique transactions: {df['transaction_id'].nunique():,}")
print(f"Unique products: {df['product_id'].nunique():,}")
print(f"Date range: {df['transaction_datetime'].min()} "
      f"to {df['transaction_datetime'].max()}")

print("\n" + "=" * 60)
print("MISSING VALUES")
print("=" * 60)

missing = df.isna().sum()
print(missing[missing > 0].sort_values(ascending=False))

print("\n" + "=" * 60)
print("DUPLICATE ROWS")
print("=" * 60)

print(f"Exact duplicate rows: {df.duplicated().sum()}")

print("\n" + "=" * 60)
print("QUANTITY CHECK")
print("=" * 60)

print("Quantity summary:")
print(df["quantity"].describe())

print("\nRows with quantity <= 0:")
print(df.loc[
    df["quantity"] <= 0,
    ["transaction_id", "line_no", "product_id",
     "line_type", "quantity", "line_amount", "line_status"]
].head(20).to_string(index=False))

print("\nLargest quantities:")
print(df.nlargest(
    10, "quantity"
)[[
    "transaction_id", "line_no", "product_id",
    "line_type", "quantity", "unit_price",
    "line_amount", "line_status"
]].to_string(index=False))

print("\n" + "=" * 60)
print("LINE AMOUNT CHECK")
print("=" * 60)

# Compare the amount against a simple expected calculation.
# This is a diagnostic only: refunds, discounts, and special
# line types may require different calculation rules.
df["calculated_amount"] = (
    df["quantity"] * df["unit_price"]
    - df["discount_amount"].fillna(0)
)

df["amount_difference"] = (
    df["line_amount"] - df["calculated_amount"]
).round(2)

mismatches = df[
    df["amount_difference"].abs() > 0.01
]

print(f"Rows not matching the simple formula: {len(mismatches):,}")

print(mismatches[[
    "transaction_id", "line_no", "product_id",
    "line_type", "quantity", "unit_price",
    "discount_amount", "line_amount",
    "line_status", "amount_difference"
]].head(20).to_string(index=False))
