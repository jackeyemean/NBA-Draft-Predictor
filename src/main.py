import logging
from scraper import scrape_draft_year

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

def main():
    output_file = "output.csv"
    header_written = False
    for yr in range(2018, 2021):
        header_written = scrape_draft_year(yr, output_file, header_written)

if __name__ == "__main__":
    main()
