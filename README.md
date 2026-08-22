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

## Machine Learning Models

| Model | Test R² | Test RMSE | Test MAE | Notes |
|---|---|---|---|---|
| **Ensemble** 🥇 | **0.3817** | 1,437 | 490 | Inverse-RMSE blend of all 4 base models |
| Ridge Baseline | 0.3550 | 1,468 | 496 | Raw target + StandardScaler |
| LightGBM | 0.2885 | 1,542 | 506 | log1p target |
| XGBoost | 0.2753 | 1,556 | 507 | log1p target |
| LSTM (PyTorch) | 0.1970 | 1,610 | 622 | PyTorch seq2one, log1p target |
| Random Forest | 0.1879 | 1,647 | 594 | Raw target + StandardScaler |

> **All 6 models (including Ensemble) generalise positively** on the temporal test split (Oct–Dec 2025). Key engineering: India 2025 holiday calendar features (is_holiday, days_to_holiday, holiday_proximity); 2021 census state population features; log1p target for gradient boosting; StandardScaler + raw target for Ridge/RF; inverse-RMSE ensemble weighting.

**Top predictive features** (SHAP — LightGBM): `rolling_mean_30`, `lag_1`, `days_since_start`, `state_mean_enrol`, `holiday_proximity`, `lag_1_per_1000`

All model artifacts are pre-trained and committed to the `pkl_models/` directory, so the app loads instantly without re-training.

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
├── app.py                               # Streamlit app (5-tab dashboard)
│
├── 01_Exploratory_Data_Analysis.ipynb   # Self-contained EDA notebook
├── 02_Model_Training_and_Evaluation.ipynb # Self-contained model training notebook
├── 03_LSTM_Time_Series_Forecasting.ipynb  # Self-contained LSTM PyTorch notebook
│
├── mlops_pipeline.py                    # Automated KS + PSI drift monitoring script
│
├── pkl_models/                          # All pre-trained model artifacts (Git-tracked)
│   ├── best_model.pkl                   # LightGBM best model (auto-loaded)
│   ├── lightgbm_model.pkl
│   ├── xgboost_model.pkl
│   ├── random_forest_model.pkl
│   ├── ridge_baseline_model.pkl
│   ├── baseline_ridge_model.pkl
│   ├── lstm_model.pt                    # PyTorch LSTM weights
│   ├── feature_metadata.json            # Feature names & engineering config
│   ├── model_comparison.json            # Benchmark metrics
│   ├── model_report.json                # Detailed model report
│   └── mlops_drift_report.json          # KS + PSI drift audit results
│
├── api_data_aadhar_enrolment/           # Enrollment CSVs (~1M rows) [git-ignored]
├── api_data_aadhar_demographic/         # Demographic CSVs (~2M rows) [git-ignored]
├── api_data_aadhar_biometric/           # Biometric CSVs (~1.8M rows) [git-ignored]
│
├── Dockerfile                           # Production container (PORT 8080)
├── .dockerignore
├── .streamlit/config.toml               # Streamlit headless server config
├── requirements.txt                     # Pinned Python dependencies
│
├── deploy_to_gcp.bat                    # One-click GCP Cloud Run deploy (Windows)
├── deploy_to_gcp.sh                     # One-click GCP Cloud Run deploy (Linux/macOS)
│
├── PROJECT_REPORT.md                    # Technical deep-dive & future roadmap
├── .gitignore                           # Ignores raw CSVs only; .pkl files are tracked
└── README.md
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

## Notebooks

All notebooks are **100% self-contained** — no external `.py` modules required.

| Notebook | Description |
|---|---|
| [`01_Exploratory_Data_Analysis.ipynb`](01_Exploratory_Data_Analysis.ipynb) | Data loading, state normalization, EDA visualizations |
| [`02_Model_Training_and_Evaluation.ipynb`](02_Model_Training_and_Evaluation.ipynb) | Feature engineering, Ridge/RF/XGBoost/LightGBM training, exports to `pkl_models/` |
| [`03_LSTM_Time_Series_Forecasting.ipynb`](03_LSTM_Time_Series_Forecasting.ipynb) | PyTorch LSTM training for time-series forecasting, exports `lstm_model.pt` |

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
