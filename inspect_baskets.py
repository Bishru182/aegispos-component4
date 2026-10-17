
import pandas as pd
from pathlib import Path

file_path = (
    Path(__file__).resolve().parent
    / "data"
    / "processed"
    / "transaction_baskets.csv"
)

baskets = pd.read_csv(file_path)

print("=" * 55)
print("BASKET SIZE ANALYSIS")
print("=" * 55)

print(f"Total transactions: {len(baskets):,}")
print(f"Average distinct products per basket: {baskets['item_count'].mean():.2f}")
print(f"Median basket size: {baskets['item_count'].median():.0f}")
print(f"Largest basket: {baskets['item_count'].max()} products")

print("\nBasket size distribution:")
print(
    baskets["item_count"]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\nPercentage of baskets by size:")
print(
    (baskets["item_count"].value_counts(normalize=True)
     .sort_index() * 100)
    .round(2)
    .to_string()
)

print("\nExample baskets:")
print(baskets.head(10).to_string(index=False))
