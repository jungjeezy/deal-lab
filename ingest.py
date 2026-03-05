import csv
from typing import List

from models import Listing, safe_float, safe_int

# Columns that only appear in Redfin exports
REDFIN_SENTINEL_COLUMNS = {"SALE TYPE", "URL (REDFIN LINK)", "MLS#"}


def detect_redfin(path: str) -> bool:
    """Peek at headers to decide if this is a Redfin export."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        headers = set(next(reader, []))
    return bool(headers & REDFIN_SENTINEL_COLUMNS)


def read_redfin_csv(path: str) -> List[Listing]:
    """Read a Redfin CSV export into Listing objects."""
    listings: List[Listing] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            price = safe_float(row.get("PRICE", ""))
            if not price:
                continue  # skip rows with no price

            listings.append(
                Listing(
                    address=(row.get("ADDRESS") or "").strip(),
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
                    property_type=(row.get("PROPERTY TYPE") or "").strip() or None,
                    state=(row.get("STATE OR PROVINCE") or "").strip() or None,
                    zip_code=(row.get("ZIP OR POSTAL CODE") or "").strip() or None,
                    source="redfin",
                )
            )
    return listings


def read_generic_csv(path: str) -> List[Listing]:
    """Read a manual/generic CSV into Listing objects."""
    listings: List[Listing] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            listings.append(
                Listing(
                    address=(row.get("address") or "").strip(),
                    city=(row.get("city") or "").strip(),
                    price=safe_float(row.get("price", "")) or 0.0,
                    beds=safe_float(row.get("beds", "")),
                    baths=safe_float(row.get("baths", "")),
                    sqft=safe_float(row.get("sqft", "")),
                    link=(row.get("link") or "").strip(),
                    notes=(row.get("notes") or "").strip(),
                    source="manual",
                )
            )
    return listings


def read_listings(path: str) -> List[Listing]:
    """Auto-detect CSV format and return Listings."""
    if detect_redfin(path):
        print("Detected Redfin CSV format.")
        return read_redfin_csv(path)
    return read_generic_csv(path)


def filter_by_zip(
    listings: List[Listing], zip_codes: List[str]
) -> List[Listing]:
    """Filter listings to only include the given zip codes.

    Returns all listings unchanged if none have zip data.
    """
    if not zip_codes:
        return listings

    # Check if any listings have zip data
    has_zips = any(l.zip_code for l in listings)
    if not has_zips:
        print(
            "Note: No zip code data in these listings "
            "(try a Redfin export). Skipping zip filter."
        )
        return listings

    zips = set(z.strip() for z in zip_codes)
    filtered = [l for l in listings if l.zip_code in zips]
    print(f"Filtered to {len(filtered)} listings in zip(s): {', '.join(sorted(zips))}")
    return filtered
