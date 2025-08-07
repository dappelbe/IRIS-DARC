import pandas as pd

# Step 1: Read the combined data file
df = pd.read_csv('output_FAME.csv')

# Define the columns you want to check for missing data
columns_to_check = ['age', 'postcode', 'randomisation_date', 'baseline_eq5d_score', 'eq5d_timestamp_8_week_follow_up_arm_1', 'eq5d_timestamp_4_month_follow_up_arm_1', 'eq5d_timestamp_12_month_follow_up_arm_1', 'eq5d_score_8_week_follow_up_arm_1', 'eq5d_score_4_month_follow_up_arm_1', 'eq5d_score_12_month_follow_up_arm_1']

# Open a file to write the SQL queries
with open('missing_data_queries.sql', 'w') as query_file:

    # Loop through each row
    for index, row in df.iterrows():
        record_id = row['record_id']
        
        # Check for missing data in the selected columns
        missing_columns = [col for col in columns_to_check if pd.isna(row[col])]
        
        # If there are missing columns, write an update query to flag or fix them
        if missing_columns:
            # For example, a query to set a flag in a hypothetical table
            # You may want to customize this according to your DB schema
            
            # Example: Update a flag column "data_missing" in your database table
            # Or update the missing columns with some default or NULL value
            
            # Here is a sample query to set a missing data flag for this record
            query = f"-- Missing data for record_id {record_id} in columns: {', '.join(missing_columns)}\n"
            query += f"UPDATE your_table SET data_missing = 1 WHERE record_id = '{record_id}';\n\n"
            
            # Write the query to the file
            query_file.write(query)

print("Queries for missing data have been written to 'missing_data_queries.sql'.")
