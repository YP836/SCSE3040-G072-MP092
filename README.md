# SCSE3040-G072-MP092

**SCSE3040 MLOps Mini Project — Group G072**

**Problem ID:** MP092  
**Problem:** Helpline Call Length Prediction (Nagpur)  
**Faculty:** Dhananjay Kumar  
**Batch:** 64

---

## 1. Project Overview

This project focuses on predicting helpline call handling time (`handle_min`) using call-related information.

The project follows an MLOps workflow covering data investigation, data preprocessing, model development, API development, deployment, monitoring and model lifecycle management.

## 2. Team Members & Roles

| Student ID | Name | Assigned Role |
|---|---|---|
| S24CSEU2668 | Yuvraj Pathania | Data Lead |
| S24CSEU2697 | Nirbhay Sisodia | Ops Lead |
| S24CSEU1730 | Shermin Reaz | Model Lead |
| S24CSEU2323 | Ayush Singh | Service Lead |

### Role Responsibilities

**Data Lead — Yuvraj Pathania**
- Data quality investigation.
- Data version control using DVC.
- Data cleaning and preprocessing.
- Identification of data leakage, unit mix-ups and sentinel values.
- Documentation of data findings.
- Preparation of cleaned datasets for model development.

**Ops Lead — Nirbhay Sisodia**
- Docker containerization.
- Kubernetes deployment and service configuration.
- Infrastructure and production operations.
- Model and service monitoring.
- Data drift detection.
- Retraining pipeline and model lifecycle management.

**Model Lead — Shermin Reaz**
- Machine learning model development.
- Model training and evaluation.
- Experiment tracking using MLflow.
- Model comparison and selection.
- Model registration.

**Service Lead — Ayush Singh**
- FastAPI application development.
- Prediction endpoint implementation.
- Input validation.
- Model and API integration.
- API testing and service functionality.

---

## 3. Project Structure

```text
SCSE3040-G072-MP092/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── reports/
│   └── findings.yaml
│
├── src/
│   └── mp092/
│       ├── __init__.py
│       ├── cleaning.py
│       └── data_checks.py
│
├── tests/
│   ├── test_cleaning.py
│   └── test_data_checks.py
│
├── README.md
├── requirements.txt
├── params.yaml
├── .gitignore
├── .dvc/
└── .dvcignore
```

Additional files and modules will be added as the Model, Service and Ops components are integrated.

---

## 4. Environment Setup

### Requirements

- Python 3.12
- Git
- DVC
- Required Python packages listed in `requirements.txt`

### Create a virtual environment

```powershell
python -m venv .venv
```

### Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
python -m pip install -r requirements.txt
```

---

## 5. Data Quality Investigation

The Data Lead implemented seven data-quality investigations:

1. **Leaking Column:** Identifies post-event information that can cause target leakage.
2. **Unit Mix-up:** Detects inconsistent measurement units between groups.
3. **Sentinel Value:** Identifies special values used to represent missing or invalid data.
4. **Duplicate Rows:** Checks for duplicate records.
5. **Stuck Sensor:** Identifies readings that remain constant over an extended period.
6. **Target Typos:** Screens for target values that may have been entered at an incorrect scale.
7. **Spelling Variants:** Identifies inconsistent categorical spellings.

### Run the investigation

```powershell
python src/mp092/data_checks.py
```

### Findings

The investigation identified:

| Issue | Finding |
|---|---|
| Leaking column | `duration_from_phone_bill` |
| Unit mix-up | `agent_exp_months` in Team Gamma, factor 30 |
| Sentinel value | `issue_count = -999`, 47 rows |
| Duplicate rows | None detected |
| Stuck sensor | None detected using the 14-day screening threshold |
| Target typos | No potential 10× candidates detected |
| Spelling variants | None detected |

Detailed findings are recorded in:

`reports/findings.yaml`

---

## 6. Data Cleaning Pipeline

The cleaning pipeline is implemented in:

`src/mp092/cleaning.py`

### Run data cleaning

```powershell
python src/mp092/cleaning.py
```

### Input datasets

- `data/raw/train.csv`
- `data/raw/later.csv`
- `data/raw/holdout_features.csv`

### Cleaning operations

- Remove exact duplicate records.
- Convert `agent_exp_months` into a numeric floating-point format.
- Correct Team Gamma's training experience values using a factor of 30.
- Replace `-999` sentinel values in `issue_count` with missing values.
- Remove `duration_from_phone_bill` because it contains post-call information and causes target leakage.
- Preserve the normal experience scale in the later and holdout datasets.

### Output datasets

The cleaned datasets are generated in:

`data/processed/`

- `train_clean.csv`
- `later_clean.csv`
- `holdout_features_clean.csv`

---

## 7. Data Version Control (DVC)

DVC is used to track the raw training and later datasets.

### Check DVC status

```powershell
dvc status
```

The raw datasets are tracked using their corresponding `.dvc` files.

---

## 8. Automated Testing

Automated tests are implemented using pytest.

### Run all tests

```powershell
python -m pytest tests/ -v
```

### Current data-related test coverage

**Cleaning tests (`test_cleaning.py`):**
- Sentinel replacement.
- Team Gamma unit correction.
- Leakage column removal.
- Duplicate row removal.

**Data investigation tests (`test_data_checks.py`):**
- Leakage detection.
- Unit mix-up detection.
- Sentinel detection.
- Duplicate row verification.
- Target typo screening.
- Spelling variant verification.

**Latest verified result:** 10 data-related tests passed.

Additional service and integration tests will be included as the remaining project components are developed.

---

## 9. Project Workflow

The overall project follows these stages:

1. Data investigation and data versioning.
2. Data cleaning and preprocessing.
3. Machine learning model development and evaluation.
4. Prediction API development.
5. Containerization and deployment.
6. Monitoring, drift detection and retraining.

---

## 10. Project Repository

**GitHub Repository:**

https://github.com/YP836/SCSE3040-G072-MP092

---

**Group G072 — SCSE3040 MLOps Mini Project**