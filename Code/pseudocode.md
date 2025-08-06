# Configuration Files

As the project will ultimately run from multiple studies we should have generic code that can handle different data sets.
An example of what you might like is shown in JSON is shown below:

```json
[
  {
    "study_name": "FAME",
    "visits": [
      "8_week_follow_up_arm_1",
      "4_month_follow_up_arm_1",
      "12_month_follow_up_arm_1"
    ],
    "completion_data": {
      "file": "Studies/FAME/FAME-FormCompletion_DATA_2025-08-04_1414.csv",
      "record_id_col": "1",
      "po_timestamp_col": "27"
    },
    "demographics_data": {
      "file": "Studies/FAME/FAME-Demographics_DATA_2025-08-04_1416.csv",
      "record_id_col": "1",
      "age": {
        "visit": "screening_arm_1",
        "variable": "age"
      },
      "gender": {
        "visit": "screening_arm_1",
        "variable": "age"
      },
      "postcode": {
        "visit": "contact_details_arm_1",
        "variable": "postalcode"
      },
      "randomisationdate": {
        "visit": "randomisation_arm_1",
        "variable": "randodate"
      },
      "withdrawaldate": {
        "visit": "adhoc_arm_1",
        "variable": "wd_date"
      },
      "deathdate": {
        "visit": "adhoc_arm_1",
        "variable": "death_date"
      }
    },
    "eq5d_data": {
      "file": "Studies/FAME/FAME-StatsEQ5D5L_DATA_2025-08-06_1700.csv",
      "record_id_col": "1",
      "pre_injury_vas": {
        "visit": "baseline_arm_1",
        "variable": "vas"
      },
      "fu_vas": [
        {
          "visit": "8_week_follow_up_arm_1",
          "variable": "vas_fu"
        },
        {
          "visit": "4_month_follow_up_arm_1",
          "variable": "vas_fu"
        },
        {
          "visit": "12_month_follow_up_arm_1",
          "variable": "vas_fu"
        }
      ]
    }
  }
]
```

# Pseudocode

Step 1: Extract data
```jsunicoderegexp
Read in the configuration file 
Create Dataframe to hold output data
Loop through each study
  Read in demographics data
  Extract record_id and age, add record_id and age to output dataframe
  Extract record_id and gender, add gender to output dataframe
  Extract record_id and postcode, add postcode to output dataframe
  Extract record_id and randomisation date, add randomisation date to output dataframe
  Extract record_id and withdrawal date, add withdrawal date to output dataframe
  Extract record_id and death date, add death date to output dataframe
  
  Read in EQ5D 
  Extract record_id and baseline eq5d, add baseline eq5d vas to output dataframe
  Loop through follow up VAS
    Extract each vas at each time point and add to output dataframe
  
  Read in completion data
  Loop through visits
    Extract primary outcome completion timestamp and add to output dataframe
  
Save output data frame to a file. 
```
 
Step 2: Data quality/missing data
```jsunicoderegexp

Read in datafile created in step 1
loop through each data row
  identify any missing data
  Write queries to file
```
In this step we are ensuring that we have all the data we can, so we need to check that we have the maximum number of items for each record, only a few records will have withdrawal/death dates.

For FAME we should have 891 participants and 51 withdrawals.

Once we have added in the missing data (for example form completion timestamps rather than survey)

Step 3: Look for correlations
