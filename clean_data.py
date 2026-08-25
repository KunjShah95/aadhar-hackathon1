"""
clean_data.py — Aadhaar Dataset Cleaning & Aggregation Pipeline
==============================================================
What this script does in simple terms:
  1. Reads all raw CSV shards across Enrolment, Demographic, and Biometric folders.
  2. Cleans up messy state names (e.g., typos like "Westbangal" -> "West Bengal").
  3. Combines everything into daily state-level records.
  4. Calculates helpful metrics like total enrolments, total updates, and system load.
  5. Exports clean, ready-to-use CSV files for modeling and dashboards:
     - cleaned_aadhaar_data.csv
     - cleaned_aadhaar_monthly_national.csv
     - cleaned_aadhaar_summary_by_state.csv
"""

import os
import glob
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Define Canonical State Reference & Population Data
# ─────────────────────────────────────────────────────────────────────────────
# Estimated population for all 28 States and 8 Union Territories in India
STATE_POPULATION = {
    "Andaman & Nicobar":    397_000, "Andhra Pradesh": 49_577_103,
    "Arunachal Pradesh": 1_570_458, "Assam": 34_293_000, "Bihar": 121_243_000,
    "Chandigarh": 1_158_000, "Chhattisgarh": 28_724_000,
    "Dadra & Nagar Haveli and Daman & Diu": 615_000, "Delhi": 20_667_656,
    "Goa": 1_586_250, "Gujarat": 66_750_000, "Haryana": 28_204_000,
    "Himachal Pradesh": 7_503_000, "Jammu and Kashmir": 14_999_397,
    "Jharkhand": 36_480_000, "Karnataka": 66_165_000, "Kerala": 35_125_000,
    "Ladakh": 316_000, "Lakshadweep": 73_183, "Madhya Pradesh": 82_232_000,
    "Maharashtra": 123_144_000, "Manipur": 3_091_545, "Meghalaya": 3_366_710,
    "Mizoram": 1_239_244, "Nagaland": 2_157_059, "Odisha": 45_429_000,
    "Puducherry": 1_413_542, "Punjab": 30_141_373, "Rajasthan": 79_502_477,
    "Sikkim": 682_000, "Tamil Nadu": 77_841_000, "Telangana": 38_705_209,
    "Tripura": 4_169_794, "Uttar Pradesh": 231_502_578,
    "Uttarakhand": 11_250_858, "West Bengal": 100_896_618,
}
_MEDIAN_POP = int(np.median(list(STATE_POPULATION.values())))

# Mapping common typos, old names, and alternative spellings to official names
STATE_ALIASES = {
    "andaman and nicobar islands": "Andaman & Nicobar",
    "andaman & nicobar islands": "Andaman & Nicobar",
    "a & n islands": "Andaman & Nicobar",
    "andhra pradesh": "Andhra Pradesh",
    "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chandigarh": "Chandigarh",
    "chhattisgarh": "Chhattisgarh",
    "chhatisgarh": "Chhattisgarh",
    "dadra and nagar haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra and nagar haveli and daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra & nagar haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "daman & diu": "Dadra & Nagar Haveli and Daman & Diu",
    "the dadra and nagar haveli and daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "delhi": "Delhi",
    "nct of delhi": "Delhi",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana": "Haryana",
    "himachal pradesh": "Himachal Pradesh",
    "jammu and kashmir": "Jammu and Kashmir",
    "jammu & kashmir": "Jammu and Kashmir",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "ladakh": "Ladakh",
    "lakshadweep": "Lakshadweep",
    "madhya pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "puducherry": "Puducherry",
    "pondicherry": "Puducherry",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil nadu": "Tamil Nadu",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "uttar pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand",
    "uttaranchal": "Uttarakhand",
    "west bengal": "West Bengal",
    "westbengal": "West Bengal",
    "west bangal": "West Bengal",
    "west  bengal": "West Bengal",
}

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Helper Functions for Name Normalization
# ─────────────────────────────────────────────────────────────────────────────
def normalize_state_name(raw_name):
    """
    Takes any raw string for a state name, strips extra spaces,
    checks against alias lookup, and returns canonical name.
    """
    if pd.isna(raw_name):
        return None
    cleaned = str(raw_name).strip().lower()
    if cleaned in STATE_ALIASES:
        return STATE_ALIASES[cleaned]
    # Filter out numeric anomalies like pincodes '100000' accidentally in state column
    if cleaned.isdigit():
        return None
    return str(raw_name).strip().title()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Load and Combine Raw Shard CSVs
# ─────────────────────────────────────────────────────────────────────────────
def load_and_clean_shards(data_dir="."):
    """
    Finds and reads all CSV files for:
      - Enrolments (age 0-5, 5-17, 18+)
      - Demographic Updates (address, phone, name changes)
      - Biometric Updates (fingerprints, iris, photo updates)
    """
    def _read_folder(subfolder_pattern):
        path = os.path.join(data_dir, subfolder_pattern)
        file_list = sorted(glob.glob(path, recursive=True))
        if not file_list:
            return pd.DataFrame()
        dfs = []
        for f in file_list:
            try:
                temp_df = pd.read_csv(f, dtype={"state": str, "district": str})
                dfs.append(temp_df)
            except Exception as e:
                print(f"Warning: Could not read {f}: {e}")
        if not dfs:
            return pd.DataFrame()
        combined = pd.concat(dfs, ignore_index=True)
        # Parse dates and normalize state names
        combined["date"] = pd.to_datetime(combined["date"], format="%d-%m-%Y", errors="coerce")
        combined["state_canonical"] = combined["state"].apply(normalize_state_name)
        # Drop rows where state could not be resolved
        return combined[combined["state_canonical"].notna()].copy()

    print("  -> Loading Enrolment shards...")
    enrol = _read_folder("api_data_aadhar_enrolment/**/*.csv")
    if not enrol.empty:
        # Sum age groups to get total new enrolments
        enrol["total_enrolments"] = enrol[["age_0_5", "age_5_17", "age_18_greater"]].fillna(0).sum(axis=1)
        enrol = enrol.groupby(["date", "state_canonical"])[
            ["age_0_5", "age_5_17", "age_18_greater", "total_enrolments"]
        ].sum().reset_index()

    print("  -> Loading Demographic update shards...")
    demo = _read_folder("api_data_aadhar_demographic/**/*.csv")
    if not demo.empty:
        # Sum demographic age columns to get demo total
        demo["demo_total"] = demo[["demo_age_5_17", "demo_age_17_"]].fillna(0).sum(axis=1)
        demo = demo.groupby(["date", "state_canonical"])[
            ["demo_age_5_17", "demo_age_17_", "demo_total"]
        ].sum().reset_index()

    print("  -> Loading Biometric update shards...")
    bio = _read_folder("api_data_aadhar_biometric/**/*.csv")
    if not bio.empty:
        # Sum biometric age columns to get bio total
        bio["bio_total"] = bio[["bio_age_5_17", "bio_age_17_"]].fillna(0).sum(axis=1)
        bio = bio.groupby(["date", "state_canonical"])[
            ["bio_age_5_17", "bio_age_17_", "bio_total"]
        ].sum().reset_index()

    # Merge the three datasets together on (date, state)
    print("  -> Merging Enrolment, Demographic, and Biometric datasets...")
    merged = enrol if not enrol.empty else pd.DataFrame()
    if not demo.empty:
        merged = pd.merge(merged, demo, on=["date", "state_canonical"], how="outer") if not merged.empty else demo
    if not bio.empty:
        merged = pd.merge(merged, bio, on=["date", "state_canonical"], how="outer") if not merged.empty else bio

    # Fill missing values with 0 (a missing record means 0 updates on that day)
    num_cols = ["age_0_5", "age_5_17", "age_18_greater", "total_enrolments",
                "demo_age_5_17", "demo_age_17_", "demo_total",
                "bio_age_5_17", "bio_age_17_", "bio_total"]
    for c in num_cols:
        if c in merged.columns:
            merged[c] = merged[c].fillna(0.0)

    # Calculate Total System Load = new enrolments + demographic updates + biometric updates
    merged["total_system_load"] = (
        merged["total_enrolments"] + merged["demo_total"] + merged["bio_total"]
    )

    # Attach population information
    merged["state_population"] = merged["state_canonical"].map(STATE_POPULATION).fillna(_MEDIAN_POP).astype(int)

    # Calculate per-capita enrolment rate per 1,000 residents
    merged["enrol_per_1000"] = (
        (merged["total_enrolments"] / merged["state_population"]) * 1000
    ).round(4)

    # Calculate Update Velocity (ratio of updates to new enrolments)
    merged["update_velocity"] = (
        (merged["demo_total"] + merged["bio_total"]) / (merged["total_enrolments"] + 1)
    ).round(2)

    # Classify Lifecycle Stage:
    # If update_velocity <= 5 -> Growth stage (many new registrations)
    # If update_velocity > 5  -> Maintenance stage (saturation reached, mostly updates)
    merged["lifecycle_stage"] = np.where(merged["update_velocity"] <= 5.0, "Growth", "Maintenance")

    # Add friendly calendar attributes
    merged["date"] = pd.to_datetime(merged["date"])
    merged["year"] = merged["date"].dt.year
    merged["month"] = merged["date"].dt.month
    merged["month_name"] = merged["date"].dt.strftime("%B")
    merged["day_of_week"] = merged["date"].dt.strftime("%A")
    merged["is_weekend"] = merged["date"].dt.dayofweek.isin([5, 6]).astype(int)

    # Sort chronologically by state
    merged = merged.sort_values(["state_canonical", "date"]).reset_index(drop=True)
    return merged

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Build Summary & Aggregation Tables
# ─────────────────────────────────────────────────────────────────────────────
def generate_summary_tables(panel_df):
    """
    Creates monthly national totals and state-level lifetime summaries.
    """
    # 1. Monthly National Summary
    monthly_national = panel_df.groupby(["year", "month", "month_name"]).agg(
        total_enrolments=("total_enrolments", "sum"),
        demo_updates=("demo_total", "sum"),
        bio_updates=("bio_total", "sum"),
        system_load=("total_system_load", "sum")
    ).reset_index().sort_values(["year", "month"])

    # 2. State-Level Summary
    state_summary = panel_df.groupby("state_canonical").agg(
        total_enrolments=("total_enrolments", "sum"),
        total_demo_updates=("demo_total", "sum"),
        total_bio_updates=("bio_total", "sum"),
        total_system_load=("total_system_load", "sum"),
        avg_daily_enrolments=("total_enrolments", "mean"),
        avg_update_velocity=("update_velocity", "mean"),
        state_population=("state_population", "first")
    ).reset_index()

    # Determine state overall lifecycle stage
    state_summary["lifecycle_stage"] = np.where(
        (state_summary["total_demo_updates"] + state_summary["total_bio_updates"]) / (state_summary["total_enrolments"] + 1) <= 5.0,
        "Growth", "Maintenance"
    )
    state_summary["enrol_per_1000_pop"] = (
        (state_summary["total_enrolments"] / state_summary["state_population"]) * 1000
    ).round(2)
    state_summary["avg_daily_enrolments"] = state_summary["avg_daily_enrolments"].round(1)
    state_summary["avg_update_velocity"] = state_summary["avg_update_velocity"].round(1)
    state_summary = state_summary.sort_values("total_enrolments", ascending=False).reset_index(drop=True)

    return monthly_national, state_summary

# ─────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print(" Aadhaar Intelligence Engine — Data Cleaning Pipeline")
    print("=" * 70)

    # 1. Load and clean
    cleaned_df = load_and_clean_shards(data_dir=".")
    print(f"\n[OK] Cleaned panel created: {len(cleaned_df):,} rows across {cleaned_df['state_canonical'].nunique()} states/UTs.")

    # 2. Summarize
    monthly_df, state_df = generate_summary_tables(cleaned_df)

    # 3. Export CSV files
    out_panel = "cleaned_aadhaar_data.csv"
    out_monthly = "cleaned_aadhaar_monthly_national.csv"
    out_state = "cleaned_aadhaar_summary_by_state.csv"

    cleaned_df.to_csv(out_panel, index=False)
    monthly_df.to_csv(out_monthly, index=False)
    state_df.to_csv(out_state, index=False)

    print(f"\n[Exported CSV Files]")
    print(f"  1. {out_panel} ({len(cleaned_df):,} rows)")
    print(f"  2. {out_monthly} ({len(monthly_df):,} rows)")
    print(f"  3. {out_state} ({len(state_df):,} rows)")
    print("=" * 70)
    print("Data cleaning completed successfully!\n")

if __name__ == "__main__":
    main()
