import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup, Comment
import time
import logging

logger = logging.getLogger(__name__)

REQUEST_DELAY = 2  # seconds between requests to avoid rate limiting

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

# Retry setup: retry up to 3 times on 429/500/502/503/504
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
session.mount('https://', HTTPAdapter(max_retries=retries))
session.mount('http://', HTTPAdapter(max_retries=retries))

def polite_sleep():
    logger.debug(f"{REQUEST_DELAY:.1f}s sleep")
    time.sleep(REQUEST_DELAY)

def get_soup(url):
    """
    Fetch a URL, parse HTML (including tables inside comments), 
    and return a BeautifulSoup object. Returns None on HTTP 429.
    """
    logger.debug(f"Fetching URL: {url}")
    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response and e.response.status_code == 429:
            logger.warning(f"429 Too Many Requests: {url}")
            return None
        else:
            raise
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Some tables are wrapped in HTML comments; extract them
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if 'table' in comment:
            soup.append(BeautifulSoup(comment, 'html.parser'))
    polite_sleep()
    return soup
