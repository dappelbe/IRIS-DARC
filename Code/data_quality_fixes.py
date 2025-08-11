import pandas as pd

# Load combined data
df = pd.read_csv('output_FAME.csv')

# Normalize column names
df.columns = df.columns.str.strip().str.lower()

# Verify 'record_id' exists
if 'record_id' not in df.columns:
    raise KeyError("The 'record_id' column is missing from the dataset.")

# Demographic columns expected
demographic_vars = ['age', 'sex', 'postcode', 'randomisation_date', 'baseline_eq5d']
demographic_vars = [col.lower() for col in demographic_vars]

# Timestamp offsets in days
timestamp_schedule = {
    '8_week': 8 * 7,
    '4_month': 4 * 30,
    '12_month': 12 * 30
}

completion_ts_cols = {f"{visit}_completion_date": offset for visit, offset in timestamp_schedule.items()}
eq5d_score_cols = {f"{visit}_eq5d": offset for visit, offset in timestamp_schedule.items()}

# Replace placeholders with NA
df.replace(to_replace=["unknown", "Unknown", "n/a", "N/A", "NA", "None", "null", ""], value=pd.NA, inplace=True)

# Convert date columns to datetime
for col in ['randomisation_date', 'deathdate', 'withdrawal_date']:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# Safely determine earliest death or withdrawal date
date_cols = [col for col in ['deathdate', 'withdrawal_date'] if col in df.columns]
if date_cols:
    df['death_or_withdrawal_date'] = df[date_cols].min(axis=1)
else:
    df['death_or_withdrawal_date'] = pd.NaT

with open('missing_data_queries.txt', 'w') as query_file:
    query_file.write("-- Missing data queries generated\n\n")
    for index, row in df.iterrows():
        record_id = row['record_id']
        missing_cols = []

        # Check demographic vars
        for col in demographic_vars:
            if col not in df.columns:
                continue
            if pd.isna(row.get(col, pd.NA)):
                missing_cols.append(col)

        rand_date = row.get('randomisation_date', pd.NaT)
        dod = row.get('death_or_withdrawal_date', pd.NaT)

        if pd.notna(rand_date):
            for ts_col, offset_days in completion_ts_cols.items():
                expected_date = rand_date + pd.Timedelta(days=offset_days)
                if ts_col in df.columns:
                    if pd.isna(row.get(ts_col)) and (pd.isna(dod) or expected_date <= dod):
                        missing_cols.append(ts_col)

            for score_col, offset_days in eq5d_score_cols.items():
                expected_date = rand_date + pd.Timedelta(days=offset_days)
                if score_col in df.columns:
                    if pd.isna(row.get(score_col)) and (pd.isna(dod) or expected_date <= dod):
                        missing_cols.append(score_col)

        if missing_cols:
            query = f"-- Missing data for record_id {record_id} in columns: {', '.join(missing_cols)}\n"
            query_file.write(query)

print("Missing data queries written to 'missing_data_queries.txt'.")


