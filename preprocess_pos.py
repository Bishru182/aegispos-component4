
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

POS_FILE = RAW_DIR / "pos_transactions.csv"
PRODUCTS_FILE = RAW_DIR / "products.csv"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Required fields for basic basket analysis.
required_pos_columns = {
    "transaction_id",
    "transaction_datetime",
    "product_id",
    "line_type",
    "quantity",
    "unit_price",
    "discount_amount",
    "line_amount",
    "line_status",
}

pos = pd.read_csv(POS_FILE)
products = pd.read_csv(PRODUCTS_FILE)

missing_columns = required_pos_columns - set(pos.columns)
if missing_columns:
    raise ValueError(f"Missing required POS columns: {missing_columns}")

if "product_id" not in products.columns:
    raise ValueError("products.csv must contain product_id.")

print(f"Original POS rows: {len(pos):,}")

# 1. Remove exact duplicate records only.
duplicate_count = int(pos.duplicated().sum())
pos = pos.drop_duplicates().copy()
print(f"Exact duplicate rows removed: {duplicate_count:,}")

# 2. Parse timestamps and identify invalid required fields.
pos["transaction_datetime"] = pd.to_datetime(
    pos["transaction_datetime"], errors="coerce"
)

valid_required = (
    pos["transaction_id"].notna()
    & pos["product_id"].notna()
    & pos["transaction_datetime"].notna()
    & pos["quantity"].notna()
    & pos["unit_price"].notna()
    & pos["line_amount"].notna()
)

print(f"Rows with missing/invalid required fields: {(~valid_required).sum():,}")

# 3. Keep rows matching the observed sale/status values.
sale_mask = (
    pos["line_type"].eq("SALE")
    & pos["line_status"].eq("COMPLETED")
)

# 4. Exclude invalid quantities and negative prices.
numeric_mask = (
    pos["quantity"].gt(0)
    & pos["unit_price"].ge(0)
    & pos["line_amount"].ge(0)
)

candidate = pos.loc[
    valid_required & sale_mask & numeric_mask
].copy()

# 5. Check product IDs against the product catalogue.
known_product_ids = set(products["product_id"].dropna())
unknown_product_mask = ~candidate["product_id"].isin(known_product_ids)

print(f"Candidate sale rows: {len(candidate):,}")
print(f"Rows with product IDs missing from catalogue: {unknown_product_mask.sum():,}")

clean = candidate.loc[~unknown_product_mask].copy()

# 6. Save the cleaned transaction lines.
clean.to_csv(
    PROCESSED_DIR / "cleaned_pos_transactions.csv",
    index=False
)

# 7. Create one row per transaction with its distinct product IDs.
# This file is convenient for later basket analysis.
baskets = (
    clean.groupby("transaction_id")
    .agg(
        transaction_datetime=("transaction_datetime", "min"),
        product_ids=("product_id", lambda values: "|".join(sorted(set(values)))),
        item_count=("product_id", "nunique"),
    )
    .reset_index()
)

baskets.to_csv(
    PROCESSED_DIR / "transaction_baskets.csv",
    index=False
)

print("\nPREPROCESSING SUMMARY")
print(f"Cleaned transaction lines: {len(clean):,}")
print(f"Unique transactions: {clean['transaction_id'].nunique():,}")
print(f"Unique products: {clean['product_id'].nunique():,}")
print(f"Transactions with multiple distinct products: {(baskets['item_count'] > 1).sum():,}")
print(f"Saved: {PROCESSED_DIR / 'cleaned_pos_transactions.csv'}")
print(f"Saved: {PROCESSED_DIR / 'transaction_baskets.csv'}")
