# SCSE3040-G072-MP092

**SCSE3040 MLOps Mini Project — Group G072**

## Problem: MP092 — Helpline Call Length Prediction

This project predicts helpline call handling time (`handle_min`) using call-related information.

## Project Structure

```text
SCSE3040-G072-MP092/
├── data/
│   ├── raw/
│   └── processed/
├── reports/
│   └── findings.yaml
├── src/
│   └── mp092/
│       ├── __init__.py
│       ├── cleaning.py
│       └── data_checks.py
├── tests/
│   ├── test_cleaning.py
│   └── test_data_checks.py
├── README.md
└── requirements.txt
```

## Setup

Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install project dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Data Quality Investigation

Run the seven data-quality investigations:

```powershell
python src/mp092/data_checks.py
```

The investigation checks:

1. Leaking columns
2. Unit mix-ups
3. Sentinel values
4. Duplicate rows
5. Stuck sensors
6. Target typos
7. Spelling variants

The findings are documented in `reports/findings.yaml`.

## Data Cleaning

Run the cleaning pipeline:

```powershell
python src/mp092/cleaning.py
```

The pipeline processes:

- `data/raw/train.csv`
- `data/raw/later.csv`
- `data/raw/holdout_features.csv`

Cleaned datasets are saved in `data/processed/`.

### Data Cleaning Decisions

- Remove duplicate records.
- Convert Team Gamma's `agent_exp_months` values in the training dataset using a factor of 30.
- Replace `-999` in `issue_count` with missing values.
- Remove `duration_from_phone_bill` because it contains post-call information and causes target leakage.
- Do not apply the Gamma unit correction to later or holdout data because those datasets already use the normal scale.

## Automated Tests

Run the tests:

```powershell
python -m pytest tests/ -v
```

The current data-related tests cover cleaning operations and the identified data-quality findings.

## Data Version Control

Raw training and later datasets are tracked using DVC.

Check DVC status:

```powershell
dvc status
```

## Data Lead

The Data Lead is responsible for data-quality investigation, data cleaning, DVC tracking and documenting data findings.
