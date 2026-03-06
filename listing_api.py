"""Fetch real estate listings by zip code.

Uses RapidAPI (Realtor) when RAPIDAPI_KEY is set (reliable from cloud),
falls back to Redfin scraping for local dev.
"""

import os
from typing import List

import httpx

from models import Listing, safe_float, safe_int


def _fetch_via_rapidapi(zip_code: str, max_listings: int = 20) -> List[Listing]:
    """Fetch listings using the Realty in US API on RapidAPI."""
    api_key = os.environ.get("RAPIDAPI_KEY", "")
    if not api_key:
        return []

    print(f"Fetching listings for {zip_code} via RapidAPI...")
    try:
        resp = httpx.post(
            "https://realty-in-us.p.rapidapi.com/properties/v3/list",
            headers={
                "Content-Type": "application/json",
                "x-rapidapi-host": "realty-in-us.p.rapidapi.com",
                "x-rapidapi-key": api_key,
            },
            json={
                "limit": max_listings,
                "offset": 0,
                "postal_code": zip_code,
                "status": ["for_sale"],
                "sort": {"direction": "desc", "field": "list_date"},
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

    # v3 response: data.home_search.results
    results = data.get("data", {}).get("home_search", {}).get("results", [])
    if not results:
        # Fallback: try top-level properties
        results = data.get("properties", [])
    if not results:
        print(f"No properties in response. Top keys: {list(data.keys())}")
        return []

    for prop in results:
        try:
            # v3 nests address under location
            loc = prop.get("location", {})
            addr = loc.get("address", {}) if loc else {}
            if not addr:
                addr = prop.get("address", {}) or {}

            address = addr.get("line", "") or ""
            city = addr.get("city", "") or ""
            state = addr.get("state_code", "") or addr.get("state", "") or ""
            postal = addr.get("postal_code", "") or ""

            # v3 uses list_price
            price = safe_float(prop.get("list_price") or prop.get("price"))
            if not price or not address:
                continue

            # v3 nests details under description
            desc = prop.get("description", {}) or {}
            beds = safe_float(desc.get("beds") or prop.get("beds"))
            baths = safe_float(desc.get("baths") or prop.get("baths"))
            sqft = safe_float(desc.get("sqft") or desc.get("sqft_raw"))
            year_built = safe_int(desc.get("year_built"))
            lot_sqft = safe_float(desc.get("lot_sqft"))
            prop_type = desc.get("type") or prop.get("prop_type")

            # Lot size as string
            lot_size = None
            if lot_sqft:
                if lot_sqft >= 43560:
                    lot_size = f"{lot_sqft / 43560:.2f} acres"
                else:
                    lot_size = f"{lot_sqft:,.0f} sqft"

            # Link
            link = prop.get("href") or ""
            if link and not link.startswith("http"):
                link = f"https://www.realtor.com{link}"

            # Price per sqft
            ppsf = None
            if price and sqft and sqft > 0:
                ppsf = round(price / sqft, 2)

            # Photos
            primary_photo_url = None
            pp = prop.get("primary_photo") or {}
            if pp:
                primary_photo_url = pp.get("href")

            photo_urls = []
            for photo in (prop.get("photos") or [])[:6]:
                href = photo.get("href")
                if href:
                    photo_urls.append(href)

            # Coordinates
            coord = loc.get("address", {}).get("coordinate", {}) if loc else {}
            latitude = safe_float(coord.get("lat"))
            longitude = safe_float(coord.get("lon"))

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
                    photo_urls=photo_urls,
                    primary_photo_url=primary_photo_url,
                    latitude=latitude,
                    longitude=longitude,
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
