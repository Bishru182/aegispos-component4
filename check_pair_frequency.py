
from pathlib import Path
from itertools import combinations
from collections import Counter

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
BASKETS_PATH = BASE_DIR / "data" / "processed" / "transaction_baskets.csv"

df = pd.read_csv(BASKETS_PATH)

pair_counts = Counter()

for value in df["product_ids"].dropna():
    products = sorted(set(str(value).split("|")))

    # Count each distinct product pair once per transaction
    for pair in combinations(products, 2):
        pair_counts[pair] += 1

print("Transactions:", len(df))
print("Distinct product pairs found:", len(pair_counts))

if pair_counts:
    print("\nTop 20 most frequent product pairs:")
    for (product_a, product_b), count in pair_counts.most_common(20):
        support = count / len(df)
        print(
            f"{product_a} + {product_b} | "
            f"Transactions: {count} | Support: {support:.4%}"
        )

    print("\nPairs meeting different support thresholds:")
    for threshold in [0.01, 0.002, 0.001, 0.0005]:
        minimum_count = threshold * len(df)
        matching = sum(
            count / len(df) >= threshold
            for count in pair_counts.values()
        )
        print(
            f"Support >= {threshold:.2%}: "
            f"{matching} pairs (minimum {minimum_count:.1f} transactions)"
        )
else:
    print("No product pairs were found.")
