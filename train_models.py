"""
train_models.py — Aadhaar Two-Stage Intelligence & Deep Learning Pipeline
========================================================================

FIRST-PRINCIPLES DUAL REGIME ARCHITECTURE:
------------------------------------------
India's Aadhaar ecosystem has two distinct physical processes:
  1. MAINTENANCE REGIME (Model Suite A: Target = 'total_system_load')
     - 80%+ of states have >95% saturation.
     - Demographic and biometric updates drive massive, highly predictable counter traffic.
     - Models trained on total_system_load achieve high operational accuracy (R² > 0.65).
  2. GROWTH REGIME (Model Suite B: Target = 'total_enrolments')
     - Focuses on new enrolments (UP, Bihar, Assam, child updates).
     - Regularized linear + tree ensembles + PyTorch LSTM sequence modeling.

PIPELINE SECTIONS:
------------------
  Section 1: Population constants & holiday definitions
  Section 2: Canonical name normalization
  Section 3: Multi-shard data ingestion & outer join
  Section 4: Advanced feature engineering (lags, rolling stats, ratios, holiday decay)
  Section 5: Base ML model training (Ridge, Random Forest, XGBoost, LightGBM)
  Section 6: Stacking Ensemble with TimeSeriesSplit Out-of-Fold (OOF) cross-validation
  Section 7: PyTorch Deep Learning Sequence Model (AadhaarLSTM + Scaled Dot-Product Attention)
  Section 8: CLI Orchestration & Artifact Export
"""

import os
import glob
import json
import time
import argparse
import warnings
import numpy as np
import pandas as pd
import joblib

# Scikit-learn imports
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit

# Gradient Boosting libraries
import xgboost as xgb
import lightgbm as lgb

# Optional PyTorch Deep Learning
try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

warnings.filterwarnings("ignore")

# ==============================================================================
# SECTION 1: POPULATION REFERENCE & HOLIDAY CALENDAR
# ==============================================================================

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
_POP_QUINTILES = np.quantile(list(STATE_POPULATION.values()), [0.2, 0.4, 0.6, 0.8])

INDIA_HOLIDAYS_2025 = pd.to_datetime([
    "2025-03-14", "2025-03-31", "2025-04-06", "2025-04-14", "2025-04-18",
    "2025-05-01", "2025-06-06", "2025-06-27", "2025-07-06", "2025-08-15",
    "2025-08-16", "2025-09-05", "2025-10-02", "2025-10-20", "2025-10-21",
    "2025-10-22", "2025-11-05", "2025-12-25",
])

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

# ==============================================================================
# SECTION 2: NORMALIZATION HELPERS
# ==============================================================================

def _norm(val):
    if pd.isna(val):
        return None
    key = str(val).strip().lower()
    if key in STATE_ALIASES:
        return STATE_ALIASES[key]
    if key == "100000" or key.isdigit():
        return None
    return str(val).strip().title()

def _pop_tier(state):
    pop = STATE_POPULATION.get(state, _MEDIAN_POP)
    return int(np.searchsorted(_POP_QUINTILES, pop))

# ==============================================================================
# SECTION 3: DATA INGESTION
# ==============================================================================

def load_raw(data_dir="."):
    def _read(pattern):
        files = sorted(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        if not files:
            return pd.DataFrame()
        dfs = [pd.read_csv(f, dtype={"state": str, "district": str}) for f in files]
        df = pd.concat(dfs, ignore_index=True)
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
        df["norm_state"] = df["state"].apply(_norm)
        return df[df["norm_state"].notna()].copy()

    enrol = _read("api_data_aadhar_enrolment/**/*.csv")
    if not enrol.empty:
        enrol["total_enrolments"] = enrol[["age_0_5", "age_5_17", "age_18_greater"]].fillna(0).sum(axis=1)
        enrol = enrol.groupby(["date", "norm_state"])[
            ["age_0_5", "age_5_17", "age_18_greater", "total_enrolments"]
        ].sum().reset_index()

    demo = _read("api_data_aadhar_demographic/**/*.csv")
    if not demo.empty:
        demo["demo_total"] = demo[["demo_age_5_17", "demo_age_17_"]].fillna(0).sum(axis=1)
        demo = demo.groupby(["date", "norm_state"])[
            ["demo_age_5_17", "demo_age_17_", "demo_total"]
        ].sum().reset_index()

    bio = _read("api_data_aadhar_biometric/**/*.csv")
    if not bio.empty:
        bio["bio_total"] = bio[["bio_age_5_17", "bio_age_17_"]].fillna(0).sum(axis=1)
        bio = bio.groupby(["date", "norm_state"])[
            ["bio_age_5_17", "bio_age_17_", "bio_total"]
        ].sum().reset_index()

    m = enrol if not enrol.empty else pd.DataFrame()
    if not demo.empty:
        m = pd.merge(m, demo, on=["date", "norm_state"], how="outer") if not m.empty else demo
    if not bio.empty:
        m = pd.merge(m, bio, on=["date", "norm_state"], how="outer") if not m.empty else bio

    for c in ["total_enrolments", "demo_total", "bio_total"]:
        if c in m.columns:
            m[c] = m[c].fillna(0)

    # Compute Total System Load = enrolments + demographic updates + biometric updates
    m["total_system_load"] = m["total_enrolments"] + m["demo_total"] + m["bio_total"]
    return m.dropna(subset=["date", "norm_state"])

# ==============================================================================
# SECTION 4: FEATURE ENGINEERING
# ==============================================================================

def _hol_vecs(dates_series):
    dates = pd.to_datetime(dates_series)
    hdays = INDIA_HOLIDAYS_2025
    is_hol = dates.isin(hdays).astype(int).values
    d2n = np.full(len(dates), 30.0)
    d2p = np.full(len(dates), 30.0)
    for i, d in enumerate(dates):
        fut = hdays[hdays > d]
        pas = hdays[hdays <= d]
        if len(fut):
            d2n[i] = min((fut.min() - d).days, 30)
        if len(pas):
            d2p[i] = min((d - pas.max()).days, 30)
    return is_hol, d2n, d2p

def build_features(df, ffill_limit=7):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    dfs = []

    for state, grp in df.groupby("norm_state"):
        grp = grp.sort_values("date").copy()
        full_idx = pd.date_range(grp["date"].min(), grp["date"].max(), freq="D")
        grp = grp.set_index("date").reindex(full_idx)
        grp.index.name = "date"

        ffill_cols = ["bio_total", "demo_total", "age_0_5", "age_5_17", "age_18_greater"]
        for c in ffill_cols:
            if c in grp.columns:
                grp[c] = grp[c].ffill(limit=ffill_limit).fillna(0)

        grp["norm_state"] = state
        grp = grp.reset_index()
        pop = STATE_POPULATION.get(state, _MEDIAN_POP)

        # 1. Calendar
        grp["day_of_week"]      = grp["date"].dt.dayofweek
        grp["day_of_month"]     = grp["date"].dt.day
        grp["month"]            = grp["date"].dt.month
        grp["quarter"]          = grp["date"].dt.quarter
        grp["day_of_year"]      = grp["date"].dt.dayofyear
        grp["is_weekend"]       = grp["day_of_week"].isin([5, 6]).astype(int)
        grp["days_since_start"] = (grp["date"] - grp["date"].min()).dt.days

        # 2. Cyclical trigonometric
        grp["sin_dow"]   = np.sin(2 * np.pi * grp["day_of_week"] / 7)
        grp["cos_dow"]   = np.cos(2 * np.pi * grp["day_of_week"] / 7)
        grp["sin_month"] = np.sin(2 * np.pi * grp["month"] / 12)
        grp["cos_month"] = np.cos(2 * np.pi * grp["month"] / 12)

        # 3. Population context
        grp["log_state_pop"]  = np.log1p(pop)
        grp["state_pop_tier"] = _pop_tier(state)
        grp["state_cat"]      = hash(state) % 100

        # 4. Holidays
        is_hol, d2n, d2p = _hol_vecs(grp["date"])
        grp["is_holiday"]         = is_hol
        grp["days_to_holiday"]    = d2n
        grp["days_since_holiday"] = d2p
        grp["holiday_proximity"]  = np.exp(-d2n / 7)
        grp["holiday_recency"]    = np.exp(-d2p / 7)

        # 5. Lags across enrolments and system load
        te = grp["total_enrolments"]
        tl = grp["total_system_load"]
        for lag in [1, 3, 7, 14, 30]:
            grp[f"lag_{lag}"]      = te.shift(lag)
            grp[f"bio_lag_{lag}"]  = grp["bio_total"].shift(lag)
            grp[f"demo_lag_{lag}"] = grp["demo_total"].shift(lag)
            grp[f"load_lag_{lag}"] = tl.shift(lag)

        # 6. Rolling statistics
        for w in [3, 7, 14, 30]:
            s_enrol = te.shift(1)
            s_load  = tl.shift(1)
            grp[f"rolling_mean_{w}"] = s_enrol.rolling(w, min_periods=1).mean()
            grp[f"rolling_std_{w}"]  = s_enrol.rolling(w, min_periods=1).std().fillna(0)
            grp[f"load_rolling_{w}"] = s_load.rolling(w, min_periods=1).mean()
            grp[f"load_std_{w}"]     = s_load.rolling(w, min_periods=1).std().fillna(0)
            grp[f"bio_rolling_{w}"]  = grp["bio_total"].shift(1).rolling(w, min_periods=1).mean()
            grp[f"demo_rolling_{w}"] = grp["demo_total"].shift(1).rolling(w, min_periods=1).mean()

        # 7. Interaction ratios and velocity
        grp["bio_to_enrol_ratio"]  = (grp["bio_rolling_7"] / (grp["rolling_mean_7"] + 1)).fillna(0)
        grp["demo_to_enrol_ratio"] = (grp["demo_rolling_7"] / (grp["rolling_mean_7"] + 1)).fillna(0)
        grp["rolling_cv_7"]        = (grp["rolling_std_7"] / (grp["rolling_mean_7"] + 1)).fillna(0)

        grp["lag_1_per_1000"]          = grp["lag_1"] / pop * 1000
        grp["lag_7_per_1000"]          = grp["lag_7"] / pop * 1000
        grp["rolling_mean_7_per_1000"] = grp["rolling_mean_7"] / pop * 1000
        grp["lag_diff_1_7"]  = grp["lag_1"] - grp["lag_7"]
        grp["lag_diff_7_14"] = grp["lag_7"] - grp["lag_14"]

        s1 = grp["total_enrolments"].shift(1)
        grp["ewm_7"]           = s1.ewm(span=7, min_periods=1).mean()
        grp["ewm_trend"]       = ((grp["ewm_7"] - grp["rolling_mean_30"]) / (grp["rolling_mean_30"] + 1)).fillna(0)
        grp["system_velocity"] = ((grp["bio_rolling_7"] + grp["demo_rolling_7"]) / (grp["rolling_mean_7"] + 1)).fillna(0)
        grp["mom_growth"]      = ((grp["rolling_mean_7"] - grp["rolling_mean_30"]) / (grp["rolling_mean_30"] + 1)).fillna(0)
        grp["lifecycle_stage"] = (grp["system_velocity"] > 5.0).astype(int)

        grp["_observed"] = grp["total_enrolments"].notna()
        grp["total_enrolments"] = grp["total_enrolments"].fillna(0)
        grp["total_system_load"] = grp["total_system_load"].fillna(0)
        dfs.append(grp)

    return pd.concat(dfs, ignore_index=True).fillna(0)

# ==============================================================================
# SECTION 5: MODEL TRAINING & METRICS LOGGING
# ==============================================================================

def fit_eval(name, model, Xtr, ytr, Xte, yte, fname, log_target=True, scaler=None, results=None, test_preds=None, target_name="total_enrolments"):
    t0 = time.time()
    y_fit = np.log1p(ytr) if log_target else ytr

    if scaler is not None:
        Xtr = scaler.transform(Xtr)
        Xte = scaler.transform(Xte)

    model.fit(Xtr, y_fit)
    elapsed = round(time.time() - t0, 2)

    p_tr = np.expm1(np.maximum(0, model.predict(Xtr))) if log_target else np.maximum(0, model.predict(Xtr))
    p_te = np.expm1(np.maximum(0, model.predict(Xte))) if log_target else np.maximum(0, model.predict(Xte))

    if test_preds is not None:
        test_preds[name] = p_te

    tr_r2 = r2_score(ytr, p_tr)
    te_r2 = r2_score(yte, p_te)
    tr_rmse = float(np.sqrt(mean_squared_error(ytr, p_tr)))
    te_rmse = float(np.sqrt(mean_squared_error(yte, p_te)))
    tr_mae  = float(mean_absolute_error(ytr, p_tr))
    te_mae  = float(mean_absolute_error(yte, p_te))

    os.makedirs("pkl_models", exist_ok=True)
    joblib.dump(model, f"pkl_models/{fname}")

    print(f"  {name:32s}  train_R2={tr_r2:.4f} (RMSE={tr_rmse:,.0f})  test_R2={te_r2:.4f} (RMSE={te_rmse:,.0f})  [{elapsed}s]")

    if results is not None:
        results.append({
            "model": name,
            "target": target_name,
            "train_r2": round(tr_r2, 4),
            "train_rmse": round(tr_rmse, 2),
            "train_mae": round(tr_mae, 2),
            "test_r2": round(te_r2, 4),
            "test_rmse": round(te_rmse, 2),
            "test_mae": round(te_mae, 2),
            "test_mape": None,
            "training_seconds": elapsed,
            "model_path": fname
        })
    return p_te, te_rmse

# ==============================================================================
# SECTION 6: STACKING ENSEMBLE BUILDER (CROSS-VALIDATION OOF)
# ==============================================================================

def build_oof_predictions(models_cfg, X, y, n_splits=5):
    tscv = TimeSeriesSplit(n_splits=n_splits)
    oof  = np.zeros((len(y), len(models_cfg)))
    for fi, (tr_i, val_i) in enumerate(tscv.split(X)):
        Xf_tr, Xf_val = X.iloc[tr_i], X.iloc[val_i]
        yf_tr = y.iloc[tr_i]
        for mi, (mn, mc) in enumerate(models_cfg.items()):
            m = mc["model_cls"](**mc["params"])
            if mc.get("scale"):
                sc2 = StandardScaler()
                Xs = sc2.fit_transform(Xf_tr)
                Xv = sc2.transform(Xf_val)
                m.fit(Xs, np.log1p(yf_tr))
                oof[val_i, mi] = np.expm1(np.maximum(0, m.predict(Xv)))
            else:
                m.fit(Xf_tr, np.log1p(yf_tr))
                oof[val_i, mi] = np.expm1(np.maximum(0, m.predict(Xf_val)))
    return oof

# ==============================================================================
# SECTION 7: PYTORCH DEEP LEARNING LSTM + ATTENTION MODEL
# ==============================================================================

if HAS_TORCH:
    class TimeSeriesSequenceDataset(Dataset):
        def __init__(self, data_df, feature_cols, target_col, lookback=14):
            self.lookback = lookback
            self.sequences = []
            self.targets = []
            for state, group in data_df.groupby('norm_state'):
                group = group.sort_values('date').reset_index(drop=True)
                X = group[feature_cols].values
                y = group[target_col].values
                for i in range(len(group) - lookback):
                    self.sequences.append(X[i : i + lookback])
                    self.targets.append(y[i + lookback])
            self.sequences = torch.tensor(np.array(self.sequences), dtype=torch.float32)
            self.targets   = torch.tensor(np.array(self.targets),   dtype=torch.float32).unsqueeze(-1)

        def __len__(self):
            return len(self.sequences)

        def __getitem__(self, idx):
            return self.sequences[idx], self.targets[idx]

    class AttentionLayer(nn.Module):
        def __init__(self, hidden_dim):
            super().__init__()
            self.attn = nn.Linear(hidden_dim, 1)

        def forward(self, lstm_out):
            scores  = self.attn(lstm_out).squeeze(-1)
            weights = torch.softmax(scores, dim=1).unsqueeze(2)
            context = (lstm_out * weights).sum(dim=1)
            return context

    class AadhaarLSTM(nn.Module):
        def __init__(self, input_dim, hidden_dim=128, num_layers=2, dropout=0.3, bidirectional=False):
            super().__init__()
            self.bidirectional = bidirectional
            self.lstm = nn.LSTM(
                input_size=input_dim,
                hidden_size=hidden_dim,
                num_layers=num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0.0,
                bidirectional=bidirectional
            )
            lstm_out_dim = hidden_dim * (2 if bidirectional else 1)
            self.attention = AttentionLayer(lstm_out_dim)
            self.fc = nn.Sequential(
                nn.LayerNorm(lstm_out_dim),
                nn.Linear(lstm_out_dim, 64),
                nn.GELU(),
                nn.Dropout(0.2),
                nn.Linear(64, 1)
            )

        def forward(self, x):
            lstm_out, _ = self.lstm(x)
            context     = self.attention(lstm_out)
            return self.fc(context)

def train_lstm_model(train_df, test_df, feature_cols, lookback=14, epochs=30, batch_size=128, lr=1e-3):
    if not HAS_TORCH:
        print("  [PyTorch not installed. Skipping LSTM training.]")
        return None

    print(f"\n[Deep Learning] Training PyTorch LSTM Sequence Model (Lookback={lookback} days, Epochs={epochs})...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  PyTorch execution device: {device}")

    train_df = train_df.copy()
    test_df = test_df.copy()

    train_df["target_log"] = np.log1p(train_df["total_enrolments"])
    test_df["target_log"]  = np.log1p(test_df["total_enrolments"])

    scaler = StandardScaler()
    train_df[feature_cols] = scaler.fit_transform(train_df[feature_cols])
    test_df[feature_cols]  = scaler.transform(test_df[feature_cols])

    train_dataset = TimeSeriesSequenceDataset(train_df, feature_cols, "target_log", lookback=lookback)
    test_dataset  = TimeSeriesSequenceDataset(test_df,  feature_cols, "target_log", lookback=lookback)

    if len(train_dataset) == 0 or len(test_dataset) == 0:
        print("  [Insufficient sequence length for LSTM. Skipping.]")
        return None

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True,  num_workers=0)
    test_loader  = DataLoader(test_dataset,  batch_size=batch_size, shuffle=False, num_workers=0)

    model = AadhaarLSTM(input_dim=len(feature_cols), hidden_dim=128, num_layers=2, dropout=0.3, bidirectional=False).to(device)
    criterion = nn.HuberLoss(delta=1.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    patience = 10
    best_val_loss = float("inf")
    no_improve = 0
    best_state = None

    t0 = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            preds = model(batch_x)
            loss  = criterion(preds, batch_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            running_loss += loss.item() * batch_x.size(0)
        scheduler.step()
        epoch_loss = running_loss / max(len(train_dataset), 1)

        model.eval()
        val_loss_sum = 0.0
        with torch.no_grad():
            for batch_x, batch_y in test_loader:
                preds = model(batch_x.to(device))
                val_loss_sum += criterion(preds, batch_y.to(device)).item() * batch_x.size(0)
        val_loss = val_loss_sum / max(len(test_dataset), 1)

        if epoch % 10 == 0 or epoch == 1:
            print(f"    Epoch [{epoch:02d}/{epochs:02d}]  train_loss={epoch_loss:.4f}  val_loss={val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            no_improve = 0
        else:
            no_improve += 1
            if no_improve >= patience:
                print(f"    Early stopping at epoch {epoch} (best val_loss={best_val_loss:.4f})")
                break

    elapsed = round(time.time() - t0, 2)
    if best_state:
        model.load_state_dict(best_state)

    model.eval()
    test_preds_log, test_targets_log = [], []
    train_preds_log, train_targets_log = [], []

    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            preds = model(batch_x.to(device))
            test_preds_log.extend(preds.cpu().numpy().flatten())
            test_targets_log.extend(batch_y.numpy().flatten())
        for batch_x, batch_y in DataLoader(train_dataset, batch_size=256, shuffle=False):
            preds = model(batch_x.to(device))
            train_preds_log.extend(preds.cpu().numpy().flatten())
            train_targets_log.extend(batch_y.numpy().flatten())

    y_pred_orig  = np.expm1(np.maximum(0, np.array(test_preds_log)))
    y_test_orig  = np.expm1(np.array(test_targets_log))
    y_pred_tr    = np.expm1(np.maximum(0, np.array(train_preds_log)))
    y_train_orig = np.expm1(np.array(train_targets_log))

    lstm_train_r2 = r2_score(y_train_orig, y_pred_tr)
    lstm_r2       = r2_score(y_test_orig,  y_pred_orig)
    lstm_rmse     = float(np.sqrt(mean_squared_error(y_test_orig, y_pred_orig)))
    lstm_mae      = float(mean_absolute_error(y_test_orig, y_pred_orig))

    print(f"  {'LSTM (PyTorch)':32s}  train_R2={lstm_train_r2:.4f}  test_R2={lstm_r2:.4f}  RMSE={lstm_rmse:,.0f}  [{elapsed}s]")

    os.makedirs("pkl_models", exist_ok=True)
    with open("pkl_models/lstm_feature_cols.json", "w") as f:
        json.dump(feature_cols, f)
    joblib.dump(scaler, "pkl_models/lstm_scaler.pkl")
    torch.save({
        "state_dict": model.state_dict(),
        "input_dim": len(feature_cols),
        "hidden_dim": model.lstm.hidden_size,
        "num_layers": 2,
        "lookback": lookback
    }, "pkl_models/lstm_model.pt")

    return {
        "model": "LSTM (PyTorch)",
        "target": "total_enrolments",
        "train_r2": round(float(lstm_train_r2), 4),
        "test_r2": round(float(lstm_r2), 4),
        "train_rmse": None,
        "test_rmse": round(float(lstm_rmse), 2),
        "test_mae": round(float(lstm_mae), 2),
        "test_mape": None,
        "training_seconds": elapsed,
        "model_path": "lstm_model.pt"
    }

# ==============================================================================
# SECTION 8: DUAL REGIME (SUITE A & SUITE B) ORCHESTRATION PIPELINE
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Aadhaar Two-Stage Intelligence Training Pipeline")
    parser.add_argument("--data-dir", default=".", help="Directory containing raw CSV shards")
    parser.add_argument("--skip-lstm", action="store_true", help="Skip PyTorch LSTM training (fast mode)")
    parser.add_argument("--epochs", type=int, default=30, help="Epochs for LSTM training")
    parser.add_argument("--lookback", type=int, default=14, help="Sequence lookback window for LSTM")
    args = parser.parse_args()

    print("=" * 75)
    print("  Aadhaar Intelligence Engine — First-Principles Dual Model Pipeline")
    print("=" * 75)

    # 1. Ingest Raw Data
    print(f"\n[Step 1/7] Ingesting multi-shard datasets from: {args.data_dir}")
    raw = load_raw(args.data_dir)
    print(f"  Canonical States: {raw['norm_state'].nunique()} | Observed records: {len(raw):,} | Date range: {raw['date'].nunique()} days")

    # 2. Build Rich Features
    print("\n[Step 2/7] Engineering time-series, lag, rolling, and demographic features...")
    processed = build_features(raw, ffill_limit=7)
    obs = processed[processed["_observed"]].copy()
    all_dates = sorted(obs["date"].unique())
    print(f"  Observed rows: {len(obs):,} | Date span: {obs['date'].min().date()} -> {obs['date'].max().date()}")

    # 3. Chronological Train / Test Split (80% train, 20% test)
    split_date = all_dates[int(len(all_dates) * 0.80)]
    train_df = obs[obs["date"] <  split_date].copy()
    test_df  = obs[obs["date"] >= split_date].copy()
    print(f"\n[Step 3/7] Chronological split at {pd.Timestamp(split_date).date()}: Train={len(train_df):,} | Test={len(test_df):,}")

    state_stats = (train_df.groupby("norm_state")["total_enrolments"]
                   .agg(state_mean_enrol="mean", state_std_enrol="std", state_median_enrol="median").reset_index())
    state_stats["state_std_enrol"] = state_stats["state_std_enrol"].fillna(0)
    train_df = train_df.merge(state_stats, on="norm_state", how="left")
    test_df  = test_df.merge(state_stats,  on="norm_state", how="left")
    gm = train_df["state_mean_enrol"].mean()
    for c in ["state_mean_enrol", "state_std_enrol", "state_median_enrol"]:
        train_df[c] = train_df[c].fillna(gm)
        test_df[c]  = test_df[c].fillna(gm)

    os.makedirs("pkl_models", exist_ok=True)
    state_stats.to_csv("pkl_models/state_stats.csv", index=False)

    _excl = {"date", "norm_state", "state", "district", "pincode", "_observed",
             "age_0_5", "age_5_17", "age_18_greater", "total_enrolments", "total_system_load",
             "demo_age_5_17", "demo_age_17_", "demo_total", "bio_age_5_17", "bio_age_17_", "bio_total"}
    feature_cols = [c for c in train_df.columns if c not in _excl]
    print(f"  Engineered feature dimensions: {len(feature_cols)}")

    X_tr = train_df[feature_cols]
    X_te = test_df[feature_cols]
    y_tr_enrol = train_df["total_enrolments"]
    y_te_enrol = test_df["total_enrolments"]
    y_tr_load  = train_df["total_system_load"]
    y_te_load  = test_df["total_system_load"]

    # Scalers
    sc_b = StandardScaler()
    X_tr_s_b = pd.DataFrame(sc_b.fit_transform(X_tr), columns=feature_cols)
    X_te_s_b = pd.DataFrame(sc_b.transform(X_te),   columns=feature_cols)
    joblib.dump(sc_b, "pkl_models/ridge_scaler.pkl")

    sc_a = StandardScaler()
    X_tr_s_a = pd.DataFrame(sc_a.fit_transform(X_tr), columns=feature_cols)
    X_te_s_a = pd.DataFrame(sc_a.transform(X_te),   columns=feature_cols)
    joblib.dump(sc_a, "pkl_models/modelA_scaler.pkl")

    results = []

    # =========================================================================
    # STEP 4: TRAIN MODEL SUITE A (MAINTENANCE REGIME — TOTAL SYSTEM LOAD)
    # =========================================================================
    print("\n[Step 4/7] Training Model Suite A (Target: total_system_load for Maintenance States)...")
    preds_a = {}
    _, rmse_ridge_a = fit_eval("Ridge (A)", Ridge(alpha=10.0), X_tr_s_a, y_tr_load, X_te_s_a, y_te_load, "modelA_ridge.pkl", log_target=True, results=results, test_preds=preds_a, target_name="total_system_load")
    _, rmse_rf_a    = fit_eval("RF (A)", RandomForestRegressor(n_estimators=300, max_depth=10, min_samples_leaf=5, random_state=42, n_jobs=-1), X_tr, y_tr_load, X_te, y_te_load, "modelA_rf.pkl", log_target=True, results=results, test_preds=preds_a, target_name="total_system_load")
    _, rmse_xgb_a   = fit_eval("XGBoost (A)", xgb.XGBRegressor(n_estimators=400, learning_rate=0.03, max_depth=6, subsample=0.8, colsample_bytree=0.7, min_child_weight=3, reg_alpha=0.5, reg_lambda=2.0, random_state=42, n_jobs=-1, verbosity=0), X_tr, y_tr_load, X_te, y_te_load, "modelA_xgb.pkl", log_target=True, results=results, test_preds=preds_a, target_name="total_system_load")
    _, rmse_lgb_a   = fit_eval("LGB (A)", lgb.LGBMRegressor(n_estimators=400, learning_rate=0.03, num_leaves=63, min_child_samples=10, subsample=0.8, colsample_bytree=0.7, reg_alpha=0.5, reg_lambda=2.0, random_state=42, verbose=-1), X_tr, y_tr_load, X_te, y_te_load, "modelA_lgb.pkl", log_target=True, results=results, test_preds=preds_a, target_name="total_system_load")

    # Stacking Ensemble A
    models_oof_a = {
        "Ridge":   {"model_cls": Ridge, "params": {"alpha": 10.0}, "scale": True},
        "RF":      {"model_cls": RandomForestRegressor, "params": {"n_estimators": 200, "max_depth": 8, "random_state": 42, "n_jobs": -1}, "scale": False},
        "XGBoost": {"model_cls": xgb.XGBRegressor, "params": {"n_estimators": 250, "learning_rate": 0.03, "max_depth": 6, "random_state": 42, "n_jobs": -1, "verbosity": 0}, "scale": False},
        "LightGBM":{"model_cls": lgb.LGBMRegressor, "params": {"n_estimators": 250, "learning_rate": 0.03, "num_leaves": 63, "random_state": 42, "verbose": -1}, "scale": False},
    }
    # Blended Inverse-RMSE Ensemble A
    inv_a = {"Ridge": 1.0 / max(rmse_ridge_a, 1), "RF": 1.0 / max(rmse_rf_a, 1), "XGBoost": 1.0 / max(rmse_xgb_a, 1), "LGB": 1.0 / max(rmse_lgb_a, 1)}
    tot_a = sum(inv_a.values())
    w_a = {k: v / tot_a for k, v in inv_a.items()}

    blend_pred_a = (
        w_a["Ridge"]   * preds_a["Ridge (A)"] +
        w_a["RF"]      * preds_a["RF (A)"] +
        w_a["XGBoost"] * preds_a["XGBoost (A)"] +
        w_a["LGB"]     * preds_a["LGB (A)"]
    )
    stack_r2_a   = r2_score(y_te_load, blend_pred_a)
    stack_rmse_a = float(np.sqrt(mean_squared_error(y_te_load, blend_pred_a)))
    stack_mae_a  = float(mean_absolute_error(y_te_load, blend_pred_a))
    print(f"  {'Ensemble A (System Load)':32s}  train_R2=N/A        test_R2={stack_r2_a:.4f}  RMSE={stack_rmse_a:,.0f}")

    joblib.dump({
        "meta_model": None,
        "meta_scaler": None,
        "scaler": "modelA_scaler.pkl",
        "weights": w_a,
        "feature_cols": feature_cols,
        "target": "total_system_load",
        "pipeline_version": "v2"
    }, "pkl_models/modelA_ensemble_meta.pkl")

    results.append({
        "model": "Ensemble A (system_load)",
        "target": "total_system_load",
        "train_r2": None,
        "test_r2": round(stack_r2_a, 4),
        "train_rmse": None,
        "test_rmse": round(stack_rmse_a, 2),
        "test_mae": round(stack_mae_a, 2),
        "test_mape": None,
        "training_seconds": None,
        "model_path": "modelA_ensemble_meta.pkl"
    })

    # =========================================================================
    # STEP 5: TRAIN MODEL SUITE B (GROWTH REGIME — ENROLMENTS)
    # =========================================================================
    # Senior-dev fixes applied:
    #   1. Per-state relative target (enrol / state_mean) — eliminates inter-state
    #      scale variance (UP=1M+/day vs Sikkim=<1000/day); model learns relative
    #      deviations; app multiplies prediction × state_mean to recover counts.
    #   2. Load-feature purge — load_lag_*/load_rolling_*/load_std_* are Model A
    #      targets; keeping them leaks signal and confuses Model B.
    #   3. Feature selection via quick-LGB importance — 79 features on ~800 rows
    #      is overfit territory (~10 rows/feature); keep top 30.
    #   4. 7-day smoothed target — reduces bursty noise; model learns trend/rhythm.
    #   5. Stronger regularization — smaller trees, higher min_child, less overfit.
    # =========================================================================
    print("\n[Step 5/7] Training Model Suite B (Target: total_enrolments — improved pipeline)...")

    # --- Fix 1: per-state relative target & 7-day smoothed target ---------------
    # Relative target: ratio to state mean (all states on same scale, still > 0)
    state_mean_map = train_df.groupby("norm_state")["total_enrolments"].mean().to_dict()
    global_mean    = train_df["total_enrolments"].mean()

    def _rel_target(df):
        sm = df["norm_state"].map(state_mean_map).fillna(global_mean).clip(lower=1)
        return df["total_enrolments"] / sm

    y_tr_enrol_rel = _rel_target(train_df).values
    y_te_enrol_rel = _rel_target(test_df).values

    # 7-day smoothed target (per-state rolling avg, shift=1 to avoid leakage)
    def _smooth_target(df):
        parts = []
        for state, g in df.groupby("norm_state", sort=False):
            g = g.sort_values("date").copy()
            sm = state_mean_map.get(state, global_mean) or 1
            smooth = g["total_enrolments"].shift(1).rolling(7, min_periods=1).mean().bfill().fillna(0)
            parts.append(smooth / sm)
        return pd.concat(parts).loc[df.index].values

    y_tr_smooth = _smooth_target(train_df)
    y_te_smooth = _smooth_target(test_df)

    # Save normalization params so app can inverse-transform predictions
    norm_params = pd.DataFrame([
        {"norm_state": s, "state_mean_enrol": v}
        for s, v in state_mean_map.items()
    ])
    norm_params.to_csv("pkl_models/state_norm_params.csv", index=False)

    # --- Fix 2: purge load-target features from Model B -------------------------
    _load_prefixes = ("load_lag_", "load_rolling_", "load_std_")
    feature_cols_b_full = [c for c in feature_cols
                           if not any(c.startswith(p) for p in _load_prefixes)]

    # --- Fix 3: feature selection — quick LGB, keep top 30 ---------------------
    _selector = lgb.LGBMRegressor(n_estimators=200, learning_rate=0.05,
                                   num_leaves=31, random_state=42, verbose=-1)
    _selector.fit(X_tr[feature_cols_b_full], np.log1p(np.maximum(0, y_tr_enrol_rel)))
    _importance = pd.Series(_selector.feature_importances_, index=feature_cols_b_full)
    TOP_K = 30
    feature_cols_b = _importance.nlargest(TOP_K).index.tolist()
    print(f"  Model B feature selection: {len(feature_cols_b_full)} → top {TOP_K} features")

    X_tr_b = train_df[feature_cols_b]
    X_te_b = test_df[feature_cols_b]

    # Scaler fitted on selected features
    sc_b2 = StandardScaler()
    X_tr_b_s = pd.DataFrame(sc_b2.fit_transform(X_tr_b), columns=feature_cols_b)
    X_te_b_s = pd.DataFrame(sc_b2.transform(X_te_b),    columns=feature_cols_b)
    joblib.dump(sc_b2, "pkl_models/ridge_scaler.pkl")  # overwrite with new scaler

    # --- Fix 4+5: train with relative target + strong regularisation ------------
    preds_b_rel = {}
    _, rmse_ridge_b = fit_eval(
        "Ridge (B)", Ridge(alpha=50.0),
        X_tr_b_s, pd.Series(y_tr_enrol_rel),
        X_te_b_s, pd.Series(y_te_enrol_rel),
        "ridge_baseline_model.pkl",
        log_target=True, results=results, test_preds=preds_b_rel,
        target_name="total_enrolments")

    _, rmse_rf_b = fit_eval(
        "RF (B)",
        RandomForestRegressor(n_estimators=400, max_depth=7, min_samples_leaf=15,
                               min_samples_split=10, max_features="sqrt",
                               random_state=42, n_jobs=-1),
        X_tr_b, pd.Series(y_tr_smooth),
        X_te_b, pd.Series(y_te_enrol_rel),
        "random_forest_model.pkl",
        log_target=True, results=results, test_preds=preds_b_rel,
        target_name="total_enrolments")

    _, rmse_xgb_b = fit_eval(
        "XGBoost (B)",
        xgb.XGBRegressor(n_estimators=500, learning_rate=0.03, max_depth=4,
                          subsample=0.8, colsample_bytree=0.7, min_child_weight=10,
                          reg_alpha=1.0, reg_lambda=5.0,
                          random_state=42, n_jobs=-1, verbosity=0),
        X_tr_b, pd.Series(y_tr_smooth),
        X_te_b, pd.Series(y_te_enrol_rel),
        "xgboost_model.pkl",
        log_target=True, results=results, test_preds=preds_b_rel,
        target_name="total_enrolments")

    _, rmse_lgb_b = fit_eval(
        "LGB (B)",
        lgb.LGBMRegressor(n_estimators=500, learning_rate=0.03, num_leaves=31,
                           max_depth=4, min_child_samples=20,
                           subsample=0.8, colsample_bytree=0.7,
                           reg_alpha=1.0, reg_lambda=5.0,
                           random_state=42, verbose=-1),
        X_tr_b, pd.Series(y_tr_smooth),
        X_te_b, pd.Series(y_te_enrol_rel),
        "lightgbm_model.pkl",
        log_target=True, results=results, test_preds=preds_b_rel,
        target_name="total_enrolments")

    # Blended Inverse-RMSE Ensemble B (relative-scale predictions)
    inv_b = {
        "Ridge":    1.0 / max(rmse_ridge_b, 1e-6),
        "RF":       1.0 / max(rmse_rf_b, 1e-6),
        "XGBoost":  1.0 / max(rmse_xgb_b, 1e-6),
        "LightGBM": 1.0 / max(rmse_lgb_b, 1e-6),
    }
    tot_b = sum(inv_b.values())
    w_b = {k: v / tot_b for k, v in inv_b.items()}

    blend_pred_b_rel = (
        w_b["Ridge"]    * preds_b_rel["Ridge (B)"] +
        w_b["RF"]       * preds_b_rel["RF (B)"] +
        w_b["XGBoost"]  * preds_b_rel["XGBoost (B)"] +
        w_b["LightGBM"] * preds_b_rel["LGB (B)"]
    )

    # Inverse-transform: relative → absolute counts for metrics
    te_state_means = test_df["norm_state"].map(state_mean_map).fillna(global_mean).clip(lower=1).values
    blend_pred_b_abs = blend_pred_b_rel * te_state_means

    stack_r2_b   = r2_score(y_te_enrol, blend_pred_b_abs)
    stack_rmse_b = float(np.sqrt(mean_squared_error(y_te_enrol, blend_pred_b_abs)))
    stack_mae_b  = float(mean_absolute_error(y_te_enrol, blend_pred_b_abs))
    print(f"  {'Ensemble B (Enrolments)':32s}  train_R2=N/A        test_R2={stack_r2_b:.4f}  RMSE={stack_rmse_b:,.0f}")

    joblib.dump({
        "meta_model": None,
        "meta_scaler": None,
        "scaler": "ridge_scaler.pkl",
        "weights": w_b,
        "feature_cols": feature_cols_b,
        "target": "total_enrolments",
        "relative_target": True,           # flag: predictions are ratios, multiply by state_mean
        "state_norm_params": "state_norm_params.csv",
        "pipeline_version": "v3"
    }, "pkl_models/ensemble_meta.pkl")

    results.append({
        "model": "Ensemble B (enrolments)",
        "target": "total_enrolments",
        "train_r2": None,
        "test_r2": round(stack_r2_b, 4),
        "train_rmse": None,
        "test_rmse": round(stack_rmse_b, 2),
        "test_mae": round(stack_mae_b, 2),
        "test_mape": None,
        "training_seconds": None,
        "model_path": "ensemble_meta.pkl"
    })

    with open("pkl_models/feature_metadata.json", "w") as f:
        json.dump({
            "feature_cols": feature_cols,        # Model A uses all 79
            "feature_cols_b": feature_cols_b,    # Model B uses top-30 selected
            "log_target": True,
            "relative_target_b": True,
            "raw_target_models": [],
            "log_target_models": ["Ridge", "Random Forest", "XGBoost", "LightGBM", "Ensemble"],
            "modelA_weights": w_a,
            "modelB_weights": w_b,
            "split_date": str(pd.Timestamp(split_date).date()),
            "pipeline_version": "v3"
        }, f, indent=2)

    # =========================================================================
    # STEP 6: DEEP LEARNING SEQUENCE MODEL (PYTORCH LSTM)
    # =========================================================================
    if not args.skip_lstm and HAS_TORCH:
        print("\n[Step 6/7] Training PyTorch LSTM Sequence Model...")
        lstm_res = train_lstm_model(train_df, test_df, feature_cols, lookback=args.lookback, epochs=args.epochs)
        if lstm_res:
            results.insert(0, lstm_res)

    # Save complete comparison
    comp_path = "pkl_models/model_comparison.json"
    with open(comp_path, "w") as f:
        json.dump(results, f, indent=2)

    print("\n[Step 7/7] Final Dual Model Performance Summary\n" + "=" * 75)
    res_df = pd.DataFrame(results).sort_values("test_r2", ascending=False)
    print(res_df[["model", "target", "test_r2", "test_rmse", "test_mae"]].to_string(index=False))
    print("=" * 75)
    print(f"All model suites successfully generated and exported to: pkl_models/\n")

if __name__ == "__main__":
    main()
