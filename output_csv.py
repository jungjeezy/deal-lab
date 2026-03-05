import csv
from typing import Any, Dict, List, Tuple

from models import Listing


def write_csv(
    results: List[Tuple[Listing, Dict[str, Any]]], path: str
) -> None:
    """Flatten scored results and write to CSV."""
    rows = []
    for listing, analysis in results:
        rows.append(
            {
                "address": listing.address,
                "city": listing.city,
                "price": listing.price,
                "beds": listing.beds,
                "baths": listing.baths,
                "sqft": listing.sqft,
                "link": listing.link,
                "deal_score": analysis["deal_score_1_to_10"],
                "rehab_tier": analysis["rehab_tier"],
                "arv_low": analysis["arv_estimate"]["low"],
                "arv_high": analysis["arv_estimate"]["high"],
                "rehab_low": analysis["rehab_cost_estimate"]["low"],
                "rehab_high": analysis["rehab_cost_estimate"]["high"],
                "mao_low": analysis["mao_estimate"]["low"],
                "mao_high": analysis["mao_estimate"]["high"],
                "flip_fit": analysis["exit_strategies"]["flip"]["fit"],
                "rental_fit": analysis["exit_strategies"]["rental"]["fit"],
                "rent_low": analysis["exit_strategies"]["rental"][
                    "rough_rent_monthly"
                ]["low"],
                "rent_high": analysis["exit_strategies"]["rental"][
                    "rough_rent_monthly"
                ]["high"],
                "top_risks": "; ".join(analysis["top_risks"]),
                "rationale": analysis["one_paragraph_rationale"],
            }
        )

    if not rows:
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
