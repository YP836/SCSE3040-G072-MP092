
from pathlib import Path
import pandas as pd

# Project paths
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


def clean_data(df, correct_gamma_units=False):
    df = df.copy()

    original_rows = len(df)

    # 1. Remove exact duplicate records
    df = df.drop_duplicates()

    # 2. Ensure experience supports decimal values
    df["agent_exp_months"] = pd.to_numeric(
        df["agent_exp_months"], errors="raise"
    ).astype("float64")

    # 3. Correct Team Gamma's unit conversion when required
    if correct_gamma_units:
        gamma_mask = df["team"].eq("Team Gamma")
        df.loc[gamma_mask, "agent_exp_months"] /= 30

    # 4. Replace sentinel values with missing values
    df["issue_count"] = df["issue_count"].replace(-999, pd.NA)

    # 5. Remove post-call information that causes target leakage
    df = df.drop(
        columns=["duration_from_phone_bill"],
        errors="ignore"
    )

    return df, original_rows


def process_file(filename, correct_gamma_units=False):
    source = RAW / filename
    df = pd.read_csv(source)

    cleaned, original_rows = clean_data(
        df,
        correct_gamma_units=correct_gamma_units
    )

    output = PROCESSED / filename.replace(".csv", "_clean.csv")
    cleaned.to_csv(output, index=False)

    gamma_median = cleaned.loc[
        cleaned["team"] == "Team Gamma",
        "agent_exp_months"
    ].median()

    print("\n===================================")
    print("Processed:", filename)
    print("===================================")
    print("Original rows:", original_rows)
    print("Cleaned rows:", len(cleaned))
    print("Duplicates removed:", original_rows - len(cleaned))
    print(
        "Remaining sentinel values:",
        (cleaned["issue_count"] == -999).sum()
    )
    print(
        "Missing issue_count values:",
        cleaned["issue_count"].isna().sum()
    )
    print(
        "Leakage column removed:",
        "duration_from_phone_bill" not in cleaned.columns
    )
    print("Team Gamma correction applied:", correct_gamma_units)
    print("Team Gamma median experience:", gamma_median)
    print("Saved to:", output)


def process_holdout():
    source = RAW / "holdout_features.csv"
    df = pd.read_csv(source)

    # Holdout Team Gamma is already on the normal scale
    df["agent_exp_months"] = pd.to_numeric(
        df["agent_exp_months"], errors="raise"
    ).astype("float64")

    # Replace sentinel values if present
    df["issue_count"] = df["issue_count"].replace(-999, pd.NA)

    output = PROCESSED / "holdout_features_clean.csv"
    df.to_csv(output, index=False)

    print("\n===================================")
    print("Processed: holdout_features.csv")
    print("===================================")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Missing values:", df.isna().sum().sum())
    print("Team Gamma correction applied: False")
    print("Saved to:", output)


def main():
    # Create processed folder if necessary
    PROCESSED.mkdir(parents=True, exist_ok=True)

    # Training data has the Team Gamma unit mix-up
    process_file("train.csv", correct_gamma_units=True)

    # Later data is already on the normal scale
    process_file("later.csv", correct_gamma_units=False)

    # Holdout data is already on the normal scale
    process_holdout()

    print("\nAll three datasets processed successfully!")


if __name__ == "__main__":
    main()
