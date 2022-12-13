import pandas as pd
import numpy as np
from tqdm import tqdm

df = pd.read_csv('countries.csv', sep=',')
ages = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64',
        '65-69', '70-74', '75-79', '80-84', '85-89', '90-94', '95-99', '100+']

fertility_ages = ['20-24', '25-29', '30-34', '35-39']

result = pd.DataFrame()

for country in tqdm(df['country'].unique()):
    data = df.loc[df['country'] == country, df.columns != 'country']
    female = data.loc[data['sex'] == 'Female', data.columns != 'sex'].reset_index(drop=True)
    male = data.loc[data['sex'] == 'Male', data.columns != 'sex'].reset_index(drop=True)

    fertility = (female['0-4'] + male['0-4']) / (female[fertility_ages].apply(lambda row: sum(row), axis=1)) * len(
        fertility_ages)

    female_percentages = female['0-4'] / (female['0-4'] + male['0-4'])

    for i in range(1, len(ages)):
        group_before = female[ages[i - 1]][0:-5].reset_index(drop=True)
        group_after = female[ages[i]][5:].reset_index(drop=True)
        survival_rate = group_after / group_before
        survival_rate.replace([np.inf, -np.inf, np.nan], 0.0, inplace=True)
        survival_rate.apply(lambda x: 2.0 if x > 2.0 else x)
        female[ages[i - 1]] = survival_rate

        group_before = male[ages[i - 1]][0:-5].reset_index(drop=True)
        group_after = male[ages[i]][5:].reset_index(drop=True)
        survival_rate = group_after / group_before
        survival_rate.replace([np.inf, -np.inf, np.nan], 0.0, inplace=True)
        survival_rate.apply(lambda x: 2.0 if x > 2.0 else x)
        male[ages[i - 1]] = survival_rate

    female = female.agg(lambda x: f'[{min(x)}, {max(x)}]')
    female = pd.DataFrame([female]).drop(labels='year', axis=1)
    female.insert(0, 'country', country)
    female = female.drop(labels='100+', axis=1)

    male = male.agg(lambda x: f'[{min(x)}, {max(x)}]')
    male = pd.DataFrame([male]).drop(labels='year', axis=1)
    male = male.drop(labels='100+', axis=1)
    datum = female.merge(male, left_index=True, right_index=True, suffixes=('_female', '_male'))
    datum.insert(1, 'fertility',  f'[{min(fertility)}, {max(fertility)}]')
    datum.insert(2, 'female_percentage', f'[{min(female_percentages)}, {max(female_percentages)}]')
    result = pd.concat([result, datum])

result.to_csv('countries_ranges.csv', sep=',', index=False)
