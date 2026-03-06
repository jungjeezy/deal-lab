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
                    "description": "Is it priced under, at, or over market value?",
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
                "explanation": {
                    "type": "string",
                    "description": "1-2 sentences on why, referencing comps or area trends",
                },
            },
            "required": ["verdict", "estimated_value", "explanation"],
        },
        "buyer_appeal": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 3,
            "description": "3 things buyers will love about this property, in plain English",
        },
        "watch_out": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 3,
            "description": "2-3 concerns: inspection items, negotiation leverage, or deal breakers",
        },
        "negotiation_insight": {
            "type": "string",
            "description": "One concrete negotiation tip for an agent representing a buyer",
        },
        "client_pitch": {
            "type": "string",
            "description": "One punchy sentence an agent could text a client about this property",
        },
        "bottom_line": {
            "type": "string",
            "description": "2-3 sentence honest assessment of this property as a purchase",
        },
        "estimated_monthly": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "mortgage": {"type": "number", "description": "Estimated monthly mortgage at 7% / 30yr / 20% down"},
                "total": {"type": "number", "description": "Mortgage + taxes + insurance + HOA estimate"},
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
        "negotiation_insight",
        "client_pitch",
        "bottom_line",
        "estimated_monthly",
    ],
}


def build_prompt(l: Listing) -> str:
    """Build the analysis prompt for agent-focused evaluation."""
    lines = [
        "You are an experienced real estate agent evaluating a listing for a buyer client.",
        "Be honest, specific, and practical. Write like you're briefing a fellow agent.",
        "",
        "Listing:",
        f"Address: {l.address}, {l.city}"
        + (f", {l.state} {l.zip_code}" if l.state else ""),
        f"Asking Price: ${l.price:,.0f}",
    ]

    if l.beds is not None:
        lines.append(f"Beds: {l.beds:.0f}")
    if l.baths is not None:
        lines.append(f"Baths: {l.baths:.0f}")
    if l.sqft is not None:
        lines.append(f"Sqft: {l.sqft:,.0f}")
    if l.year_built:
        lines.append(f"Year Built: {l.year_built}")
    if l.lot_size:
        lines.append(f"Lot Size: {l.lot_size}")
    if l.days_on_market is not None:
        lines.append(f"Days on Market: {l.days_on_market}")
    if l.hoa_monthly:
        lines.append(f"HOA/Month: ${l.hoa_monthly:,.0f}")
    if l.price_per_sqft:
        lines.append(f"Price per Sqft: ${l.price_per_sqft:,.0f}")
    if l.property_type:
        lines.append(f"Property Type: {l.property_type}")
    if l.link:
        lines.append(f"Link: {l.link}")
    if l.notes:
        lines.append(f"Notes: {l.notes}")

    lines.extend(
        [
            "",
            "Evaluate this listing as if advising a buyer client.",
            "Consider: Is the price right? What will buyers love? What should they watch for?",
            "What negotiation leverage exists? What would you text a client about this one?",
            "For monthly costs, assume 7% rate, 30yr fixed, 20% down.",
            "",
            "Return ONLY valid JSON matching the required schema.",
        ]
    )
    return "\n".join(lines)


def call_openai(prompt: str) -> Dict[str, Any]:
    """Call OpenAI with structured output and return parsed JSON."""
    response = _get_client().responses.create(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": "You are a sharp real estate agent. Return ONLY valid JSON. No markdown.",
            },
            {"role": "user", "content": prompt},
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
    analysis = call_openai(build_prompt(listing))
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
        # Collect results preserving original order
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
