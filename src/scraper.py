from network import get_soup
from extractors import extract_height_weight, extract_sr_cbb_link, get_stat
from feature_engineering import engineer_features_full
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)
BBREF_BASE = 'https://www.basketball-reference.com'

def scrape_bbref_meta(player_url):
    soup = get_soup(player_url)
    if soup is None:
        return None, 0, None, None

    relatives = 0
    for strong in soup.find_all('strong'):
        if 'Relatives' in strong.text:
            p = strong.find_parent('p')
            if p:
                relatives = len(p.find_all('a'))
            break

    birth_tag = soup.find('span', id='necro-birth')
    birth_date = birth_tag.get('data-birth') if birth_tag and birth_tag.has_attr('data-birth') else None
    cbb_url = extract_sr_cbb_link(soup)
    return '', relatives, cbb_url, birth_date

def scrape_cbbref_stats_and_meta(cbb_url, nba_team, college):
    soup = get_soup(cbb_url)
    if soup is None:
        return 0, 0, None, 0, pd.DataFrame()

    height, weight = extract_height_weight(soup)
    per_game = soup.find('table', id='players_per_game')
    if not per_game:
        return height, weight, None, 0, pd.DataFrame()

    rows = per_game.find('tbody').find_all('tr')
    rows = [r for r in rows if not r.get('class') or 'thead' not in r.get('class')]
    if not rows:
        return height, weight, None, 0, pd.DataFrame()
    last_pg = rows[-1]

    pos_cell = last_pg.find('td', {'data-stat': 'pos'})
    pos = pos_cell.text.strip() if pos_cell else None

    last_stats = {
        'G': get_stat(last_pg, 'games'),
        'GS%': round(get_stat(last_pg, 'games_started') / get_stat(last_pg, 'games') * 100, 2)
        if get_stat(last_pg, 'games') > 0 else 0.0,
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
        'Height': height,
        'Weight': weight,
        'POS': pos or '',
        'NBA Team': nba_team or '',
        'College': college or ''
    }

    from extractors import get_advanced_stats, get_per40_stats, get_per100_stats
    last_stats.update(get_advanced_stats(soup))
    last_stats.update(get_per40_stats(soup))
    last_stats.update(get_per100_stats(soup))

    df = pd.DataFrame([last_stats])
    enriched = engineer_features_full(df)
    return height, weight, pos, len(rows), enriched

def scrape_draft_year(year: int, output_file: str, header_written: bool) -> bool:
    logger.info(f"Scraping draft year {year}")
    url = f"{BBREF_BASE}/draft/NBA_{year}.html"
    soup = get_soup(url)
    if soup is None:
        logger.warning(f"Skipping draft year {year}")
        return header_written

    table = soup.find('table', id='stats')
    if not table:
        logger.error(f"No draft table found for {year}")
        return header_written

    def get_cell(row, stat):
        cell = row.find('td', {'data-stat': stat})
        return cell.text.strip() if cell else None

    for row in table.find('tbody').find_all('tr'):
        if row.get('class') and 'thead' in row.get('class'):
            continue

        pick = get_cell(row, 'pick_overall')
        team = get_cell(row, 'team_id')
        name = get_cell(row, 'player')
        college = get_cell(row, 'college_name')

        a_tag = row.find('td', {'data-stat': 'player'}).find('a')
        if not a_tag:
            continue
        bbref_url = BBREF_BASE + a_tag['href']

        shoots, relatives, cbb_url, birth_date = scrape_bbref_meta(bbref_url)
        if not cbb_url:
            logger.info(f"Skipping {name} – no college stats link")
            continue

        age = 0.0
        if birth_date:
            try:
                birth_dt = datetime.strptime(birth_date, "%Y-%m-%d")
                draft_dt = datetime(year, 6, 25)
                age = round((draft_dt - birth_dt).days / 365.25, 2)
            except Exception as e:
                logger.warning(f"Failed to parse age for {name}: {e}")

        height, weight, pos, seasons, enriched_df = scrape_cbbref_stats_and_meta(cbb_url, team, college)
        if enriched_df is None or enriched_df.empty:
            continue

        stats = enriched_df.iloc[0].to_dict()

        record = {
            'Draft Year': year,
            'Pick Number': int(pick) if pick and pick.isdigit() else 0,
            'NBA Team': team or '',
            'Name': name or '',
            'Age': age,
            'College': college or '',
            'Height': height,
            'Weight': weight,
            'NBA Relatives': relatives,
            'Seasons Played (College)': seasons,
            'POS': pos or ''
        }
        record.update(stats)

        logger.debug(f"{name} – Raw stats: {stats}")
        logger.debug(f"{name} – Engineered features: {stats}")

        pd.DataFrame([record]).to_csv(output_file, mode='a', header=not header_written, index=False)
        header_written = True

    logger.info(f"Finished writing data for {year}")
    return header_written
