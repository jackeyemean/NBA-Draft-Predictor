import pandas as pd

NBA_AVG_OFFRTG = {
    2011: 107.3,
    2012: 104.6,
    2013: 105.8,
    2014: 106.6,
    2015: 105.6,
    2016: 106.4,
    2017: 108.8,
    2018: 108.6,
    2019: 110.4,
    2020: 110.6,
    2021: 112.3,
    2022: 112.0,
    2023: 114.8,
    2024: 115.3
    # , 2025: 114.5
}
NBA_AVG_PPG = {
    2011: 99.6,
    2012: 96.3,
    2013: 98.1,
    2014: 101.0,
    2015: 100.0,
    2016: 102.7,
    2017: 105.6,
    2018: 106.3,
    2019: 111.2,
    2020: 111.8,
    2021: 112.1,
    2022: 110.6,
    2023: 114.7,
    2024: 114.2,
    # 2025: 113.8
}

data = "model-4/data/drafts-2011-to-2024.csv"

df = pd.read_csv(data)

# obtain relative offensive and defensive rating
df['LAST_YR_REL_ORtg'] = df['LAST_YR_ORtg'] - df['Draft Year'].map(NBA_AVG_OFFRTG)
df['LAST_YR_REL_DRtg'] = df['LAST_YR_DRtg'] - df['Draft Year'].map(NBA_AVG_OFFRTG)

# obtain relative team ppg and opponent ppg
df['LAST_YR_REL_PTS/G'] = df['LAST_YR_PTS/G'] - df['Draft Year'].map(NBA_AVG_PPG)
df['LAST_YR_REL_OPTS/G'] = df['LAST_YR_OPTS/G'] - df['Draft Year'].map(NBA_AVG_PPG)

# calculate net team ppg
df['LAST_YR_NET_PTS/G'] = df['LAST_YR_PTS/G'] - df['LAST_YR_OPTS/G']

# round values
df['LAST_YR_REL_ORtg'] = df['LAST_YR_REL_ORtg'].round(1)
df['LAST_YR_REL_DRtg'] = df['LAST_YR_REL_DRtg'].round(1)
df['LAST_YR_REL_PTS/G'] = df['LAST_YR_REL_PTS/G'].round(1)
df['LAST_YR_REL_OPTS/G'] = df['LAST_YR_REL_OPTS/G'].round(1)
df['LAST_YR_NET_PTS/G'] = df['LAST_YR_NET_PTS/G'].round(1)

df.to_csv('populated-2011-2024.csv', index=False)
