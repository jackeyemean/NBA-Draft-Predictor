import pandas as pd

NBA_AVG_PACE = {
    2011: 92.1, 2012: 91.3, 2013: 92.0, 2014: 93.9,
    2015: 93.9, 2016: 95.8, 2017: 96.4, 2018: 97.3,
    2019: 100.0, 2020: 100.3, 2021: 99.2, 2022: 98.2,
    2023: 99.2, 2024: 98.5
}

data = "model-5/data/final-training.csv"
df = pd.read_csv(data)

# relative NBA pace
df['Rel NBA Pace'] = df['NBA Pace'] - df['Draft Year'].map(NBA_AVG_PACE)

# rounding
df['Rel NBA Pace'] = df['Rel NBA Pace'].round(1)

df.to_csv('TRAINING.csv', index=False)

# ---------------------------------------------------------------------------------------------
test_data = "model-5/data/featured-testing.csv"
test_df = pd.read_csv(test_data)

# relative NBA pace
test_df['Rel NBA Pace'] = test_df['NBA Pace'] - test_df['Draft Year'].map(NBA_AVG_PACE)

# rounding
test_df['Rel NBA Pace'] = test_df['Rel NBA Pace'].round(1)

test_df.to_csv('TESTING.csv', index=False)
