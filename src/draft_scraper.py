import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup, Comment
import pandas as pd
import time
import re

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

BBREF_BASE = 'https://www.basketball-reference.com'
CBBREF_BASE = 'https://www.sports-reference.com/cbb'

# Set up a Session with retries and a custom User-Agent, plus realistic browser headers
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
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
session.mount('https://', HTTPAdapter(max_retries=retries))
session.mount('http://', HTTPAdapter(max_retries=retries))

REQUEST_DELAY = 3.0

def polite_sleep():
    logger.debug(f"Sleeping for {REQUEST_DELAY:.1f}s to respect rate limit")
    time.sleep(REQUEST_DELAY)

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
    polite_sleep()
    return soup

def extract_height_weight(soup):
    text = soup.get_text()
    match = re.search(r'(\d+-\d+),\s*(\d+)lb', text)
    if match:
        return match.group(1), match.group(2)
    return None, None

def scrape_cbbref_stats_and_meta(name):
    formatted_name = name.lower().replace('.', '').replace("'", '').replace(' ', '-')
    url = f"{CBBREF_BASE}/players/{formatted_name}-1.html"
    soup = get_soup(url)
    if soup is None:
        return None, None, None, None, {}

    height, weight = extract_height_weight(soup)

    per_game = soup.find('table', id='players_per_game')
    totals = soup.find('table', id='players_totals')
    if not per_game or not totals:
        return height, weight, None, None, {}

    rows = per_game.find('tbody').find_all('tr')
    rows = [r for r in rows if not r.get('class') or 'thead' not in r.get('class')]
    last_pg = rows[-1]

    def get_stat(row, stat):
        cell = row.find('td', {'data-stat': stat})
        return cell.text.strip() if cell else None

    pos = get_stat(last_pg, 'pos')
    last_stats = {
        'G': get_stat(last_pg, 'games'),
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
        'ORB': get_stat(last_pg, 'orb_per_g'),
        'TRB': get_stat(last_pg, 'trb_per_g'),
        'AST': get_stat(last_pg, 'ast_per_g'),
        'STL': get_stat(last_pg, 'stl_per_g'),
        'BLK': get_stat(last_pg, 'blk_per_g'),
        'TOV': get_stat(last_pg, 'tov_per_g'),
        'PF': get_stat(last_pg, 'pf_per_g'),
        'PTS': get_stat(last_pg, 'pts_per_g'),
    }

    return height, weight, pos, len(rows), last_stats

def scrape_bbref_meta(player_url):
    soup = get_soup(player_url)
    if soup is None:
        return None, 0

    shoots = None
    for strong in soup.find_all('strong'):
        if 'Shoots' in strong.text:
            shoots = strong.next_sibling.strip()
            break

    relatives = 0
    for strong in soup.find_all('strong'):
        if 'Relatives' in strong.text:
            p = strong.find_parent('p')
            if p:
                relatives = len(p.find_all('a'))
            break

    return shoots, relatives

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
            continue

        pick = get_cell(row, 'pick_overall')
        team = get_cell(row, 'team_id')
        name = get_cell(row, 'player')
        college = get_cell(row, 'college_name')
        age = get_cell(row, 'age')

        player_td = row.find('td', {'data-stat': 'player'})
        a_tag = player_td.find('a') if player_td else None
        if not a_tag:
            continue

        bbref_url = BBREF_BASE + a_tag['href']

        shoots, relatives = scrape_bbref_meta(bbref_url)
        height, weight, pos, seasons, stats = scrape_cbbref_stats_and_meta(name)

        if not stats:
            logger.info(f"Skipping {name} – no college stats")
            continue

        record = {
            'Draft Year': year,
            'Pick Number': pick,
            'NBA Team': team,
            'Name': name,
            'Age': age,
            'College': college,
            'Height': height,
            'Weight': weight,
            'Dominant Hand': shoots,
            'NBA Relatives': relatives,
            'Seasons Played (College)': seasons,
            'POS': pos,
            'MPG': stats.get('MP'),
            'PPG': stats.get('PTS'),
            'RPG': stats.get('TRB'),
            'APG': stats.get('AST'),
        }
        record.update(stats)

        df = pd.DataFrame([record])
        df.to_csv(output_file, mode='a', header=not header_written, index=False)
        header_written = True

    logger.info(f"Finished writing data for {year}")
    return header_written

def main():
    output_file = 'draft_prospects_2010_2022.csv'
    header_written = False

    for yr in range(2010, 2023):
        header_written = scrape_draft_year(yr, output_file, header_written)

if __name__ == "__main__":
    main()
