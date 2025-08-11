import pandas as pd

# Load combined data
df = pd.read_csv('output_FAME.csv')

# Normalize column names
df.columns = df.columns.str.strip().str.lower()

# Define demographic columns expected to always be present
demographic_vars = ['age', 'postcode', 'randomisation_date', 'baseline_eq5d']

# Define timestamp schedule offsets (days from randomisation) by short visit name
timestamp_schedule = {
    '8_week': 8 * 7,
    '4_month': 4 * 30,
    '12_month': 12 * 30
}

# Construct expected column names for completion timestamps and eq5d scores based on short names
completion_ts_cols = {f"{visit}_completion_date": offset for visit, offset in timestamp_schedule.items()}
eq5d_score_cols = {f"{visit}_eq5d": offset for visit, offset in timestamp_schedule.items()}

# Replace common placeholders with NA for missing data detection
df.replace(to_replace=["unknown", "Unknown", "n/a", "N/A", "NA", "None", "null", ""], value=pd.NA, inplace=True)

# Convert relevant date columns to datetime
for col in ['randomisation_date', 'deathdate', 'withdrawal_date']:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# Determine earliest of death or withdrawal date
df['death_or_withdrawal_date'] = df[['deathdate', 'withdrawal_date']].min(axis=1)

# Open output file for missing data queries
with open('missing_data_queries.txt', 'w') as query_file:
    for index, row in df.iterrows():
        record_id = row['record_id']
        missing_cols = []

        # Check demographic columns
        for col in demographic_vars:
            if col not in df.columns:
                continue  # If column missing in dataframe, skip
            if pd.isna(row.get(col, pd.NA)):
                missing_cols.append(col)

        rand_date = row.get('randomisation_date', pd.NaT)
        dod = row.get('death_or_withdrawal_date', pd.NaT)

        if pd.notna(rand_date):
            # Check completion timestamp columns
            for ts_col, offset_days in completion_ts_cols.items():
                expected_date = rand_date + pd.Timedelta(days=offset_days)
                # If data missing and expected_date before death/withdrawal (or no death/withdrawal)
                if ts_col in df.columns:
                    if pd.isna(row.get(ts_col)) and (pd.isna(dod) or expected_date <= dod):
                        missing_cols.append(ts_col)

            # Check EQ5D score columns
            for score_col, offset_days in eq5d_score_cols.items():
                expected_date = rand_date + pd.Timedelta(days=offset_days)
                if score_col in df.columns:
                    if pd.isna(row.get(score_col)) and (pd.isna(dod) or expected_date <= dod):
                        missing_cols.append(score_col)

        # Write query for missing data if any columns missing
        if missing_cols:
            query = f"-- Missing data for record_id {record_id} in columns: {', '.join(missing_cols)}\n"
            query_file.write(query)

print("Missing data queries written to 'missing_data_queries.txt'.")

