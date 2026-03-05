"""Pull active listings from Redfin by zip code."""

import csv
import io
import re
import time
from typing import List, Optional

import httpx

from models import Listing, safe_float, safe_int

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.redfin.com/",
}


def _get_region_id(zip_code: str) -> Optional[str]:
    """Get Redfin's internal region_id for a zip code."""
    client = httpx.Client(
        headers=HEADERS, follow_redirects=True, timeout=15
    )
    resp = client.get(f"https://www.redfin.com/zipcode/{zip_code}")
    if resp.status_code != 200:
        return None

    match = re.search(r'region_id["=:]+(\d+)', resp.text)
    return match.group(1) if match else None


def _download_csv(region_id: str, num_homes: int = 20) -> str:
    """Download listing CSV from Redfin."""
    client = httpx.Client(
        headers=HEADERS, follow_redirects=True, timeout=30
    )
    resp = client.get(
        "https://www.redfin.com/stingray/api/gis-csv",
        params={
            "al": "1",
            "region_id": region_id,
            "region_type": "2",
            "status": "9",
            "uipt": "1,2,3",
            "num_homes": str(num_homes),
            "ord": "redfin-recommended-asc",
            "v": "8",
        },
    )
    resp.raise_for_status()
    return resp.text


def _parse_csv_text(csv_text: str) -> List[Listing]:
    """Parse Redfin CSV text into Listing objects."""
    listings: List[Listing] = []
    reader = csv.DictReader(io.StringIO(csv_text))

    for row in reader:
        price = safe_float(row.get("PRICE", ""))
        address = (row.get("ADDRESS") or "").strip()
        if not price or not address:
            continue

        listings.append(
            Listing(
                address=address,
                city=(row.get("CITY") or "").strip(),
                price=price,
                beds=safe_float(row.get("BEDS", "")),
                baths=safe_float(row.get("BATHS", "")),
                sqft=safe_float(row.get("SQUARE FEET", "")),
                link=(row.get("URL (REDFIN LINK)") or "").strip(),
                notes="",
                year_built=safe_int(row.get("YEAR BUILT", "")),
                lot_size=(row.get("LOT SIZE") or "").strip() or None,
                days_on_market=safe_int(row.get("DAYS ON MARKET", "")),
                hoa_monthly=safe_float(row.get("HOA/MONTH", "")),
                price_per_sqft=safe_float(row.get("$/SQUARE FEET", "")),
                property_type=(
                    row.get("PROPERTY TYPE") or ""
                ).strip()
                or None,
                state=(row.get("STATE OR PROVINCE") or "").strip() or None,
                zip_code=(
                    row.get("ZIP OR POSTAL CODE") or ""
                ).strip()
                or None,
                source="redfin",
            )
        )

    return listings


def fetch_listings(zip_code: str, max_listings: int = 20) -> List[Listing]:
    """Fetch active listings from Redfin for a zip code."""
    print(f"Looking up zip code {zip_code} on Redfin...")
    region_id = _get_region_id(zip_code)
    if not region_id:
        print(f"Could not find zip code {zip_code} on Redfin.")
        return []

    time.sleep(1)  # Be polite

    print(f"Pulling listings...")
    csv_text = _download_csv(region_id, num_homes=max_listings)
    listings = _parse_csv_text(csv_text)
    print(f"Found {len(listings)} active listings in {zip_code}.")
    return listings
