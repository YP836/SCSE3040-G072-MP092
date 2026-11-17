
from pathlib import Path
import pandas as pd
import numpy as np
import re
import string

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "raw"

train = pd.read_csv(DATA / "train.csv")
later = pd.read_csv(DATA / "later.csv")
holdout = pd.read_csv(DATA / "holdout_features.csv")

TARGET = "handle_min"
DATE_COLUMN = "date"
GROUP_COLUMN = "team"

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def normalize_text(value):
    """Normalize text to identify spelling variations."""
    if pd.isna(value):
        return ""

    value = str(value).strip().lower()
    value = value.translate(str.maketrans("", "", string.punctuation))
    return re.sub(r"\s+", " ", value)


def find_longest_runs(df, column):
    """Find consecutive equal readings after sorting by date."""

    dated = df[[DATE_COLUMN, column]].copy()
    dated[DATE_COLUMN] = pd.to_datetime(dated[DATE_COLUMN])
    dated = dated.sort_values(DATE_COLUMN).reset_index(drop=True)

    groups = dated[column].ne(dated[column].shift()).cumsum()

    runs = (
        dated.groupby(groups)
        .agg(
            value=(column, "first"),
            count=(column, "size"),
            start=(DATE_COLUMN, "min"),
            end=(DATE_COLUMN, "max")
        )
        .reset_index(drop=True)
    )

    runs["duration_days"] = (
        runs["end"] - runs["start"]
    ).dt.days

    return runs.sort_values(
        ["duration_days", "count"],
        ascending=False
    )


# --------------------------------------------------
# REPORT HEADER
# --------------------------------------------------

print("\n========== MP092 DATA QUALITY REPORT ==========")

print("Training rows:", len(train))
print("Later rows:", len(later))
print("Holdout rows:", len(holdout))

findings = {}

# --------------------------------------------------
# 1. LEAKING COLUMN
# --------------------------------------------------

print("\n1. LEAKING COLUMN")

leaking_candidates = []

for col in train.columns:

    if col == TARGET or col in holdout.columns:
        continue

    if pd.api.types.is_numeric_dtype(train[col]):

        correlation = train[col].corr(train[TARGET])

        print(
            f"{col}: target correlation = {correlation:.6f}"
        )

        if abs(correlation) >= 0.95:
            leaking_candidates.append({
                "column": col,
                "correlation": float(correlation)
            })

findings["leaking_column"] = leaking_candidates

print("Detected leaking columns:", leaking_candidates)


# --------------------------------------------------
# 2. UNIT MIXUP
# --------------------------------------------------

print("\n2. UNIT MIXUP")

unit_candidates = []

for col in train.select_dtypes(include="number").columns:

    if col == TARGET:
        continue

    print(f"\nColumn: {col}")

    stats = train.groupby(GROUP_COLUMN)[col].agg(
        ["min", "median", "mean", "max"]
    )

    print(stats)

    # Compare Team Gamma against the other teams
    if col == "agent_exp_months":

        gamma = train.loc[
            train[GROUP_COLUMN] == "Team Gamma", col
        ].dropna()

        other = train.loc[
            train[GROUP_COLUMN] != "Team Gamma", col
        ].dropna()

        if len(gamma) and len(other):

            ratio = gamma.median() / other.median()

            # Check whether Gamma values are consistently
            # multiples of the suspected conversion factor.
            divisible_by_30 = np.isclose(
                gamma % 30, 0
            ).all()

            scaled = gamma / 30

            scaled_ratio = (
                scaled.median() / other.median()
            )

            print("Gamma/other median ratio:", ratio)
            print("Gamma values divisible by 30:", divisible_by_30)
            print("Ratio after dividing Gamma by 30:", scaled_ratio)

            if divisible_by_30 and 0.8 <= scaled_ratio <= 1.2:

                unit_candidates.append({
                    "column": col,
                    "group": "Team Gamma",
                    "factor": 30
                })

findings["unit_mixup"] = unit_candidates

print("Detected unit mixups:", unit_candidates)


# --------------------------------------------------
# 3. SENTINEL VALUE
# --------------------------------------------------

print("\n3. SENTINEL VALUE")

sentinels = [-1, -999, 999, 9999]
sentinel_findings = []

for col in train.select_dtypes(include="number").columns:

    counts = train[col].value_counts()

    for value in sentinels:

        if value in counts.index:

            count = int(counts[value])

            print(
                f"{col}: sentinel {value}, count {count}"
            )

            sentinel_findings.append({
                "column": col,
                "value": int(value),
                "count": count
            })

findings["sentinel_value"] = sentinel_findings


# --------------------------------------------------
# 4. DUPLICATE ROWS
# --------------------------------------------------

print("\n4. DUPLICATE ROWS")

duplicates = int(train.duplicated().sum())

print("Extra duplicate rows:", duplicates)

findings["duplicate_rows"] = duplicates


# --------------------------------------------------
# 5. STUCK SENSOR
# --------------------------------------------------

print("\n5. STUCK SENSOR")

stuck_findings = []

dated_train = train.copy()
dated_train[DATE_COLUMN] = pd.to_datetime(
    dated_train[DATE_COLUMN]
)

for col in train.select_dtypes(include="number").columns:

    runs = find_longest_runs(dated_train, col)

    # Handbook describes a reading that stays constant
    # for multiple weeks. Use 14 days as the screening window.
    long_runs = runs[runs["duration_days"] >= 14]

    if not long_runs.empty:

        print(f"\nPossible stuck sensor: {col}")

        for _, run in long_runs.iterrows():

            result = {
                "column": col,
                "value": run["value"],
                "count": int(run["count"]),
                "start": str(run["start"].date()),
                "end": str(run["end"].date()),
                "duration_days": int(run["duration_days"])
            }

            print(result)
            stuck_findings.append(result)

    else:
        longest = runs.iloc[0]

        print(
            f"{col}: no constant run lasting 14 days. "
            f"Longest date span: {longest['duration_days']} days"
        )

findings["stuck_sensor"] = stuck_findings


# --------------------------------------------------
# 6. TARGET TYPOS
# --------------------------------------------------

print("\n6. TARGET TYPOS")

target = train[TARGET].dropna()

sorted_target = target.sort_values()

gaps = sorted_target.diff().dropna().sort_values(
    ascending=False
)

print("\nLargest target gaps:")
print(gaps.head(10))

print("\nLargest 20 target values:")
print(sorted_target.tail(20).to_list())

median_target = target.median()
maximum_target = target.max()

print("\nTarget median:", median_target)
print("Target maximum:", maximum_target)

# A candidate is at least 10 times the median and
# dividing it by 10 brings it into the observed range.
typo_mask = (
    (train[TARGET] >= 10 * median_target)
    & ((train[TARGET] / 10) <= maximum_target)
)

typo_candidates = train.loc[
    typo_mask,
    ["record_id", TARGET]
].copy()

print("\nPotential 10x target typo candidates:")
print(typo_candidates.to_string(index=False))

findings["target_typos"] = typo_candidates.to_dict(
    orient="records"
)


# --------------------------------------------------
# 7. SPELLING VARIANTS
# --------------------------------------------------

print("\n7. SPELLING VARIANTS")

spelling_findings = []

for col in train.select_dtypes(
    include=["object", "str"]
).columns:

    if col in ["record_id", DATE_COLUMN]:
        continue

    print(f"\nColumn: {col}")

    train_counts = train[col].value_counts(
        dropna=False
    )

    later_counts = later[col].value_counts(
        dropna=False
    ) if col in later.columns else pd.Series(dtype=int)

    print("Training values:")
    print(train_counts)

    print("Later values:")
    print(later_counts)

    # Later dataset supplies the clean reference spellings.
    clean_lookup = {}

    for value in later[col].dropna().unique():

        normalized = normalize_text(value)

        clean_lookup.setdefault(normalized, []).append(
            str(value)
        )

    variants = []

    for value in train[col].dropna().unique():

        normalized = normalize_text(value)

        matching = clean_lookup.get(normalized, [])

        if matching and str(value) not in matching:

            variants.append({
                "variant": str(value),
                "correct_spelling": matching[0]
            })

    if variants:

        result = {
            "column": col,
            "variants": variants,
            "true_levels": len(clean_lookup)
        }

        spelling_findings.append(result)

        print("Possible spelling variants:", variants)

findings["spelling_variants"] = spelling_findings


# --------------------------------------------------
# FINAL INVESTIGATION SUMMARY
# --------------------------------------------------

print("\n========== INVESTIGATION SUMMARY ==========")

summary = {
    "1. leaking_column": len(leaking_candidates) > 0,
    "2. unit_mixup": len(unit_candidates) > 0,
    "3. sentinel_value": len(sentinel_findings) > 0,
    "4. duplicate_rows": duplicates > 0,
    "5. stuck_sensor": len(stuck_findings) > 0,
    "6. target_typos": len(typo_candidates) > 0,
    "7. spelling_variants": len(spelling_findings) > 0
}

for name, present in summary.items():

    print(
        f"{name}: {'PRESENT' if present else 'ABSENT'}"
    )

print("\n========== END OF REPORT ==========")
