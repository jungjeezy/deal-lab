"""Fetch real estate listings by zip code.

Uses RapidAPI (Realtor) when RAPIDAPI_KEY is set (reliable from cloud),
falls back to Redfin scraping for local dev.
"""

import os
from typing import List

import httpx

from models import Listing, safe_float, safe_int


def _fetch_via_rapidapi(zip_code: str, max_listings: int = 20) -> List[Listing]:
    """Fetch listings using the Realtor API on RapidAPI."""
    api_key = os.environ.get("RAPIDAPI_KEY", "")
    if not api_key:
        return []

    print(f"Fetching listings for {zip_code} via RapidAPI...")
    try:
        resp = httpx.get(
            "https://realty-in-us.p.rapidapi.com/properties/v2/list-for-sale",
            params={
                "postal_code": zip_code,
                "limit": str(max_listings),
                "offset": "0",
                "sort": "relevance",
            },
            headers={
                "x-rapidapi-key": api_key,
                "x-rapidapi-host": "realty-in-us.p.rapidapi.com",
            },
            timeout=30,
        )
        print(f"RapidAPI status: {resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"RapidAPI error: {e}")
        return []

    # Parse the response into Listing objects
    listings: List[Listing] = []
    properties = data.get("properties", [])

    if not properties:
        print(f"No properties in RapidAPI response. Keys: {list(data.keys())}")
        return []

    for prop in properties:
        try:
            addr = prop.get("address", {})
            address = addr.get("line", "") or ""
            city = addr.get("city", "") or ""
            state = addr.get("state_code", "") or addr.get("state", "") or ""
            postal = addr.get("postal_code", "") or ""

            price = safe_float(prop.get("price"))
            if not price or not address:
                continue

            beds = safe_float(prop.get("beds"))
            baths = safe_float(prop.get("baths"))

            # Square footage
            building = prop.get("building_size", {}) or {}
            sqft = safe_float(building.get("size"))

            # Lot size
            lot = prop.get("lot_size", {}) or {}
            lot_sqft = safe_float(lot.get("size"))
            lot_size = None
            if lot_sqft:
                lot_units = lot.get("units", "sqft")
                if lot_units == "acres" or lot_sqft >= 43560:
                    lot_size = f"{lot_sqft / 43560:.2f} acres" if lot_units == "sqft" else f"{lot_sqft} acres"
                else:
                    lot_size = f"{lot_sqft:,.0f} sqft"

            year_built = safe_int(prop.get("year_built"))

            # Property type
            prop_type = prop.get("prop_type") or prop.get("property_type")

            # Link
            link = prop.get("rdc_web_url") or ""

            # Price per sqft
            ppsf = None
            if price and sqft and sqft > 0:
                ppsf = round(price / sqft, 2)

            listings.append(
                Listing(
                    address=address.strip(),
                    city=city.strip(),
                    price=price,
                    beds=beds,
                    baths=baths,
                    sqft=sqft,
                    link=link,
                    notes="",
                    year_built=year_built,
                    lot_size=lot_size,
                    days_on_market=None,
                    hoa_monthly=None,
                    price_per_sqft=ppsf,
                    property_type=prop_type,
                    state=state,
                    zip_code=postal or zip_code,
                    source="realtor",
                )
            )
        except Exception as e:
            print(f"Skipping property: {e}")
            continue

    print(f"Found {len(listings)} listings via RapidAPI.")
    return listings


def fetch_listings(zip_code: str, max_listings: int = 20) -> List[Listing]:
    """Fetch listings — tries RapidAPI first, falls back to Redfin scraping."""

    # Try RapidAPI first (works from cloud servers)
    listings = _fetch_via_rapidapi(zip_code, max_listings)
    if listings:
        return listings

    # Fall back to Redfin scraping (works locally)
    print("RapidAPI not available or returned no results, trying Redfin...")
    from redfin_api import fetch_listings as redfin_fetch
    return redfin_fetch(zip_code, max_listings)
