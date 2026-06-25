import os
import json
import pandas as pd
import numpy as np
from scipy import stats

# Define paths
script_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(script_dir, "..", "Case Analista de Dados — the news [Dataset Palavritas].xlsx")
data_dir = os.path.join(script_dir, "public", "data")

# Create output directories
os.makedirs(data_dir, exist_ok=True)

print("Starting Data Pipeline...")

# 1. Load datasets
df_sessions_raw = pd.read_excel(excel_path, sheet_name='palavritas_sessions')
df_attempts_raw = pd.read_excel(excel_path, sheet_name='palavritas_attempts')
df_profile_raw = pd.read_excel(excel_path, sheet_name='user_profile')

raw_shapes = {
    "sessions": df_sessions_raw.shape,
    "attempts": df_attempts_raw.shape,
    "profile": df_profile_raw.shape
}
print(f"Raw shapes: Sessions={raw_shapes['sessions']}, Attempts={raw_shapes['attempts']}, Profile={raw_shapes['profile']}")

# 2. Data Cleaning & Diagnosis
# ============================
# Track cleaning stats
cleaning_log = {}

# A. Sessions Cleaning
# Standardize device casing
def clean_device(device_str):
    if pd.isna(device_str):
        return "Unknown"
    device_lower = str(device_str).lower()
    if 'ios' in device_lower:
        return 'iOS'
    elif 'android' in device_lower:
        return 'Android'
    return device_str

df_sessions = df_sessions_raw.copy()
df_sessions['device_clean'] = df_sessions['device'].apply(clean_device)
device_inconsistencies = (df_sessions['device'] != df_sessions['device_clean']).sum()

# Clean attempts (keep 1-6)
invalid_attempts_mask = ~df_sessions['attempts'].isin([1, 2, 3, 4, 5, 6])
invalid_attempts_count = invalid_attempts_mask.sum()

# Drop rows where result is missing
missing_result_count = df_sessions['result'].isnull().sum()

# Apply sessions cleaning filters
df_sessions_cleaned = df_sessions[~invalid_attempts_mask & df_sessions['result'].notnull()].copy()
df_sessions_cleaned['device'] = df_sessions_cleaned['device_clean']
df_sessions_cleaned.drop(columns=['device_clean'], inplace=True)

# B. Profile Cleaning
df_profile = df_profile_raw.copy()
# Standardize orders_food_delivery
def clean_delivery(val):
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip().lower()
    if val_str in ['true', 'sim', '1', '1.0']:
        return True
    elif val_str in ['false', 'não', 'nao', '0', '0.0']:
        return False
    return np.nan

df_profile['orders_food_delivery_clean'] = df_profile['orders_food_delivery'].apply(clean_delivery)
delivery_inconsistencies = (df_profile['orders_food_delivery'] != df_profile['orders_food_delivery_clean']).sum()
df_profile['orders_food_delivery'] = df_profile['orders_food_delivery_clean']
df_profile.drop(columns=['orders_food_delivery_clean'], inplace=True)

# C. Attempts Cleaning
df_attempts = df_attempts_raw.copy()
# Keep attempts 1-6
invalid_attempt_num_mask = ~df_attempts['attempt_number'].isin([1, 2, 3, 4, 5, 6])
invalid_attempt_num_count = invalid_attempt_num_mask.sum()
df_attempts_cleaned = df_attempts[~invalid_attempt_num_mask].copy()

# Keep only attempts for valid sessions
before_session_filter_count = len(df_attempts_cleaned)
valid_session_ids = set(df_sessions_cleaned['session_id'])
df_attempts_cleaned = df_attempts_cleaned[df_attempts_cleaned['session_id'].isin(valid_session_ids)]
orphaned_attempts_count = before_session_filter_count - len(df_attempts_cleaned)

# Document Cleaning Results
cleaning_summary = {
    "raw_records": {
        "sessions": len(df_sessions_raw),
        "attempts": len(df_attempts_raw),
        "profiles": len(df_profile_raw)
    },
    "cleaned_records": {
        "sessions": len(df_sessions_cleaned),
        "attempts": len(df_attempts_cleaned),
        "profiles": len(df_profile)
    },
    "anomalies_removed": {
        "invalid_sessions_attempts_count": int(invalid_attempts_count),
        "missing_results_sessions_count": int(missing_result_count),
        "invalid_attempts_detail_count": int(invalid_attempt_num_count),
        "orphaned_attempts_detail_count": int(orphaned_attempts_count)
    },
    "standardizations": {
        "device_casing_fixes": int(device_inconsistencies),
        "delivery_boolean_fixes": int(delivery_inconsistencies)
    }
}

with open(os.path.join(data_dir, "cleaning.json"), "w", encoding="utf-8") as f:
    json.dump(cleaning_summary, f, ensure_ascii=False, indent=2)

print("Data Cleaning completed. Summary exported.")

# 3. Overall Product Metrics
# ============================
total_sessions = len(df_sessions_cleaned)
total_users = df_sessions_cleaned['user_id'].nunique()
win_rate = float((df_sessions_cleaned['result'] == 'win').mean() * 100)
avg_attempts = float(df_sessions_cleaned['attempts'].mean())
avg_time = float(df_sessions_cleaned['time_to_complete_sec'].mean())
played_next_day_rate = float(df_sessions_cleaned['played_next_day'].mean() * 100)
active_d30_rate = float(df_sessions_cleaned['active_d30'].mean() * 100)

overall_metrics = {
    "total_sessions": total_sessions,
    "total_users": total_users,
    "win_rate_pct": round(win_rate, 2),
    "avg_attempts": round(avg_attempts, 2),
    "avg_time_sec": round(avg_time, 2),
    "d1_retention_pct": round(played_next_day_rate, 2),
    "d30_active_pct": round(active_d30_rate, 2)
}

with open(os.path.join(data_dir, "overall.json"), "w", encoding="utf-8") as f:
    json.dump(overall_metrics, f, ensure_ascii=False, indent=2)

# 4. Correlation & Hypothesis Testing: Newsletter
# ===============================================
# A. Session level: newsletter_open_before_game
newsletter_group = df_sessions_cleaned.groupby('newsletter_open_before_game').agg(
    sessions=('session_id', 'count'),
    win_rate=('result', lambda x: (x == 'win').mean() * 100),
    avg_attempts=('attempts', 'mean'),
    avg_time=('time_to_complete_sec', 'mean'),
    played_next_day=('played_next_day', lambda x: x.mean() * 100),
    active_d30=('active_d30', lambda x: x.mean() * 100)
).reset_index()

# Chi-square tests
# played_next_day vs newsletter_open_before_game
contingency_d1 = pd.crosstab(df_sessions_cleaned['newsletter_open_before_game'], df_sessions_cleaned['played_next_day'])
chi2_d1, p_val_d1, _, _ = stats.chi2_contingency(contingency_d1)

# active_d30 vs newsletter_open_before_game
contingency_d30 = pd.crosstab(df_sessions_cleaned['newsletter_open_before_game'], df_sessions_cleaned['active_d30'])
chi2_d30, p_val_d30, _, _ = stats.chi2_contingency(contingency_d30)

newsletter_data = {
    "by_open_before_game": newsletter_group.to_dict(orient='records'),
    "stats": {
        "d1_retention": {
            "chi2": float(chi2_d1),
            "p_value": float(p_val_d1),
            "significant": bool(p_val_d1 < 0.05)
        },
        "d30_active": {
            "chi2": float(chi2_d30),
            "p_value": float(p_val_d30),
            "significant": bool(p_val_d30 < 0.05)
        }
    }
}

# B. Join with user profile for subscriber-level analysis
df_user_sessions = pd.merge(df_sessions_cleaned, df_profile, on='user_id', how='left')

# Analyze newsletter_subscriber
sub_group = df_user_sessions.groupby('newsletter_subscriber').agg(
    sessions=('session_id', 'count'),
    win_rate=('result', lambda x: (x == 'win').mean() * 100),
    avg_attempts=('attempts', 'mean'),
    played_next_day=('played_next_day', lambda x: x.mean() * 100),
    active_d30=('active_d30', lambda x: x.mean() * 100)
).reset_index()

contingency_sub_d30 = pd.crosstab(df_user_sessions['newsletter_subscriber'].fillna(False), df_user_sessions['active_d30'])
chi2_sub_d30, p_val_sub_d30, _, _ = stats.chi2_contingency(contingency_sub_d30)

newsletter_data["by_subscriber"] = sub_group.to_dict(orient='records')
newsletter_data["stats"]["subscriber_d30"] = {
    "chi2": float(chi2_sub_d30),
    "p_value": float(p_val_sub_d30),
    "significant": bool(p_val_sub_d30 < 0.05)
}

with open(os.path.join(data_dir, "newsletter.json"), "w", encoding="utf-8") as f:
    json.dump(newsletter_data, f, ensure_ascii=False, indent=2)

# 5. Device analysis
# ============================
device_group = df_sessions_cleaned.groupby('device').agg(
    sessions=('session_id', 'count'),
    win_rate=('result', lambda x: (x == 'win').mean() * 100),
    avg_attempts=('attempts', 'mean'),
    played_next_day=('played_next_day', lambda x: x.mean() * 100),
    active_d30=('active_d30', lambda x: x.mean() * 100)
).reset_index().to_dict(orient='records')

with open(os.path.join(data_dir, "device.json"), "w", encoding="utf-8") as f:
    json.dump(device_group, f, ensure_ascii=False, indent=2)

# 6. Hourly metrics & typical playtime comparison
# ===============================================
hourly_group = df_sessions_cleaned.groupby('session_hour').agg(
    sessions=('session_id', 'count'),
    played_next_day=('played_next_day', lambda x: x.mean() * 100),
    active_d30=('active_d30', lambda x: x.mean() * 100)
).reset_index()

# Hourly play patterns by subscriber type
hourly_sub_group = df_user_sessions.groupby(['session_hour', 'newsletter_subscriber']).size().unstack(fill_value=0).reset_index()
hourly_sub_group_dict = hourly_sub_group.to_dict(orient='records')

# Comparison of actual hour vs typical playtime
# Map actual hour to period:
# 5 - 11: morning, 12 - 17: afternoon, 18 - 23: evening, 0 - 4: night
def hour_to_period(h):
    if 5 <= h < 12:
        return 'morning'
    elif 12 <= h < 18:
        return 'afternoon'
    elif 18 <= h <= 23:
        return 'evening'
    else:
        return 'night'

df_user_sessions['actual_period'] = df_user_sessions['session_hour'].apply(hour_to_period)
period_alignment = df_user_sessions.groupby(['typical_play_time', 'actual_period']).size().unstack(fill_value=0).reset_index().to_dict(orient='records')

hourly_data = {
    "by_hour": hourly_group.to_dict(orient='records'),
    "by_hour_sub": hourly_sub_group_dict,
    "alignment": period_alignment
}

with open(os.path.join(data_dir, "hourly.json"), "w", encoding="utf-8") as f:
    json.dump(hourly_data, f, ensure_ascii=False, indent=2)

# 7. Word Difficulty Analysis
# ============================
word_group = df_sessions_cleaned.groupby('word').agg(
    sessions=('session_id', 'count'),
    win_rate=('result', lambda x: (x == 'win').mean() * 100),
    avg_attempts=('attempts', 'mean'),
    avg_time=('time_to_complete_sec', 'mean'),
    played_next_day=('played_next_day', lambda x: x.mean() * 100),
    active_d30=('active_d30', lambda x: x.mean() * 100)
).reset_index()

# Rank words by win_rate (ascending = hardest first)
word_group_sorted = word_group.sort_values(by='win_rate').to_dict(orient='records')

with open(os.path.join(data_dir, "words.json"), "w", encoding="utf-8") as f:
    json.dump(word_group_sorted, f, ensure_ascii=False, indent=2)

# 8. User Profile Demographics (Age, Salary, Job, Sector, State)
# ==============================================================
demographics_data = {}

for col in ['age_range', 'salary_range', 'sector', 'company_size', 'state']:
    # Fill NAs for grouping
    df_user_sessions[col] = df_user_sessions[col].fillna('Não Informado')
    
    group = df_user_sessions.groupby(col).agg(
        sessions=('session_id', 'count'),
        unique_users=('user_id', 'nunique'),
        win_rate=('result', lambda x: (x == 'win').mean() * 100),
        avg_attempts=('attempts', 'mean'),
        played_next_day=('played_next_day', lambda x: x.mean() * 100),
        active_d30=('active_d30', lambda x: x.mean() * 100)
    ).reset_index()
    
    # Chi-square for active_d30 vs this demograph col
    df_filtered = df_user_sessions[df_user_sessions[col] != 'Não Informado']
    if df_filtered[col].nunique() > 1:
        contingency = pd.crosstab(df_filtered[col], df_filtered['active_d30'])
        chi2, p_val, _, _ = stats.chi2_contingency(contingency)
        sig = bool(p_val < 0.05)
    else:
        chi2, p_val, sig = 0.0, 1.0, False
        
    demographics_data[col] = {
        "data": group.to_dict(orient='records'),
        "stats": {
            "chi2": float(chi2),
            "p_value": float(p_val),
            "significant": sig
        }
    }

# Top 10 Job Roles by Sessions
top_jobs = df_user_sessions.groupby('job_role').agg(
    sessions=('session_id', 'count'),
    played_next_day=('played_next_day', lambda x: x.mean() * 100),
    active_d30=('active_d30', lambda x: x.mean() * 100)
).reset_index().sort_values(by='sessions', ascending=False).head(10).to_dict(orient='records')
demographics_data["top_jobs"] = top_jobs

with open(os.path.join(data_dir, "demographics.json"), "w", encoding="utf-8") as f:
    json.dump(demographics_data, f, ensure_ascii=False, indent=2)

# 9. Food Delivery Habits
# ============================
delivery_data = {}

# A. Platform preference
platform_group = df_user_sessions.groupby('food_delivery_platform').agg(
    sessions=('session_id', 'count'),
    unique_users=('user_id', 'nunique'),
    played_next_day=('played_next_day', lambda x: x.mean() * 100),
    active_d30=('active_d30', lambda x: x.mean() * 100)
).reset_index().to_dict(orient='records')
delivery_data["platform"] = platform_group

# B. Frequency per week
freq_group = df_user_sessions.groupby('food_delivery_freq_week').agg(
    sessions=('session_id', 'count'),
    played_next_day=('played_next_day', lambda x: x.mean() * 100),
    active_d30=('active_d30', lambda x: x.mean() * 100)
).reset_index().to_dict(orient='records')
delivery_data["frequency"] = freq_group

# C. Orders food delivery boolean
orders_group = df_user_sessions.groupby('orders_food_delivery').agg(
    sessions=('session_id', 'count'),
    played_next_day=('played_next_day', lambda x: x.mean() * 100),
    active_d30=('active_d30', lambda x: x.mean() * 100)
).reset_index().to_dict(orient='records')
delivery_data["orders"] = orders_group

# Chi-square tests
contingency_orders = pd.crosstab(df_user_sessions['orders_food_delivery'].fillna(False), df_user_sessions['active_d30'])
chi2_ord, p_val_ord, _, _ = stats.chi2_contingency(contingency_orders)

delivery_data["stats"] = {
    "orders_d30": {
        "chi2": float(chi2_ord),
        "p_value": float(p_val_ord),
        "significant": bool(p_val_ord < 0.05)
    }
}

with open(os.path.join(data_dir, "food_delivery.json"), "w", encoding="utf-8") as f:
    json.dump(delivery_data, f, ensure_ascii=False, indent=2)

# 10. Streaks and Numerical Correlations
# =======================================
# Streak analysis
streak_group = df_sessions_cleaned.groupby('streak_day').agg(
    sessions=('session_id', 'count'),
    played_next_day=('played_next_day', lambda x: x.mean() * 100),
    active_d30=('active_d30', lambda x: x.mean() * 100)
).reset_index().to_dict(orient='records')

# T-tests for numerical features against played_next_day and active_d30
numerical_features = ['attempts', 'time_to_complete_sec', 'streak_day']
numeric_stats = {}

for feat in numerical_features:
    # played_next_day groups
    g_true_d1 = df_sessions_cleaned[df_sessions_cleaned['played_next_day'] == True][feat]
    g_false_d1 = df_sessions_cleaned[df_sessions_cleaned['played_next_day'] == False][feat]
    t_stat_d1, p_val_d1 = stats.ttest_ind(g_true_d1, g_false_d1, equal_var=False)
    
    # active_d30 groups
    g_true_d30 = df_sessions_cleaned[df_sessions_cleaned['active_d30'] == True][feat]
    g_false_d30 = df_sessions_cleaned[df_sessions_cleaned['active_d30'] == False][feat]
    t_stat_d30, p_val_d30 = stats.ttest_ind(g_true_d30, g_false_d30, equal_var=False)
    
    numeric_stats[feat] = {
        "mean_played_next_day_true": float(g_true_d1.mean()),
        "mean_played_next_day_false": float(g_false_d1.mean()),
        "d1_t_stat": float(t_stat_d1),
        "d1_p_value": float(p_val_d1),
        "d1_significant": bool(p_val_d1 < 0.05),
        
        "mean_active_d30_true": float(g_true_d30.mean()),
        "mean_active_d30_false": float(g_false_d30.mean()),
        "d30_t_stat": float(t_stat_d30),
        "d30_p_value": float(p_val_d30),
        "d30_significant": bool(p_val_d30 < 0.05)
    }

streaks_data = {
    "by_streak": streak_group,
    "stats": numeric_stats
}

with open(os.path.join(data_dir, "streaks.json"), "w", encoding="utf-8") as f:
    json.dump(streaks_data, f, ensure_ascii=False, indent=2)

print("Data analysis pipeline finished. All JSON files exported to:", data_dir)
