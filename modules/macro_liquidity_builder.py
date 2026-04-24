from fred_fetcher import fetch_fred_series
from datetime import timedelta, datetime

# ✅ NEW IMPORTS (DB)
from database import get_db_session
from models import MacroIndicator


# ---------------------------------------------------------
# MACRO SERIES CONFIG
# ---------------------------------------------------------
MACRO_SERIES = {
    "Fed Balance Sheet": "WALCL",
    "Reverse Repo Usage": "RRPONTSYD",
    "High Yield Spread": "BAMLH0A0HYM2",
    "Investment Grade Spread": "BAMLC0A0CM",
    "US 10Y Real Yield (TIPS)": "DFII10",
}


# ---------------------------------------------------------
# DELTA CALCULATION
# ---------------------------------------------------------
def compute_delta(df, months):

    if df.empty:
        return None

    latest_date = df["date"].iloc[-1]
    latest_value = df["value"].iloc[-1]

    target_date = latest_date - timedelta(days=30 * months)

    past_rows = df[df["date"] <= target_date]

    if past_rows.empty:
        return None

    past_value = past_rows.iloc[-1]["value"]

    return latest_value - past_value


# ---------------------------------------------------------
# ✅ SAVE TO DATABASE (NEW)
# ---------------------------------------------------------
def save_macro_to_db(rows):

    session = get_db_session()
    today = datetime.utcnow().date()

    try:
        for r in rows:

            # avoid duplicates (same day)
            exists = session.query(MacroIndicator).filter(
                MacroIndicator.name == r["name"],
                MacroIndicator.timestamp == today
            ).first()

            if exists:
                continue

            session.add(
                MacroIndicator(
                    name=r["name"],
                    latest=r["latest"],
                    delta_3m=r["delta_3m"],
                    delta_6m=r["delta_6m"],
                    timestamp=today
                )
            )

        session.commit()

    except Exception as e:
        session.rollback()
        print("Macro DB Error:", e)

    finally:
        session.close()


# ---------------------------------------------------------
# BUILD MACRO TABLE (MAIN LOGIC)
# ---------------------------------------------------------
def build_macro_table():

    rows = []

    for name, series in MACRO_SERIES.items():

        df = fetch_fred_series(series, days=400)

        if df.empty:
            continue

        latest = df["value"].iloc[-1]
        delta_3m = compute_delta(df, 3)
        delta_6m = compute_delta(df, 6)

        rows.append({
            "name": name,
            "latest": latest,
            "delta_3m": delta_3m,
            "delta_6m": delta_6m
        })

    # ✅ CRITICAL: store in DB
    save_macro_to_db(rows)

    return rows


# ---------------------------------------------------------
# FORMATTERS
# ---------------------------------------------------------
def format_value(name, value):

    if value is None:
        return "—"

    if "Balance Sheet" in name:
        return f"${value/1_000_000:.2f}T"

    if "Reverse Repo" in name:
        return f"${value:.2f}T"

    if "Spread" in name or "Yield" in name:
        return f"{value:.2f}%"

    return f"{value:.2f}"


def format_delta(name, value):

    if value is None:
        return "—"

    color = "#0a8a0a" if value >= 0 else "#c0392b"

    if "Balance Sheet" in name:
        text = f"{value/1_000_000:+.2f}T"
    elif "Reverse Repo" in name:
        text = f"{value:+.2f}T"
    elif "Spread" in name or "Yield" in name:
        text = f"{value:+.2f}%"
    else:
        text = f"{value:+.2f}"

    return f'<span style="color:{color}; font-weight:bold;">{text}</span>'


# ---------------------------------------------------------
# ✅ GENERATE HTML (UPDATED - NO EXTRA FETCH)
# ---------------------------------------------------------
def generate_macro_html(rows):

    html = """
    <div style="margin-top:35px;">
    <h2 style="font-family:Arial;">Global Liquidity & Credit</h2>

    <table border="1" cellpadding="6" cellspacing="0"
    style="border-collapse:collapse;font-family:Arial;font-size:13px;width:100%;table-layout:fixed;">

    <thead>
    <tr style="background:#f0f0f0;">
        <th align="left">Indicator</th>
        <th align="right">Latest</th>
        <th align="right">3M Δ</th>
        <th align="right">6M Δ</th>
    </tr>
    </thead>

    <tbody>
    """

    for r in rows:

        html += f"""
        <tr>
            <td><b>{r['name']}</b></td>
            <td align="right">{format_value(r['name'], r['latest'])}</td>
            <td align="right">{format_delta(r['name'], r['delta_3m'])}</td>
            <td align="right">{format_delta(r['name'], r['delta_6m'])}</td>
        </tr>
        """

    html += "</tbody></table></div>"

    return html