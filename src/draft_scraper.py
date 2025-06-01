# === Imports ===
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup, Comment
import pandas as pd
import time
import re
from datetime import datetime

# === Logging Configuration ===
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# === Constants ===
BBREF_BASE = 'https://www.basketball-reference.com'
REQUEST_DELAY = 1.5  # Delay between requests to respect rate limits

# === Setup HTTP Session with Retries and Headers ===
session = requests.Session()
session.headers.update({
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/115.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.basketball-reference.com/',
    'Connection': 'keep-alive'
})
retries = Retry(
    total=3,  # Retry failed requests up to 3 times
    backoff_factor=1,  # Wait 1s, 2s, 4s... between retries
    status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
    allowed_methods=["GET"]
)
session.mount('https://', HTTPAdapter(max_retries=retries))
session.mount('http://', HTTPAdapter(max_retries=retries))

# === Respectful Delay for Rate Limits ===
def polite_sleep():
    logger.debug(f"{REQUEST_DELAY:.1f}s sleep (20 req/min limit for bbref and sports ref)")
    time.sleep(REQUEST_DELAY)

# === Request URL and Return Parsed BeautifulSoup (includes commented-out tables) ===
def get_soup(url):
    logger.debug(f"Fetching URL: {url}")
    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else None
        if status == 429:
            logger.warning(f"429 Too Many Requests for URL: {url} – skipping this URL")
            return None
        else:
            raise
    logger.debug(f"Received response {resp.status_code} for URL: {url}")
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Append commented-out HTML (e.g., hidden tables) to the soup
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if 'table' in comment:
            soup.append(BeautifulSoup(comment, 'html.parser'))

    polite_sleep()
    return soup

# === Extract Player Height and Weight from Page Text ===
def extract_height_weight(soup):
    text = soup.get_text()
    match = re.search(r'\((\d{3})cm,\s*(\d{2,3})kg\)', text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0  # Return zeros if height/weight not found

# === Extract Final-Season Advanced College Stats from SR/CBB Page ===
def get_advanced_stats(soup):
    adv_table = soup.find('table', id='players_advanced')
    if not adv_table:
        return {}

    # Filter valid rows (ignore header repeats)
    rows = adv_table.find('tbody').find_all('tr')
    rows = [r for r in rows if not r.get('class') or 'thead' not in r.get('class')]
    if not rows:
        return {}

    last_row = rows[-1]  # Use last season row

    def adv_stat(stat):
        cell = last_row.find('td', {'data-stat': stat})
        return float(cell.text.strip()) if cell and cell.text.strip() else 0.0

    # Return a dictionary of desired advanced stats
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

# === Extract Final-Season Per-40-Minute Stats ===
def get_per40_stats(soup):
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
        'PTS/40': per40('pts_per_min'),
    }

# === Extract Final-Season Per-100-Possession Stats ===
def get_per100_stats(soup):
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
        'DRtg': per100('def_rtg'),
    }

# === Scrape Height, Weight, Position, and Stats from SR/CBB Page ===
def scrape_cbbref_stats_and_meta(cbb_url):
    soup = get_soup(cbb_url)
    if soup is None:
        return 0, 0, None, 0, {}

    height, weight = extract_height_weight(soup)

    # Find basic stat tables
    per_game = soup.find('table', id='players_per_game')
    totals = soup.find('table', id='players_totals')
    if not per_game or not totals:
        return height, weight, None, 0, {}

    # Get last college season row
    rows = per_game.find('tbody').find_all('tr')
    rows = [r for r in rows if not r.get('class') or 'thead' not in r.get('class')]
    if not rows:
        return height, weight, None, 0, {}
    last_pg = rows[-1]

    def get_stat(row, stat):
        cell = row.find('td', {'data-stat': stat})
        return float(cell.text.strip()) if cell and cell.text.strip() else 0.0

    # Extract position
    pos_cell = last_pg.find('td', {'data-stat': 'pos'})
    pos = pos_cell.text.strip() if pos_cell else None

    # Per-game stat dictionary
    last_stats = {
        'G': get_stat(last_pg, 'games'),
        'GS%': round(get_stat(last_pg, 'games_started') / get_stat(last_pg, 'games') * 100, 2) if get_stat(last_pg, 'games') > 0 else 0.0,
        'MP': get_stat(last_pg, 'mp_per_g'),
        'FG': get_stat(last_pg, 'fg_per_g'),
        'FGA': get_stat(last_pg, 'fga_per_g'),
        'FG%': get_stat(last_pg, 'fg_pct'),
        '3P': get_stat(last_pg, 'fg3_per_g'),
        '3PA': get_stat(last_pg, 'fg3a_per_g'),
        '3P%': get_stat(last_pg, 'fg3_pct'),
        'FT': get_stat(last_pg, 'ft_per_g'),
        'FTA': get_stat(last_pg, 'fta_per_g'),
        'FT%': get_stat(last_pg, 'ft_pct'),
        'DRB': get_stat(last_pg, 'drb_per_g'),
        'ORB': get_stat(last_pg, 'orb_per_g'),
        'TRB': get_stat(last_pg, 'trb_per_g'),
        'AST': get_stat(last_pg, 'ast_per_g'),
        'STL': get_stat(last_pg, 'stl_per_g'),
        'BLK': get_stat(last_pg, 'blk_per_g'),
        'TOV': get_stat(last_pg, 'tov_per_g'),
        'PF': get_stat(last_pg, 'pf_per_g'),
        'PTS': get_stat(last_pg, 'pts_per_g'),
    }

    # Merge advanced stats
    advanced = get_advanced_stats(soup)
    last_stats.update(advanced)

    # Merge per-40-minute stats
    per40 = get_per40_stats(soup)
    last_stats.update(per40)

    # Merge per-100-possession stats
    per100 = get_per100_stats(soup)
    last_stats.update(per100)

    return height, weight, pos, len(rows), last_stats

# === Extract SR/CBB College Stats URL from BBRef Page ===
def extract_sr_cbb_link(soup):
    anchor = soup.find('a', string=lambda text: text and 'More College Stats on SR/CBB' in text)
    if anchor and 'href' in anchor.attrs:
        return anchor['href'].split('?')[0]
    return None

# === Scrape Meta Info from BBRef Player Page (Handedness, Relatives, Birth Date, SR/CBB Link) ===
def scrape_bbref_meta(player_url):
    soup = get_soup(player_url)
    if soup is None:
        return None, 0, None, None

    # Count NBA relatives
    relatives = 0
    for strong in soup.find_all('strong'):
        if 'Relatives' in strong.text:
            p = strong.find_parent('p')
            if p:
                relatives = len(p.find_all('a'))
            break

    # Get birthdate
    birth_tag = soup.find('span', id='necro-birth')
    birth_date = birth_tag.get('data-birth') if birth_tag and birth_tag.has_attr('data-birth') else None

    # Get SR/CBB link
    cbb_url = extract_sr_cbb_link(soup)
    return shoots, relatives, cbb_url, birth_date

# === Scrape Entire Draft Class and Write to CSV ===
def scrape_draft_year(year: int, output_file: str, header_written: bool) -> bool:
    logger.info(f"Scraping draft year {year}")
    url = f"{BBREF_BASE}/draft/NBA_{year}.html"
    soup = get_soup(url)
    if soup is None:
        logger.warning(f"Skipping draft year {year} due to 429 error")
        return header_written

    table = soup.find('table', id='stats')
    if not table:
        logger.error(f"No draft table found for {year}")
        return header_written

    def get_cell(row, stat: str):
        cell = row.find('td', {'data-stat': stat})
        return cell.text.strip() if cell else None

    for row in table.find('tbody').find_all('tr'):
        if row.get('class') and 'thead' in row.get('class'):
            continue  # skip header rows

        # Extract basic draft info
        pick = get_cell(row, 'pick_overall')
        team = get_cell(row, 'team_id')
        name = get_cell(row, 'player')
        college = get_cell(row, 'college_name')

        # Get player profile link
        player_td = row.find('td', {'data-stat': 'player'})
        a_tag = player_td.find('a') if player_td else None
        if not a_tag:
            continue
        bbref_url = BBREF_BASE + a_tag['href']

        # Scrape metadata
        shoots, relatives, cbb_url, birth_date = scrape_bbref_meta(bbref_url)
        if not cbb_url:
            logger.info(f"Skipping {name} – no college stats link")
            continue

        # Calculate age at draft day
        age = 0.0
        if birth_date:
            try:
                birth_dt = datetime.strptime(birth_date, "%Y-%m-%d")
                draft_dt = datetime(year, 6, 25)
                age = round((draft_dt - birth_dt).days / 365.25, 2)
            except Exception as e:
                logger.warning(f"Failed to parse age for {name}: {e}")

        # Scrape stats from SR/CBB
        height, weight, pos, seasons, stats = scrape_cbbref_stats_and_meta(cbb_url)
        if not stats:
            logger.info(f"Skipping {name} – no college stats")
            continue

        # Build and write record
        record = {
            'Draft Year': year,
            'Pick Number': int(pick) if pick and pick.isdigit() else 0,
            'NBA Team': team or '',
            'Name': name or '',
            'Age': age,
            'College': college or '',
            'Height': height,
            'Weight': weight,
            'Dominant Hand': shoots or '',
            'NBA Relatives': relatives,
            'Seasons Played (College)': seasons,
            'POS': pos or ''
        }
        record.update(stats)

        df = pd.DataFrame([record])
        df.to_csv(output_file, mode='a', header=not header_written, index=False)
        header_written = True

    logger.info(f"Finished writing data for {year}")
    return header_written

# === Entry Point ===
def main():
    output_file = 'draft_prospects_2011.csv'
    header_written = False
    for yr in range(2011, 2012):  # Can adjust range for multiple years
        header_written = scrape_draft_year(yr, output_file, header_written)

if __name__ == "__main__":
    main()
