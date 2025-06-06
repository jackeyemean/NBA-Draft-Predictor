import os
import logging
from scraper import get_draft_picks, process_player, write_record

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

def main():
    start_year, end_year = 2008, 2024
    data_dir = "raw-data"
    os.makedirs(data_dir, exist_ok=True)

    # build filename in format: "drafts_2008_2024.csv"
    filename = f"drafts-{start_year}-to-{end_year}.csv"
    output_file = os.path.join(data_dir, filename)
    header_written = False

    for year in range(start_year, end_year + 1):
        picks = get_draft_picks(year)
        for pick in picks:
            record = process_player(pick, year)
            if record:
                header_written = write_record(record, output_file, header_written)

    logging.info("Finished scraping all years.")

if __name__ == "__main__":
    main()
