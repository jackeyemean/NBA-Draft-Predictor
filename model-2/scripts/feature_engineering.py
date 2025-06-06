import pandas as pd
import argparse

def engineer_features_full(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame with basic and advanced stats, compute additional features:
    - Efficiency ratios (e.g., AST/TOV, PTS/USG)
    - Scoring mix metrics (e.g., 3PAr_TS, ShotTouchBlend)
    - Size-adjusted metrics (e.g., Weight/Height)
    - Team and college strength scores (mapped from preset dicts)
    """
    df = df.copy()

    # === Efficiency Ratios ===
    df['AST/TOV'] = (df['AST%'] / df['TOV%'].replace(0, pd.NA)).round(3)
    df['PTS/USG'] = (df['PTS/40'] / df['USG%'].replace(0, pd.NA)).round(3)
    df['3PA/FGA'] = (df['3PA'] / df['FGA'].replace(0, pd.NA)).round(3)

    # === Scoring Mix ===
    df['3PAr_TS'] = (df['3PAr'] * df['TS%']).round(3)
    df['ShotTouchBlend'] = (0.6 * df['FT%'].fillna(0) + 0.4 * df['3P%'].fillna(0)).round(3)

    # === Size-Adjusted Metrics ===
    df['Weight/Height'] = (df['Weight'] / df['Height'].replace(0, pd.NA)).round(3)

    # === Team Development Scores (preset mapping) ===
    team_dev = {
        'SAS': 10, 'MIA': 10, 'TOR': 10, 'OKC': 10,
        'GSW':  9,  'BOS':  9,
        'CLE':  8,  'IND':  8,
        'MEM':  7,  'DEN':  7,
        'MIL':  6,
        'ATL':  5,  'UTA':  5,  'DAL':  5,
        'CHI':  4,  'NYK':  4,  'ORL':  4,
        'PHX':  3,  'DET':  3,  'MIN':  3,  'LAL':  3, 'PHI':  3,
        'LAC':  2,  'POR':  2,  'HOU':  2,  'BKN':  2,
        'SAC':  1,  'CHA':  1,  'NOP':  1,  'WAS':  1
    }
    df['Team Dev Score'] = df['NBA Team'].map(team_dev).fillna(5).round(1)

    # === College Strength Scores (preset mapping) ===
    college_score = {
        'Kentucky':10, 'Duke':10, 'Kansas':9, 'UNC':9, 'UCLA':8, 'Michigan State':7,
        'Arizona':7, 'Villanova':7, 'Florida':7, 'Ohio State':6, 'Connecticut':6,
        'Indiana':6, 'Louisville':6, 'LSU':6, 'Texas':6, 'Gonzaga':6, 'Baylor':6,
        'Marquette':5, 'Tennessee':5, 'Iowa State':5, 'West Virginia':5,
        'North Carolina State':5, 'Washington':5, 'Oregon':5, 'Purdue':5,
        'Illinois':5, 'Memphis':4, 'Kansas State':4, 'Xavier':4, 'Cincinnati':4,
        'Arizona State':4, 'Maryland':4, 'SMU':4, 'Dayton':4, 'California':4,
        'San Diego State':4, 'Miami (FL)':3, 'Seton Hall':3, 'Virginia':3,
        'Mississippi State':3, 'Oklahoma State':3, 'Nebraska':3, 'Rhode Island':3,
        'Richmond':3, 'TCU':3, 'Tulsa':3, 'Pittsburgh':3, 'Missouri':3,
        'Colorado':3, 'Georgia':3, 'Illinois State':3, 'Buffalo':3,
        'Marist':3, 'Clemson':3, 'Auburn':3, 'Minnesota':3, 'Rutgers':3,
        'Southern Illinois':3, 'Fresno State':3, 'Nevada':3, 'Belmont':3,
        'Boise State':3, 'Utah State University':3, 'Ball State':3,
        'Northern Iowa':3, 'High Point':3, 'Pacific':3, 'San Francisco':3,
        'Washington State':3, 'Wyoming':3, 'Colorado State':3,
        'Vanderbilt':3, 'Miami (Ohio)':3, "St. John's":3, 'Morehead State':3,
        'Murray State':3, 'Bradley':3, 'Troy':3, 'UNC Asheville':3,
        'Charleston':3, 'Cleveland State':3, 'Weber State':3,
        'Northern Colorado':3, 'South Carolina':3, 'UNC Greensboro':3,
        'South Dakota State':3, 'UAB':3, 'Stephen F. Austin':3,
        'Long Beach State':3, 'Wofford':3, 'New Mexico State':3,
        'Oklahoma':3, 'Wichita State':3, 'The Citadel':3, 'Samford':3,
        'UC Santa Barbara':3, 'Winthrop':3, 'Appalachian State':3,
        'Liberty':3, 'Furman':3, 'Eastern Kentucky':3,
        'Jacksonville State':3, 'McNeese State':3, 'Northern Kentucky':3,
        'New Orleans':3, 'South Florida':3, 'LA Tech':3, 'Georgia State':3,
        'Howard':3, 'UNC Wilmington':3, "Saint Joseph's":3, 'Mercer':3,
        'Wright State':3, 'UIC':3, 'Stetson':3, 'Radford':3, 'Army':3,
        'Georgia Tech':3, 'Hofstra':3, 'Milwaukee':3, 'Kennesaw State':3,
        'UMBC':3, 'Presbyterian':3, 'East Tennessee State':3,
        "Saint Mary's":3, 'Jackson State':3, 'Sacred Heart':3,
        'Nicholls State':3, 'Wagner':3, 'Bryant':3, 'Alabama':3,
        'Middle Tennessee State':3, 'Western Kentucky':3,
        'Northern Illinois':3, 'Mississippi Valley State':3
    }
    df['College Strength'] = df['College'].map(college_score).fillna(5).round(1)

    return df


def main():
    parser = argparse.ArgumentParser(
        description="Read a raw draft CSV, engineer extra features, and write a new CSV."
    )
    parser.add_argument(
        'input_csv',
        help="Path to the raw CSV output by the scraper (with all stat columns)."
    )
    parser.add_argument(
        'output_csv',
        help="Path where the engineered-­features CSV should be saved."
    )
    args = parser.parse_args()

    df_raw = pd.read_csv(args.input_csv)
    df_eng = engineer_features_full(df_raw)
    df_eng.to_csv(args.output_csv, index=False)


if __name__ == "__main__":
    main()
