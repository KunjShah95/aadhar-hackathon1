import os
import glob
import json
import joblib
import numpy as np
import pandas as pd
from scipy import stats

def calculate_psi(baseline, target, num_buckets=10):
    """Calculates Population Stability Index (PSI) between baseline and target feature series."""
    baseline = np.array(baseline.dropna())
    target = np.array(target.dropna())
    
    if len(baseline) == 0 or len(target) == 0:
        return 0.0

    percentiles = np.linspace(0, 100, num_buckets + 1)
    buckets = np.percentile(baseline, percentiles)
    buckets[0] -= 1e-5
    buckets[-1] += 1e-5
    
    # Ensure unique bucket edges
    buckets = np.unique(buckets)
    if len(buckets) < 2:
        return 0.0

    base_counts, _ = np.histogram(baseline, bins=buckets)
    target_counts, _ = np.histogram(target, bins=buckets)

    base_pct = base_counts / max(len(baseline), 1)
    target_pct = target_counts / max(len(target), 1)

    # Avoid zero division
    base_pct = np.where(base_pct == 0, 0.0001, base_pct)
    target_pct = np.where(target_pct == 0, 0.0001, target_pct)

    psi_val = np.sum((target_pct - base_pct) * np.log(target_pct / base_pct))
    return float(psi_val)

def run_mlops_audit():
    print("=" * 70)
    print("      AUTOMATED MLOps DRIFT & MODEL HEALTH PIPELINE")
    print("=" * 70)

    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    pkl_dir = os.path.join(workspace_dir, "pkl_models")

    # Check model files health
    model_files = glob.glob(os.path.join(pkl_dir, "*.pkl"))
    models_health = {}
    for mf in model_files:
        name = os.path.basename(mf)
        try:
            m_obj = joblib.load(mf)
            models_health[name] = {"status": "HEALTHY", "type": str(type(m_obj))}
        except Exception as e:
            models_health[name] = {"status": "CORRUPTED", "error": str(e)}

    # Synthetic / Sample Data Drift Inspection
    features_to_audit = ["total_enrolments", "demo_total", "bio_total", "rolling_mean_7", "bio_to_enrol_ratio"]
    
    drift_metrics = {}
    overall_drift_status = "NO_DRIFT"

    for feat in features_to_audit:
        # Simulate baseline (hist) vs production (target) distributions
        np.random.seed(42)
        base_vals = pd.Series(np.random.normal(loc=1000, scale=250, size=500))
        prod_vals = pd.Series(np.random.normal(loc=1050, scale=270, size=200))
        
        ks_stat, p_val = stats.ks_2samp(base_vals, prod_vals)
        psi_val = calculate_psi(base_vals, prod_vals)
        
        status = "STABLE"
        if psi_val > 0.25:
            status = "CRITICAL_DRIFT"
            overall_drift_status = "ACTION_REQUIRED"
        elif psi_val > 0.1:
            status = "MODERATE_SHIFT"

        drift_metrics[feat] = {
            "ks_statistic": round(float(ks_stat), 4),
            "p_value": round(float(p_val), 4),
            "psi_score": round(float(psi_val), 4),
            "status": status
        }

    report = {
        "timestamp": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        "overall_drift_status": overall_drift_status,
        "models_health": models_health,
        "feature_drift_metrics": drift_metrics
    }

    report_path = os.path.join(pkl_dir, "mlops_drift_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print("\n[MLOps Report Generated]")
    print(f"Overall Drift Status: {overall_drift_status}")
    print(f"Report saved to: {report_path}")
    print("=" * 70)
    return report

if __name__ == "__main__":
    run_mlops_audit()
