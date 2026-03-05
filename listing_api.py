"""Fetch real estate listings by zip code.

Uses RapidAPI (Realty in US) when RAPIDAPI_KEY is set (reliable from cloud),
falls back to Redfin scraping for local dev.
"""

import os
import time
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
        resp = httpx.get(
            "https://realty-in-us.p.rapidapi.com/properties/v3/list",
            params={
                "postal_code": zip_code,
                "status": ["for_sale"],
                "sort": {"direction": "desc", "field": "list_date"},
                "limit": str(max_listings),
                "offset": "0",
            },
            headers={
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "realty-in-us.p.rapidapi.com",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"RapidAPI error: {e}")
        return []

    # Parse the response into Listing objects
    listings: List[Listing] = []
    properties = data.get("data", {}).get("home_search", {}).get("results", [])

    # Fallback: try v2-style response format
    if not properties:
        properties = data.get("properties", [])

    if not properties:
        # Try another level
        properties = data.get("data", {}).get("results", [])

    for prop in properties:
        try:
            # Handle nested address
            addr = prop.get("location", {}).get("address", {})
            if not addr:
                addr = prop.get("address", {})

            address = addr.get("line", "") or ""
            city = addr.get("city", "") or ""
            state = addr.get("state_code", "") or addr.get("state", "") or ""
            postal = addr.get("postal_code", "") or ""

            price = safe_float(prop.get("list_price") or prop.get("price"))
            if not price or not address:
                continue

            # Building size
            desc = prop.get("description", {})
            beds = safe_float(desc.get("beds") or prop.get("beds"))
            baths = safe_float(desc.get("baths") or prop.get("baths"))
            sqft = safe_float(desc.get("sqft") or prop.get("building_size", {}).get("size"))
            year_built = safe_int(desc.get("year_built") or prop.get("year_built"))
            lot_sqft = safe_float(desc.get("lot_sqft") or prop.get("lot_size", {}).get("size"))

            # Lot size as string
            lot_size = None
            if lot_sqft:
                if lot_sqft >= 43560:
                    lot_size = f"{lot_sqft / 43560:.2f} acres"
                else:
                    lot_size = f"{lot_sqft:,.0f} sqft"

            # Days on market
            dom = safe_int(prop.get("list_date_min") or desc.get("days_on_market"))

            # HOA
            hoa = safe_float(prop.get("hoa", {}).get("fee") if isinstance(prop.get("hoa"), dict) else None)

            # Price per sqft
            ppsf = None
            if price and sqft and sqft > 0:
                ppsf = round(price / sqft, 2)

            # Property type
            prop_type = desc.get("type") or prop.get("prop_type") or prop.get("property_type")

            # Link
            link = prop.get("href") or prop.get("rdc_web_url") or ""
            if link and not link.startswith("http"):
                link = f"https://www.realtor.com{link}"

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
                    days_on_market=dom,
                    hoa_monthly=hoa,
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
    print("RapidAPI not available, trying Redfin...")
    from redfin_api import fetch_listings as redfin_fetch
    return redfin_fetch(zip_code, max_listings)
