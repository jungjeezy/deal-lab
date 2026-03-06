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
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif;
      background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
      min-height: 100vh;
      padding: 16px;
      color: #f0f0f5;
      -webkit-font-smoothing: antialiased;
    }}

    .header {{
      text-align: center;
      margin-bottom: 24px;
      padding: 24px 0 16px;
    }}
    .header h1 {{
      font-size: 1.75rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      background: linear-gradient(135deg, #fff 0%, #a5b4fc 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .header p {{
      color: rgba(255,255,255,0.5);
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
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.2);
      border-radius: 10px;
      font-size: 0.9rem;
      font-family: inherit;
      text-align: center;
      letter-spacing: 0.1em;
      color: #fff;
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
    }}
    .zip-bar input:focus {{
      outline: none;
      border-color: rgba(165,180,252,0.6);
    }}
    .zip-bar button {{
      padding: 8px 16px;
      background: rgba(255,255,255,0.15);
      color: #fff;
      border: 1px solid rgba(255,255,255,0.2);
      border-radius: 10px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      transition: background 0.2s;
    }}
    .zip-bar button:hover {{ background: rgba(255,255,255,0.25); }}
    .zip-bar span {{
      color: rgba(255,255,255,0.5);
      font-size: 0.85rem;
    }}

    .card {{
      background: rgba(255,255,255,0.08);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 20px;
      padding: 20px;
      margin-bottom: 16px;
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }}

    .card-top {{
      display: flex;
      align-items: flex-start;
      gap: 14px;
      margin-bottom: 16px;
    }}
    .score-ring {{
      position: relative;
      width: 56px;
      height: 56px;
      flex-shrink: 0;
    }}
    .score-ring svg {{
      width: 56px;
      height: 56px;
      transform: rotate(-90deg);
    }}
    .score-ring .bg {{
      fill: none;
      stroke: rgba(255,255,255,0.1);
      stroke-width: 4;
    }}
    .score-ring .fg {{
      fill: none;
      stroke: var(--accent);
      stroke-width: 4;
      stroke-linecap: round;
      stroke-dasharray: var(--dash);
      stroke-dashoffset: var(--offset);
      transition: stroke-dashoffset 0.6s ease;
    }}
    .score-num {{
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--accent);
    }}
    .score-tag {{
      display: inline-block;
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 0.65rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      background: var(--accent-bg);
      color: var(--accent);
      margin-top: 6px;
    }}

    .card-info {{ flex: 1; }}
    .card-info h2 {{
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.3;
      color: #fff;
    }}
    .card-info .price {{
      font-size: 1.2rem;
      font-weight: 700;
      color: #fff;
      margin-top: 2px;
    }}
    .card-info .meta {{
      font-size: 0.78rem;
      color: rgba(255,255,255,0.45);
      margin-top: 3px;
    }}

    .pitch {{
      background: rgba(165,180,252,0.1);
      border: 1px solid rgba(165,180,252,0.2);
      border-radius: 12px;
      padding: 12px 14px;
      margin-bottom: 16px;
      font-size: 0.9rem;
      line-height: 1.5;
      color: rgba(255,255,255,0.85);
      font-style: italic;
    }}

    .stats {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 16px;
    }}
    .stat {{
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 14px;
      padding: 12px;
    }}
    .stat-label {{
      font-size: 0.65rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: rgba(255,255,255,0.4);
      margin-bottom: 4px;
    }}
    .stat-value {{
      font-size: 0.95rem;
      font-weight: 600;
      color: #fff;
    }}
    .stat-hint {{
      font-size: 0.7rem;
      color: rgba(255,255,255,0.35);
      margin-top: 2px;
    }}

    .verdict-under {{ color: #4ade80; }}
    .verdict-fair {{ color: #facc15; }}
    .verdict-over {{ color: #f87171; }}

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
      background: rgba(74,222,128,0.12);
      color: #4ade80;
      border: 1px solid rgba(74,222,128,0.2);
    }}
    .pill-warn {{
      background: rgba(251,191,36,0.1);
      color: #fbbf24;
      border-color: rgba(251,191,36,0.2);
    }}

    .detail-toggle {{
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 12px;
      padding: 11px 16px;
      width: 100%;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 500;
      color: rgba(255,255,255,0.6);
      font-family: inherit;
      transition: background 0.2s;
    }}
    .detail-toggle:hover {{ background: rgba(255,255,255,0.1); }}

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
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: rgba(255,255,255,0.4);
      margin-bottom: 8px;
    }}
    .detail-section p {{
      font-size: 0.875rem;
      line-height: 1.6;
      color: rgba(255,255,255,0.75);
    }}
    .detail-section ul {{
      list-style: none;
      padding: 0;
    }}
    .detail-section ul li {{
      font-size: 0.85rem;
      padding: 4px 0;
      color: rgba(255,255,255,0.7);
    }}

    .listing-link {{
      display: inline-block;
      margin-top: 8px;
      color: #a5b4fc;
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 500;
      transition: color 0.15s;
    }}
    .listing-link:hover {{ color: #c7d2fe; }}

    @media (min-width: 768px) {{
      body {{ max-width: 800px; margin: 0 auto; }}
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
        return "#4ade80"
    elif score >= 6:
        return "#a5b4fc"
    elif score >= 4:
        return "#facc15"
    return "#f87171"


def _accent_bg(score: float) -> str:
    if score >= 8:
        return "rgba(74,222,128,0.15)"
    elif score >= 6:
        return "rgba(165,180,252,0.15)"
    elif score >= 4:
        return "rgba(250,204,21,0.15)"
    return "rgba(248,113,113,0.15)"


def _fmt_price(val: float) -> str:
    if val >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    elif val >= 1_000:
        return f"${val / 1_000:.0f}K"
    return f"${val:,.0f}"


def _esc(text: str) -> str:
    return html.escape(str(text))


def _score_ring(score: float, accent: str) -> str:
    """SVG circular progress ring for the score."""
    circumference = 2 * 3.14159 * 22  # radius = 22
    dash = circumference
    offset = circumference - (score / 10) * circumference
    return f"""\
    <div class="score-ring" style="--accent: {accent}; --dash: {dash:.1f}; --offset: {offset:.1f}">
      <svg viewBox="0 0 48 48">
        <circle class="bg" cx="24" cy="24" r="22"/>
        <circle class="fg" cx="24" cy="24" r="22"/>
      </svg>
      <div class="score-num">{score:.0f}</div>
    </div>"""


def _render_card(
    listing: Listing, analysis: Dict[str, Any], rank: int
) -> str:
    score = analysis["score"]
    accent = _accent_color(score)
    accent_bg = _accent_bg(score)
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

    return f"""\
  <div class="card" style="--accent: {accent}; --accent-bg: {accent_bg}">
    <div class="card-top">
      {_score_ring(score, accent)}
      <div class="card-info">
        <h2>{_esc(listing.address)}, {_esc(listing.city)}</h2>
        <div class="price">{_fmt_price(listing.price)}</div>
        <div class="meta">{meta_line}</div>
        <span class="score-tag">{_esc(label)}</span>
      </div>
    </div>

    <div class="pitch">&ldquo;{_esc(analysis["client_pitch"])}&rdquo;</div>

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
