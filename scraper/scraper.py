import logging
from datetime import datetime
import pandas as pd

from network import get_soup
from extractors import (
    extract_height_weight, extract_sr_cbb_link, get_stat,
    get_advanced_stats, get_per40_stats, get_per100_stats
)

logger = logging.getLogger(__name__)
BBREF_BASE = 'https://www.basketball-reference.com'


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

    return relatives, cbb_url, birth_date, position_abbrev


def get_college_stats(cbb_url, nba_team, college):
    """
    Given a SR/CBB URL, fetch college stats and meta:
    - height (cm), weight (kg), seasons played
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

    # input basic per-game stats and meta data from sports ref and draft year page
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

    # advanced, per-40, per-100 stats
    stats.update(get_advanced_stats(soup))
    stats.update(get_per40_stats(soup))
    stats.update(get_per100_stats(soup))

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

    relatives, cbb_url, birth_date, player_position = get_player_meta(pick_info['bbref_url'])
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
