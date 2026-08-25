# Aadhaar Analytics Dashboard

**ML-powered analytics platform for Aadhaar enrollment & update trends across India.**  
Analyzes ~5M records spanning enrollment, demographic, and biometric data — with interactive dashboards, multi-model predictions, quantile forecasting, anomaly detection, and MLOps drift monitoring.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=flat-square)](https://streamlit.io)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.0-9ACD32?style=flat-square)](https://lightgbm.readthedocs.io)
[![XGBoost](https://img.shields.io/badge/XGBoost-1.7-orange?style=flat-square)](https://xgboost.readthedocs.io)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-EE4C2C?style=flat-square)](https://pytorch.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square)](https://docker.com)
[![GCP Cloud Run](https://img.shields.io/badge/GCP-Cloud%20Run-4285F4?style=flat-square)](https://cloud.google.com/run)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## Overview

Built for the **UIDAI Aadhaar Hackathon**, this project addresses the challenge of uncovering societal trends in Aadhaar enrollment and update data. The system turns raw government datasets into actionable intelligence — from capacity planning to anomaly response.

**Demo:** [YouTube walkthrough](https://youtu.be/293kr7-k5S4?si=VvmeDya12exBM5JB)

---

## Application Modules (5 Tabs)

### 1. Executive Dashboard
- KPI cards: total enrollments, unique states, daily average, data span
- Daily enrollment time-series with rolling 30-day average
- Top 10 states by enrollment (horizontal bar chart)
- Age group demographics pie chart
- CSV export of filtered data

### 2. Geospatial & EDA
- India state-level GIS density map (Plotly `scatter_geo`)
- Day-of-week seasonality box plots
- Cross-shard feature correlation heatmap

### 3. ML Model Leaderboard & MLOps Drift
- Model benchmark leaderboard table (R², RMSE, MAE)
- Test R² comparison bar chart across all 5 trained models
- Kolmogorov-Smirnov (KS) test + Population Stability Index (PSI) feature drift monitoring
- CSV leaderboard exporter

### 4. Live Forecast Predictor with Quantile Bounds
- Real-time inference engine for 1–30 day forecasting horizon
- P10 lower bound, P50 median prediction, P90 upper bound with shaded confidence intervals
- Configurable state and feature inputs

### 5. Anomaly Alert Engine
- Z-score spike detector across enrollment time-series
- Interactive webhook alert payload simulator (Slack / Email)
- CSV anomaly log exporter

---

## Machine Learning & Deep Learning Benchmark Results

Models are evaluated using an **80/20 chronological time-series split** (training on historical dates and validating on unseen future dates).

### Model Suite A: Operational System Load (`total_system_load`)
> **Primary Use Case:** Forecasting Aadhaar center traffic, biometric scanner throughput, and operator counter staffing for saturated/maintenance states (where updates account for >85% of traffic).

| Model Architecture | Train $R^2$ | Train RMSE | Train MAE | Test $R^2$ | Test RMSE | Test MAE | Primary Operational Role |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **Ensemble A** *(Meta-Blend)* 🥇 | — | — | — | **0.7422** | **13,108** | **6,453** | **Primary Ops Routing** (Center Staffing & Servers) |
| **LightGBM (A)** 🥈 | **0.9541** | 30,111 | 9,842 | **0.7333** | 13,334 | 6,481 | High-speed gradient boosting on rolling/lag features |
| **Random Forest (A)** 🥉 | **0.8498** | 54,436 | 14,210 | **0.7152** | 13,778 | 6,956 | Bagged decision tree ensemble |
| **XGBoost (A)** | **0.9476** | 32,163 | 10,120 | **0.7071** | 13,973 | 6,601 | Regularized gradient boosted decision trees |
| **Ridge Baseline (A)** | -3.1426 | 285,927 | 78,340 | **0.0113** | 25,672 | 13,762 | Linear baseline for total workload |

---

### Model Suite B & Deep Learning: New Enrolments (`total_enrolments`)
> **Primary Use Case:** Forecasting new registrations and child enrolment backlogs for growth states (UP, Bihar, Assam, Meghalaya).

| Model Architecture | Train $R^2$ | Train RMSE | Train MAE | Test $R^2$ | Test RMSE | Test MAE | Primary Operational Role |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **PyTorch LSTM + Attention** 🧠 | **0.1134** | 2,120 | 854 | **0.1649** | **1,939** | **912** | **Deep Sequence**: 14-day sliding context window |
| **Ensemble B (Enrolments)** | — | — | — | **-0.0737** | 2,505 | 892 | Inverse-RMSE blended tree predictor |
| **LightGBM (B)** | **0.9704** | 850 | 290 | -0.1405 | 2,582 | 908 | Tree baseline for new registrations |
| **Random Forest (B)** | **0.4820** | 3,557 | 1,120 | -0.1405 | 2,582 | 908 | Balanced depth tree ensemble |
| **XGBoost (B)** | **0.9724** | 822 | 275 | -0.1406 | 2,582 | 908 | Tree baseline with L2 shrinkage |

> **Key Feature Engineering**: 79 temporal, holiday decay, lag, rolling statistical, population quintile, and system velocity features. Target variables are `log1p`-transformed to stabilize variance across states of vastly different populations. All trained weights and scalers are persisted in [`pkl_models/`](pkl_models/).

---

## Quickstart

### Local Execution
```bash
git clone https://github.com/KunjShah95/aadhar-hackathon1.git
cd aadhar-hackathon1
pip install -r requirements.txt
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### Docker
```bash
docker build -t aadhaar-analytics .
docker run -p 8080:8080 aadhaar-analytics
```
Open [http://localhost:8080](http://localhost:8080) in your browser.

---

## Project Structure

```
aadhar-hackathon1/
│
├── app.py                               # Streamlit Web App (Interactive intelligence dashboard)
├── train_models.py                      # Unified ML & Deep Learning (Ridge, RF, XGB, LGBM, Stacking, LSTM)
├── mlops_pipeline.py                    # Automated KS + PSI drift monitoring & model health audit
│
├── pkl_models/                          # Pre-trained model artifacts & metrics
│   ├── best_model.pkl                   # LightGBM best model
│   ├── lightgbm_model.pkl
│   ├── xgboost_model.pkl
│   ├── random_forest_model.pkl
│   ├── ridge_baseline_model.pkl
│   ├── ensemble_meta.pkl                # Stacking ensemble meta-learner
│   ├── lstm_model.pt                    # PyTorch LSTM weights
│   ├── lstm_scaler.pkl                  # Fitted LSTM feature scaler
│   ├── lstm_feature_cols.json           # Sequence feature definitions
│   ├── feature_metadata.json            # Feature names & engineering config
│   ├── model_comparison.json            # Benchmark metrics
│   └── mlops_drift_report.json          # KS + PSI drift audit results
│
├── api_data_aadhar_enrolment/           # Enrollment CSV shards (~1M rows)
├── api_data_aadhar_demographic/         # Demographic CSV shards (~2M rows)
├── api_data_aadhar_biometric/           # Biometric CSV shards (~1.8M rows)
│
├── cleaned_aadhaar_data.csv             # Unified panel dataset
├── cleaned_aadhaar_monthly_national.csv # Monthly national aggregations
├── cleaned_aadhaar_summary_by_state.csv # State-level total enrollments
│
├── Dockerfile                           # Production container (PORT 8080)
├── requirements.txt                     # Python dependencies
├── deploy_to_gcp.bat                    # One-click GCP Cloud Run deploy (Windows)
├── deploy_to_gcp.sh                     # One-click GCP Cloud Run deploy (Linux/macOS)
└── PROJECT_REPORT.md                    # Technical deep-dive & architecture
```

---

## Cloud Deployment

### Google Cloud Run

**Prerequisites**: Enable billing at [console.cloud.google.com/billing](https://console.cloud.google.com/billing) (offers **$300 free credits**).

**Option A — One-Click Script (Windows):**
```cmd
deploy_to_gcp.bat
```

**Option B — Manual gcloud command:**
```bash
gcloud run deploy aadhaar-analytics-app \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080
```

**Always Free Cloud Run Tier** (after free trial):
- 2 Million Requests / month
- 360,000 GB-seconds memory / month
- 180,000 vCPU-seconds / month

### Other Free Cloud Options

| Platform | Free Tier | Notes |
|---|---|---|
| **Streamlit Community Cloud** | 1 GB RAM, unlimited apps | Easiest — 1-click GitHub deploy |
| **Hugging Face Spaces** | **16 GB RAM CPU** | Best for PyTorch LSTM models |
| **Oracle Cloud (OCI)** | 4 vCPUs + 24 GB RAM forever | Most generous always-free tier |
| **Render** | 512 MB, sleeps on inactivity | Uses existing Dockerfile |

---

## MLOps — Drift Monitoring

Run the automated drift audit script after collecting new inference data:

```bash
python mlops_pipeline.py
```

This calculates:
- **Kolmogorov-Smirnov (KS) Test** — detects distribution shift per feature
- **Population Stability Index (PSI)** — flags features with PSI > 0.2 for retraining alerts

Results are saved to `pkl_models/mlops_drift_report.json` and visualized in the **ML Leaderboard & MLOps Drift** tab of the Streamlit app.

---

## Model Training & Automation

The entire data engineering, feature generation, model training, and artifact export pipeline is consolidated into [`train_models.py`](train_models.py):

```bash
# Run full training pipeline (Tabular models + Stacking Ensemble + PyTorch LSTM)
python train_models.py

# Run tabular models only (fast mode)
python train_models.py --skip-lstm
```

To run the automated MLOps drift audit and model health check:
```bash
python mlops_pipeline.py
```

---

## Key Insights

- **Top states** (UP, Bihar, Maharashtra) account for a disproportionate share of enrollments; CV across states is 42%.
- **Age 18+** makes up 55% of enrollments; child enrollment (0–17) is an underserved segment.
- **Mid-week peaks** (Tue–Thu) with ~20% dip on weekends — actionable for staffing.
- **Biometric updates** lag demographic updates (38% vs 62%) — a target for awareness campaigns.
- **847 anomalies** detected (5.2% of data), 22% high-severity — indicating localized campaign spikes or data issues.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Data & ML** | Python 3.11, Pandas, NumPy, Scikit-learn, XGBoost, LightGBM |
| **Deep Learning** | PyTorch 2.0 (LSTM Time-Series) |
| **Dashboard** | Streamlit 1.28+, Plotly |
| **MLOps** | KS-test, PSI drift monitoring (`mlops_pipeline.py`) |
| **Containerization** | Docker (Python 3.11-slim, PORT 8080) |
| **Cloud** | GCP Cloud Run (`asia-south1`) |

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `FileNotFoundError: best_model.pkl` | `pkl_models/` not cloned | Pull latest Git (`pkl_models/` is now tracked) |
| `ValueError: X has N features, expecting M` | Feature mismatch | Check `pkl_models/feature_metadata.json` |
| `MemoryError` | Dataset too large | Process CSVs in batches; close other apps |
| GCP billing error | Billing not enabled | Enable at [console.developers.google.com/billing](https://console.developers.google.com/billing/enable?project=vortex-arena-ai-92843) |

---

## License

MIT — built for the UIDAI Aadhaar Hackathon.

---

## Acknowledgements

- **UIDAI** for dataset availability and problem framing
- Scikit-learn, XGBoost, LightGBM, PyTorch, Streamlit, and Plotly open-source communities
