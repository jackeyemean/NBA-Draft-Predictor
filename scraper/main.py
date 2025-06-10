import os
import logging
import csv
from scraper import get_draft_picks, process_player, write_record

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

def main():
    start_year, end_year = 2011, 2024
    data_dir = "raw-data"
    os.makedirs(data_dir, exist_ok=True)

    # build filename in format: "drafts_2008_2024.csv"
    filename = f"drafts-{start_year}-to-{end_year}.csv"
    output_file = os.path.join(data_dir, filename)
    header_written = False

    error_log = []

    for year in range(start_year, end_year + 1):
        picks = get_draft_picks(year)
        for pick in picks:
            try:
                record = process_player(pick, year)
            except Exception as e:
                error_log.append((year, pick['name'], str(e)))
                record = {
                    'Draft Year': year,
                    'Pick Number': pick['pick'],
                    'Name'       : pick['name'],
                    'NBA Team'   : pick['team'],
                    'College'    : pick['college']
                }

            # write it (whether full or minimal)
            if record:
                header_written = write_record(record, output_file, header_written)

    # dump all the failures afterwards
    with open('failed_players.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['year', 'name', 'error'])
        writer.writerows(error_log)

    logging.info("Finished scraping all years.")

if __name__ == "__main__":
    main()
