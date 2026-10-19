
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

CANDIDATES_PATH = DATA_DIR / "processed" / "bundle_candidates.csv"
PRICING_PATH = DATA_DIR / "raw" / "pricing_history.csv"
PRODUCTS_PATH = DATA_DIR / "raw" / "products.csv"
OUTPUT_PATH = DATA_DIR / "processed" / "ranked_bundle_candidates.csv"

# Transparent prototype weights
ASSOCIATION_WEIGHT = 0.60
MARGIN_WEIGHT = 0.40

candidates = pd.read_csv(CANDIDATES_PATH)
pricing = pd.read_csv(PRICING_PATH)
products = pd.read_csv(PRODUCTS_PATH)

pricing["effective_from"] = pd.to_datetime(
    pricing["effective_from"], errors="coerce"
)
pricing["effective_to"] = pd.to_datetime(
    pricing["effective_to"], errors="coerce"
)

# Select the latest open-ended price record for each product.
# This is a current-price candidate, not proof that the price
# was valid on every historical transaction date.
current_prices = (
    pricing[pricing["effective_to"].isna()]
    .sort_values("effective_from")
    .drop_duplicates("product_id", keep="last")
    .copy()
)

# Build product ID and product-name lookups
name_to_id = products.drop_duplicates("product_name").set_index(
    "product_name"
)["product_id"].to_dict()

price_lookup = current_prices.set_index("product_id").to_dict("index")

def get_product_id(name):
    return name_to_id.get(name)

def get_price_details(product_name):
    product_id = get_product_id(product_name)

    if product_id is None or product_id not in price_lookup:
        return None

    return price_lookup[product_id]

# Attach prices and costs to both products in each candidate
records = []

for _, row in candidates.iterrows():
    product_a = row["product_a"]
    product_b = row["product_b"]

    a = get_price_details(product_a)
    b = get_price_details(product_b)

    record = row.to_dict()

    if a is None or b is None:
        record["price_data_available"] = False
        record["combined_selling_price"] = None
        record["combined_unit_cost"] = None
        record["combined_gross_margin_pct"] = None
    else:
        total_price = float(a["selling_price"]) + float(b["selling_price"])
        total_cost = float(a["unit_cost"]) + float(b["unit_cost"])

        record["price_data_available"] = True
        record["combined_selling_price"] = total_price
        record["combined_unit_cost"] = total_cost
        record["combined_gross_margin_pct"] = (
            (total_price - total_cost) / total_price * 100
            if total_price > 0
            else None
        )

    records.append(record)

ranked = pd.DataFrame(records)

# Normalize lift and margin to a 0-1 range across candidates.
# This makes the two different scales comparable.
def min_max_scale(series):
    minimum = series.min()
    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum):
        return pd.Series(0.0, index=series.index)

    if maximum == minimum:
        return pd.Series(1.0, index=series.index)

    return (series - minimum) / (maximum - minimum)

ranked["association_score"] = min_max_scale(ranked["lift"])

ranked["margin_score"] = min_max_scale(
    ranked["combined_gross_margin_pct"]
)

# Do not silently treat missing margin data as zero.
# Exclude candidates without both products' price data from the
# combined score until the missing data can be investigated.
ranked["business_score"] = (
    ASSOCIATION_WEIGHT * ranked["association_score"]
    + MARGIN_WEIGHT * ranked["margin_score"]
)

ranked.loc[
    ~ranked["price_data_available"], "business_score"
] = None

ranked = ranked.sort_values(
    "business_score",
    ascending=False,
    na_position="last",
)

ranked["rank"] = range(1, len(ranked) + 1)

ranked.to_csv(OUTPUT_PATH, index=False)

display_columns = [
    "rank",
    "product_a",
    "product_b",
    "lift",
    "confidence",
    "combined_selling_price",
    "combined_unit_cost",
    "combined_gross_margin_pct",
    "business_score",
]

print("Candidates processed:", len(ranked))
print("Candidates with pricing for both products:",
      int(ranked["price_data_available"].sum()))
print("\nTop 15 ranked candidates:")
print(ranked[display_columns].head(15).to_string(index=False))

print(f"\nSaved ranked candidates to: {OUTPUT_PATH}")
