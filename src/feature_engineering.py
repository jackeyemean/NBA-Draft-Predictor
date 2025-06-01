import pandas as pd

def engineer_features_full(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # === Efficiency Ratios ===
    df['AST/TOV'] = (df['AST%'] / df['TOV%'].replace(0, pd.NA)).round(3)
    df['PTS/USG'] = (df['PTS/40'] / df['USG%'].replace(0, pd.NA)).round(3)
    df['3PA/FGA'] = (df['3PA'] / df['FGA'].replace(0, pd.NA)).round(3)

    # === Scoring Mix ===
    df['3PAr_TS'] = (df['3PAr'] * df['TS%']).round(3)
    df['ShotTouchBlend'] = (0.6 * df['FT%'].fillna(0) + 0.4 * df['3P%'].fillna(0)).round(3)

    # === Size-Adjusted Metrics ===
    pos_avg_heights = {'PG': 188, 'SG': 193, 'SF': 201, 'PF': 206, 'C': 211}
    def get_pos_height(pos):
        if not pos or not isinstance(pos, str): return None
        for key in pos_avg_heights:
            if key in pos: return pos_avg_heights[key]
        return None

    # df['POS Avg Height'] = df['POS'].map(get_pos_height)
    # df['Size_vs_POS'] = (df['Height'] / df['POS Avg Height'].replace(0, pd.NA)).round(3)
    df['Weight/Height'] = (df['Weight'] / df['Height'].replace(0, pd.NA)).round(3)

    # === Team Development Scores ===
    team_dev = {
        'SAS': 10, 'MIA': 9, 'TOR': 8, 'DEN': 9, 'GSW': 9,
        'OKC': 8, 'BOS': 8, 'MEM': 7, 'LAL': 7, 'MIL': 7,
        'ATL': 6, 'UTA': 6, 'PHX': 6, 'CLE': 5, 'CHI': 5,
        'NOP': 5, 'NYK': 5, 'ORL': 5, 'MIN': 4, 'DET': 4,
        'CHA': 4, 'HOU': 4, 'WSB': 4, 'BKN': 3, 'SAC': 3,
        'POR': 3, 'IND': 6, 'PHI': 5, 'LAC': 5, 'DAL': 6
    }
    df['Team Dev Score'] = df['NBA Team'].map(team_dev).fillna(5).round(1)

    # === College Strength Scores ===
    college_score = {
        'Duke': 10, 'Kentucky': 10, 'Kansas': 9, 'North Carolina': 9,
        'UCLA': 9, 'Michigan State': 8, 'Villanova': 8, 'Arizona': 8,
        'Texas': 8, 'UConn': 7, 'Gonzaga': 7, 'Indiana': 7, 'LSU': 7,
        'Florida': 7, 'Syracuse': 7, 'Baylor': 7, 'Oregon': 7,
        'Washington': 6, 'Colorado': 6, 'Louisville': 6, 'Iowa State': 6,
        'Maryland': 6, 'BYU': 5, 'Murray State': 4, 'Weber State': 3,
        'Davidson': 4, 'Morehead State': 3
    }
    df['College Strength'] = df['College'].map(college_score).fillna(5).round(1)

    return df
