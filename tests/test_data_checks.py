
from pathlib import Path
import runpy

import pandas as pd


# Run the actual data investigation script.
ROOT = Path(__file__).resolve().parents[1]

results = runpy.run_path(
    str(ROOT / "src" / "mp092" / "data_checks.py"),
    run_name="data_checks_test"
)

findings = results["findings"]


def test_leaking_column_is_detected():
    assert any(
        item["column"] == "duration_from_phone_bill"
        for item in findings["leaking_column"]
    )


def test_gamma_unit_mixup_is_detected():
    assert any(
        item["column"] == "agent_exp_months"
        and item["group"] == "Team Gamma"
        and item["factor"] == 30
        for item in findings["unit_mixup"]
    )


def test_sentinel_value_is_detected():
    assert any(
        item["column"] == "issue_count"
        and item["value"] == -999
        and item["count"] == 47
        for item in findings["sentinel_value"]
    )


def test_no_duplicate_rows_are_reported():
    assert findings["duplicate_rows"] == 0


def test_no_target_typos_are_reported():
    assert findings["target_typos"] == []


def test_no_spelling_variants_are_reported():
    assert findings["spelling_variants"] == []
