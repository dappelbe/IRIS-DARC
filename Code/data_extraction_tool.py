import pandas as pd
import json

# Load configuration
with open(r'Code/configuration.json', 'r') as f:
    config_data = json.load(f)

# Looping through studies
for study in config_data:
    study_name = study["study_name"]
    demographics_info = study["demographics_data"]
    completion_info = study["completion_data"]
    eq5d_info = study["eq5d_data"]

    # -------------------------
    # Load Completion Data
    # -------------------------
    comp_file = completion_info["file"]
    comp_record_id_col_idx = int(completion_info["record_id_col"]) - 1
    comp_df = pd.read_csv(comp_file, low_memory=False)
    comp_record_id_col = comp_df.columns[comp_record_id_col_idx]

    event_col_candidates = [col for col in comp_df.columns if 'event' in col.lower()]
    if not event_col_candidates:
        raise ValueError("No event column found in completion data CSV.")
    comp_event_col = event_col_candidates[0]

    # Extract Completion Timestamps using short_name from config
    completion_ts_frames = []
    for visit_info in completion_info.get("follow_up_visits", []):
        visit = visit_info["visit"]
        short_visit = visit_info.get("short_name", visit)
        variable = visit_info["variable"]

        filtered_rows = comp_df[comp_df[comp_event_col] == visit]
        if variable not in filtered_rows.columns:
            print(f"Warning: variable '{variable}' not found in visit '{visit}'. Skipping.")
            continue

        ts_df = filtered_rows[[comp_record_id_col, variable]].copy()
        ts_df.columns = ["record_id", f"{short_visit}_completion_date"]
        completion_ts_frames.append(ts_df)

    if completion_ts_frames:
        all_ts_df = completion_ts_frames[0]
        for df in completion_ts_frames[1:]:
            all_ts_df = pd.merge(all_ts_df, df, on="record_id", how="outer")
    else:
        all_ts_df = pd.DataFrame(columns=["record_id"])

    # -------------------------
    # Load Demographics Data
    # -------------------------
    demo_file = demographics_info["file"]
    demo_record_id_col_idx = int(demographics_info["record_id_col"]) - 1
    demo_df = pd.read_csv(demo_file, low_memory=False)
    demo_record_id_col = demo_df.columns[demo_record_id_col_idx]

    demo_event_col_candidates = [col for col in demo_df.columns if 'event' in col.lower()]
    if not demo_event_col_candidates:
        raise ValueError("No event column found in demographics data CSV.")
    demo_event_col = demo_event_col_candidates[0]

    # Extract Demographics Variables
    demo_vars = {
        "age": demographics_info["age"],
        "sex": demographics_info["sex"],
        "postcode": demographics_info["postcode"],
        "randomisation_date": demographics_info["randomisation_date"],
        "deathdate": demographics_info.get("deathdate"),
        "withdrawal_date": demographics_info.get("withdrawal_date")
    }

    demo_frames = []
    for var_name, var_info in demo_vars.items():
        if not var_info:
            continue

        visit = var_info["visit"]
        variable = var_info["variable"]

        filtered = demo_df[demo_df[demo_event_col] == visit]
        if variable not in filtered.columns:
            print(f"Warning: variable '{variable}' not found in visit '{visit}' of demographics. Skipping.")
            continue

        var_df = filtered[[demo_record_id_col, variable]].copy()
        var_df.columns = ["record_id", var_name]

        # Apply mapping if provided in JSON
        if "mapping" in var_info:
            mapping_dict = {str(k): v for k, v in var_info["mapping"].items()}
            var_df[var_name] = (
                var_df[var_name]
                .astype(str)
                .str.strip()
                .str.split(".").str[0]
                .map(mapping_dict)
                .fillna(var_df[var_name])
            )

        demo_frames.append(var_df)

    if demo_frames:
        demo_merged_df = demo_frames[0]
        for df_var in demo_frames[1:]:
            demo_merged_df = pd.merge(demo_merged_df, df_var, on="record_id", how="outer")
    else:
        demo_merged_df = pd.DataFrame(columns=["record_id"] + list(demo_vars.keys()))

    # -------------------------
    # Load EQ5D Data
    # -------------------------
    eq5d_file = eq5d_info["file"]
    eq5d_record_id_col_idx = int(eq5d_info["record_id_col"]) - 1
    eq5d_df = pd.read_csv(eq5d_file, low_memory=False)
    eq5d_record_id_col = eq5d_df.columns[eq5d_record_id_col_idx]

    eq5d_event_col_candidates = [col for col in eq5d_df.columns if 'event' in col.lower()]
    if not eq5d_event_col_candidates:
        raise ValueError("No event column found in EQ5D data CSV.")
    eq5d_event_col = eq5d_event_col_candidates[0]

    # Baseline EQ5D
    baseline_eq5d_info = eq5d_info["baseline_eq5d"]
    baseline_eq5d_df = eq5d_df[
        eq5d_df[eq5d_event_col] == baseline_eq5d_info["visit"]
    ][[eq5d_record_id_col, baseline_eq5d_info["variable"]]].copy()
    baseline_eq5d_df.columns = ["record_id", "baseline_eq5d"]

    # Follow-up EQ5D using short_name
    follow_up_eq5d_frames = []
    for fu in eq5d_info.get("follow_up_visits", []):
        visit = fu["visit"]
        short_visit = fu.get("short_name", visit)
        variable = fu["variable"]

        filtered = eq5d_df[eq5d_df[eq5d_event_col] == visit]
        if variable not in filtered.columns:
            print(f"Warning: variable '{variable}' not found in visit '{visit}' of EQ5D data. Skipping.")
            continue

        fu_df = filtered[[eq5d_record_id_col, variable]].copy()
        fu_df.columns = ["record_id", f"{short_visit}_eq5d"]
        follow_up_eq5d_frames.append(fu_df)

    all_eq5d_df = baseline_eq5d_df
    for df_fu in follow_up_eq5d_frames:
        all_eq5d_df = pd.merge(all_eq5d_df, df_fu, on="record_id", how="outer")

    # -------------------------
    # Final Merge
    # -------------------------
    final_df = demo_merged_df.merge(all_ts_df, on="record_id", how="outer")
    final_df = final_df.merge(all_eq5d_df, on="record_id", how="outer")
    final_df["study_name"] = study_name

    print(f"Final combined dataframe sample for study '{study_name}':\n", final_df.head())

    # Save output
    final_df.to_csv(f"output_{study_name}.csv", index=False)
