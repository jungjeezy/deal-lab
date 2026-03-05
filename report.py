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
  <title>Deal Lab Report</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f0f2f5;
      padding: 16px;
      color: #1a1a1a;
    }}
    .header {{
      text-align: center;
      margin-bottom: 24px;
      padding: 20px 0;
    }}
    .header h1 {{
      font-size: 1.5rem;
      font-weight: 700;
      margin-bottom: 4px;
    }}
    .header p {{
      color: #666;
      font-size: 0.875rem;
    }}
    .zip-bar {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin-bottom: 20px;
    }}
    .zip-bar form {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .zip-bar input {{
      width: 80px;
      padding: 8px 10px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      font-size: 0.9rem;
      font-family: inherit;
      text-align: center;
      letter-spacing: 0.1em;
    }}
    .zip-bar input:focus {{
      outline: none;
      border-color: #2563eb;
    }}
    .zip-bar button {{
      padding: 8px 14px;
      background: #2563eb;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
    }}
    .zip-bar button:hover {{ background: #1d4ed8; }}
    .zip-bar span {{
      color: #888;
      font-size: 0.85rem;
    }}
    .card {{
      background: white;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      border-left: 5px solid var(--score-color);
    }}
    .card-top {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .score-area {{
      display: flex;
      flex-direction: column;
      align-items: center;
      flex-shrink: 0;
      min-width: 56px;
    }}
    .score-badge {{
      width: 48px;
      height: 48px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: 700;
      font-size: 1.25rem;
      background: var(--score-color);
    }}
    .score-label {{
      font-size: 0.65rem;
      font-weight: 600;
      color: var(--score-color);
      margin-top: 4px;
      text-align: center;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .card-title {{
      flex: 1;
    }}
    .card-title h2 {{
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.3;
    }}
    .card-title .price {{
      font-size: 1.1rem;
      font-weight: 700;
      color: #111;
      margin-top: 2px;
    }}
    .card-title .meta {{
      font-size: 0.8rem;
      color: #888;
      margin-top: 2px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-bottom: 12px;
    }}
    .metric {{
      background: #f8f9fa;
      border-radius: 8px;
      padding: 10px;
    }}
    .metric-label {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #888;
      margin-bottom: 2px;
    }}
    .metric-value {{
      font-size: 0.9rem;
      font-weight: 600;
    }}
    .metric-hint {{
      font-size: 0.7rem;
      color: #aaa;
      margin-top: 2px;
    }}
    .tag {{
      display: inline-block;
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 600;
    }}
    .tag-good {{ background: #dcfce7; color: #166534; }}
    .tag-ok {{ background: #fef9c3; color: #854d0e; }}
    .tag-bad {{ background: #fee2e2; color: #991b1b; }}
    .tag-light {{ background: #dbeafe; color: #1e40af; }}
    .tag-medium {{ background: #fef9c3; color: #854d0e; }}
    .tag-heavy {{ background: #fee2e2; color: #991b1b; }}
    .tag-unknown {{ background: #f3f4f6; color: #6b7280; }}
    .detail-toggle {{
      background: none;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 10px 16px;
      width: 100%;
      cursor: pointer;
      font-size: 0.875rem;
      color: #555;
      transition: background 0.15s;
    }}
    .detail-toggle:hover {{ background: #f8f9fa; }}
    .details {{
      overflow: hidden;
      max-height: 0;
      transition: max-height 0.3s ease;
      margin-top: 0;
    }}
    .details.open {{
      max-height: 2000px;
      margin-top: 12px;
    }}
    .details-inner {{
      padding-top: 4px;
    }}
    .detail-section {{
      margin-bottom: 14px;
    }}
    .detail-section h3 {{
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #888;
      margin-bottom: 6px;
    }}
    .detail-section p, .detail-section li {{
      font-size: 0.875rem;
      line-height: 1.5;
      color: #333;
    }}
    .detail-section ul {{
      list-style: none;
      padding: 0;
    }}
    .detail-section ul li {{
      padding: 4px 0;
    }}
    .detail-section ul li::before {{
      content: "\\26A0\\FE0F  ";
    }}
    .profit-row {{
      display: flex;
      gap: 8px;
      margin-bottom: 8px;
      align-items: flex-start;
      font-size: 0.875rem;
      line-height: 1.4;
    }}
    .profit-row strong {{
      white-space: nowrap;
    }}
    .listing-link {{
      display: inline-block;
      margin-top: 8px;
      color: #2563eb;
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 500;
    }}
    .listing-link:hover {{ text-decoration: underline; }}
    .money-in {{
      background: #f8f9fa;
      border-radius: 10px;
      padding: 14px;
      margin-bottom: 12px;
      display: flex;
      gap: 12px;
    }}
    .money-in-block {{
      flex: 1;
    }}
    .money-in-label {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #888;
      margin-bottom: 2px;
    }}
    .money-in-value {{
      font-size: 1.1rem;
      font-weight: 700;
      color: #111;
    }}
    .money-in-hint {{
      font-size: 0.7rem;
      color: #aaa;
      margin-top: 2px;
    }}
    .money-in-value.upside {{ color: #16a34a; }}
    .money-in-value.downside {{ color: #dc2626; }}
    @media (min-width: 768px) {{
      body {{ max-width: 800px; margin: 0 auto; }}
      .metrics {{ grid-template-columns: 1fr 1fr 1fr 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>Deal Lab</h1>
    <p>{deal_count} deal{deal_plural} &middot; {generated_date}</p>
  </div>
  {zip_bar_html}
  {cards_html}
  <script>
    document.querySelectorAll('.detail-toggle').forEach(function(btn) {{
      btn.addEventListener('click', function() {{
        var details = btn.nextElementSibling;
        details.classList.toggle('open');
        btn.textContent = details.classList.contains('open') ? 'Hide Details' : 'See the full breakdown';
      }});
    }});
  </script>
</body>
</html>
"""


def _score_color(score: float) -> str:
    if score >= 7:
        return "#22c55e"
    elif score >= 4:
        return "#f59e0b"
    return "#ef4444"


def _score_label(score: float) -> str:
    if score >= 8:
        return "Great Deal"
    elif score >= 6:
        return "Worth a Look"
    elif score >= 4:
        return "Decent"
    return "Risky"


_FIT_LABELS = {"good": "Good fit", "ok": "Maybe", "bad": "Tough"}

_WORK_LABELS = {
    "light": "Light touch",
    "medium": "Moderate",
    "heavy": "Major project",
    "unknown": "Hard to tell",
}


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
    score = analysis["deal_score_1_to_10"]
    color = _score_color(score)
    label = _score_label(score)
    arv = analysis["arv_estimate"]
    rehab = analysis["rehab_cost_estimate"]
    mao = analysis["mao_estimate"]
    exits = analysis["exit_strategies"]

    # Build meta line
    meta_parts = []
    if listing.beds is not None:
        meta_parts.append(f"{listing.beds:.0f} bed")
    if listing.baths is not None:
        meta_parts.append(f"{listing.baths:.0f} bath")
    if listing.sqft is not None:
        meta_parts.append(f"{listing.sqft:,.0f} sqft")
    if listing.year_built:
        meta_parts.append(f"Built {listing.year_built}")
    if listing.days_on_market is not None:
        meta_parts.append(f"{listing.days_on_market} days listed")
    meta_line = " &middot; ".join(meta_parts)

    # Exit strategy labels
    flip_fit = exits["flip"]["fit"]
    rental_fit = exits["rental"]["fit"]
    rent = exits["rental"]["rough_rent_monthly"]

    flip_label = _FIT_LABELS.get(flip_fit, flip_fit.title())
    rental_label = _FIT_LABELS.get(rental_fit, rental_fit.title())

    # Work level
    rehab_tier = analysis["rehab_tier"]
    work_label = _WORK_LABELS.get(rehab_tier, rehab_tier.title())

    # Total money in = asking price + rehab
    total_in_low = listing.price + rehab["low"]
    total_in_high = listing.price + rehab["high"]
    # Potential upside = ARV - total money in (use conservative: high cost, low ARV)
    upside_low = arv["low"] - total_in_high
    upside_high = arv["high"] - total_in_low
    upside_positive = upside_low > 0

    # Risks
    risks_html = "".join(
        f"<li>{_esc(r)}</li>" for r in analysis["top_risks"]
    )

    # Listing link
    link_html = ""
    if listing.link and listing.link != "https://example.com":
        link_html = (
            f'<a class="listing-link" href="{_esc(listing.link)}" '
            f'target="_blank" rel="noopener">View listing &rarr;</a>'
        )

    return f"""\
  <div class="card" style="--score-color: {color}">
    <div class="card-top">
      <div class="score-area">
        <div class="score-badge">{score}</div>
        <div class="score-label">{label}</div>
      </div>
      <div class="card-title">
        <h2>#{rank} &mdash; {_esc(listing.address)}, {_esc(listing.city)}</h2>
        <div class="price">Asking {_fmt_price(listing.price)}</div>
        <div class="meta">{meta_line}</div>
      </div>
    </div>
    <div class="money-in">
      <div class="money-in-block">
        <div class="money-in-label">Total money in</div>
        <div class="money-in-value">{_fmt_price(total_in_low)} &ndash; {_fmt_price(total_in_high)}</div>
        <div class="money-in-hint">Purchase + renovation</div>
      </div>
      <div class="money-in-block">
        <div class="money-in-label">Potential upside</div>
        <div class="money-in-value {"upside" if upside_positive else "downside"}">{_fmt_price(abs(upside_low))} &ndash; {_fmt_price(abs(upside_high))}{" profit" if upside_positive else " loss"}</div>
        <div class="money-in-hint">{"What you could make" if upside_positive else "You'd likely lose money"}</div>
      </div>
    </div>
    <div class="metrics">
      <div class="metric">
        <div class="metric-label">What it could be worth</div>
        <div class="metric-value">{_fmt_price(arv["low"])} &ndash; {_fmt_price(arv["high"])}</div>
        <div class="metric-hint">After fixing it up</div>
      </div>
      <div class="metric">
        <div class="metric-label">Renovation costs</div>
        <div class="metric-value">{_fmt_price(rehab["low"])} &ndash; {_fmt_price(rehab["high"])}</div>
        <div class="metric-hint">To get it market-ready</div>
      </div>
      <div class="metric">
        <div class="metric-label">Max you should offer</div>
        <div class="metric-value">{_fmt_price(mao["low"])} &ndash; {_fmt_price(mao["high"])}</div>
        <div class="metric-hint">{_esc(mao["method"])}</div>
      </div>
      <div class="metric">
        <div class="metric-label">How much work</div>
        <div class="metric-value"><span class="tag tag-{rehab_tier}">{work_label}</span></div>
      </div>
    </div>
    <button class="detail-toggle">See the full breakdown</button>
    <div class="details">
      <div class="details-inner">
        <div class="detail-section">
          <h3>Ways to profit</h3>
          <div class="profit-row">
            <strong>Fix &amp; sell:</strong>
            <span class="tag tag-{flip_fit}">{flip_label}</span>
            <span>{_esc(exits["flip"]["notes"])}</span>
          </div>
          <div class="profit-row">
            <strong>Rent it out:</strong>
            <span class="tag tag-{rental_fit}">{rental_label}</span>
            <span>{_esc(exits["rental"]["notes"])}</span>
          </div>
          <div class="profit-row">
            <strong>Expected rent:</strong>
            <span>{_fmt_price(rent["low"])} &ndash; {_fmt_price(rent["high"])}/mo</span>
          </div>
        </div>
        <div class="detail-section">
          <h3>Watch out for</h3>
          <ul>{risks_html}</ul>
        </div>
        <div class="detail-section">
          <h3>The bottom line</h3>
          <p>{_esc(analysis["one_paragraph_rationale"])}</p>
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
        results, key=lambda r: r[1]["deal_score_1_to_10"], reverse=True
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
