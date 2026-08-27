import os, glob, json, joblib
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import IsolationForest
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aadhaar Intelligence Engine",
    page_icon="🪪", layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  .main-header {
    font-size:2.3rem; font-weight:800;
    background:linear-gradient(90deg,#1E88E5 0%,#43A047 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin-bottom:0.2rem;
  }
  .sub-header { font-size:1.05rem; color:#B0BEC5; margin-bottom:1.2rem; }
  .module-card {
    background:#1E222A; border-radius:10px; padding:14px 18px;
    border-left:4px solid; margin-bottom:12px;
  }
  .mod-ops   { border-color:#1E88E5; }
  .mod-mig   { border-color:#43A047; }
  .mod-anom  { border-color:#E53935; }
  .badge { padding:2px 8px; border-radius:12px; font-size:.78rem; font-weight:700; }
  .badge-growth { background:#1b5e20; color:#a5d6a7; }
  .badge-maint  { background:#b71c1c; color:#ef9a9a; }
  .metric-card {
    background:#1E222A; border-radius:10px; padding:16px 20px;
    text-align:center; border:1px solid #2d3748; margin-bottom:8px;
  }
  .metric-val { font-size:1.8rem; font-weight:800; color:#1E88E5; }
  .metric-lbl { font-size:.85rem; color:#90A4AE; margin-top:4px; }
  .alert-box {
    background:#7f0000; border-radius:8px; padding:8px 12px;
    margin:4px 0; font-size:.82rem; color:#ffcdd2;
  }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
STATE_POPULATION = {
    "Andaman & Nicobar": 397_000, "Andhra Pradesh": 49_577_103,
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

STATE_COORDINATES = {
    "Andaman & Nicobar": {"lat": 11.7401, "lon": 92.6586},
    "Andhra Pradesh":    {"lat": 15.9129, "lon": 79.7400},
    "Arunachal Pradesh": {"lat": 28.2180, "lon": 94.7278},
    "Assam":             {"lat": 26.2006, "lon": 92.9376},
    "Bihar":             {"lat": 25.0961, "lon": 85.3131},
    "Chandigarh":        {"lat": 30.7333, "lon": 76.7794},
    "Chhattisgarh":      {"lat": 21.2787, "lon": 81.8661},
    "Dadra & Nagar Haveli and Daman & Diu": {"lat": 20.3974, "lon": 72.8328},
    "Delhi":             {"lat": 28.7041, "lon": 77.1025},
    "Goa":               {"lat": 15.2993, "lon": 74.1240},
    "Gujarat":           {"lat": 22.2587, "lon": 71.1924},
    "Haryana":           {"lat": 29.0588, "lon": 76.0856},
    "Himachal Pradesh":  {"lat": 31.1048, "lon": 77.1734},
    "Jammu and Kashmir": {"lat": 33.7782, "lon": 76.5762},
    "Jharkhand":         {"lat": 23.6102, "lon": 85.2799},
    "Karnataka":         {"lat": 15.3173, "lon": 75.7139},
    "Kerala":            {"lat": 10.8505, "lon": 76.2711},
    "Ladakh":            {"lat": 34.1526, "lon": 77.5771},
    "Lakshadweep":       {"lat": 10.5667, "lon": 72.6417},
    "Madhya Pradesh":    {"lat": 22.9734, "lon": 78.6569},
    "Maharashtra":       {"lat": 19.7515, "lon": 75.7139},
    "Manipur":           {"lat": 24.6637, "lon": 93.9063},
    "Meghalaya":         {"lat": 25.4670, "lon": 91.3662},
    "Mizoram":           {"lat": 23.1645, "lon": 92.9376},
    "Nagaland":          {"lat": 26.1584, "lon": 94.5624},
    "Odisha":            {"lat": 20.9517, "lon": 85.0985},
    "Puducherry":        {"lat": 11.9416, "lon": 79.8083},
    "Punjab":            {"lat": 31.1471, "lon": 75.3412},
    "Rajasthan":         {"lat": 27.0238, "lon": 74.2179},
    "Sikkim":            {"lat": 27.5330, "lon": 88.5122},
    "Tamil Nadu":        {"lat": 11.1271, "lon": 78.6569},
    "Telangana":         {"lat": 18.1124, "lon": 79.0193},
    "Tripura":           {"lat": 23.9408, "lon": 91.9882},
    "Uttar Pradesh":     {"lat": 26.8467, "lon": 80.9462},
    "Uttarakhand":       {"lat": 30.0668, "lon": 79.0193},
    "West Bengal":       {"lat": 22.9868, "lon": 87.8550},
}

STATE_ALIASES = {
    "andaman and nicobar islands": "Andaman & Nicobar",
    "andaman & nicobar islands": "Andaman & Nicobar",
    "a & n islands": "Andaman & Nicobar",
    "andhra pradesh": "Andhra Pradesh", "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam", "bihar": "Bihar", "chandigarh": "Chandigarh",
    "chhattisgarh": "Chhattisgarh", "chhatisgarh": "Chhattisgarh",
    "dadra and nagar haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra and nagar haveli and daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra & nagar haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "daman & diu": "Dadra & Nagar Haveli and Daman & Diu",
    "the dadra and nagar haveli and daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "delhi": "Delhi", "nct of delhi": "Delhi", "goa": "Goa", "gujarat": "Gujarat",
    "haryana": "Haryana", "himachal pradesh": "Himachal Pradesh",
    "jammu and kashmir": "Jammu and Kashmir", "jammu & kashmir": "Jammu and Kashmir",
    "jharkhand": "Jharkhand", "karnataka": "Karnataka", "kerala": "Kerala",
    "ladakh": "Ladakh", "lakshadweep": "Lakshadweep",
    "madhya pradesh": "Madhya Pradesh", "maharashtra": "Maharashtra",
    "manipur": "Manipur", "meghalaya": "Meghalaya", "mizoram": "Mizoram",
    "nagaland": "Nagaland", "odisha": "Odisha", "orissa": "Odisha",
    "puducherry": "Puducherry", "pondicherry": "Puducherry", "punjab": "Punjab",
    "rajasthan": "Rajasthan", "sikkim": "Sikkim", "tamil nadu": "Tamil Nadu",
    "telangana": "Telangana", "tripura": "Tripura", "uttar pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand", "uttaranchal": "Uttarakhand",
    "west bengal": "West Bengal", "westbengal": "West Bengal",
    "west  bengal": "West Bengal", "west bangal": "West Bengal",
}

INDIA_HOLIDAYS_2025 = pd.to_datetime([
    "2025-03-14","2025-03-31","2025-04-06","2025-04-14","2025-04-18",
    "2025-05-01","2025-06-06","2025-06-27","2025-07-06","2025-08-15",
    "2025-08-16","2025-09-05","2025-10-02","2025-10-20","2025-10-21",
    "2025-10-22","2025-11-05","2025-12-25",
])

def _norm(val):
    """Strict state normalizer — no fallback, numeric guard."""
    if pd.isna(val): return np.nan
    s = str(val).strip()
    try:
        int(s); return np.nan
    except ValueError:
        pass
    result = STATE_ALIASES.get(s.lower())
    return result if result else np.nan

# ── Inference feature helpers (mirrors train_models.py build_features) ────────
_POP_QUINTILES = np.quantile(list(STATE_POPULATION.values()), [0.2, 0.4, 0.6, 0.8])

def _pop_tier(state):
    return int(np.searchsorted(_POP_QUINTILES, STATE_POPULATION.get(state, _MEDIAN_POP)))

def _hol_vecs(dates_series):
    dates = pd.to_datetime(dates_series)
    hdays = INDIA_HOLIDAYS_2025
    is_hol = dates.isin(hdays).astype(int).values
    d2n = np.full(len(dates), 30.0)
    d2p = np.full(len(dates), 30.0)
    for i, d in enumerate(dates):
        fut = hdays[hdays > d]
        pas = hdays[hdays <= d]
        if len(fut): d2n[i] = min((fut.min() - d).days, 30)
        if len(pas): d2p[i] = min((d - pas.max()).days, 30)
    return is_hol, d2n, d2p

@st.cache_data(show_spinner=False)
def build_inference_df(df):
    """Feature engineering matching train_models.py — used for model predictions."""
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    if "total_system_load" not in df.columns:
        for c in ["total_enrolments","demo_total","bio_total"]:
            if c not in df.columns: df[c] = 0
        df["total_system_load"] = df["total_enrolments"] + df["demo_total"] + df["bio_total"]

    dfs = []
    for state, grp in df.groupby("norm_state"):
        grp = grp.sort_values("date").copy()
        full_idx = pd.date_range(grp["date"].min(), grp["date"].max(), freq="D")
        grp = grp.set_index("date").reindex(full_idx); grp.index.name = "date"
        for c in ["bio_total","demo_total","age_0_5","age_5_17","age_18_greater"]:
            if c in grp.columns: grp[c] = grp[c].ffill(limit=7).fillna(0)
        grp["norm_state"] = state; grp = grp.reset_index()
        pop = STATE_POPULATION.get(state, _MEDIAN_POP)
        grp["day_of_week"]  = grp["date"].dt.dayofweek
        grp["day_of_month"] = grp["date"].dt.day
        grp["month"]        = grp["date"].dt.month
        grp["quarter"]      = grp["date"].dt.quarter
        grp["day_of_year"]  = grp["date"].dt.dayofyear
        grp["is_weekend"]   = grp["day_of_week"].isin([5,6]).astype(int)
        grp["days_since_start"] = (grp["date"] - grp["date"].min()).dt.days
        grp["sin_dow"]   = np.sin(2*np.pi*grp["day_of_week"]/7)
        grp["cos_dow"]   = np.cos(2*np.pi*grp["day_of_week"]/7)
        grp["sin_month"] = np.sin(2*np.pi*grp["month"]/12)
        grp["cos_month"] = np.cos(2*np.pi*grp["month"]/12)
        grp["log_state_pop"]  = np.log1p(pop)
        grp["state_pop_tier"] = _pop_tier(state)
        grp["state_cat"]      = hash(state) % 100
        is_hol, d2n, d2p = _hol_vecs(grp["date"])
        grp["is_holiday"]         = is_hol
        grp["days_to_holiday"]    = d2n
        grp["days_since_holiday"] = d2p
        grp["holiday_proximity"]  = np.exp(-d2n / 7)
        grp["holiday_recency"]    = np.exp(-d2p / 7)
        te = grp["total_enrolments"]; tl = grp["total_system_load"]
        for lag in [1, 3, 7, 14, 30]:
            grp[f"lag_{lag}"]      = te.shift(lag)
            grp[f"bio_lag_{lag}"]  = grp["bio_total"].shift(lag)
            grp[f"demo_lag_{lag}"] = grp["demo_total"].shift(lag)
            grp[f"load_lag_{lag}"] = tl.shift(lag)
        for w in [3, 7, 14, 30]:
            se = te.shift(1); sl = tl.shift(1)
            grp[f"rolling_mean_{w}"] = se.rolling(w, min_periods=1).mean()
            grp[f"rolling_std_{w}"]  = se.rolling(w, min_periods=1).std().fillna(0)
            grp[f"load_rolling_{w}"] = sl.rolling(w, min_periods=1).mean()
            grp[f"load_std_{w}"]     = sl.rolling(w, min_periods=1).std().fillna(0)
            grp[f"bio_rolling_{w}"]  = grp["bio_total"].shift(1).rolling(w, min_periods=1).mean()
            grp[f"demo_rolling_{w}"] = grp["demo_total"].shift(1).rolling(w, min_periods=1).mean()
        grp["bio_to_enrol_ratio"]  = (grp["bio_rolling_7"]  / (grp["rolling_mean_7"] + 1)).fillna(0)
        grp["demo_to_enrol_ratio"] = (grp["demo_rolling_7"] / (grp["rolling_mean_7"] + 1)).fillna(0)
        grp["rolling_cv_7"]        = (grp["rolling_std_7"]  / (grp["rolling_mean_7"] + 1)).fillna(0)
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
        grp["total_enrolments"]  = grp["total_enrolments"].fillna(0)
        grp["total_system_load"] = grp["total_system_load"].fillna(0)
        dfs.append(grp)

    if not dfs:
        return pd.DataFrame()
    out = pd.concat(dfs, ignore_index=True).fillna(0)
    ss_path = os.path.join("pkl_models", "state_stats.csv")
    if os.path.exists(ss_path):
        ss = pd.read_csv(ss_path)
        out = out.merge(ss, on="norm_state", how="left")
        for c in ["state_mean_enrol","state_std_enrol","state_median_enrol"]:
            if c in out.columns:
                out[c] = out[c].fillna(out[c].mean())
    return out

# ── Data loaders ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_raw_data():
    def _read(pattern):
        files = sorted(glob.glob(os.path.join(".", pattern), recursive=True))
        dfs = [pd.read_csv(f, dtype={"state": str, "district": str}) for f in files]
        if not dfs: return pd.DataFrame()
        df = pd.concat(dfs, ignore_index=True)
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
        df["norm_state"] = df["state"].apply(_norm)
        return df.dropna(subset=["norm_state"])

    enrol = _read("api_data_aadhar_enrolment/**/*.csv")
    if not enrol.empty:
        enrol["total_enrolments"] = enrol[["age_0_5","age_5_17","age_18_greater"]].fillna(0).sum(axis=1)
        enrol = enrol.groupby(["date","norm_state"])[
            ["age_0_5","age_5_17","age_18_greater","total_enrolments"]].sum().reset_index()

    demo = _read("api_data_aadhar_demographic/**/*.csv")
    if not demo.empty:
        demo["demo_total"] = demo[["demo_age_5_17","demo_age_17_"]].fillna(0).sum(axis=1)
        demo = demo.groupby(["date","norm_state"])[
            ["demo_age_5_17","demo_age_17_","demo_total"]].sum().reset_index()

    bio = _read("api_data_aadhar_biometric/**/*.csv")
    if not bio.empty:
        bio["bio_total"] = bio[["bio_age_5_17","bio_age_17_"]].fillna(0).sum(axis=1)
        bio = bio.groupby(["date","norm_state"])[
            ["bio_age_5_17","bio_age_17_","bio_total"]].sum().reset_index()

    m = pd.merge(enrol, demo, on=["date","norm_state"], how="outer") if not enrol.empty else demo
    if not bio.empty: m = pd.merge(m, bio, on=["date","norm_state"], how="outer")
    for c in ["total_enrolments","demo_total","bio_total"]:
        if c in m.columns: m[c] = m[c].fillna(0)
    return m

@st.cache_data(show_spinner=False)
def build_feature_panel(df):
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["norm_state","date"]).reset_index(drop=True)
    if df["date"].dropna().empty:
        return pd.DataFrame()

    states    = df["norm_state"].dropna().unique()
    all_dates = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    grid = pd.MultiIndex.from_product([states, all_dates], names=["norm_state","date"]).to_frame(index=False)
    full = pd.merge(grid, df, on=["norm_state","date"], how="left")

    for c in ["age_0_5","age_5_17","age_18_greater","total_enrolments",
              "demo_age_5_17","demo_age_17_","demo_total","bio_age_5_17","bio_age_17_","bio_total"]:
        if c in full.columns: full[c] = full[c].fillna(0)

    full["total_system_load"] = full["total_enrolments"] + full["demo_total"] + full["bio_total"]
    full["day_of_week"] = full["date"].dt.dayofweek
    full["month"]       = full["date"].dt.month
    full["is_weekend"]  = full["day_of_week"].isin([5,6]).astype(int)
    full["sin_dow"]     = np.sin(2*np.pi*full["day_of_week"]/7)
    full["cos_dow"]     = np.cos(2*np.pi*full["day_of_week"]/7)
    full["sin_month"]   = np.sin(2*np.pi*full["month"]/12)
    full["cos_month"]   = np.cos(2*np.pi*full["month"]/12)
    full["log_state_pop"] = np.log1p(full["norm_state"].map(STATE_POPULATION).fillna(_MEDIAN_POP))

    dates_arr = pd.to_datetime(full["date"])
    full["is_holiday"] = dates_arr.isin(INDIA_HOLIDAYS_2025).astype(int)
    days_to_next = np.zeros(len(full), dtype=float)
    for i, d in enumerate(dates_arr):
        fut = INDIA_HOLIDAYS_2025[INDIA_HOLIDAYS_2025 > d]
        days_to_next[i] = min((fut.min() - d).days, 30) if len(fut) > 0 else 30
    full["days_to_holiday"]   = days_to_next
    full["holiday_proximity"] = np.exp(-days_to_next / 7)

    dfs = []
    for state, grp in full.groupby("norm_state"):
        grp = grp.sort_values("date").copy()
        pop = STATE_POPULATION.get(state, _MEDIAN_POP)
        for lag in [1, 7]:
            grp[f"lag_{lag}"]       = grp["total_enrolments"].shift(lag)
            grp[f"bio_lag_{lag}"]   = grp["bio_total"].shift(lag)
            grp[f"demo_lag_{lag}"]  = grp["demo_total"].shift(lag)
            grp[f"load_lag_{lag}"]  = grp["total_system_load"].shift(lag)
        s_enrol = grp["total_enrolments"].shift(1)
        s_load  = grp["total_system_load"].shift(1)
        grp["rolling_mean_7"]  = s_enrol.rolling(7,  min_periods=1).mean()
        grp["rolling_mean_30"] = s_enrol.rolling(30, min_periods=1).mean()
        grp["rolling_std_7"]   = s_enrol.rolling(7,  min_periods=1).std().fillna(0)
        grp["load_rolling_7"]  = s_load.rolling(7,  min_periods=1).mean()
        grp["load_rolling_30"] = s_load.rolling(30, min_periods=1).mean()
        grp["bio_rolling_7"]   = grp["bio_total"].shift(1).rolling(7, min_periods=1).mean()
        grp["demo_rolling_7"]  = grp["demo_total"].shift(1).rolling(7, min_periods=1).mean()
        grp["bio_to_enrol_ratio"]  = (grp["bio_rolling_7"]  / (grp["rolling_mean_7"] + 1)).fillna(0)
        grp["demo_to_enrol_ratio"] = (grp["demo_rolling_7"] / (grp["rolling_mean_7"] + 1)).fillna(0)
        grp["lag_1_per_1000"]          = grp["lag_1"] / pop * 1000
        grp["rolling_mean_7_per_1000"] = grp["rolling_mean_7"] / pop * 1000
        s1 = grp["total_enrolments"].shift(1)
        grp["ewm_7"]           = s1.ewm(span=7, min_periods=1).mean()
        grp["ewm_trend"]       = ((grp["ewm_7"] - grp["rolling_mean_30"]) / (grp["rolling_mean_30"] + 1)).fillna(0)
        grp["system_velocity"] = ((grp["bio_rolling_7"] + grp["demo_rolling_7"]) / (grp["rolling_mean_7"] + 1)).fillna(0)
        grp["mom_growth"]      = ((grp["rolling_mean_7"] - grp["rolling_mean_30"]) / (grp["rolling_mean_30"] + 1)).fillna(0)
        grp["lifecycle_stage"] = (grp["system_velocity"] > 5.0).astype(int)
        dfs.append(grp)
    return pd.concat(dfs, ignore_index=True).fillna(0)

@st.cache_resource(show_spinner=False)
def load_models():
    pkl = "pkl_models"
    out = {"model_A": None, "model_B": None, "meta": {}}
    if not os.path.exists(pkl): return out

    meta_path = os.path.join(pkl, "feature_metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            out["meta"] = json.load(f)

    # Model B (enrolments)
    try:
        em_b = joblib.load(os.path.join(pkl, "ensemble_meta.pkl"))
        sc_b = joblib.load(os.path.join(pkl, em_b.get("scaler", "ridge_scaler.pkl")))
        base_b = {
            "Ridge":         joblib.load(os.path.join(pkl, "ridge_baseline_model.pkl")),
            "Random Forest": joblib.load(os.path.join(pkl, "random_forest_model.pkl")),
            "XGBoost":       joblib.load(os.path.join(pkl, "xgboost_model.pkl")),
            "LightGBM":      joblib.load(os.path.join(pkl, "lightgbm_model.pkl")),
        }
        # Load per-state normalization params (v3 pipeline: relative target)
        norm_path = os.path.join(pkl, "state_norm_params.csv")
        state_norm_map = {}
        if os.path.exists(norm_path):
            _np = pd.read_csv(norm_path)
            state_norm_map = dict(zip(_np["norm_state"], _np["state_mean_enrol"]))
        out["model_B"] = {"ensemble_meta": em_b, "scaler": sc_b, "models": base_b,
                          "state_norm_map": state_norm_map}
    except Exception as e:
        st.warning(f"Model B load: {e}")

    # Model A (system_load)
    try:
        em_a = joblib.load(os.path.join(pkl, "modelA_ensemble_meta.pkl"))
        sc_a = joblib.load(os.path.join(pkl, em_a.get("scaler", "modelA_scaler.pkl")))
        base_a = {
            "Ridge":         joblib.load(os.path.join(pkl, "modelA_ridge.pkl")),
            "Random Forest": joblib.load(os.path.join(pkl, "modelA_rf.pkl")),
            "XGBoost":       joblib.load(os.path.join(pkl, "modelA_xgb.pkl")),
            "LightGBM":      joblib.load(os.path.join(pkl, "modelA_lgb.pkl")),
        }
        out["model_A"] = {"ensemble_meta": em_a, "scaler": sc_a, "models": base_a}
    except Exception as e:
        st.warning(f"Model A load: {e}")

    return out

def _get_feature_cols(em):
    """ensemble_meta may store feature list under 'feature_cols' or 'features'."""
    return em.get("feature_cols") or em.get("features") or []

def _weight_key(model_name):
    """Map display model name → weight dict key (handles both cases)."""
    n = model_name.lower()
    if "random" in n or n == "rf":    return ("RF", "rf")
    if "xgboost" in n or n == "xgb":  return ("XGBoost", "xgb")
    if "lightgbm" in n or n == "lgb": return ("LightGBM", "lgb")
    if "ridge" in n:                   return ("Ridge", "ridge")
    return (model_name.split()[0], model_name.split()[0].lower())

def _ensemble_predict(mdl_dict, feature_row_df, state=None):
    em    = mdl_dict["ensemble_meta"]
    sc    = mdl_dict["scaler"]
    wts   = em["weights"]
    fcols = _get_feature_cols(em)
    avail = [c for c in fcols if c in feature_row_df.columns]
    if not avail:
        return 0.0
    Xs    = sc.transform(feature_row_df[avail])
    pred  = 0.0
    for mn, mp in mdl_dict["models"].items():
        candidates = _weight_key(mn)
        w = next((wts[k] for k in candidates if k in wts), None)
        if w is None: continue
        pred += w * max(0.0, float(mp.predict(Xs)[0]))
    pred = max(0.0, pred)
    # v3 pipeline: Model B trains on relative target (enrol / state_mean);
    # multiply back by state mean to recover absolute count prediction.
    if em.get("relative_target") and state is not None:
        norm_map = mdl_dict.get("state_norm_map", {})
        state_mean = norm_map.get(state, 1.0) or 1.0
        pred = pred * state_mean
    return pred

def _single_model_predict(mdl_dict, model_name, feature_row_df):
    sc    = mdl_dict["scaler"]
    em    = mdl_dict["ensemble_meta"]
    fcols = _get_feature_cols(em)
    avail = [c for c in fcols if c in feature_row_df.columns]
    if not avail:
        return None
    Xs    = sc.transform(feature_row_df[avail])
    mp    = mdl_dict["models"].get(model_name)
    if mp is None: return None
    return max(0.0, float(mp.predict(Xs)[0]))

# ── Load everything ───────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🪪 Aadhaar Intelligence Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">36 States · Two-Model Routing · Operations · Migration · Fraud Prevention</div>', unsafe_allow_html=True)

with st.spinner("Loading data & models…"):
    panel_df     = load_raw_data()
    feature_df   = build_feature_panel(panel_df)   # used for charts/viz
    inference_df = build_inference_df(panel_df)    # used for model predictions
    mdls         = load_models()

# ── Pull R² from model_comparison.json (best per group) ──────────────────────
_r2_A, _r2_B = "–", "–"
_comp_path = os.path.join("pkl_models", "model_comparison.json")
if os.path.exists(_comp_path):
    try:
        _cj = json.load(open(_comp_path))
        _best_A, _best_B = None, None
        for row in _cj:
            name = str(row.get("Model","")).lower()
            r2   = row.get("R2", row.get("test_r2", row.get("r2", None)))
            if r2 is None:
                continue
            r2 = float(r2)
            if "(a)" in name or "model a" in name or "system_load" in name:
                if _best_A is None or r2 > _best_A:
                    _best_A = r2
            elif "(b)" in name or "model b" in name or "enrol" in name:
                if _best_B is None or r2 > _best_B:
                    _best_B = r2
        if _best_A is not None: _r2_A = f"{_best_A:.4f}"
        if _best_B is not None: _r2_B = f"{_best_B:.4f}"
    except Exception:
        pass

# ── Lifecycle classification ──────────────────────────────────────────────────
_lc_df = panel_df.groupby("norm_state").agg(
    te=("total_enrolments","sum"), dt=("demo_total","sum"), bt=("bio_total","sum")).reset_index()
_lc_df["ratio"] = (_lc_df["dt"] + _lc_df["bt"]) / (_lc_df["te"] + 1)
_lc_df["stage"] = _lc_df["ratio"].apply(lambda r: "Growth" if r <= 5 else "Maintenance")
growth_states = set(_lc_df[_lc_df["stage"] == "Growth"]["norm_state"])

# ── Predicted loads for sidebar alerts ───────────────────────────────────────
@st.cache_data(show_spinner=False)
def _compute_predicted_loads(_feature_df, _mdls):
    """Predict system load for all states on last date — used for 90th-pct alerts."""
    if _mdls["model_A"] is None: return {}
    last_date = _feature_df["date"].max()
    last_feat = _feature_df[_feature_df["date"] == last_date]
    preds = {}
    for _, row in last_feat.iterrows():
        try:
            p = _ensemble_predict(_mdls["model_A"], pd.DataFrame([row]))
            preds[row["norm_state"]] = p
        except Exception:
            pass
    return preds

pred_loads = _compute_predicted_loads(inference_df, mdls)
_thresh_90 = np.percentile(list(pred_loads.values()), 90) if pred_loads else 0
_alert_states = [s for s, v in pred_loads.items() if v >= _thresh_90]

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🎛️ Navigation & Filters")
_states = sorted(panel_df["norm_state"].dropna().unique())
selected_state = st.sidebar.selectbox("Filter State", ["All States"] + _states)

_date_col = panel_df["date"].dropna()
if not _date_col.empty:
    d_min, d_max = _date_col.min().date(), _date_col.max().date()
    sel_dates = st.sidebar.date_input("Date Range", [d_min, d_max], min_value=d_min, max_value=d_max)
    s_date, e_date = (sel_dates[0], sel_dates[1]) if len(sel_dates) == 2 else (d_min, d_max)
    filt = panel_df[(panel_df["date"].dt.date >= s_date) & (panel_df["date"].dt.date <= e_date)].copy()
else:
    st.sidebar.warning("No data found.")
    filt = panel_df.copy()

if selected_state != "All States":
    filt = filt[filt["norm_state"] == selected_state].copy()

# 90th-percentile workload alerts in sidebar
if _alert_states:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚠️ High-Load Alerts (>90th pct)")
    for s in _alert_states[:5]:
        v = pred_loads.get(s, 0)
        st.sidebar.markdown(
            f'<div class="alert-box">⚠️ <b>{s}</b><br>Pred Load: {int(v):,}</div>',
            unsafe_allow_html=True
        )
    if len(_alert_states) > 5:
        st.sidebar.markdown(f"*+{len(_alert_states)-5} more states above threshold*")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Data:** {len(panel_df):,} rows · {panel_df['norm_state'].nunique()} states")
st.sidebar.markdown(f"**Threshold:** {int(_thresh_90):,} system load units")

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Executive Dashboard",
    "🗺️ Geo Heatmap",
    "🚶 Migration Intelligence",
    "🤖 Model Leaderboard",
    "🔮 7-Day Forecast",
    "🚨 Anomaly Engine",
    "🧠 Intelligence Engine",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: Executive Dashboard
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("📌 Key Activity Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Enrolments",    f"{int(filt['total_enrolments'].sum()):,}")
    c2.metric("Demographic Updates", f"{int(filt['demo_total'].sum()):,}")
    c3.metric("Biometric Updates",   f"{int(filt['bio_total'].sum()):,}")
    c4.metric("States Covered",      f"{filt['norm_state'].nunique()}")

    # System velocity (avg update-to-enrolment ratio)
    _te = filt["total_enrolments"].sum()
    _up = filt["demo_total"].sum() + filt["bio_total"].sum()
    _sv = _up / (_te + 1)
    c1b, c2b, c3b = st.columns(3)
    c1b.metric("System Velocity (Updates÷Enrolments)", f"{_sv:,.1f}x", help=">5x → Maintenance phase")
    c2b.metric("Growth States", f"{len(growth_states)}", delta=f"of {panel_df['norm_state'].nunique()}")
    c3b.metric("Maintenance States", f"{panel_df['norm_state'].nunique() - len(growth_states)}", delta="Aadhaar saturated")

    st.download_button("📥 Export Summary CSV",
        filt.to_csv(index=False).encode(), "aadhaar_summary.csv", "text/csv")

    daily = filt.groupby("date")[["total_enrolments","demo_total","bio_total"]].sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["total_enrolments"], name="Enrolments",   line=dict(color="#1f77b4", width=2)))
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["demo_total"],       name="Demo Updates", line=dict(color="#ff7f0e", width=2)))
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["bio_total"],        name="Bio Updates",  line=dict(color="#2ca02c", width=2)))
    fig.update_layout(template="plotly_dark", height=420, hovermode="x unified",
                      xaxis_title="Date", yaxis_title="Volume",
                      title="National Daily Activity (Enrolments vs Updates)")
    st.plotly_chart(fig, width='stretch')

    a, b = st.columns(2)
    with a:
        top10 = filt.groupby("norm_state")["total_enrolments"].sum().reset_index().sort_values("total_enrolments", ascending=False).head(10)
        fig2  = px.bar(top10, x="total_enrolments", y="norm_state", orientation="h",
                       color="total_enrolments", color_continuous_scale="Viridis", template="plotly_dark",
                       title="Top 10 States by Enrolments")
        fig2.update_layout(yaxis={"categoryorder":"total ascending"}, height=380)
        st.plotly_chart(fig2, width='stretch')
    with b:
        age_sums = {
            "Age 0–5":  filt["age_0_5"].sum()        if "age_0_5"        in filt.columns else 0,
            "Age 5–17": filt["age_5_17"].sum()       if "age_5_17"       in filt.columns else 0,
            "Age 18+":  filt["age_18_greater"].sum() if "age_18_greater" in filt.columns else 0,
        }
        fig3 = px.pie(names=list(age_sums), values=list(age_sums.values()),
                      hole=0.4, template="plotly_dark", title="Age Group Share",
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig3.update_layout(height=380)
        st.plotly_chart(fig3, width='stretch')

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: Geo Heatmap (Scattermapbox)
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("🗺️ Live Geo Intelligence — State Workload Heatmap")

    geo_metric = st.radio("Map metric", ["System Load (Forecast)", "Total Enrolments", "Bio+Demo Updates"],
                          horizontal=True)

    sgeo = filt.groupby("norm_state").agg(
        total_enrolments=("total_enrolments","sum"),
        demo_total=("demo_total","sum"),
        bio_total=("bio_total","sum"),
    ).reset_index()
    sgeo["update_total"]  = sgeo["demo_total"] + sgeo["bio_total"]
    sgeo["system_load"]   = sgeo["total_enrolments"] + sgeo["update_total"]
    sgeo["predicted_load"] = sgeo["norm_state"].map(pred_loads).fillna(sgeo["system_load"])
    sgeo["lifecycle"]     = sgeo["norm_state"].apply(lambda s: "Growth" if s in growth_states else "Maintenance")
    sgeo["lat"] = sgeo["norm_state"].map(lambda s: STATE_COORDINATES.get(s, {}).get("lat", np.nan))
    sgeo["lon"] = sgeo["norm_state"].map(lambda s: STATE_COORDINATES.get(s, {}).get("lon", np.nan))
    sgeo = sgeo.dropna(subset=["lat","lon"])

    size_col = {"System Load (Forecast)": "predicted_load",
                "Total Enrolments": "total_enrolments",
                "Bio+Demo Updates": "update_total"}[geo_metric]
    sgeo["bubble_size"] = np.log1p(sgeo[size_col]) * 5

    color_map = {"Growth": "#2ca02c", "Maintenance": "#d62728"}

    try:
        fig_map = px.scatter_map(
            sgeo, lat="lat", lon="lon",
            hover_name="norm_state",
            hover_data={"total_enrolments": True, "update_total": True,
                        "predicted_load": True, "lifecycle": True, "lat": False, "lon": False},
            size="bubble_size", size_max=50,
            color="lifecycle",
            color_discrete_map=color_map,
            map_style="carto-darkmatter",
            zoom=3.8, center={"lat": 22.5, "lon": 82.0},
            title=f"Aadhaar State Intelligence Map — {geo_metric}",
            height=580,
        )
        fig_map.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_map, width='stretch')
    except Exception as _map_err:
        st.warning(f"Map render failed (check network/tile access): {_map_err}")
        # Fallback: plain bar chart
        _fb = sgeo.sort_values(size_col, ascending=False).head(20)
        fig_fallback = px.bar(_fb, x=size_col, y="norm_state", orientation="h",
                              color="lifecycle", color_discrete_map=color_map,
                              template="plotly_dark", height=500,
                              title=f"State Workload — {geo_metric} (map unavailable)")
        fig_fallback.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_fallback, width='stretch')

    leg_a, leg_b = st.columns(2)
    leg_a.markdown("🟢 **Growth** — active new registrations (Model B routing)")
    leg_b.markdown("🔴 **Maintenance** — Aadhaar saturation, update load dominates (Model A routing)")

    # Enrolment by day-of-week + correlation
    a, b = st.columns(2)
    with a:
        sdf = filt.dropna(subset=["date"]).copy()
        sdf["day_name"] = pd.to_datetime(sdf["date"]).dt.day_name()
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        fig_box = px.box(sdf, x="day_name", y="total_enrolments", category_orders={"day_name": day_order},
                         color="day_name", template="plotly_dark", title="Enrolment by Day of Week")
        fig_box.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig_box, width='stretch')
    with b:
        corr = filt[["total_enrolments","demo_total","bio_total"]].corr()
        fig_c = px.imshow(corr, text_auto=".2f", color_continuous_scale="Blues",
                          template="plotly_dark", title="Cross-Shard Correlation")
        fig_c.update_layout(height=380)
        st.plotly_chart(fig_c, width='stretch')

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: Migration Intelligence
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("🚶 Migration Intelligence — Demographic Update Patterns")
    st.markdown("""
    **Demographic updates** (address changes, name corrections) serve as a **proxy for migration activity**.
    High `demo_total` in a state signals residents relocating there — creating Aadhaar update demand.
    """)

    # Top metric cards
    m1, m2, m3 = st.columns(3)
    state_demo = panel_df.groupby("norm_state")["demo_total"].sum().reset_index()
    top_hub_state = "N/A"
    top_hub_val   = 0
    if not state_demo.empty:
        _th = state_demo.sort_values("demo_total", ascending=False).iloc[0]
        top_hub_state = _th["norm_state"]
        top_hub_val   = int(_th["demo_total"])
    daily_inflow  = panel_df.groupby("date")["demo_total"].sum()
    latest_inflow = int(daily_inflow.iloc[-1]) if not daily_inflow.empty else 0
    total_updates = panel_df["demo_total"].sum()

    m1.markdown(f"""<div class="metric-card">
        <div class="metric-val">{latest_inflow:,}</div>
        <div class="metric-lbl">Daily Demo Updates (Latest)</div>
    </div>""", unsafe_allow_html=True)
    m2.markdown(f"""<div class="metric-card">
        <div class="metric-val">{top_hub_state}</div>
        <div class="metric-lbl">Top Migration Hub</div>
    </div>""", unsafe_allow_html=True)
    m3.markdown(f"""<div class="metric-card">
        <div class="metric-val">{top_hub_val:,}</div>
        <div class="metric-lbl">Updates in Top Hub (Period)</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # State selector for trend
    mig_state = st.selectbox("Select state for migration trend", _states, key="mig_state")
    state_mig  = panel_df[panel_df["norm_state"] == mig_state].groupby("date")[["demo_total","bio_total","total_enrolments"]].sum().reset_index()

    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(
        x=state_mig["date"], y=state_mig["demo_total"],
        name="Demographic Updates", fill="tozeroy",
        line=dict(color="#43A047", width=2), fillcolor="rgba(67,160,71,0.25)"
    ))
    fig_area.add_trace(go.Scatter(
        x=state_mig["date"], y=state_mig["bio_total"],
        name="Biometric Updates", fill="tozeroy",
        line=dict(color="#1E88E5", width=2), fillcolor="rgba(30,136,229,0.20)"
    ))
    fig_area.add_trace(go.Scatter(
        x=state_mig["date"], y=state_mig["total_enrolments"],
        name="New Enrolments", line=dict(color="#FDD835", width=2, dash="dot")
    ))
    fig_area.update_layout(
        template="plotly_dark", height=400, hovermode="x unified",
        title=f"Migration Proxy Trend — {mig_state}",
        xaxis_title="Date", yaxis_title="Volume"
    )
    st.plotly_chart(fig_area, width='stretch')

    st.markdown("---")

    # Top 5 migration corridors (states with highest demo velocity = updates/enrolments)
    st.subheader("📍 Top Migration Corridors (Update Velocity Ranking)")
    mig_df = panel_df.groupby("norm_state").agg(
        demo=("demo_total","sum"), bio=("bio_total","sum"), enrol=("total_enrolments","sum")
    ).reset_index()
    mig_df["update_velocity"] = (mig_df["demo"] + mig_df["bio"]) / (mig_df["enrol"] + 1)
    mig_df["lifecycle"] = mig_df["norm_state"].apply(lambda s: "Growth" if s in growth_states else "Maintenance")
    mig_df = mig_df.sort_values("update_velocity", ascending=False)

    fig_mig = px.bar(mig_df, x="update_velocity", y="norm_state", orientation="h",
                     color="lifecycle", color_discrete_map={"Growth":"#2ca02c","Maintenance":"#d62728"},
                     template="plotly_dark", height=600,
                     title="State Migration Pressure (Update-to-Enrolment Velocity)",
                     labels={"update_velocity":"Update Velocity (ratio)","norm_state":"State"})
    fig_mig.update_layout(yaxis={"categoryorder":"total ascending"})
    st.plotly_chart(fig_mig, width='stretch')

    # Monthly migration heatmap
    st.subheader("📅 Monthly Demo Update Heatmap (Top 15 States)")
    top15_states = mig_df.head(15)["norm_state"].tolist()
    heat_df = panel_df[panel_df["norm_state"].isin(top15_states)].copy()
    heat_df["month_str"] = heat_df["date"].dt.to_period("M").astype(str)
    pivot = heat_df.groupby(["norm_state","month_str"])["demo_total"].sum().unstack(fill_value=0)
    fig_heat = px.imshow(
        pivot, color_continuous_scale="Greens",
        template="plotly_dark", height=480,
        title="Monthly Demographic Update Volume (Migration Proxy)",
        labels={"x":"Month","y":"State","color":"Demo Updates"}
    )
    st.plotly_chart(fig_heat, width='stretch')

    # Policy alert table
    st.subheader("📋 Policy Alert: States Needing Awareness Campaigns")
    alert_df = mig_df[mig_df["lifecycle"] == "Growth"][["norm_state","enrol","demo","update_velocity"]].copy()
    alert_df.columns = ["State","Total Enrolments","Demo Updates","Update Velocity"]
    alert_df["Recommended Action"] = alert_df["Update Velocity"].apply(
        lambda v: "🔴 Deploy Mobile Camp" if v < 1 else ("🟡 Awareness Drive" if v < 3 else "🟢 Monitor")
    )
    st.dataframe(alert_df.reset_index(drop=True), width='stretch')

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: Model Leaderboard
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("🤖 ML Model Benchmarks — Two-Model Strategy")

    st.markdown("""
    | Model | Target | Routing | R² |
    |-------|--------|---------|-----|
    | **Ensemble A** | `total_system_load` | Maintenance states (velocity > 5) | ~0.69 |
    | **Ensemble B** | `total_enrolments`  | Growth states | ~0.39 |
    """)

    comp_file = os.path.join("pkl_models", "model_comparison.json")
    if os.path.exists(comp_file):
        try:
            comp_df = pd.DataFrame(json.load(open(comp_file)))
            # Normalise column names: accept test_r2 or r2 or R2
            _col_map = {}
            for col in comp_df.columns:
                lc = col.lower().replace(" ", "_")
                if lc in ("test_r2", "r2", "val_r2"):    _col_map[col] = "test_r2"
                if lc in ("test_rmse", "rmse", "val_rmse"): _col_map[col] = "test_rmse"
                if lc in ("model", "model_name", "name"):   _col_map[col] = "model"
            comp_df = comp_df.rename(columns=_col_map)

            if "test_r2" in comp_df.columns:
                comp_df = comp_df.sort_values("test_r2", ascending=False, na_position="last")
            styled = comp_df.style
            if "test_r2"   in comp_df.columns and comp_df["test_r2"].notna().any():
                styled = styled.highlight_max(axis=0, subset=["test_r2"],   color="#2e7d32")
            if "test_rmse" in comp_df.columns and comp_df["test_rmse"].notna().any():
                styled = styled.highlight_min(axis=0, subset=["test_rmse"], color="#2e7d32")
            st.dataframe(styled, width='stretch')
            st.download_button("📥 Download Leaderboard CSV",
                comp_df.to_csv(index=False).encode(), "model_leaderboard.csv", "text/csv")
            if "test_r2" in comp_df.columns and "model" in comp_df.columns:
                fig_lb = px.bar(comp_df, x="model", y="test_r2", color="test_r2",
                                color_continuous_scale="Greens", template="plotly_dark",
                                title="Test R² — All Models")
                fig_lb.update_layout(height=400)
                st.plotly_chart(fig_lb, width='stretch')
            else:
                st.dataframe(comp_df, width='stretch')
        except Exception as _lb_err:
            st.warning(f"Could not load model leaderboard: {_lb_err}")
    else:
        st.info("Run NB02 to populate model_comparison.json")

    st.markdown("---")
    st.subheader("🔍 Feature Importance (LightGBM Model B)")
    _lgb_path = os.path.join("pkl_models", "lightgbm_model.pkl")
    if os.path.exists(_lgb_path):
        try:
            _lgb2 = joblib.load(_lgb_path)
            _fi = pd.Series(
                _lgb2.feature_importances_,
                index=_lgb2.feature_name_
            ).sort_values(ascending=False).head(20)
            fig_fi = px.bar(
                x=_fi.values[::-1], y=_fi.index[::-1],
                orientation="h", template="plotly_dark",
                title="Top 20 Features — LightGBM Gain Importance",
                labels={"x": "Importance (Gain)", "y": "Feature"},
                color=_fi.values[::-1], color_continuous_scale="Teal",
            )
            fig_fi.update_layout(height=520, showlegend=False)
            st.plotly_chart(fig_fi, width='stretch')
        except Exception as _fi_err:
            st.info(f"Feature importance unavailable: {_fi_err}")
    else:
        st.info("LightGBM model not found — run NB02 to train.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: 7-Day Forecast (two-model routing + model selector)
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.subheader("🔮 7-Day State Forecast — Two-Model Intelligence Routing")

    fc_col1, fc_col2 = st.columns([2, 1])
    with fc_col1:
        state_choice = st.selectbox("State", _states, key="fc_state")
        days_ahead   = st.slider("Forecast horizon (days)", 1, 30, 7)
    with fc_col2:
        lc = _lc_df[_lc_df["norm_state"] == state_choice]["stage"].values
        lc_stage = lc[0] if len(lc) > 0 else "Maintenance"
        badge_cls = "badge-growth" if lc_stage == "Growth" else "badge-maint"
        st.markdown(f"""
        **Lifecycle:** <span class="badge {badge_cls}">{lc_stage}</span><br><br>
        - **Growth** → Model B (enrolments, R²≈0.39)
        - **Maintenance** → Model A (system load, R²≈0.69)
        """, unsafe_allow_html=True)

    active_mdl_dict = mdls["model_B"] if lc_stage == "Growth" else mdls["model_A"]
    if active_mdl_dict and "models" in active_mdl_dict:
        model_names = list(active_mdl_dict["models"].keys()) + ["Ensemble"]
    else:
        model_names = ["Ensemble"]
    model_choice = st.selectbox("Model selector", model_names, index=len(model_names)-1)

    if st.button("🚀 Run Forecast"):
        if not active_mdl_dict:
            st.error("No model loaded for this lifecycle stage. Run NB02 to train models.")
        else:
            state_feat = inference_df[inference_df["norm_state"] == state_choice].sort_values("date")
            if state_feat.empty:
                st.warning("No feature data for selected state.")
            else:
                latest = state_feat.tail(1)
                try:
                    if model_choice == "Ensemble":
                        pred_val = _ensemble_predict(active_mdl_dict, latest)
                    else:
                        pred_val = _single_model_predict(active_mdl_dict, model_choice, latest)
                        if pred_val is None:
                            pred_val = _ensemble_predict(active_mdl_dict, latest)
                except Exception as e:
                    st.warning(f"Prediction error: {e}")
                    pred_val = 0

                # Also compute both models for comparison
                pred_enrol = pred_load = None
                if mdls["model_B"]:
                    try: pred_enrol = _ensemble_predict(mdls["model_B"], latest, state=state_choice)
                    except: pass
                if mdls["model_A"]:
                    try: pred_load = _ensemble_predict(mdls["model_A"], latest)
                    except: pass

                c_a, c_b, c_c = st.columns(3)
                c_a.metric(f"📌 {model_choice} Prediction", f"{int(pred_val or 0):,}")
                if pred_enrol is not None: c_b.metric("Model B — Enrolments",  f"{int(pred_enrol):,}")
                if pred_load  is not None: c_c.metric("Model A — System Load", f"{int(pred_load):,}")

                # Multi-step quantile forecast
                hist = state_feat.tail(60)
                hist_std = float(state_feat["total_enrolments"].tail(30).std() or 0) or max(pred_val or 1, 1) * 0.15
                future_dates = [hist["date"].max() + pd.Timedelta(days=i) for i in range(1, days_ahead+1)]
                preds_p50 = [(pred_val or 0) * (1 + 0.02*np.sin(i/3)) for i in range(1, days_ahead+1)]
                preds_p10 = [max(0, p - 1.28*hist_std*np.sqrt(i)) for i, p in enumerate(preds_p50, 1)]
                preds_p90 = [p + 1.28*hist_std*np.sqrt(i)          for i, p in enumerate(preds_p50, 1)]

                y_col = "total_enrolments" if lc_stage == "Growth" else "total_system_load"
                if y_col not in hist.columns: y_col = "total_enrolments"

                fig_fc = go.Figure()
                fig_fc.add_trace(go.Scatter(x=hist["date"], y=hist[y_col],
                    name="Historical", line=dict(color="#1f77b4", width=2)))
                fig_fc.add_trace(go.Scatter(x=future_dates, y=preds_p90,
                    name="P90", line=dict(color="rgba(255,127,14,0.3)", dash="dash")))
                fig_fc.add_trace(go.Scatter(x=future_dates, y=preds_p10,
                    name="P10", fill="tonexty",
                    fillcolor="rgba(255,127,14,0.12)",
                    line=dict(color="rgba(255,127,14,0.3)", dash="dash")))
                fig_fc.add_trace(go.Scatter(x=future_dates, y=preds_p50,
                    name=f"P50 — {model_choice}", line=dict(color="#ff7f0e", width=3)))
                fig_fc.update_layout(
                    template="plotly_dark", height=480, hovermode="x unified",
                    title=f"{days_ahead}-Day Forecast — {state_choice} [{lc_stage}] · {model_choice}"
                )
                st.plotly_chart(fig_fc, width='stretch')

                # Forecast table
                fc_table = pd.DataFrame({
                    "Date": future_dates,
                    "P10 (Low)": [int(p) for p in preds_p10],
                    "P50 (Forecast)": [int(p) for p in preds_p50],
                    "P90 (High)": [int(p) for p in preds_p90],
                })
                st.dataframe(fc_table, width='stretch')
                st.download_button("📥 Download Forecast CSV",
                    fc_table.to_csv(index=False).encode(), "forecast.csv", "text/csv")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: Anomaly Engine
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.subheader("🚨 Anomaly Alert Engine")

    a6_col1, a6_col2 = st.columns(2)
    with a6_col1:
        z_thresh = st.slider("Z-Score Threshold", 2.0, 5.0, 3.0, 0.1)
    with a6_col2:
        iso_contamination = st.slider("Isolation Forest contamination", 0.01, 0.15, 0.05, 0.01)

    # Z-score anomaly detection
    anom_rows = []
    for state, grp in filt.sort_values(["norm_state","date"]).groupby("norm_state"):
        grp = grp.copy()
        rm  = grp["total_enrolments"].rolling(14, min_periods=3).mean()
        rs  = grp["total_enrolments"].rolling(14, min_periods=3).std().fillna(1)
        grp["z_score"]   = ((grp["total_enrolments"] - rm) / np.maximum(rs, 1e-5)).fillna(0)
        grp["is_anomaly"] = np.abs(grp["z_score"]) > z_thresh
        anom_rows.append(grp[grp["is_anomaly"]])

    anom_full = pd.concat(anom_rows, ignore_index=True) if anom_rows else pd.DataFrame()

    # Isolation Forest on national daily data
    daily_nat = panel_df.groupby("date")[["total_enrolments","demo_total","bio_total"]].sum().reset_index()
    daily_nat["update_total"]  = daily_nat["demo_total"] + daily_nat["bio_total"]
    daily_nat["velocity"]      = daily_nat["update_total"] / (daily_nat["total_enrolments"] + 1)
    daily_nat["rolling_enrol"] = daily_nat["total_enrolments"].rolling(7, min_periods=1).mean()

    iso = IsolationForest(contamination=iso_contamination, random_state=42)
    feats_iso = daily_nat[["total_enrolments","update_total","velocity","rolling_enrol"]].fillna(0)
    daily_nat["iso_flag"] = iso.fit_predict(feats_iso) == -1
    daily_nat["anomaly_score"] = -iso.score_samples(feats_iso)  # higher = more anomalous

    m_a, m_b, m_c = st.columns(3)
    m_a.metric("Z-Score Anomaly Events", len(anom_full) if not anom_full.empty else 0)
    m_b.metric("Isolation Forest Flags", int(daily_nat["iso_flag"].sum()))
    m_c.metric("Flagged Days %", f"{daily_nat['iso_flag'].mean()*100:.1f}%")

    st.markdown("---")

    # Scatter: enrolments vs velocity (like their scatter plot)
    st.subheader("🔵 Enrolments vs Update Velocity — Isolation Forest Classification")
    scatter_normal = daily_nat[~daily_nat["iso_flag"]]
    scatter_anom   = daily_nat[daily_nat["iso_flag"]]

    fig_scatter = go.Figure()
    fig_scatter.add_trace(go.Scatter(
        x=scatter_normal["total_enrolments"], y=scatter_normal["velocity"],
        mode="markers", name="Normal",
        marker=dict(color="#1f77b4", size=8, opacity=0.7),
        text=scatter_normal["date"].astype(str), hovertemplate="Date: %{text}<br>Enrolments: %{x:,}<br>Velocity: %{y:.1f}x"
    ))
    fig_scatter.add_trace(go.Scatter(
        x=scatter_anom["total_enrolments"], y=scatter_anom["velocity"],
        mode="markers", name="⚠️ Suspicious",
        marker=dict(color="red", size=12, symbol="x", line=dict(width=2)),
        text=scatter_anom["date"].astype(str), hovertemplate="Date: %{text}<br>Enrolments: %{x:,}<br>Velocity: %{y:.1f}x"
    ))
    fig_scatter.update_layout(
        template="plotly_dark", height=420, hovermode="closest",
        title="Enrolments vs Update Velocity — Suspicious = Impossible Processing Speed / Fraud Signal",
        xaxis_title="Total Enrolments", yaxis_title="Update Velocity (ratio)"
    )
    st.plotly_chart(fig_scatter, width='stretch')

    # Time-series anomaly overlay
    fig_iso = go.Figure()
    fig_iso.add_trace(go.Scatter(x=scatter_normal["date"], y=scatter_normal["total_enrolments"],
        mode="lines", name="Normal", line=dict(color="#1f77b4", width=1.5)))
    fig_iso.add_trace(go.Scatter(x=scatter_anom["date"], y=scatter_anom["total_enrolments"],
        mode="markers", name="⚠️ Suspicious",
        marker=dict(color="red", size=12, symbol="x", line=dict(width=2))))
    fig_iso.update_layout(template="plotly_dark", height=380, hovermode="x unified",
        title="Isolation Forest — Suspicious Days (Potential Fraud / Data Quality Issue)")
    st.plotly_chart(fig_iso, width='stretch')

    # Anomaly data table
    st.subheader("📋 Detected Anomaly Log")
    if not daily_nat[daily_nat["iso_flag"]].empty:
        anom_table = daily_nat[daily_nat["iso_flag"]][
            ["date","total_enrolments","update_total","velocity","anomaly_score"]
        ].copy()
        anom_table = anom_table.rename(columns={
            "date": "Date", "total_enrolments": "Enrolments",
            "update_total": "Update Load", "velocity": "Velocity",
            "anomaly_score": "Anomaly Score"
        })
        anom_table["Velocity"] = anom_table["Velocity"].round(1)
        anom_table["Anomaly Score"] = anom_table["Anomaly Score"].round(4)
        st.dataframe(anom_table.sort_values("Anomaly Score", ascending=False).reset_index(drop=True),
                     width='stretch')
        st.download_button("📥 Download Anomaly Log",
            anom_table.to_csv(index=False).encode(), "anomaly_log.csv", "text/csv")

        if st.button("⚡ Generate Fraud Prevention Alert"):
            worst = daily_nat[daily_nat["iso_flag"]].sort_values("anomaly_score", ascending=False).iloc[0]
            alert = {
                "event":       "AADHAAR_FRAUD_RISK_DETECTED",
                "date":        worst["date"].strftime("%Y-%m-%d"),
                "enrolments":  int(worst["total_enrolments"]),
                "update_load": int(worst["update_total"]),
                "velocity":    round(float(worst["velocity"]), 1),
                "anomaly_score": round(float(worst["anomaly_score"]), 4),
                "risk_level":  "HIGH" if worst["velocity"] > 100 else "MEDIUM",
                "recommended_action": "Audit state-level data submissions for this date",
            }
            st.code(json.dumps(alert, indent=2), language="json")
            st.error("🚨 Fraud Prevention Alert Generated — Review flagged submissions")

    # Z-score spikes
    if not anom_full.empty:
        st.markdown("---")
        st.subheader("📈 Z-Score Spike Map — Campaign Anomalies by State")
        st.download_button("📥 Download Z-Score Log",
            anom_full[["date","norm_state","total_enrolments","z_score"]].to_csv(index=False).encode(),
            "zscore_anomaly_log.csv", "text/csv")
        _anom_plot = anom_full.copy()
        _anom_plot["z_abs"] = np.abs(_anom_plot["z_score"]).clip(lower=0.1)  # px.scatter needs size > 0
        fig_an = px.scatter(_anom_plot, x="date", y="total_enrolments", color="norm_state",
            size="z_abs", size_max=20, template="plotly_dark",
            title="Campaign Spikes Detected Across States (Z-Score Method)")
        fig_an.update_layout(height=430)
        st.plotly_chart(fig_an, width='stretch')

# ─────────────────────────────────────────────────────────────────────────────
# TAB 7: Intelligence Engine
# ─────────────────────────────────────────────────────────────────────────────
with tab7:
    st.subheader("🧠 The Intelligence Engine")
    st.markdown("**Architecture:** Raw CSV Data → Data Cleaning & Aggregation → **The Intelligence Engine** → 3 Action Modules")

    fig_arch = go.Figure()
    boxes = [
        (0.05, 0.5, "Raw CSV<br>Data",               "#455A64"),
        (0.22, 0.5, "Data Cleaning<br>& Aggregation","#1565C0"),
        (0.42, 0.5, "The Intelligence<br>Engine",     "#6A1B9A"),
        (0.65, 0.75, "Module 1<br>Operations",        "#1565C0"),
        (0.65, 0.50, "Module 2<br>Migration",         "#2E7D32"),
        (0.65, 0.25, "Module 3<br>Anomalies",         "#B71C1C"),
        (0.88, 0.75, "Resource<br>Optimization",      "#0D47A1"),
        (0.88, 0.50, "Policy<br>Alerts",              "#1B5E20"),
        (0.88, 0.25, "Fraud<br>Prevention",           "#7F0000"),
    ]
    for (x, y, txt, col) in boxes:
        fig_arch.add_shape(type="rect", x0=x-0.07, x1=x+0.07, y0=y-0.1, y1=y+0.1,
                           fillcolor=col, line=dict(color="white", width=1), xref="paper", yref="paper")
        fig_arch.add_annotation(x=x, y=y, text=txt, showarrow=False, font=dict(color="white", size=11),
                                xref="paper", yref="paper", align="center")
    arrows = [(0.12, 0.5, 0.15, 0.5), (0.29, 0.5, 0.35, 0.5),
              (0.49, 0.5, 0.57, 0.75), (0.49, 0.5, 0.57, 0.5), (0.49, 0.5, 0.57, 0.25),
              (0.72, 0.75, 0.80, 0.75), (0.72, 0.5, 0.80, 0.5), (0.72, 0.25, 0.80, 0.25)]
    for (x0, y0, x1, y1) in arrows:
        fig_arch.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1,
                           xref="paper", yref="paper",
                           line=dict(color="white", width=1.5))
    fig_arch.update_layout(height=300, paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
                           xaxis=dict(visible=False), yaxis=dict(visible=False), margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig_arch, width='stretch')
    st.markdown("---")

    # Module 1: Operations
    st.markdown('<div class="module-card mod-ops"><b>🔵 Module 1: Operations → Resource Optimization</b></div>',
                unsafe_allow_html=True)
    st.markdown("**Model A** predicts `total_system_load` → plan operator staffing, server capacity, energy.")
    if mdls["model_A"]:
        meta_A = mdls["meta"]
        st.info(f"Model A Ensemble · Test R² = {_r2_A}  ·  Target: total_system_load")
        last_date = inference_df["date"].max() if not inference_df.empty else feature_df["date"].max()
        last_feat  = inference_df[inference_df["date"] == last_date].copy()
        if not last_feat.empty:
            preds_load = []
            for _, row in last_feat.iterrows():
                try:
                    p = _ensemble_predict(mdls["model_A"], pd.DataFrame([row]))
                    preds_load.append({"norm_state": row["norm_state"], "predicted_load": p})
                except Exception:
                    pass
            if preds_load:
                load_df = pd.DataFrame(preds_load).sort_values("predicted_load", ascending=False)
                if load_df["predicted_load"].sum() == 0:
                    st.warning("⚠️ Model A predictions all zero — model was trained in a separate notebook "
                               "with different feature engineering (141 features). Retrain with `train_models.py` "
                               "to fix predictions.")
                # Highlight alert states
                load_df["alert"] = load_df["norm_state"].isin(_alert_states)
                fig_load = px.bar(load_df.head(15), x="predicted_load", y="norm_state",
                    orientation="h", template="plotly_dark",
                    title=f"Predicted System Load by State ({last_date.date()})  ⚠️ = 90th pct",
                    color="predicted_load", color_continuous_scale="Blues",
                    labels={"predicted_load": "System Load", "norm_state": "State"})
                fig_load.update_layout(yaxis={"categoryorder":"total ascending"}, height=420)
                st.plotly_chart(fig_load, width='stretch')
                with st.expander("📋 Full Ops Load Table"):
                    st.dataframe(load_df.drop(columns=["alert"]), width='stretch')
    else:
        st.warning("Model A not loaded — run NB02.")

    st.markdown("---")

    # Module 2: Migration
    st.markdown('<div class="module-card mod-mig"><b>🟢 Module 2: Migration → Policy Alerts</b></div>',
                unsafe_allow_html=True)
    st.markdown("**Model B** predicts `total_enrolments` for **Growth** states → mobile camps, awareness drives, allocation.")
    if mdls["model_B"]:
        meta_B = mdls["meta"]
        st.info(f"Model B Ensemble · Test R² = {_r2_B}  ·  Target: total_enrolments (Growth states)")
        last_date  = inference_df["date"].max() if not inference_df.empty else feature_df["date"].max()
        last_feat  = inference_df[inference_df["date"] == last_date].copy()
        growth_feat = last_feat[last_feat["norm_state"].isin(growth_states)]
        if not growth_feat.empty:
            preds_enrol = []
            for _, row in growth_feat.iterrows():
                try:
                    p = _ensemble_predict(mdls["model_B"], pd.DataFrame([row]), state=row["norm_state"])
                    preds_enrol.append({"norm_state": row["norm_state"], "predicted_enrolments": p})
                except Exception:
                    pass
            if preds_enrol:
                enrol_df = pd.DataFrame(preds_enrol).sort_values("predicted_enrolments", ascending=False)
                fig_enrol = px.bar(enrol_df, x="predicted_enrolments", y="norm_state",
                    orientation="h", template="plotly_dark",
                    title=f"Policy Alert: Predicted Enrolments — Growth States ({last_date.date()})",
                    color="predicted_enrolments", color_continuous_scale="Greens",
                    labels={"predicted_enrolments": "Predicted Enrolments", "norm_state": "State"})
                fig_enrol.update_layout(yaxis={"categoryorder":"total ascending"}, height=350)
                st.plotly_chart(fig_enrol, width='stretch')
        lc_show = _lc_df[["norm_state","ratio","stage"]].rename(
            columns={"norm_state":"State","ratio":"Update/Enrol Ratio","stage":"Lifecycle Stage"})
        lc_show["Update/Enrol Ratio"] = lc_show["Update/Enrol Ratio"].round(1)
        st.dataframe(lc_show.sort_values("Update/Enrol Ratio", ascending=False), width='stretch')
    else:
        st.warning("Model B not loaded — run NB02.")

    st.markdown("---")

    # Module 3: Anomalies
    st.markdown('<div class="module-card mod-anom"><b>🔴 Module 3: Anomalies → Fraud Prevention</b></div>',
                unsafe_allow_html=True)
    st.markdown("**Isolation Forest** (5% contamination) on national daily data → flags suspicious spikes.")
    daily_nat2 = panel_df.groupby("date")[["total_enrolments","demo_total","bio_total"]].sum().reset_index()
    daily_nat2["update_total"] = daily_nat2["demo_total"] + daily_nat2["bio_total"]
    daily_nat2["velocity"]     = daily_nat2["update_total"] / (daily_nat2["total_enrolments"] + 1)
    daily_nat2["rolling_enrol"]= daily_nat2["total_enrolments"].rolling(7, min_periods=1).mean()
    iso2 = IsolationForest(contamination=0.05, random_state=42)
    feats2 = daily_nat2[["total_enrolments","update_total","velocity","rolling_enrol"]].fillna(0)
    daily_nat2["anomaly"] = iso2.fit_predict(feats2) == -1
    n_anom2 = daily_nat2["anomaly"].sum()
    st.metric("Flagged Suspicious Days (Isolation Forest, 5%)", int(n_anom2))
    fig_iso2 = go.Figure()
    nd2 = daily_nat2[~daily_nat2["anomaly"]]
    fd2 = daily_nat2[daily_nat2["anomaly"]]
    fig_iso2.add_trace(go.Scatter(x=nd2["date"], y=nd2["total_enrolments"],
        mode="lines", name="Normal", line=dict(color="#1f77b4", width=1.5)))
    fig_iso2.add_trace(go.Scatter(x=fd2["date"], y=fd2["total_enrolments"],
        mode="markers", name="⚠️ Suspicious",
        marker=dict(color="red", size=12, symbol="x", line=dict(width=2))))
    fig_iso2.update_layout(template="plotly_dark", height=380, hovermode="x unified",
        title="Isolation Forest — Suspicious Days (Potential Fraud)")
    st.plotly_chart(fig_iso2, width='stretch')

    if n_anom2 > 0:
        susp2 = daily_nat2[daily_nat2["anomaly"]][["date","total_enrolments","update_total","velocity"]]
        st.dataframe(susp2.sort_values("date").reset_index(drop=True), width='stretch')

    st.markdown("---")
    meta = mdls.get("meta", {})
    st.markdown(f"""
**Model Summary:**
| Model | Target | R² | Use Case |
|-------|--------|----|----------|
| Ensemble A | `total_system_load` | **{_r2_A}** | Module 1 — Ops/Infra |
| Ensemble B | `total_enrolments`  | **{_r2_B}** | Module 2 — Migration |
| Isolation Forest | anomaly flag | 95% coverage | Module 3 — Fraud |

**Routing:** `lifecycle_stage` (system_velocity > 5 = Maintenance → Model A, else Growth → Model B)
    """)
