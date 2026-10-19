
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "data" / "processed" / "ranked_bundle_candidates.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "explained_bundle_recommendations.csv"

df = pd.read_csv(INPUT_PATH)

# Calculate gross margin amount at current recorded prices
df["combined_gross_margin_amount"] = (
    df["combined_selling_price"] - df["combined_unit_cost"]
)

def explain(row):
    if pd.isna(row["business_score"]):
        return "Not ranked: required pricing information is unavailable."

    return (
        f"Ranked using association strength (60%) and combined gross "
        f"margin percentage (40%). Lift is {row['lift']:.2f}, "
        f"confidence is {row['confidence']:.2%}, and combined gross "
        f"margin percentage is {row['combined_gross_margin_pct']:.2f}%. "
        f"Current-price gross margin amount is Rs. "
        f"{row['combined_gross_margin_amount']:.2f} before any bundle "
        f"discount or other operating expenses. This is a candidate for "
        f"manager review, not a proven profitable offer."
    )

df["recommendation_explanation"] = df.apply(explain, axis=1)

columns = [
    "rank",
    "product_a",
    "product_b",
    "combined_selling_price",
    "combined_unit_cost",
    "combined_gross_margin_amount",
    "combined_gross_margin_pct",
    "support",
    "confidence",
    "lift",
    "business_score",
    "recommendation_explanation",
]

df[columns].to_csv(OUTPUT_PATH, index=False)

print("Saved explanations for", len(df), "bundle candidates.")
print("\nTop 5 explained recommendations:\n")
print(df[columns].head(5).to_string(index=False))
print(f"\nOutput: {OUTPUT_PATH}")
