
import pandas as pd

from src.mp092.cleaning import clean_data


def sample_data():
    return pd.DataFrame({
        "record_id": [1, 2, 3],
        "team": ["Team Alpha", "Team Gamma", "Team Beta"],
        "agent_exp_months": [24, 930, 36],
        "issue_count": [2, -999, 3],
        "duration_from_phone_bill": [10.5, 12.0, 8.5],
        "handle_min": [10.0, 12.0, 8.0],
    })


def test_sentinel_value_is_replaced():
    cleaned, _ = clean_data(sample_data())

    assert pd.isna(cleaned.loc[1, "issue_count"])
    assert not (cleaned["issue_count"] == -999).any()


def test_gamma_unit_correction():
    cleaned, _ = clean_data(
        sample_data(),
        correct_gamma_units=True
    )

    assert cleaned.loc[1, "agent_exp_months"] == 31
    assert cleaned.loc[0, "agent_exp_months"] == 24


def test_leakage_column_is_removed():
    cleaned, _ = clean_data(sample_data())

    assert "duration_from_phone_bill" not in cleaned.columns


def test_duplicate_rows_are_removed():
    df = sample_data()
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)

    cleaned, original_rows = clean_data(df)

    assert original_rows == 4
    assert len(cleaned) == 3
