#!/usr/bin/env python3
"""Deal Lab - Score real estate deals and generate reports."""

import argparse
import sys

from ingest import read_listings, filter_by_zip
from scorer import score_listings
from output_csv import write_csv
from report import generate_report

CSV_OUTPUT = "scored_listings.csv"
HTML_OUTPUT = "deal_report.html"


def main():
    parser = argparse.ArgumentParser(
        description="Score real estate deals and generate reports."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="listings.csv",
        help="CSV file with listings (default: listings.csv)",
    )
    parser.add_argument(
        "--zip",
        dest="zip_codes",
        default=None,
        help="Filter to specific zip codes, comma-separated (e.g. 94601,94577)",
    )
    args = parser.parse_args()

    print(f"Reading listings from {args.input}...")
    listings = read_listings(args.input)
    if not listings:
        print(f"No listings found in {args.input}.")
        sys.exit(1)
    print(f"Found {len(listings)} listings.")

    if args.zip_codes:
        listings = filter_by_zip(
            listings, args.zip_codes.split(",")
        )
        if not listings:
            print("No listings matched those zip codes.")
            sys.exit(1)

    print()
    results = score_listings(listings)

    write_csv(results, CSV_OUTPUT)
    print(f"\nWrote {CSV_OUTPUT}")

    generate_report(results, HTML_OUTPUT)
    print(f"Wrote {HTML_OUTPUT}")
    print(f"\nOpen {HTML_OUTPUT} in your browser to see the report.")


if __name__ == "__main__":
    main()
