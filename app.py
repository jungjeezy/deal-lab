#!/usr/bin/env python3
"""Deal Lab — Web app for scoring real estate deals."""

import os
import traceback

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, abort

from listing_api import fetch_listings
from scorer import score_listings
from report import generate_report_html
from db import init_db, save_dashboard, get_dashboard

load_dotenv()

app = Flask(__name__)
init_db()


@app.route("/")
def index():
    return render_template("form.html", error=None)


@app.route("/search", methods=["POST"])
def search():
    zip_code = request.form.get("zip_code", "").strip()

    if not zip_code or len(zip_code) != 5 or not zip_code.isdigit():
        return render_template(
            "form.html", error="Please enter a valid 5-digit zip code."
        )

    try:
        # Pull listings
        listings = fetch_listings(zip_code, max_listings=8)
        if not listings:
            return render_template(
                "form.html",
                error=f"No active listings found in {zip_code}. Try a different zip or pick a market below.",
            )

        # Score them all
        results = score_listings(listings)

        # Save to database
        dashboard_id = save_dashboard(zip_code, results)

        return redirect(url_for("view_dashboard", dashboard_id=dashboard_id))

    except Exception as e:
        traceback.print_exc()
        return render_template(
            "form.html",
            error="Something went wrong pulling listings. Please try again or pick a market below.",
        )


@app.route("/report/<dashboard_id>")
def view_dashboard(dashboard_id):
    data = get_dashboard(dashboard_id)
    if not data:
        abort(404)

    zip_code, results, created_at = data
    html = generate_report_html(results, zip_code=zip_code)
    return html


@app.route("/debug")
def debug():
    """Quick check that API keys are set."""
    rapid = os.environ.get("RAPIDAPI_KEY", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    return {
        "rapidapi_key_set": bool(rapid),
        "rapidapi_key_preview": rapid[:8] + "..." if rapid else "NOT SET",
        "openai_key_set": bool(openai_key),
        "openai_key_preview": openai_key[:8] + "..." if openai_key else "NOT SET",
    }


@app.route("/debug/fetch/<zip_code>")
def debug_fetch(zip_code):
    """Test listing fetch without scoring."""
    try:
        listings = fetch_listings(zip_code, max_listings=3)
        return {
            "count": len(listings),
            "listings": [
                {
                    "address": l.address,
                    "price": l.price,
                    "photos": len(l.photo_urls),
                    "has_coords": bool(l.latitude),
                }
                for l in listings
            ],
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8000)
