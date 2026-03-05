from dataclasses import dataclass
from typing import Optional


@dataclass
class Listing:
    address: str
    city: str
    price: float
    beds: Optional[float] = None
    baths: Optional[float] = None
    sqft: Optional[float] = None
    link: str = ""
    notes: str = ""
    # Redfin-enriched fields
    year_built: Optional[int] = None
    lot_size: Optional[str] = None
    days_on_market: Optional[int] = None
    hoa_monthly: Optional[float] = None
    price_per_sqft: Optional[float] = None
    property_type: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    source: str = "manual"


def safe_float(x: str) -> Optional[float]:
    try:
        x = x.strip().replace("$", "").replace(",", "")
        return float(x) if x else None
    except (ValueError, AttributeError):
        return None


def safe_int(x: str) -> Optional[int]:
    try:
        x = x.strip().replace(",", "")
        return int(float(x)) if x else None
    except (ValueError, AttributeError):
        return None
