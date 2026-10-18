
from pathlib import Path

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules


# 1. Define input and output paths
BASE_DIR = Path(__file__).resolve().parent
BASKETS_PATH = BASE_DIR / "data" / "processed" / "transaction_baskets.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

# 2. Load the transaction baskets
baskets_df = pd.read_csv(BASKETS_PATH)

print("Total transactions:", len(baskets_df))
print("Columns:", baskets_df.columns.tolist())

# 3. Convert each basket into a list of product IDs

baskets = (
    baskets_df["product_ids"]
    .fillna("")
    .apply(lambda value: [item for item in value.split("|") if item])
)


# 4. Create a transaction-product matrix
all_products = sorted(set(product for basket in baskets for product in basket))

basket_matrix = pd.DataFrame(
    [
        {product: product in basket for product in all_products}
        for basket in baskets
    ]
).fillna(False).astype(bool)

print("Unique products:", len(all_products))
print("Matrix shape:", basket_matrix.shape)

# 5. Discover frequent product combinations
frequent_itemsets = apriori(
    basket_matrix,
    min_support=0.0005,
    use_colnames=True,
    max_len=3,
)

frequent_itemsets["item_count"] = frequent_itemsets["itemsets"].apply(len)

print("\nItemsets by size:")
print(frequent_itemsets["item_count"].value_counts().sort_index())

print("\nLargest itemset size:", frequent_itemsets["item_count"].max())

print("\nFrequent itemsets found:", len(frequent_itemsets))
print(
    frequent_itemsets.sort_values("support", ascending=False)
    .head(10)
    .to_string(index=False)
)

# 6. Generate association rules
if not frequent_itemsets.empty and frequent_itemsets["item_count"].max() >= 2:
    rules = association_rules(
        frequent_itemsets,
        metric="confidence",
        min_threshold=0.0,
    )

    if not rules.empty:
        rules["antecedents"] = rules["antecedents"].apply(
            lambda items: ", ".join(sorted(items))
        )
        rules["consequents"] = rules["consequents"].apply(
            lambda items: ", ".join(sorted(items))
        )

        rules = rules[
            [
                "antecedents",
                "consequents",
                "support",
                "confidence",
                "lift",
            ]
        ].sort_values(
            ["lift", "confidence", "support"],
            ascending=False,
        )

        print("\nTop 20 association rules:")
        print(rules.head(20).to_string(index=False))

        rules.to_csv(OUTPUT_DIR / "association_rules.csv", index=False)
        print("\nSaved association rules to association_rules.csv")
    else:
        print("\nNo association rules met the selected thresholds.")
else:
    print("\nNo frequent multi-product combinations found.")

# 7. Save the frequent combinations
frequent_itemsets["itemsets"] = frequent_itemsets["itemsets"].apply(
    lambda items: " | ".join(sorted(items))
)
frequent_itemsets.to_csv(
    OUTPUT_DIR / "frequent_itemsets.csv",
    index=False,
)

print("Saved frequent itemsets to frequent_itemsets.csv")
