import re
from bs4 import BeautifulSoup
from network import get_soup

BBREF_BASE = 'https://www.basketball-reference.com'

def get_team_summary(team_abbr: str, season_year: int) -> dict:
    """
    Scrape the team page for {team_abbr}/{season_year} and return key
    performance metrics in a flat dict, ensuring each field is present (defaulting to 0.0).
    """
    # Handle historical abbreviation changes relevant for 2011 to 2024

    # Brooklyn Nets (BRK) were New Jersey Nets (NJN) until 2013
    if team_abbr == "BRK" and season_year < 2013:
        team_abbr = "NJN"
    # Pelicans (NOP) were the Hornets (NOH) until 2014
    if team_abbr == "NOP" and season_year < 2014:
        team_abbr = "NOH"
    # Hornets (CHO) were the Bobcats (CHA) until 2015
    if team_abbr == "CHO" and season_year < 2015:
        team_abbr = "CHA"

    # Player did not play for an NBA team despite getting drafted
    if team_abbr == '':
        return {
            'PREV_YR_Win%': 0,
            'PREV_YR_PTS/G': 0,
            'PREV_YR_OPTS/G': 0,
            'PREV_YR_SRS': 0,
            'PREV_YR_Pace': 0,
            'PREV_YR_ORtg': 0,
            'PREV_YR_DRtg': 0,
            'PREV_YR_NRtg': 0,
            'PREV_YR_Expected_Win%': 0
        }
    
    url = f"{BBREF_BASE}/teams/{team_abbr}/{season_year}.html"    
    soup = get_soup(url)
    summary = soup.find('div', {'data-template': 'Partials/Teams/Summary'})

    def team_stat(label: str) -> float:
        # Find the <strong> tag matching the BBRef label
        strong = summary.find('strong', text=lambda t: t and t.strip().rstrip(':') == label)
        if not strong:
            return 0.0
        raw = (strong.next_sibling or '').strip()
        value = raw.split('(')[0].strip()

        # Handle win-loss records
        if label in ('Record', 'Expected W-L'):
            match = re.search(r'(\d+)-(\d+)', value)
            if match:
                w, l = map(int, match.groups())
                total = w + l
                return round(w / total, 3) if total > 0 else 0.0
            return 0.0

        # Extract numeric metrics
        match = re.search(r'-?\d+\.?\d+', value)
        return float(match.group()) if match else 0.0

    # Explicit mapping like get_advanced_stats
    return {
        'PREV_YR_Win%': team_stat('Record'),
        'PREV_YR_PTS/G': team_stat('PTS/G'),
        'PREV_YR_OPTS/G': team_stat('Opp PTS/G'),
        'PREV_YR_SRS': team_stat('SRS'),
        'PREV_YR_Pace': team_stat('Pace'),
        'PREV_YR_ORtg': team_stat('Off Rtg'),
        'PREV_YR_DRtg': team_stat('Def Rtg'),
        'PREV_YR_NRtg': team_stat('Net Rtg'),
        'PREV_YR_Expected_Win%': team_stat('Expected W-L')
    }

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
        'COLLEGE_PER': adv_stat('per'),
        'COLLEGE_TS%': adv_stat('ts_pct'),
        'COLLEGE_3PAr': adv_stat('fg3a_per_fga_pct'),
        'COLLEGE_FTr': adv_stat('fta_per_fga_pct'),
        'COLLEGE_PProd': adv_stat('pprod'),
        'COLLEGE_ORB%': adv_stat('orb_pct'),
        'COLLEGE_DRB%': adv_stat('drb_pct'),
        'COLLEGE_TRB%': adv_stat('trb_pct'),
        'COLLEGE_AST%': adv_stat('ast_pct'),
        'COLLEGE_STL%': adv_stat('stl_pct'),
        'COLLEGE_BLK%': adv_stat('blk_pct'),
        'COLLEGE_TOV%': adv_stat('tov_pct'),
        'COLLEGE_USG%': adv_stat('usg_pct'),
        'COLLEGE_OWS': adv_stat('ows'),
        'COLLEGE_DWS': adv_stat('dws'),
        'COLLEGE_WS': adv_stat('ws'),
        'COLLEGE_WS/40': adv_stat('ws_per_40'),
        'COLLEGE_OBPM': adv_stat('obpm'),
        'COLLEGE_DBPM': adv_stat('dbpm'),
        'COLLEGE_BPM': adv_stat('bpm')
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
        'COLLEGE_FG/40': per40('fg_per_min'),
        'COLLEGE_FGA/40': per40('fga_per_min'),
        'COLLEGE_3P/40': per40('fg3_per_min'),
        'COLLEGE_3PA/40': per40('fg3a_per_min'),
        'COLLEGE_FT/40': per40('ft_per_min'),
        'COLLEGE_FTA/40': per40('fta_per_min'),
        'COLLEGE_ORB/40': per40('orb_per_min'),
        'COLLEGE_DRB/40': per40('drb_per_min'),
        'COLLEGE_TRB/40': per40('trb_per_min'),
        'COLLEGE_AST/40': per40('ast_per_min'),
        'COLLEGE_STL/40': per40('stl_per_min'),
        'COLLEGE_BLK/40': per40('blk_per_min'),
        'COLLEGE_TOV/40': per40('tov_per_min'),
        'COLLEGE_PF/40': per40('pf_per_min'),
        'COLLEGE_PTS/40': per40('pts_per_min')
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
        'COLLEGE_FG/100': per100('fg_per_poss'),
        'COLLEGE_FGA/100': per100('fga_per_poss'),
        'COLLEGE_3P/100': per100('fg3_per_poss'),
        'COLLEGE_3PA/100': per100('fg3a_per_poss'),
        'COLLEGE_FT/100': per100('ft_per_poss'),
        'COLLEGE_FTA/100': per100('fta_per_poss'),
        'COLLEGE_ORB/100': per100('orb_per_poss'),
        'COLLEGE_DRB/100': per100('drb_per_poss'),
        'COLLEGE_TRB/100': per100('trb_per_poss'),
        'COLLEGE_AST/100': per100('ast_per_poss'),
        'COLLEGE_STL/100': per100('stl_per_poss'),
        'COLLEGE_BLK/100': per100('blk_per_poss'),
        'COLLEGE_TOV/100': per100('tov_per_poss'),
        'COLLEGE_PF/100': per100('pf_per_poss'),
        'COLLEGE_PTS/100': per100('pts_per_poss'),
        'COLLEGE_ORtg': per100('off_rtg'),
        'COLLEGE_DRtg': per100('def_rtg')
    }

def get_college_season_summary(soup: BeautifulSoup) -> dict:
    """
    Parse the college team page summary and return a dict of season metrics
    prefixed with 'COLLEGE_'. Returns {} if no summary found.
    """
    summary = soup.find('div', {'data-template': 'Partials/Teams/Summary'})
    if not summary:
        return {}

    def col_stat(label: str) -> float:
        # look through every <strong> … </strong> in that summary
        strong = None
        for tag in summary.find_all('strong'):
            # strip() cleans whitespace and rstrip(':') drops the colon
            if tag.get_text(strip=True).rstrip(':') == label:
                strong = tag
                break

        if not strong:
            return 0.0

        # the numeric text is usually in strong.next_sibling,
        # but sometimes wrapped in another tag—so handle both:
        raw = ''
        sib = strong.next_sibling
        if isinstance(sib, str):
            raw = sib.strip()
        elif sib:
            raw = sib.get_text(strip=True)

        # drop any parenthetical notes like "(18th of 363)"
        val = raw.split('(')[0].strip()

        if label == 'Record':
            m = re.search(r'(\d+)-(\d+)', val)
            if m:
                w, l = map(int, m.groups())
                return round(w / (w + l), 3) if (w + l) > 0 else 0.0
            return 0.0

        m = re.search(r'-?\d+\.?\d+', val)
        return float(m.group()) if m else 0.0

    return {
        'COLLEGE_TEAM_Win%':    col_stat('Record'),
        'COLLEGE_TEAM_PTS/G':     col_stat('PS/G'),
        'COLLEGE_TEAM_PTSA/G':     col_stat('PA/G'),
        'COLLEGE_TEAM_SRS':      col_stat('SRS'),
        'COLLEGE_TEAM_SOS':      col_stat('SOS'),
        'COLLEGE_TEAM_ORtg':  col_stat('ORtg'),
        'COLLEGE_TEAM_DRtg':  col_stat('DRtg'),
    }

def get_nba_career_stats(career_tr, nba_seasons) -> dict:
    """
    Parse the career <tr> row and return a dict of career per-game stats
    from 'g' through 'pts_per_g', plus the total number of seasons under 'seasons'.
    Missing or empty cells are treated as 0.0.
    """
    def stat(key: str) -> float:
        cell = career_tr.find('td', {'data-stat': key})
        text = cell.get_text(strip=True) if cell else ''
        return float(text) if text else 0.0

    return {
        'NBA_seasons': nba_seasons,
        'NBA_G':     stat('games'),
        'NBA_GS':    stat('games_started'),
        'NBA_MP/G':  stat('mp_per_g'),
        'NBA_FG/G':  stat('fg_per_g'),
        'NBA_FGA/G': stat('fga_per_g'),
        'NBA_FG%':   stat('fg_pct'),
        'NBA_3P/G':  stat('fg3_per_g'),
        'NBA_3PA/G': stat('fg3a_per_g'),
        'NBA_3P%':   stat('fg3_pct'),
        'NBA_2P/G':  stat('fg2_per_g'),
        'NBA_2PA/G': stat('fg2a_per_g'),
        'NBA_2P%':   stat('fg2_pct'),
        'NBA_eFG%':  stat('efg_pct'),
        'NBA_FT/G':  stat('ft_per_g'),
        'NBA_FTA/G': stat('fta_per_g'),
        'NBA_FT%':   stat('ft_pct'),
        'NBA_ORB/G': stat('orb_per_g'),
        'NBA_DRB/G': stat('drb_per_g'),
        'NBA_TRB/G': stat('trb_per_g'),
        'NBA_AST/G': stat('ast_per_g'),
        'NBA_STL/G': stat('stl_per_g'),
        'NBA_BLK/G': stat('blk_per_g'),
        'NBA_TOV/G': stat('tov_per_g'),
        'NBA_PF/G':  stat('pf_per_g'),
        'NBA_PTS/G': stat('pts_per_g'),
    }