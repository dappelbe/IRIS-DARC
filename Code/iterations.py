import pandas as pd

# Load the combined CSV
df = pd.read_csv('output_FAME.csv')

# Normalise column names
df.columns = df.columns.str.strip().str.lower()

# Identify completion date columns
completion_cols = [
    '8_week_completion_date',
    '4_month_completion_date',
    '12_month_completion_date'
]

# Convert to datetime (invalid values become NaT)
for col in completion_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# --------------------------------
# 1. Count completions
# --------------------------------
df['completion_count'] = df[completion_cols].notna().sum(axis=1)
count_summary = df['completion_count'].value_counts().sort_index()

# --------------------------------
# 2. Count patterns
# --------------------------------
def pattern_label(row):
    completed = [name.split('_')[0] for name, done in zip(completion_cols, row[completion_cols].notna()) if done]
    if not completed:
        return "None"
    return " & ".join(completed)

df['completion_pattern'] = df.apply(pattern_label, axis=1)
pattern_counts = df['completion_pattern'].value_counts()

# --------------------------------
# Export to TXT
# --------------------------------
output_file = "completion_summary.txt"
with open(output_file, "w") as f:
    f.write("Number of participants by completion count:\n")
    for count, num_people in count_summary.items():
        f.write(f"{count} completions: {num_people} participants\n")

    f.write("\nNumber of participants by specific completion patterns:\n")
    for pattern, num_people in pattern_counts.items():
        f.write(f"{pattern}: {num_people} participants\n")

print(f"Summary exported to {output_file}")

