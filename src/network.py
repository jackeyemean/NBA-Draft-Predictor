import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup, Comment
import time
import logging

logger = logging.getLogger(__name__)

REQUEST_DELAY = 1.5

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

def polite_sleep():
    logger.debug(f"{REQUEST_DELAY:.1f}s sleep (20 req/min limit)")
    time.sleep(REQUEST_DELAY)

def get_soup(url):
    logger.debug(f"Fetching URL: {url}")
    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else None
        if status == 429:
            logger.warning(f"429 Too Many Requests: {url}")
            return None
        else:
            raise
    soup = BeautifulSoup(resp.text, 'html.parser')
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if 'table' in comment:
            soup.append(BeautifulSoup(comment, 'html.parser'))
    polite_sleep()
    return soup
