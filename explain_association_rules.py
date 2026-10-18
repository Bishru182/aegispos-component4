
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

RULES_PATH = BASE_DIR / "data" / "processed" / "association_rules.csv"
PRODUCTS_PATH = BASE_DIR / "data" / "raw" / "products.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "readable_association_rules.csv"

# Load association rules and product catalogue
rules = pd.read_csv(RULES_PATH)
products = pd.read_csv(PRODUCTS_PATH)

# Create a lookup from product ID to product details
product_lookup = products.set_index("product_id")

def get_product_names(product_ids):
    names = []

    for product_id in str(product_ids).split(", "):
        if product_id in product_lookup.index:
            names.append(str(product_lookup.loc[product_id, "product_name"]))
        else:
            names.append(product_id)

    return " + ".join(names)

# Convert IDs into readable product names
rules["antecedent_names"] = rules["antecedents"].apply(get_product_names)
rules["consequent_names"] = rules["consequents"].apply(get_product_names)

# Add approximate transaction counts for context
total_transactions = 90123
rules["approx_transactions"] = (
    rules["support"] * total_transactions
).round().astype(int)

# Sort by lift, then support
rules = rules.sort_values(
    ["lift", "support"],
    ascending=False,
)

columns = [
    "antecedent_names",
    "consequent_names",
    "approx_transactions",
    "support",
    "confidence",
    "lift",
]

print("\nTop 20 readable association rules:\n")
print(rules[columns].head(20).to_string(index=False))

rules.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved readable report to: {OUTPUT_PATH}")
