import pandas as pd
import numpy as np

Main = pd.read_csv('./data/IRISDARC_DATA.csv')
DataDictionary = pd.read_csv('./data/DATADICTIONARY_DATA.csv', encoding='cp1252')
FormCompletion = pd.read_csv('./data/FORMCOMPLETION_DATA.csv', encoding='cp1252', low_memory=False)
InstrumentDesignations = pd.read_csv('./data/INSTRUMENTDESIGNATIONS_DATA.csv', encoding='cp1252')
SurveyQueue = pd.read_csv('./data/SURVEYQUEUE_DATA.csv', encoding='cp1252')
Demographic = pd.read_csv('./data/DEMOGRAPHIC_DATA.csv', encoding='cp1252')

filtered = FormCompletion[FormCompletion.iloc[:, 1].astype(str).str.contains("8_week_follow_up_arm_1", na=False)]

result = filtered.iloc[:, [0, 1, 25]]

result.columns = ['ID', 'Event', 'Timestamp']

result_sorted = result.sort_values(by='ID')

id_string_map = Demographic.iloc[:, [0, 5]]
id_string_map_columns = ['ID', 'Postcode']

merged_result = pd.merge(result_sorted, id_string_map, left_on='ID', right_on='record_id', how='left')

merged_result = merged_result.drop(columns=['record_id'])

merged_result = merged_result[merged_result['postcode'].notna()]

print(merged_result)


