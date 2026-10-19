
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

pricing = pd.read_csv(BASE_DIR / "data/raw/pricing_history.csv")
products = pd.read_csv(BASE_DIR / "data/raw/products.csv")
promotions = pd.read_csv(BASE_DIR / "data/raw/promotions.csv")

# Parse pricing dates
pricing["effective_from"] = pd.to_datetime(
    pricing["effective_from"], errors="coerce"
)
pricing["effective_to"] = pd.to_datetime(
    pricing["effective_to"], errors="coerce"
)

print("=== PRICING DATA ===")
print("Total price records:", len(pricing))
print("Products with price records:", pricing["product_id"].nunique())

# Records without an end date may be the current records.
# We will inspect them rather than assuming they are all valid.
current_candidates = pricing[pricing["effective_to"].isna()].copy()

print("\nRecords with no effective_to:", len(current_candidates))
print("Unique products among these records:",
      current_candidates["product_id"].nunique())
print("Products with multiple such records:",
      (current_candidates["product_id"].value_counts() > 1).sum())

print("\nPrice and cost checks:")
print("Missing selling prices:", pricing["selling_price"].isna().sum())
print("Missing unit costs:", pricing["unit_cost"].isna().sum())
print("Non-positive selling prices:",
      (pricing["selling_price"] <= 0).sum())
print("Negative unit costs:", (pricing["unit_cost"] < 0).sum())
print("Cost greater than selling price:",
      (pricing["unit_cost"] > pricing["selling_price"]).sum())

# Calculate gross margin for records with valid positive selling prices
valid = pricing[pricing["selling_price"] > 0].copy()
valid["gross_margin_pct"] = (
    (valid["selling_price"] - valid["unit_cost"])
    / valid["selling_price"]
    * 100
)

print("\nGross margin percentage summary:")
print(valid["gross_margin_pct"].describe().round(2).to_string())

print("\n=== PRODUCT CATALOGUE ===")
print("Products in catalogue:", products["product_id"].nunique())
print("Duplicate product IDs:", products["product_id"].duplicated().sum())

print("\n=== PROMOTIONS ===")
print("Total promotion records:", len(promotions))
print("Unique promoted products:", promotions["product_id"].nunique())
print("Missing promotion responses:",
      promotions["recorded_response"].isna().sum())
print("\nPromotion types:")
print(promotions["promotion_type"].value_counts(dropna=False).to_string())
