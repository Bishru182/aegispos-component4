
from pathlib import Path
import pandas as pd

path = (
    Path(__file__).resolve().parent
    / "data"
    / "processed"
    / "transaction_baskets.csv"
)

df = pd.read_csv(path)

print("Columns:", df.columns.tolist())
print("\nFirst 10 product_ids values:")
print(df["product_ids"].head(10).to_string(index=False))

print("\nItem count distribution:")
print(df["item_count"].value_counts().sort_index().to_string())

# Count products by splitting the product_ids field
split_counts = (
    df["product_ids"]
    .fillna("")
    .apply(lambda value: len([x for x in str(value).split("|") if x]))
)

print("\nProduct count based on splitting product_ids:")
print(split_counts.value_counts().sort_index().to_string())

print("\nRows with more than one product:", (split_counts > 1).sum())
print("Rows where split count differs from item_count:",
      (split_counts != df["item_count"]).sum())
