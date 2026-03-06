import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple

from openai import OpenAI

from models import Listing

MODEL = "gpt-4o-mini"


def _get_client() -> OpenAI:
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


DEAL_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "score": {
            "type": "number",
            "description": "1-10 how strong of a buy this is",
        },
        "score_label": {
            "type": "string",
            "enum": ["Strong Buy", "Worth Seeing", "Fair Deal", "Overpriced", "Pass"],
        },
        "price_assessment": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "verdict": {
                    "type": "string",
                    "enum": ["under", "fair", "over"],
                },
                "estimated_value": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "low": {"type": "number"},
                        "high": {"type": "number"},
                    },
                    "required": ["low", "high"],
                },
                "explanation": {"type": "string"},
            },
            "required": ["verdict", "estimated_value", "explanation"],
        },
        "buyer_appeal": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 3,
        },
        "watch_out": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 3,
        },
        "photo_insights": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 3,
            "description": "3 specific observations from the listing photos about condition, style, updates, or red flags. If no photos, base on listing details.",
        },
        "negotiation_insight": {"type": "string"},
        "client_pitch": {
            "type": "string",
            "description": "One punchy sentence an agent could text a client",
        },
        "bottom_line": {"type": "string"},
        "estimated_monthly": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "mortgage": {"type": "number"},
                "total": {"type": "number"},
            },
            "required": ["mortgage", "total"],
        },
    },
    "required": [
        "score",
        "score_label",
        "price_assessment",
        "buyer_appeal",
        "watch_out",
        "photo_insights",
        "negotiation_insight",
        "client_pitch",
        "bottom_line",
        "estimated_monthly",
    ],
}


def _build_content(listing: Listing) -> list:
    """Build the message content with text + optional photos."""
    lines = [
        "You are an experienced real estate agent evaluating a listing for a buyer client.",
        "Be specific and practical. Reference what you SEE in the photos.",
        "",
        "Listing:",
        f"Address: {listing.address}, {listing.city}"
        + (f", {listing.state} {listing.zip_code}" if listing.state else ""),
        f"Asking Price: ${listing.price:,.0f}",
    ]

    if listing.beds is not None:
        lines.append(f"Beds: {listing.beds:.0f}")
    if listing.baths is not None:
        lines.append(f"Baths: {listing.baths:.0f}")
    if listing.sqft is not None:
        lines.append(f"Sqft: {listing.sqft:,.0f}")
    if listing.year_built:
        lines.append(f"Year Built: {listing.year_built}")
    if listing.lot_size:
        lines.append(f"Lot Size: {listing.lot_size}")
    if listing.days_on_market is not None:
        lines.append(f"Days on Market: {listing.days_on_market}")
    if listing.hoa_monthly:
        lines.append(f"HOA/Month: ${listing.hoa_monthly:,.0f}")
    if listing.price_per_sqft:
        lines.append(f"Price per Sqft: ${listing.price_per_sqft:,.0f}")
    if listing.property_type:
        lines.append(f"Property Type: {listing.property_type}")

    has_photos = bool(listing.photo_urls)

    if has_photos:
        lines.append("")
        lines.append("I've attached photos of this property. Look at them carefully.")
        lines.append("For photo_insights, describe SPECIFIC things you see — kitchen condition,")
        lines.append("flooring type, bathroom updates, roof condition, yard state, staging quality, etc.")
    else:
        lines.append("")
        lines.append("No photos available. Base photo_insights on what you'd expect given the")
        lines.append("listing details (age, price point, area).")

    lines.extend([
        "",
        "For monthly costs, assume 7% rate, 30yr fixed, 20% down.",
        "Return ONLY valid JSON matching the required schema.",
    ])

    # Build content blocks
    content = [{"type": "text", "text": "\n".join(lines)}]

    # Add up to 4 photos for vision analysis
    if has_photos:
        for url in listing.photo_urls[:4]:
            content.append({
                "type": "image_url",
                "image_url": {"url": url, "detail": "low"},
            })

    return content


def call_openai(listing: Listing) -> Dict[str, Any]:
    """Call OpenAI with structured output + optional vision."""
    content = _build_content(listing)

    response = _get_client().responses.create(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": "You are a sharp real estate agent. Return ONLY valid JSON. No markdown.",
            },
            {"role": "user", "content": content},
        ],
        temperature=0.3,
        text={
            "format": {
                "type": "json_schema",
                "name": "deal_analysis",
                "strict": True,
                "schema": DEAL_SCHEMA,
            }
        },
    )
    return json.loads(response.output_text)


def _score_one(listing: Listing) -> Tuple[Listing, Dict[str, Any]]:
    """Score a single listing. Used for parallel execution."""
    analysis = call_openai(listing)
    return (listing, analysis)


def score_listings(
    listings: List[Listing],
) -> List[Tuple[Listing, Dict[str, Any]]]:
    """Score all listings in parallel. Returns list of (listing, analysis_dict) pairs."""
    results: List[Tuple[Listing, Dict[str, Any]]] = []

    with ThreadPoolExecutor(max_workers=min(len(listings), 10)) as executor:
        futures = {
            executor.submit(_score_one, listing): i
            for i, listing in enumerate(listings)
        }
        ordered = [None] * len(listings)
        for future in as_completed(futures):
            idx = futures[future]
            try:
                ordered[idx] = future.result()
            except Exception as e:
                print(f"Error scoring listing {idx}: {e}")

        results = [r for r in ordered if r is not None]

    print(f"Scored {len(results)}/{len(listings)} listings.")
    return results
