import html
from datetime import datetime
from typing import Any, Dict, List, Tuple

from models import Listing

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Deal Lab</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #F9F5F0;
      min-height: 100vh;
      padding: 16px;
      color: #3D3929;
    }}

    .header {{
      text-align: center;
      margin-bottom: 20px;
      padding: 24px 0 12px;
    }}
    .header h1 {{
      font-size: 1.5rem;
      font-weight: 700;
      color: #2C2516;
      letter-spacing: -0.02em;
    }}
    .header p {{
      color: #B5A898;
      font-size: 0.85rem;
      margin-top: 4px;
    }}

    .zip-bar {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin-bottom: 24px;
    }}
    .zip-bar form {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .zip-bar input {{
      width: 80px;
      padding: 8px 10px;
      background: #fff;
      border: 1.5px solid #E8E0D5;
      border-radius: 12px;
      font-size: 0.9rem;
      font-family: inherit;
      text-align: center;
      letter-spacing: 0.1em;
      color: #2C2516;
    }}
    .zip-bar input:focus {{
      outline: none;
      border-color: #D4A574;
    }}
    .zip-bar button {{
      padding: 8px 16px;
      background: #D4A574;
      color: #fff;
      border: none;
      border-radius: 12px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.15s;
    }}
    .zip-bar button:hover {{ background: #C4946A; }}
    .zip-bar span {{
      color: #B5A898;
      font-size: 0.85rem;
    }}

    .card {{
      background: #fff;
      border-radius: 20px;
      padding: 22px;
      margin-bottom: 16px;
      box-shadow: 0 1px 3px rgba(60,40,10,0.04), 0 6px 20px rgba(60,40,10,0.05);
      border-left: 4px solid var(--accent);
      transition: box-shadow 0.2s, transform 0.15s;
    }}
    .card:hover {{
      box-shadow: 0 2px 8px rgba(60,40,10,0.06), 0 12px 32px rgba(60,40,10,0.07);
      transform: translateY(-1px);
    }}

    .card-top {{
      display: flex;
      align-items: flex-start;
      gap: 14px;
      margin-bottom: 16px;
    }}

    .score-circle {{
      width: 52px;
      height: 52px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 1.25rem;
      color: #fff;
      background: var(--accent);
      flex-shrink: 0;
    }}

    .card-info {{ flex: 1; }}
    .card-info h2 {{
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.3;
      color: #2C2516;
    }}
    .card-info .price {{
      font-size: 1.15rem;
      font-weight: 700;
      color: #2C2516;
      margin-top: 2px;
    }}
    .card-info .meta {{
      font-size: 0.78rem;
      color: #B5A898;
      margin-top: 3px;
    }}
    .score-tag {{
      display: inline-block;
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 0.68rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      background: var(--accent-light);
      color: var(--accent);
      margin-top: 6px;
    }}

    .pitch {{
      background: #FAF7F3;
      border-radius: 14px;
      padding: 14px 16px;
      margin-bottom: 16px;
      font-size: 0.9rem;
      line-height: 1.55;
      color: #5C5344;
      font-style: italic;
      border-left: 3px solid #E8E0D5;
    }}

    .stats {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 16px;
    }}
    .stat {{
      background: #FAF7F3;
      border-radius: 14px;
      padding: 12px;
    }}
    .stat-label {{
      font-size: 0.68rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #B5A898;
      margin-bottom: 3px;
    }}
    .stat-value {{
      font-size: 0.95rem;
      font-weight: 600;
      color: #2C2516;
    }}
    .stat-hint {{
      font-size: 0.7rem;
      color: #C8BDB0;
      margin-top: 2px;
    }}

    .verdict-under {{ color: #3B8C5E; }}
    .verdict-fair {{ color: #B8860B; }}
    .verdict-over {{ color: #C44B3A; }}

    .pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 16px;
    }}
    .pill {{
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 500;
      background: #F0F5ED;
      color: #3B6B3A;
    }}
    .pill-warn {{
      background: #FDF5E6;
      color: #8B6914;
    }}

    .detail-toggle {{
      background: #FAF7F3;
      border: 1.5px solid #EDE7DE;
      border-radius: 14px;
      padding: 11px 16px;
      width: 100%;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 500;
      color: #9C8E7C;
      font-family: inherit;
      transition: background 0.15s, border-color 0.15s;
    }}
    .detail-toggle:hover {{
      background: #F5EFE7;
      border-color: #D4A574;
    }}

    .details {{
      overflow: hidden;
      max-height: 0;
      transition: max-height 0.35s ease;
      margin-top: 0;
    }}
    .details.open {{
      max-height: 2000px;
      margin-top: 14px;
    }}
    .details-inner {{ padding-top: 2px; }}

    .detail-section {{
      margin-bottom: 16px;
    }}
    .detail-section h3 {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #B5A898;
      margin-bottom: 8px;
    }}
    .detail-section p {{
      font-size: 0.875rem;
      line-height: 1.6;
      color: #5C5344;
    }}

    .listing-link {{
      display: inline-block;
      margin-top: 8px;
      color: #D4A574;
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 500;
    }}
    .listing-link:hover {{ text-decoration: underline; color: #C4946A; }}

    .gallery {{
      display: flex;
      gap: 6px;
      overflow-x: auto;
      margin-bottom: 16px;
      border-radius: 14px;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
    }}
    .gallery::-webkit-scrollbar {{ display: none; }}
    .gallery img {{
      height: 140px;
      min-width: 140px;
      object-fit: cover;
      border-radius: 12px;
      flex-shrink: 0;
    }}
    .gallery img:first-child {{
      min-width: 200px;
      height: 140px;
    }}

    .media-row {{
      display: flex;
      gap: 10px;
      margin-bottom: 16px;
    }}
    .media-row .gallery {{
      flex: 1;
      margin-bottom: 0;
    }}
    .mini-map {{
      width: 140px;
      height: 140px;
      border-radius: 14px;
      overflow: hidden;
      flex-shrink: 0;
      border: 1px solid #EDE7DE;
    }}
    .mini-map iframe {{
      width: 100%;
      height: 100%;
      border: none;
    }}

    .photo-insights {{
      margin-bottom: 16px;
    }}
    .photo-insights ul {{
      list-style: none;
      padding: 0;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .photo-insights li {{
      font-size: 0.82rem;
      line-height: 1.5;
      color: #5C5344;
      padding: 10px 14px;
      background: #FAF7F3;
      border-radius: 12px;
      border-left: 3px solid #D4A574;
    }}

    @media (min-width: 768px) {{
      body {{ max-width: 720px; margin: 0 auto; }}
      .stats {{ grid-template-columns: 1fr 1fr 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>Deal Lab</h1>
    <p>{deal_count} listing{deal_plural} &middot; {generated_date}</p>
  </div>
  {zip_bar_html}
  {cards_html}
  <script>
    document.querySelectorAll('.detail-toggle').forEach(function(btn) {{
      btn.addEventListener('click', function() {{
        var details = btn.nextElementSibling;
        details.classList.toggle('open');
        btn.textContent = details.classList.contains('open') ? 'Less' : 'Full breakdown';
      }});
    }});
  </script>
</body>
</html>
"""


def _accent_color(score: float) -> str:
    if score >= 8:
        return "#3B8C5E"
    elif score >= 6:
        return "#D4A574"
    elif score >= 4:
        return "#B8860B"
    return "#C44B3A"


def _accent_light(score: float) -> str:
    if score >= 8:
        return "#E8F5ED"
    elif score >= 6:
        return "#FDF5EC"
    elif score >= 4:
        return "#FDF5E6"
    return "#FDEAE7"


def _fmt_price(val: float) -> str:
    if val >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    elif val >= 1_000:
        return f"${val / 1_000:.0f}K"
    return f"${val:,.0f}"


def _esc(text: str) -> str:
    return html.escape(str(text))


def _render_card(
    listing: Listing, analysis: Dict[str, Any], rank: int
) -> str:
    score = analysis["score"]
    accent = _accent_color(score)
    accent_light = _accent_light(score)
    label = analysis["score_label"]
    price_info = analysis["price_assessment"]
    monthly = analysis["estimated_monthly"]

    # Meta line
    meta_parts = []
    if listing.beds is not None:
        meta_parts.append(f"{listing.beds:.0f} bd")
    if listing.baths is not None:
        meta_parts.append(f"{listing.baths:.0f} ba")
    if listing.sqft is not None:
        meta_parts.append(f"{listing.sqft:,.0f} sqft")
    if listing.year_built:
        meta_parts.append(f"Built {listing.year_built}")
    meta_line = " &middot; ".join(meta_parts)

    # Price verdict
    verdict = price_info["verdict"]
    verdict_class = f"verdict-{verdict}"
    verdict_labels = {"under": "Under market", "fair": "Fair price", "over": "Over market"}
    ev = price_info["estimated_value"]

    # Buyer appeal pills
    appeal_html = "".join(
        f'<span class="pill">{_esc(item)}</span>' for item in analysis["buyer_appeal"]
    )

    # Watch out pills
    watch_html = "".join(
        f'<span class="pill pill-warn">{_esc(item)}</span>' for item in analysis["watch_out"]
    )

    # Link
    link_html = ""
    if listing.link and listing.link != "https://example.com":
        link_html = (
            f'<a class="listing-link" href="{_esc(listing.link)}" '
            f'target="_blank" rel="noopener">View listing &rarr;</a>'
        )

    # Photo gallery
    gallery_html = ""
    if listing.photo_urls:
        imgs = "".join(
            f'<img src="{_esc(url)}" alt="Listing photo" loading="lazy">'
            for url in listing.photo_urls[:6]
        )
        gallery_html = f'<div class="gallery">{imgs}</div>'

    # Mini map
    map_html = ""
    if listing.latitude and listing.longitude:
        lat, lon = listing.latitude, listing.longitude
        osm_url = (
            f"https://www.openstreetmap.org/export/embed.html"
            f"?bbox={lon-0.005},{lat-0.003},{lon+0.005},{lat+0.003}"
            f"&layer=mapnik&marker={lat},{lon}"
        )
        map_html = f'<div class="mini-map"><iframe src="{osm_url}" loading="lazy"></iframe></div>'

    # Combine gallery + map
    if gallery_html and map_html:
        media_html = f'<div class="media-row">{gallery_html}{map_html}</div>'
    elif gallery_html:
        media_html = gallery_html
    elif map_html:
        media_html = map_html
    else:
        media_html = ""

    # Photo insights
    photo_insights_html = ""
    insights = analysis.get("photo_insights", [])
    if insights:
        items = "".join(f"<li>{_esc(i)}</li>" for i in insights)
        photo_insights_html = f'<div class="photo-insights"><ul>{items}</ul></div>'

    return f"""\
  <div class="card" style="--accent: {accent}; --accent-light: {accent_light}">
    <div class="card-top">
      <div class="score-circle">{score:.0f}</div>
      <div class="card-info">
        <h2>{_esc(listing.address)}, {_esc(listing.city)}</h2>
        <div class="price">{_fmt_price(listing.price)}</div>
        <div class="meta">{meta_line}</div>
        <span class="score-tag">{_esc(label)}</span>
      </div>
    </div>

    {media_html}

    <div class="pitch">&ldquo;{_esc(analysis["client_pitch"])}&rdquo;</div>

    {photo_insights_html}

    <div class="stats">
      <div class="stat">
        <div class="stat-label">Price Check</div>
        <div class="stat-value {verdict_class}">{verdict_labels.get(verdict, verdict.title())}</div>
        <div class="stat-hint">Worth {_fmt_price(ev["low"])} &ndash; {_fmt_price(ev["high"])}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Est. Monthly</div>
        <div class="stat-value">{_fmt_price(monthly["total"])}/mo</div>
        <div class="stat-hint">Mortgage + taxes + ins</div>
      </div>
    </div>

    <div class="pills">{appeal_html}</div>

    <button class="detail-toggle">Full breakdown</button>
    <div class="details">
      <div class="details-inner">
        <div class="detail-section">
          <h3>Watch for</h3>
          <div class="pills">{watch_html}</div>
        </div>
        <div class="detail-section">
          <h3>Negotiation Tip</h3>
          <p>{_esc(analysis["negotiation_insight"])}</p>
        </div>
        <div class="detail-section">
          <h3>Price Analysis</h3>
          <p>{_esc(price_info["explanation"])}</p>
        </div>
        <div class="detail-section">
          <h3>The Bottom Line</h3>
          <p>{_esc(analysis["bottom_line"])}</p>
        </div>
        {link_html}
      </div>
    </div>
  </div>
"""


def _build_zip_bar(zip_code: str = "") -> str:
    if not zip_code:
        return ""
    return f"""\
  <div class="zip-bar">
    <span>Showing deals in</span>
    <form method="POST" action="/search">
      <input type="text" name="zip_code" value="{_esc(zip_code)}" maxlength="5" pattern="[0-9]{{5}}">
      <button type="submit">Change</button>
    </form>
  </div>
"""


def _build_page_html(
    results: List[Tuple[Listing, Dict[str, Any]]],
    zip_code: str = "",
) -> str:
    """Build the full HTML page as a string."""
    sorted_results = sorted(
        results, key=lambda r: r[1]["score"], reverse=True
    )

    cards = []
    for rank, (listing, analysis) in enumerate(sorted_results, 1):
        cards.append(_render_card(listing, analysis, rank))

    cards_html = "\n".join(cards)
    count = len(results)

    return HTML_TEMPLATE.format(
        deal_count=count,
        deal_plural="" if count == 1 else "s",
        generated_date=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        cards_html=cards_html,
        zip_bar_html=_build_zip_bar(zip_code),
    )


def generate_report(
    results: List[Tuple[Listing, Dict[str, Any]]], path: str
) -> None:
    """Generate a self-contained HTML report file (for CLI use)."""
    page = _build_page_html(results)
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)


def generate_report_html(
    results: List[Tuple[Listing, Dict[str, Any]]],
    zip_code: str = "",
) -> str:
    """Return the HTML report as a string (for web app use)."""
    return _build_page_html(results, zip_code=zip_code)


def generate_single_report_html(
    listing: Listing, analysis: Dict[str, Any]
) -> str:
    """Generate an HTML report for a single deal (for web app use)."""
    return _build_page_html([(listing, analysis)])
