# Aadhaar Intelligence Engine

**Dual-model ML platform for Aadhaar enrollment & system-load analytics across India's 36 states and UTs.**  
Turns raw UIDAI datasets into actionable intelligence — capacity planning, policy alerts, anomaly detection, and MLOps drift monitoring.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=flat-square)](https://streamlit.io)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.0-9ACD32?style=flat-square)](https://lightgbm.readthedocs.io)
[![XGBoost](https://img.shields.io/badge/XGBoost-1.7-orange?style=flat-square)](https://xgboost.readthedocs.io)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-EE4C2C?style=flat-square)](https://pytorch.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## Overview

Built for the **UIDAI Aadhaar Hackathon**, this project addresses the challenge of uncovering societal trends in Aadhaar enrollment and update data. The system routes predictions through two purpose-built model suites depending on the operational context.

**Demo:** [YouTube walkthrough](https://youtu.be/293kr7-k5S4?si=VvmeDya12exBM5JB)

---

## Two-Model Architecture

India's Aadhaar ecosystem has two distinct regimes requiring separate models:

| | Model Suite A | Model Suite B |
|---|---|---|
| **Regime** | Maintenance (80%+ saturation) | Growth (new enrolments) |
| **Target** | `total_system_load` | `total_enrolments` |
| **States** | All 36 | Growth-focused states |
| **Ensemble R²** | **0.747** | **0.371** |
| **Use case** | Capacity planning, staffing | Policy alerts, mobile camps |

### Why two models?
- **Model A**: Biometric/demographic updates dominate traffic. Highly predictable with lag/rolling features.
- **Model B**: Raw enrolments are bursty and state-scale-variant (UP: 1M+/day vs Sikkim: <1000/day). Model B trains on per-state relative values (`enrolments / state_mean`) then inverse-transforms predictions — eliminates scale variance as the dominant noise source.

---

## Application (7 Tabs)

### Tab 1 · Executive Dashboard
- KPI cards: total enrolments, unique states, daily average, data span
- Daily enrolment time-series with rolling 30-day average
- Top 10 states by enrolment (bar chart)
- Age group demographics pie chart
- CSV export of filtered data

### Tab 2 · Geospatial & EDA
- India state-level density map (Plotly `scatter_geo`)
- Day-of-week seasonality box plots
- Cross-feature correlation heatmap

### Tab 3 · Demographic Deep Dive
- Per-state age-group breakdowns
- Biometric vs. demographic update ratios
- Population-normalized enrolment rates

### Tab 4 · ML Model Leaderboard & MLOps Drift
- Model benchmark table (R², RMSE, MAE) for all trained models
- KS-test + Population Stability Index (PSI) feature drift monitoring
- CSV leaderboard export

### Tab 5 · Live Forecast Predictor
- Real-time inference — 1–30 day horizon
- P10 / P50 / P90 quantile bounds with shaded confidence intervals
- State selector + lifecycle stage routing (Model A vs B)

### Tab 6 · Anomaly Alert Engine
- Z-score spike detection across enrolment time-series
- IsolationForest ensemble anomaly scoring
- Webhook alert payload simulator (Slack / Email)
- CSV anomaly log export

### Tab 7 · Policy Intelligence (Two-Module)
- **Module 1 – Operations**: Model A predicts system load per state; flags 90th-percentile overload states
- **Module 2 – Migration**: Model B predicts enrolment levels for growth states; drives mobile camp and awareness campaign allocation

---

## Benchmark Results

**80/20 chronological time-series split** (train on past, evaluate on unseen future dates).

| Model | Target | Test R² | Test RMSE |
|---|---|---|---|
| **Ensemble A** | total_system_load | **0.747** | 12,982 |
| LightGBM (A) | total_system_load | 0.738 | 13,206 |
| XGBoost (A) | total_system_load | 0.724 | 13,570 |
| Random Forest (A) | total_system_load | 0.709 | 13,923 |
| **Ensemble B** | total_enrolments | **0.371** | 1,917 |
| LightGBM (B) | total_enrolments | 0.225 | — |
| XGBoost (B) | total_enrolments | 0.216 | — |
| Random Forest (B) | total_enrolments | 0.151 | — |
| LSTM (PyTorch) | total_enrolments | −0.372 | 3,501 |

> Model B individual scores are on the relative (ratio) scale. Ensemble B RMSE is after inverse-transforming back to absolute counts.

---

## Feature Engineering (79 features, shared pipeline)

Each state's daily record is enriched with:

| Group | Features |
|---|---|
| Calendar | day_of_week, day_of_month, month, quarter, day_of_year, is_weekend |
| Cyclical | sin/cos DOW, sin/cos month |
| Population | log_state_pop, state_pop_tier, state_cat |
| Holidays | is_holiday, days_to_holiday, days_since_holiday, holiday_proximity, holiday_recency |
| Lags | lag_1/3/7/14/30 (enrolments + bio + demo) |
| Rolling stats | rolling_mean/std 3/7/14/30 (enrolments + load + bio + demo) |
| Velocity | ewm_7, ewm_trend, mom_growth, system_velocity, rolling_cv_7 |
| Ratios | bio_to_enrol_ratio, demo_to_enrol_ratio, per-1000 variants |
| State stats | state_mean_enrol, state_std_enrol, state_median_enrol |

**Model B additionally:**
- Purges `load_lag_*` / `load_rolling_*` (Model A target leakage)
- Selects top 30 features by LightGBM importance (prevents overfit on sparse data)
- Trains on 7-day smoothed relative target

---

## Quick Start

```bash
# Clone
git clone https://github.com/KunjShah95/aadhar-hackathon.git
cd aadhar-hackathon

# Install dependencies
pip install -r requirements.txt

# Train models (full pipeline incl. LSTM)
python train_models.py

# Train without LSTM (fast mode)
python train_models.py --skip-lstm

# Launch dashboard
streamlit run app.py
```

---

## Model Training

```bash
# Full pipeline: tabular ensembles + PyTorch LSTM
python train_models.py

# Fast mode: skip LSTM
python train_models.py --skip-lstm

# Custom LSTM settings
python train_models.py --epochs 50 --lookback 21
```

Artifacts saved to `pkl_models/`:

| File | Contents |
|---|---|
| `modelA_ensemble_meta.pkl` | Model A weights, feature list, scaler ref |
| `ensemble_meta.pkl` | Model B weights, top-30 feature list, relative_target flag |
| `state_norm_params.csv` | Per-state mean enrolment for inverse-transform |
| `state_stats.csv` | Per-state mean/std/median for feature engineering |
| `feature_metadata.json` | Full feature list, pipeline version, split date |
| `model_comparison.json` | Benchmark results for all models |
| `lstm_model.pt` | PyTorch LSTM checkpoint |

---

## MLOps — Drift Monitoring

```bash
python mlops_pipeline.py
```

Calculates:
- **Kolmogorov-Smirnov (KS) Test** — distribution shift per feature
- **Population Stability Index (PSI)** — PSI > 0.25 triggers retraining alert

Results saved to `pkl_models/mlops_drift_report.json` and visualized in Tab 4.

---

## Project Structure

```
.
├── app.py                    # Streamlit dashboard (7 tabs)
├── train_models.py           # Full dual-model training pipeline (v3)
├── mlops_pipeline.py         # KS + PSI drift monitoring
├── requirements.txt
├── Dockerfile
├── pkl_models/
│   ├── modelA_*.pkl          # Model Suite A (system load)
│   ├── ensemble_meta.pkl     # Model Suite B ensemble
│   ├── state_norm_params.csv # Per-state enrolment normalization
│   ├── state_stats.csv       # Per-state feature stats
│   ├── feature_metadata.json
│   ├── model_comparison.json
│   └── lstm_model.pt
└── api_data_aadhar_enrolment/
    └── **/*.csv              # Raw UIDAI CSV shards
```

---

## Deployment

### Docker

```bash
docker build -t aadhaar-engine .
docker run -p 8501:8501 aadhaar-engine
```

### GCP Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/aadhaar-engine
gcloud run deploy aadhaar-engine \
  --image gcr.io/PROJECT_ID/aadhaar-engine \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080
```

### Free Hosting Options

| Platform | Free Tier | Notes |
|---|---|---|
| **Streamlit Community Cloud** | 1 GB RAM, unlimited apps | Easiest — 1-click GitHub deploy |
| **Hugging Face Spaces** | 16 GB RAM CPU | Best for PyTorch LSTM |
| **Oracle Cloud (OCI)** | 4 vCPUs + 24 GB RAM forever | Most generous always-free tier |
| **Render** | 512 MB, sleeps on inactivity | Uses existing Dockerfile |

---

## Key Insights

- **Top 3 states** (UP, Bihar, Maharashtra) account for a disproportionate share of enrolments; CV across states is ~42%.
- **Age 18+** makes up ~55% of enrolments; child enrollment (0–17) is an underserved segment.
- **Mid-week peaks** (Tue–Thu) with ~20% dip on weekends — actionable for staffing.
- **Biometric updates** lag demographic updates (38% vs 62%) — a target for awareness campaigns.
- Anomaly detection flags localized campaign spikes and data quality issues automatically.

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `ValueError: X has N features, expecting M` | Stale pkl vs new feature pipeline | Re-run `python train_models.py` |
| `KeyError: norm_state` | Raw CSV missing `state` column | Check CSV shard format |
| Predictions all zero | Old notebook-trained pkl loaded | Re-run `python train_models.py` |
| `MemoryError` | Dataset too large | Process CSVs in batches |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Data & ML** | Python 3.11, Pandas, NumPy, Scikit-learn, XGBoost, LightGBM |
| **Deep Learning** | PyTorch 2.0 (LSTM + Attention) |
| **Dashboard** | Streamlit 1.28+, Plotly |
| **MLOps** | KS-test, PSI drift monitoring |
| **Containerization** | Docker (Python 3.11-slim) |
| **Cloud** | GCP Cloud Run (`asia-south1`) |

---

## License

MIT — built for the UIDAI Aadhaar Hackathon.

---

## Acknowledgements

- **UIDAI** for dataset availability and problem framing
- Scikit-learn, XGBoost, LightGBM, PyTorch, Streamlit, and Plotly open-source communities
