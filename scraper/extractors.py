import re
from bs4 import BeautifulSoup
from network import get_soup

BBREF_BASE = 'https://www.basketball-reference.com'

def get_team_summary(team_abbr: str, season_year: int) -> dict:
    """
    Scrape the team page for {team_abbr}/{season_year} and return key
    performance metrics in a flat dict, e.g.:

      {
        'Team Win %': 0.305,
        'Team PTS/G': 111.5,
        'Team Opp PTS/G': 114.9,
        'Team SRS': -3.26,
        'Team Pace': 98.0,
        'Team Off Rtg': 112.6,
        'Team Def Rtg': 116.1,
        'Team Net Rtg': -3.5,
        'Team Exp Win %': 0.390
      }
    """
    if team_abbr == "BRK" and season_year < 2013:
        team_abbr = "NJN"
    if team_abbr == "NOP" and season_year < 2014:
        team_abbr = "NOH"

    url = f"{BBREF_BASE}/teams/{team_abbr}/{season_year}.html"
    soup = get_soup(url)
    if not soup:
        return {}
    summary = soup.find('div', {'data-template': 'Partials/Teams/Summary'})
    if not summary:
        return {}

    data = {}
    for strong in summary.find_all('strong'):
        label = strong.text.strip().rstrip(':')
        raw = strong.next_sibling
        if not raw or not raw.strip():
            continue
        # drop any trailing “(14th of 30)” etc.
        val = raw.strip().split('(')[0].strip()

        if label == 'Record':
            # compute actual win % by extracting "W-L" via regex
            match = re.search(r'(\d+)-(\d+)', raw)
            if match:
                wins, losses = int(match.group(1)), int(match.group(2))
                data['Team Win %'] = round(wins / (wins + losses), 3) if (wins + losses) > 0 else 0.0
            else:
                data['Team Win %'] = 0.0

        elif label == 'PTS/G':
            num = re.search(r'-?\d+\.?\d+', val)
            data['Team PTS/G'] = float(num.group()) if num else 0.0

        elif label == 'Opp PTS/G':
            num = re.search(r'-?\d+\.?\d+', val)
            data['Team Opp PTS/G'] = float(num.group()) if num else 0.0

        elif label == 'SRS':
            num = re.search(r'-?\d+\.?\d+', val)
            data['Team SRS'] = float(num.group()) if num else 0.0

        elif label == 'Pace':
            num = re.search(r'-?\d+\.?\d+', val)
            data['Team Pace'] = float(num.group()) if num else 0.0

        elif label == 'Off Rtg':
            num = re.search(r'-?\d+\.?\d+', val)
            data['Team Off Rtg'] = float(num.group()) if num else 0.0

        elif label == 'Def Rtg':
            num = re.search(r'-?\d+\.?\d+', val)
            data['Team Def Rtg'] = float(num.group()) if num else 0.0

        elif label == 'Net Rtg':
            num = re.search(r'-?\d+\.?\d+', val)
            data['Team Net Rtg'] = float(num.group()) if num else 0.0

        elif label == 'Expected W-L':
            # compute expected win % by extracting "W-L" via regex
            match = re.search(r'(\d+)-(\d+)', raw)
            if match:
                exp_wins, exp_losses = int(match.group(1)), int(match.group(2))
                data['Team Exp Win %'] = round(exp_wins / (exp_wins + exp_losses), 3) if (exp_wins + exp_losses) > 0 else 0.0
            else:
                data['Team Exp Win %'] = 0.0

    return data

def extract_height_weight(soup):
    """
    Look for "(###cm, ##kg)" text and return height (cm) and weight (kg).
    """
    text = soup.get_text()
    match = re.search(r'\((\d{3})cm,\s*(\d{2,3})kg\)', text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0

def extract_sr_cbb_link(soup):
    """
    Find "More College Stats on SR/CBB" link in bbref and return base URL.
    """
    anchor = soup.find('a', string=lambda text: text and 'More College Stats on SR/CBB' in text)
    if anchor and 'href' in anchor.attrs:
        return anchor['href'].split('?')[0]
    return None

def get_stat(row, stat):
    """
    Given a <tr> row and a data-stat name, return float value or 0.0.
    """
    cell = row.find('td', {'data-stat': stat})
    return float(cell.text.strip()) if cell and cell.text.strip() else 0.0

def get_advanced_stats(soup):
    """
    Parse the last row of the "players_advanced" table and return a dict of advanced stats.
    """
    table = soup.find('table', id='players_advanced')
    if not table:
        return {}
    rows = table.find('tbody').find_all('tr')
    # filter out header rows
    rows = [r for r in rows if not r.get('class') or 'thead' not in r.get('class')]
    if not rows:
        return {}
    last_row = rows[-1]
    def adv_stat(stat):
        cell = last_row.find('td', {'data-stat': stat})
        return float(cell.text.strip()) if cell and cell.text.strip() else 0.0
    return {
        'PER': adv_stat('per'),
        'TS%': adv_stat('ts_pct'),
        '3PAr': adv_stat('fg3a_per_fga_pct'),
        'FTr': adv_stat('fta_per_fga_pct'),
        'PProd': adv_stat('pprod'),
        'ORB%': adv_stat('orb_pct'),
        'DRB%': adv_stat('drb_pct'),
        'TRB%': adv_stat('trb_pct'),
        'AST%': adv_stat('ast_pct'),
        'STL%': adv_stat('stl_pct'),
        'BLK%': adv_stat('blk_pct'),
        'TOV%': adv_stat('tov_pct'),
        'USG%': adv_stat('usg_pct'),
        'OWS': adv_stat('ows'),
        'DWS': adv_stat('dws'),
        'WS': adv_stat('ws'),
        'WS/40': adv_stat('ws_per_40'),
        'OBPM': adv_stat('obpm'),
        'DBPM': adv_stat('dbpm'),
        'BPM': adv_stat('bpm')
    }

def get_per40_stats(soup):
    """
    Parse the last row of the "players_per_min" table and return per-40-minute stats.
    """
    table = soup.find('table', id='players_per_min')
    if not table:
        return {}
    rows = table.find('tbody').find_all('tr')
    rows = [r for r in rows if not r.get('class') or 'thead' not in r.get('class')]
    if not rows:
        return {}
    last_row = rows[-1]
    def per40(stat):
        cell = last_row.find('td', {'data-stat': stat})
        return float(cell.text.strip()) if cell and cell.text.strip() else 0.0
    return {
        'FG/40': per40('fg_per_min'),
        'FGA/40': per40('fga_per_min'),
        '3P/40': per40('fg3_per_min'),
        '3PA/40': per40('fg3a_per_min'),
        'FT/40': per40('ft_per_min'),
        'FTA/40': per40('fta_per_min'),
        'ORB/40': per40('orb_per_min'),
        'DRB/40': per40('drb_per_min'),
        'TRB/40': per40('trb_per_min'),
        'AST/40': per40('ast_per_min'),
        'STL/40': per40('stl_per_min'),
        'BLK/40': per40('blk_per_min'),
        'TOV/40': per40('tov_per_min'),
        'PF/40': per40('pf_per_min'),
        'PTS/40': per40('pts_per_min')
    }

def get_per100_stats(soup):
    """
    Parse the last row of the "players_per_poss" table and return per-100-possession stats.
    """
    table = soup.find('table', id='players_per_poss')
    if not table:
        return {}
    rows = table.find('tbody').find_all('tr')
    rows = [r for r in rows if not r.get('class') or 'thead' not in r.get('class')]
    if not rows:
        return {}
    last_row = rows[-1]
    def per100(stat):
        cell = last_row.find('td', {'data-stat': stat})
        return float(cell.text.strip()) if cell and cell.text.strip() else 0.0
    return {
        'FG/100': per100('fg_per_poss'),
        'FGA/100': per100('fga_per_poss'),
        '3P/100': per100('fg3_per_poss'),
        '3PA/100': per100('fg3a_per_poss'),
        'FT/100': per100('ft_per_poss'),
        'FTA/100': per100('fta_per_poss'),
        'ORB/100': per100('orb_per_poss'),
        'DRB/100': per100('drb_per_poss'),
        'TRB/100': per100('trb_per_poss'),
        'AST/100': per100('ast_per_poss'),
        'STL/100': per100('stl_per_poss'),
        'BLK/100': per100('blk_per_poss'),
        'TOV/100': per100('tov_per_poss'),
        'PF/100': per100('pf_per_poss'),
        'PTS/100': per100('pts_per_poss'),
        'ORtg': per100('off_rtg'),
        'DRtg': per100('def_rtg')
    }
