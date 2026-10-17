
import pandas as pd
from pathlib import Path

file_path = Path("data/raw/pos_transactions.csv")
df = pd.read_csv(file_path)

print("=" * 55)
print("LINE TYPE COUNTS")
print("=" * 55)
print(df["line_type"].value_counts(dropna=False).to_string())

print("\n" + "=" * 55)
print("LINE STATUS COUNTS")
print("=" * 55)
print(df["line_status"].value_counts(dropna=False).to_string())

print("\n" + "=" * 55)
print("LINE TYPE + STATUS COMBINATIONS")
print("=" * 55)
print(
    df.groupby(
        ["line_type", "line_status"],
        dropna=False
    ).size().sort_values(ascending=False).to_string()
)

print("\n" + "=" * 55)
print("ORIGINAL TRANSACTION ID")
print("=" * 55)
print(
    df.loc[
        df["original_transaction_id"].notna(),
        [
            "transaction_id",
            "original_transaction_id",
            "line_type",
            "line_status",
            "quantity",
            "line_amount"
        ]
    ].head(20).to_string(index=False)
)

print("\n" + "=" * 55)
print("PROMOTION LINKAGE")
print("=" * 55)
print(f"Rows with promotion ID: {df['promotion_id'].notna().sum():,}")
print(f"Rows without promotion ID: {df['promotion_id'].isna().sum():,}")

print("\n" + "=" * 55)
print("DATE COVERAGE BY YEAR")
print("=" * 55)
df["transaction_datetime"] = pd.to_datetime(
    df["transaction_datetime"],
    errors="coerce"
)
print(df["transaction_datetime"].dt.year.value_counts().sort_index())
