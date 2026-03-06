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


@app.route("/debug")
def debug():
    """Temp debug endpoint to check what's happening."""
    import json
    info = {
        "rapidapi_key_set": bool(os.environ.get("RAPIDAPI_KEY")),
        "openai_key_set": bool(os.environ.get("OPENAI_API_KEY")),
    }
    # Quick test of RapidAPI
    try:
        from listing_api import _fetch_via_rapidapi
        listings = _fetch_via_rapidapi("94601", max_listings=1)
        info["rapidapi_listings"] = len(listings)
        if listings:
            info["first_listing"] = listings[0].address
    except Exception as e:
        info["rapidapi_error"] = str(e)

    return f"<pre>{json.dumps(info, indent=2)}</pre>"


@app.route("/search", methods=["POST"])
def search():
    zip_code = request.form.get("zip_code", "").strip()

    if not zip_code or len(zip_code) != 5 or not zip_code.isdigit():
        return render_template(
            "form.html", error="Please enter a valid 5-digit zip code."
        )

    try:
        # Pull listings
        listings = fetch_listings(zip_code, max_listings=5)
        if not listings:
            return render_template(
                "form.html",
                error=f"No active listings found in {zip_code}. Try a different zip code.",
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
            error="Something went wrong pulling listings. Please try again in a moment.",
        )


@app.route("/report/<dashboard_id>")
def view_dashboard(dashboard_id):
    data = get_dashboard(dashboard_id)
    if not data:
        abort(404)

    zip_code, results, created_at = data
    html = generate_report_html(results, zip_code=zip_code)
    return html


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8000)
