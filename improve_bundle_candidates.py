
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RULES_PATH = BASE_DIR / "data" / "processed" / "association_rules.csv"
PRODUCTS_PATH = BASE_DIR / "data" / "raw" / "products.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "bundle_candidates.csv"

# Exploratory thresholds: document these for later evaluation
MIN_SUPPORT = 0.0005       # At least about 45 transactions
MIN_CONFIDENCE = 0.03      # At least 3% confidence
MIN_LIFT = 1.10            # At least 10% lift above independence

rules = pd.read_csv(RULES_PATH)
products = pd.read_csv(PRODUCTS_PATH)

# Keep rules that meet all three thresholds
candidates = rules[
    (rules["support"] >= MIN_SUPPORT)
    & (rules["confidence"] >= MIN_CONFIDENCE)
    & (rules["lift"] >= MIN_LIFT)
].copy()

# Treat A -> B and B -> A as the same unordered bundle.
# Keep the direction with the higher confidence.
candidates["pair_key"] = candidates.apply(
    lambda row: " | ".join(
        sorted([row["antecedents"], row["consequents"]])
    ),
    axis=1,
)

candidates = (
    candidates.sort_values(
        ["confidence", "lift", "support"],
        ascending=False,
    )
    .drop_duplicates(subset="pair_key")
    .copy()
)

# Map product IDs to readable names
product_names = products.set_index("product_id")["product_name"].to_dict()

def readable_name(product_ids):
    ids = str(product_ids).split(", ")
    return " + ".join(
        product_names.get(product_id, product_id)
        for product_id in ids
    )

candidates["product_a"] = candidates["pair_key"].apply(
    lambda pair: readable_name(pair.split(" | ")[0])
)
candidates["product_b"] = candidates["pair_key"].apply(
    lambda pair: readable_name(pair.split(" | ")[1])
)

candidates["approx_transactions"] = (
    candidates["support"] * 90123
).round().astype(int)

candidates = candidates.sort_values(
    ["lift", "confidence", "support"],
    ascending=False,
)

output_columns = [
    "product_a",
    "product_b",
    "approx_transactions",
    "support",
    "confidence",
    "lift",
]

candidates[output_columns].to_csv(OUTPUT_PATH, index=False)

print("Rules before filtering:", len(rules))
print("Candidates after filtering and deduplication:", len(candidates))
print("\nTop bundle candidates:")
print(candidates[output_columns].head(15).to_string(index=False))
print(f"\nSaved baseline candidates to: {OUTPUT_PATH}")
