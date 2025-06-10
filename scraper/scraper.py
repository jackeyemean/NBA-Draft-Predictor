import logging
from datetime import datetime
import pandas as pd
import re

from network import get_soup
from extractors import (
    extract_height_weight, extract_sr_cbb_link, get_stat,
    get_advanced_stats, get_per40_stats, get_per100_stats, get_team_summary
)

logger = logging.getLogger(__name__)

BBREF_BASE = 'https://www.basketball-reference.com'
CBB_BASE = 'https://www.sports-reference.com'

TEAM_PLAYER_DEVELOPMENT = {
    # Great reputation
    'SAS': 4, 'GSW': 4, 'BOS': 4, 'TOR': 4, 'MIA': 4, 'OKC': 4,
    # Good
    'MIL': 3, 'DEN': 3, 'MEM': 3, 'IND': 3, 'ATL': 3, 'CLE': 3, 'ORL': 3,
    # Average
    'MIN': 2, 'LAL': 2, 'NYK': 2, 'HOU': 2, 'DAL': 3,
    # Not Ideal
    'BKN': 1, 'DET': 1, 'PHI': 1, 'UTA': 1, 'POR': 1, 'LAC': 1, 
    # Poverty franchises
    'PHX': 0, 'NOP': 0, 'NOH': 0, 'SAC': 0, 'CHI': 0, 'WAS': 0, 'CHO': 0, 'CHA': 0
}

COLLEGE_STRENGTH = {
    # Elite “Blue Bloods”
    'Duke': 4, 'Kentucky': 4, 'Kansas': 4, 'UNC': 4,
    # NBA Factories / Near-Blue-Bloods
    'UCLA': 3, 'Arizona': 3, 'UConn': 3, 'Villanova': 3,
    'Gonzaga': 3, 'Michigan State': 3, 'Texas': 3,
    'Alabama': 3, 'Houston': 3, 'Baylor': 3,
    'Louisville': 3,
    # Respected Power Programs
    'Florida': 2, 'Virginia': 2, 'Tennessee': 2, 'Arkansas': 2,
    'Oregon': 2, 'Auburn': 2, 'Michigan': 2, 'Indiana': 2,
    'USC': 2, 'Ohio State': 2, 'Purdue': 2, 'Creighton': 2,
    'Marquette': 2, 'Illinois': 2, 'Miami (FL)': 2, 'LSU': 2,
    'Iowa': 2, 'Oklahoma': 2, 'San Diego State': 2, 'VCU': 2,
    # Decent / Recognizable but Less Typical
    'Florida State': 1, 'Georgia': 1, 'Wisconsin': 1,
    'Colorado': 1, 'Texas Tech': 1, 'Seton Hall': 1, 'Syracuse': 1,
    'Providence': 1, 'NC State': 1, 'Maryland': 1, "Saint Mary's": 1,
    'Dayton': 1, 'Memphis': 1, 'Wake Forest': 1, 'Missouri': 1,
    'Arizona State': 1, 'Xavier': 1
    # Everything else will default to 0
}

def get_draft_picks(year):
    """
    Fetch draft page, return a list of player dicts with:
    - pick, team, name, bbref_url, college
    """
    url = f"{BBREF_BASE}/draft/NBA_{year}.html"
    soup = get_soup(url)
    if not soup:
        logger.warning(f"Cannot fetch draft page for {year}")
        return []
    table = soup.find('table', id='stats')
    if not table:
        logger.error(f"No draft table for {year}")
        return []

    picks = []
    for row in table.find('tbody').find_all('tr'):
        if row.get('class') and 'thead' in row.get('class'):
            continue
        # pick number
        pick_cell = row.find('td', {'data-stat': 'pick_overall'})
        pick = pick_cell.text.strip() if pick_cell else None
        # NBA team
        team_cell = row.find('td', {'data-stat': 'team_id'})
        team = team_cell.text.strip() if team_cell else None
        # player name and BBRef URL
        name_cell = row.find('td', {'data-stat': 'player'})
        if not name_cell:
            continue
        name = name_cell.text.strip()
        a_tag = name_cell.find('a')
        if not a_tag:
            continue
        bbref_url = BBREF_BASE + a_tag['href']
        # college name
        college_cell = row.find('td', {'data-stat': 'college_name'})
        college = college_cell.text.strip() if college_cell else None

        picks.append({
            'pick': pick,
            'team': team,
            'name': name,
            'bbref_url': bbref_url,
            'college': college
        })
    return picks


def get_player_meta(bbref_url):
    """
    Fetch player's BBRef page and return:
    - # of NBA relatives
    - sports reference college stats URL
    - birth_date ("YYYY-MM-DD")
    - position ("PG,SG")
    """
    soup = get_soup(bbref_url)
    if not soup:
        return 0, None, None, ''

    # count relatives if listed
    relatives = 0
    for strong in soup.find_all('strong'):
        if 'Relatives' in strong.text:
            p = strong.find_parent('p')
            if p:
                relatives = len(p.find_all('a'))
            break

    # birth date from necro-birth span
    birth_tag = soup.find('span', id='necro-birth')
    birth_date = (
        birth_tag.get('data-birth')
        if birth_tag and birth_tag.has_attr('data-birth')
        else None
    )

    # link to sport reference college bball stats
    cbb_url = extract_sr_cbb_link(soup)

    # parse “Position:” line
    position = ''
    for p_tag in soup.select('div#meta p'):
        strong_tag = p_tag.find('strong')
        if strong_tag and 'Position:' in strong_tag.text:
            raw_text = p_tag.get_text()
            after = raw_text.split('Position:')[1].strip()
            position_text = after.split('▪')[0].strip()
            position = position_text
            break

    # normalize to comma-separated abbreviations
    fullname_to_abbrev = {
        'Point Guard':      'PG',
        'Shooting Guard':   'SG',
        'Small Forward':    'SF',
        'Power Forward':    'PF',
        'Center':           'C',
    }

    def split_and_map(raw: str) -> str:
        """
        Given: "Shooting Guard and Power Forward",
        return "SG,PF".
        """
        parts = []
        tmp = raw.replace(' and ', '|').replace(' / ', '|').replace('-', '|')
        for token in tmp.split('|'):
            name = token.strip()
            if name in fullname_to_abbrev:
                parts.append(fullname_to_abbrev[name])
            else:
                upper = name.upper()
                if upper in fullname_to_abbrev.values():
                    parts.append(upper)
                else:
                    pass
        seen = set()
        ordered = []
        for code in parts:
            if code not in seen:
                seen.add(code)
                ordered.append(code)
        return ','.join(ordered)

    position_abbrev = split_and_map(position)

    # ===== Getting nba career stats and main nba team ========
    table = soup.find('table', id='per_game_stats')
    if not table or not table.find('tfoot'):
        return {}, ''

    tfoot = table.find('tfoot')
    rows = tfoot.find_all('tr')

    # Career aggregate row is the first <tr> in <tfoot>
    career_row = rows[0]
    career_stats = {}
    for cell in career_row.find_all('td'):
        stat = cell['data-stat']
        text = cell.text.strip()
        career_stats[stat] = float(text) if text else 0.0

    # === compute MAIN NBA TEAM over first four seasons, excluding any 2TM rows ===
    tbody = table.find('tbody')
    all_rows = tbody.find_all('tr')

    # 1) collect the earliest four distinct seasons (by csk)
    seasons = []
    for r in all_rows:
        th = r.find('th', {'data-stat': 'year_id'})
        if not th or not th.get('csk'): 
            continue
        yr = int(th['csk'])
        if yr not in seasons:
            seasons.append(yr)
    seasons = sorted(seasons)[:4]

    # 2) sum up games for each team in those seasons (skip any '2TM' rows)
    team_games = {}
    for r in all_rows:
        th = r.find('th', {'data-stat': 'year_id'})
        if not th or not th.get('csk'):
            continue
        yr = int(th['csk'])
        if yr not in seasons:
            continue
        team_td = r.find('td', {'data-stat': 'team_name_abbr'})
        team = team_td.text.strip() if team_td else ''
        if team == '2TM' or not team:
            continue
        games_td = r.find('td', {'data-stat': 'games'})
        games = float(games_td.text.strip()) if games_td and games_td.text.strip() else 0.0
        team_games[team] = team_games.get(team, 0) + games

    main_team = max(team_games, key=team_games.get) if team_games else ''

    return relatives, cbb_url, birth_date, position_abbrev, career_stats, main_team


def get_college_stats(cbb_url, nba_team, college):
    """
    Given a SR/CBB URL, fetch college stats, meta, and team performance:
    - height (cm), weight (kg), seasons played
    - college team season summary metrics prefixed with COLLEGE_
    """
    soup = get_soup(cbb_url)
    if not soup:
        return 0, 0, 0, pd.DataFrame()

    # height & weight
    height, weight = extract_height_weight(soup)

    # per-game stats table
    per_game = soup.find('table', id='players_per_game')
    if not per_game:
        return height, weight, 0, pd.DataFrame()

    rows = per_game.find('tbody').find_all('tr')
    rows = [r for r in rows if not r.get('class') or 'thead' not in r.get('class')]
    if not rows:
        return height, weight, 0, pd.DataFrame()

    last_row = rows[-1]
    seasons = len(rows)

    # build basic stats dict
    stats = {
        'G': get_stat(last_row, 'games'),
        'GS%': round(
            get_stat(last_row, 'games_started') / get_stat(last_row, 'games') * 100, 2
        ) if get_stat(last_row, 'games') > 0 else 0.0,
        'MPG': get_stat(last_row, 'mp_per_g'),
        'FG': get_stat(last_row, 'fg_per_g'),
        'FGA': get_stat(last_row, 'fga_per_g'),
        'FG%': get_stat(last_row, 'fg_pct'),
        '3P': get_stat(last_row, 'fg3_per_g'),
        '3PA': get_stat(last_row, 'fg3a_per_g'),
        '3P%': get_stat(last_row, 'fg3_pct'),
        'FT': get_stat(last_row, 'ft_per_g'),
        'FTA': get_stat(last_row, 'fta_per_g'),
        'FT%': get_stat(last_row, 'ft_pct'),
        'DRB': get_stat(last_row, 'drb_per_g'),
        'ORB': get_stat(last_row, 'orb_per_g'),
        'TRB': get_stat(last_row, 'trb_per_g'),
        'AST': get_stat(last_row, 'ast_per_g'),
        'STL': get_stat(last_row, 'stl_per_g'),
        'BLK': get_stat(last_row, 'blk_per_g'),
        'TOV': get_stat(last_row, 'tov_per_g'),
        'PF': get_stat(last_row, 'pf_per_g'),
        'PTS': get_stat(last_row, 'pts_per_g'),
        'Height': height,
        'Weight': weight,
        'NBA Team': nba_team or '',
        'College': college or ''
    }

    # extract college team summary link
    team_cell = last_row.find('td', {'data-stat': 'team_name_abbr'})
    team_link = None
    if team_cell:
        a = team_cell.find('a')
        if a and a.get('href'):
            team_link = f"{CBB_BASE}{a['href']}"

    # scrape college team season summary
    college_perf = {}
    if team_link:
        c_soup = get_soup(team_link)
        if c_soup:
            summary = c_soup.find('div', {'data-template': 'Partials/Teams/Summary'})
            if summary:
                for strong in summary.find_all('strong'):
                    label = strong.text.strip().rstrip(':')
                    raw = strong.next_sibling
                    if not raw or not raw.strip():
                        continue
                    val = raw.strip().split('(')[0].strip()

                    if label == 'Record':
                        match = re.search(r'(\d+)-(\d+)', raw)
                        if match:
                            wins, losses = int(match.group(1)), int(match.group(2))
                            college_perf['COLLEGE_Win %'] = wins / (wins + losses) if (wins + losses) > 0 else 0.0

                    elif label == 'PS/G':
                        num = re.search(r'-?\d+\.?\d+', val)
                        college_perf['COLLEGE_PS/G'] = float(num.group()) if num else 0.0

                    elif label == 'PA/G':
                        num = re.search(r'-?\d+\.?\d+', val)
                        college_perf['COLLEGE_PA/G'] = float(num.group()) if num else 0.0

                    elif label == 'SRS':
                        num = re.search(r'-?\d+\.?\d+', val)
                        college_perf['COLLEGE_SRS'] = float(num.group()) if num else 0.0

                    elif label == 'SOS':
                        num = re.search(r'-?\d+\.?\d+', val)
                        college_perf['COLLEGE_SOS'] = float(num.group()) if num else 0.0

                    elif label == 'ORtg':
                        num = re.search(r'-?\d+\.?\d+', val)
                        college_perf['COLLEGE_Off Rtg'] = float(num.group()) if num else 0.0

                    elif label == 'DRtg':
                        num = re.search(r'-?\d+\.?\d+', val)
                        college_perf['COLLEGE_Def Rtg'] = float(num.group()) if num else 0.0

    # advanced, per-40, per-100 stats
    stats.update(get_advanced_stats(soup))
    stats.update(get_per40_stats(soup))
    stats.update(get_per100_stats(soup))

    # merge college performance
    stats.update(college_perf)

    df = pd.DataFrame([stats])

    return height, weight, seasons, df


def calculate_age(birth_date, draft_year):
    """
    Age (in years) assuming draft date is on June 25.
    """
    if not birth_date:
        return 0.0
    try:
        bdt = datetime.strptime(birth_date, "%Y-%m-%d")
        draft_dt = datetime(draft_year, 6, 25)
        return round((draft_dt - bdt).days / 365.25, 2)
    except Exception as e:
        logger.warning(f"Failed to parse birth date {birth_date}: {e}")
        return 0.0

# Called in main.py
def process_player(pick_info, draft_year):
    """
    Given a dict with 'pick', 'team', 'name', 'bbref_url', 'college' and draft_year,
    fetch meta info (including Position), college stats (raw), and return a record dict.
    """
    name = pick_info['name']
    team = pick_info['team']
    college = pick_info['college']

    relatives, cbb_url, birth_date, player_position, career_stats, main_team = get_player_meta(pick_info['bbref_url'])


    if not cbb_url:
        logger.info(f"Skipping {name} – no college stats link")
        return None

    age = calculate_age(birth_date, draft_year)

    height, weight, seasons, raw_df = get_college_stats(cbb_url, team, college)
    if raw_df.empty:
        return None

    stats = raw_df.iloc[0].to_dict()

    record = {
        'Draft Year': draft_year,
        'Pick Number': int(pick_info['pick']) if pick_info['pick'] and pick_info['pick'].isdigit() else 0,
        'NBA Team': team or '',
        'POS': player_position or '',        
        'Name': name or '',
        'Age': age,
        'College': college or '',
        'Height': height,
        'Weight': weight,
        'Height/Weight': round(height/weight, 3),
        'NBA Relatives': relatives,
        'Seasons Played (College)': seasons
    }
    record.update(stats)

    record['MAIN NBA TEAM'] = main_team
    for stat, val in career_stats.items():
        record[f'NBA_{stat}'] = val

    # — add NBA Team Development & College Strength —
    record['NBA Team Development'] = TEAM_PLAYER_DEVELOPMENT.get(
        record.get('MAIN NBA TEAM', ''),
        0
    )
    record['College Strength'] = COLLEGE_STRENGTH.get(
        record.get('College', ''),
        0
    )

    # — pre-draft team performance for MAIN NBA TEAM —
    team = record.get('MAIN NBA TEAM', '')
    year = record.get('Draft Year')
    perf = get_team_summary(team, year)
    # merge those metrics right into the record
    record.update(perf)
    
    return record

# Called in main.py
def write_record(record, output_file, header_written):
    """
    Append a single player's record to CSV.
    If header_written is False, write header row first.
    Returns True (header is now written).
    """
    df = pd.DataFrame([record])
    df.to_csv(output_file, mode='a', header=not header_written, index=False)
    return True
