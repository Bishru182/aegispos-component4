# AegisPOS — Component 4

**AI-Driven Offer, Bundle & Campaign Recommendation Engine**

## Overview

This research component aims to identify product associations from
historical supermarket POS transactions and develop explainable
product bundle, offer, and campaign recommendations.

## Current Progress — Day 1

- Inspected the POS, product, pricing, and promotion datasets.
- Performed initial data-quality checks.
- Created a POS preprocessing pipeline.
- Generated transaction baskets.
- Analysed transaction basket sizes.

## Technology

- Python
- pandas
- CSV data processing

## Project Structure

- `inspect_dataset.py` — inspect dataset schemas and sample records
- `check_data_quality.py` — run initial data-quality checks
- `inspect_transaction_types.py` — inspect transaction types and statuses
- `preprocess_pos.py` — prepare transaction data and baskets
- `inspect_baskets.py` — analyse basket sizes
- `data/` — local datasets; excluded from Git

## Running the Scripts

Run commands from the project root:

```bash
python3 inspect_dataset.py
python3 check_data_quality.py
python3 inspect_transaction_types.py
python3 preprocess_pos.py
python3 inspect_baskets.py