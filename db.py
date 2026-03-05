import json
import sqlite3
import string
import random
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from models import Listing

DB_PATH = "deallab.db"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS dashboards (
            id TEXT PRIMARY KEY,
            zip_code TEXT NOT NULL,
            results_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def _generate_id(length: int = 6) -> str:
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=length))


def _listing_to_dict(listing: Listing) -> dict:
    return {
        "address": listing.address,
        "city": listing.city,
        "price": listing.price,
        "beds": listing.beds,
        "baths": listing.baths,
        "sqft": listing.sqft,
        "link": listing.link,
        "notes": listing.notes,
        "year_built": listing.year_built,
        "lot_size": listing.lot_size,
        "days_on_market": listing.days_on_market,
        "hoa_monthly": listing.hoa_monthly,
        "price_per_sqft": listing.price_per_sqft,
        "property_type": listing.property_type,
        "state": listing.state,
        "zip_code": listing.zip_code,
        "source": listing.source,
    }


def _dict_to_listing(d: dict) -> Listing:
    return Listing(**d)


def save_dashboard(
    zip_code: str,
    results: List[Tuple[Listing, Dict[str, Any]]],
) -> str:
    """Save a scored dashboard and return its unique ID."""
    dashboard_id = _generate_id()

    # Serialize all (listing, analysis) pairs
    data = []
    for listing, analysis in results:
        data.append({
            "listing": _listing_to_dict(listing),
            "analysis": analysis,
        })

    conn = _connect()
    conn.execute(
        "INSERT INTO dashboards (id, zip_code, results_json, created_at) VALUES (?, ?, ?, ?)",
        (
            dashboard_id,
            zip_code,
            json.dumps(data),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()
    return dashboard_id


def get_dashboard(
    dashboard_id: str,
) -> Optional[Tuple[str, List[Tuple[Listing, Dict[str, Any]]], str]]:
    """Load a dashboard by ID.

    Returns (zip_code, results, created_at) or None.
    """
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM dashboards WHERE id = ?", (dashboard_id,)
    ).fetchone()
    conn.close()

    if not row:
        return None

    data = json.loads(row["results_json"])
    results = []
    for item in data:
        listing = _dict_to_listing(item["listing"])
        results.append((listing, item["analysis"]))

    return row["zip_code"], results, row["created_at"]
