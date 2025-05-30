import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import pandas as pd
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = 'https://www.basketball-reference.com'

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
    total=3,               # fail fast
    backoff_factor=1,      # exponential backoff: 1s, 2s, 4s
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
session.mount('https://', HTTPAdapter(max_retries=retries))
session.mount('http://', HTTPAdapter(max_retries=retries))

# Fixed rate limit: exactly 20 requests/minute => 3s per request
REQUEST_DELAY = 3.0

def polite_sleep():
    """Sleep fixed interval to respect 20 req/min rate limit."""
    logger.debug(f"Sleeping for {REQUEST_DELAY:.1f}s to respect rate limit")
    time.sleep(REQUEST_DELAY)


def get_soup(url):
    """Fetch page with retries and return BeautifulSoup."""
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


def normalize_pos(pos):
    if 'G' in pos:
        return 'G'
    if 'F' in pos:
        return 'F'
    if 'C' in pos:
        return 'C'
    return pos


def scrape_player_page(player_url):
    """Scrape dominant hand, NBA relatives count, seasons, and last-season college stats."""
    logger.debug(f"Scraping player page: {player_url}")
    soup = get_soup(player_url)
    if soup is None:
        return None, 0, 0, {}

    # Dominant hand
    shoots = None
    for strong in soup.find_all('strong'):
        if 'Shoots' in strong.text:
            shoots = strong.next_sibling.strip()
            break

    # NBA relatives count
    relatives = 0
    for strong in soup.find_all('strong'):
        if 'Relatives' in strong.text:
            p = strong.find_parent('p')
            if p:
                relatives = len(p.find_all('a'))
            break

    # College per-game stats
    col_table = soup.find('table', id='per_game-college')
    if col_table:
        rows = [r for r in col_table.find('tbody').find_all('tr') if 'class' not in r.attrs]
        seasons = len(rows)
        last = rows[-1]
        def get_stat(stat):
            cell = last.find('td', {'data-stat': stat})
            return cell.text if cell else None
        last_stats = {
            'G': get_stat('g'),
            'MP': get_stat('mp_per_g'),
            'FG': get_stat('fg_per_g'),
            'FGA': get_stat('fga_per_g'),
            'FG%': get_stat('fg_pct'),
            '3P': get_stat('fg3_per_g'),
            '3PA': get_stat('fg3a_per_g'),
            '3P%': get_stat('fg3_pct'),
            'FT': get_stat('ft_per_g'),
            'FTA': get_stat('fta_per_g'),
            'FT%': get_stat('ft_pct'),
            'ORB': get_stat('orb_per_g'),
            'TRB': get_stat('trb_per_g'),
            'AST': get_stat('ast_per_g'),
            'STL': get_stat('stl_per_g'),
            'BLK': get_stat('blk_per_g'),
            'TOV': get_stat('tov_per_g'),
            'PF': get_stat('pf_per_g'),
            'PTS': get_stat('pts_per_g'),
        }
    else:
        seasons = 0
        last_stats = {}
        logger.warning(f"No per_game-college table found on player page: {player_url}")

    return shoots, relatives, seasons, last_stats


def scrape_draft_year(year: int):
    """Scrape draft prospects for a given year; skip on 429 errors."""
    logger.info(f"Scraping draft year {year}")

    url = f"{BASE_URL}/draft/NBA_{year}.html"
    soup = get_soup(url)
    if soup is None:
        logger.warning(f"Skipping draft year {year} due to 429 error")
        return []

    table = soup.find('table', id='stats')
    if not table:
        logger.error(f"No draft table found for {year}")
        return []

    def get_cell(row, stat: str):
        cell = row.find('td', {'data-stat': stat})
        return cell.text.strip() if cell else None

    data = []
    for row in table.find('tbody').find_all('tr'):
        if row.get('class') and 'thead' in row.get('class'):
            continue

        pick    = get_cell(row, 'pick_overall')
        team    = get_cell(row, 'team_id')
        name    = get_cell(row, 'player')
        college = get_cell(row, 'college_name')
        age     = get_cell(row, 'age')
        pos     = get_cell(row, 'pos')
        height  = get_cell(row, 'height')
        weight  = get_cell(row, 'weight')

        rel_url = row.find('td', {'data-stat': 'player'}).find('a')['href']
        full_url = BASE_URL + rel_url
        shoots, relatives, seasons, stats = scrape_player_page(full_url)
        if shoots is None and relatives == 0 and seasons == 0 and not stats:
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
            'POS': normalize_pos(pos) if pos else None,
        }
        record.update(stats)
        record['MPG'] = stats.get('MP')
        record['PPG'] = stats.get('PTS')
        record['RPG'] = stats.get('TRB')
        record['APG'] = stats.get('AST')

        data.append(record)

    logger.info(f"Year {year}: scraped {len(data)} players")
    return data


def main():
    all_data = []
    for yr in range(2010, 2023):
        all_data.extend(scrape_draft_year(yr))
    df = pd.DataFrame(all_data)
    df.to_csv('draft_prospects_2010_2022.csv', index=False)
    logger.info("Saved data to draft_prospects_2010_2022.csv")


if __name__ == "__main__":
    main()
