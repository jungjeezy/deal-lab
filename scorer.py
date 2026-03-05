import json
import os
from typing import Any, Dict, List, Tuple

from openai import OpenAI
from tqdm import tqdm

from models import Listing

MODEL = "gpt-4o-mini"


def _get_client() -> OpenAI:
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

DEAL_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "deal_score_1_to_10": {"type": "number"},
        "rehab_tier": {
            "type": "string",
            "enum": ["light", "medium", "heavy", "unknown"],
        },
        "arv_estimate": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "low": {"type": "number"},
                "high": {"type": "number"},
                "assumptions": {"type": "string"},
            },
            "required": ["low", "high", "assumptions"],
        },
        "rehab_cost_estimate": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "low": {"type": "number"},
                "high": {"type": "number"},
                "assumptions": {"type": "string"},
            },
            "required": ["low", "high", "assumptions"],
        },
        "mao_estimate": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "low": {"type": "number"},
                "high": {"type": "number"},
                "method": {"type": "string"},
            },
            "required": ["low", "high", "method"],
        },
        "exit_strategies": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "flip": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "fit": {"type": "string", "enum": ["good", "ok", "bad"]},
                        "notes": {"type": "string"},
                    },
                    "required": ["fit", "notes"],
                },
                "rental": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "fit": {"type": "string", "enum": ["good", "ok", "bad"]},
                        "notes": {"type": "string"},
                        "rough_rent_monthly": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "low": {"type": "number"},
                                "high": {"type": "number"},
                            },
                            "required": ["low", "high"],
                        },
                    },
                    "required": ["fit", "notes", "rough_rent_monthly"],
                },
            },
            "required": ["flip", "rental"],
        },
        "top_risks": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 3,
        },
        "one_paragraph_rationale": {"type": "string"},
    },
    "required": [
        "deal_score_1_to_10",
        "rehab_tier",
        "arv_estimate",
        "rehab_cost_estimate",
        "mao_estimate",
        "exit_strategies",
        "top_risks",
        "one_paragraph_rationale",
    ],
}


def build_prompt(l: Listing) -> str:
    """Build the analysis prompt, including enriched fields when available."""
    lines = [
        "You are a conservative real estate investor analyzing deals.",
        "",
        "Listing:",
        f"Address: {l.address}, {l.city}"
        + (f", {l.state} {l.zip_code}" if l.state else ""),
        f"Price: ${l.price:,.0f}",
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
            "Be conservative. Assume high labor + permit costs typical of California.",
            "If uncertain, widen ranges.",
            "",
            "Return ONLY valid JSON that matches the required schema.",
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
                "content": "Return ONLY valid JSON. No markdown. No extra commentary.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
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


def score_listings(
    listings: List[Listing],
) -> List[Tuple[Listing, Dict[str, Any]]]:
    """Score all listings. Returns list of (listing, analysis_dict) pairs."""
    results = []
    for listing in tqdm(listings, desc="Scoring deals"):
        analysis = call_openai(build_prompt(listing))
        results.append((listing, analysis))
    return results
