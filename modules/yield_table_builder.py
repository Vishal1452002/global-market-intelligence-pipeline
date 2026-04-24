from fred_fetcher import fetch_fred_series
from datetime import timedelta, datetime

# ✅ DB imports
from database import get_db_session
from models import YieldCurve


# ---------------------------------------------------------
# COUNTRY SERIES MAP
# ---------------------------------------------------------
COUNTRY_YIELD_SERIES = {
    "United States": {
        "role": "Global Anchor",
        "10Y": "DGS10",
        "2Y": "DGS2",
    },
    "Japan": {
        "role": "Liquidity Source",
        "10Y": "IRLTLT01JPM156N",
        "2Y": "IR3TIB01JPM156N",
    },
    "Germany": {
        "role": "EU Core",
        "10Y": "IRLTLT01DEM156N",
        "2Y": "IR3TIB01DEM156N",
    },
    "Canada": {
        "role": "Energy Proxy",
        "10Y": "IRLTLT01CAM156N",
        "2Y": "IR3TIB01CAM156N",
    },
    "Australia": {
        "role": "Commodity Proxy",
        "10Y": "IRLTLT01AUM156N",
        "2Y": "IR3TIB01AUM156N",
    },
    "India": {
        "role": "High Growth EM",
        "10Y": "INDIRLTLT01STM",
        "2Y": None,
    },
}


# ---------------------------------------------------------
# DELTA
# ---------------------------------------------------------
def compute_delta(df, months):

    if df is None or df.empty:
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
# CURVE TYPE
# ---------------------------------------------------------
def classify_curve(spread):

    if spread is None:
        return None

    if spread < 0:
        return "Inverted"

    if spread > 1:
        return "Steep"

    return "Normal"


# ---------------------------------------------------------
# ✅ SAVE TO DB (NEW)
# ---------------------------------------------------------
def save_yield_to_db(rows):

    session = get_db_session()
    today = datetime.utcnow().date()

    try:
        for r in rows:

            exists = session.query(YieldCurve).filter(
                YieldCurve.country == r["country"],
                YieldCurve.timestamp == today
            ).first()

            if exists:
                continue

            session.add(
                YieldCurve(
                    country=r["country"],
                    role=r["role"],
                    y10=r["y10"],
                    y10_3m=r["y10_3m"],
                    y10_6m=r["y10_6m"],
                    y2=r["y2"],
                    y2_3m=r["y2_3m"],
                    y2_6m=r["y2_6m"],
                    spread=r["spread"],
                    curve=r["curve"],
                    timestamp=today
                )
            )

        session.commit()

    except Exception as e:
        session.rollback()
        print("Yield DB Error:", e)

    finally:
        session.close()


# ---------------------------------------------------------
# BUILD TABLE
# ---------------------------------------------------------
def build_yield_table():

    rows = []

    for country, data in COUNTRY_YIELD_SERIES.items():

        role = data["role"]

        df10 = fetch_fred_series(data["10Y"], days=400)
        df2 = fetch_fred_series(data["2Y"], days=400) if data["2Y"] else None

        if df10 is None or df10.empty:
            continue

        y10 = df10["value"].iloc[-1]
        y10_3m = compute_delta(df10, 3)
        y10_6m = compute_delta(df10, 6)

        if df2 is not None and not df2.empty:
            y2 = df2["value"].iloc[-1]
            y2_3m = compute_delta(df2, 3)
            y2_6m = compute_delta(df2, 6)
        else:
            y2 = y2_3m = y2_6m = None

        spread = None
        curve_label = None

        if y2 is not None:
            spread = y10 - y2
            curve_label = classify_curve(spread)

        rows.append({
            "country": country,
            "role": role,
            "y10": y10,
            "y10_3m": y10_3m,
            "y10_6m": y10_6m,
            "y2": y2,
            "y2_3m": y2_3m,
            "y2_6m": y2_6m,
            "spread": spread,
            "curve": curve_label,
        })

    # ✅ SAVE TO DB
    save_yield_to_db(rows)

    return rows


# ---------------------------------------------------------
# HTML (NO FETCH)
# ---------------------------------------------------------
def generate_yield_html(rows):

    html = """
    <h2>Global Bond Market</h2>

    <table border="1" cellpadding="6" cellspacing="0" width="100%"
    style="border-collapse:collapse;font-family:Arial;font-size:13px;margin-bottom:20px;">

    <thead>
    <tr style="background-color:#f0f0f0;">
        <th align="left">Country (Role)</th>
        <th align="right">10Y</th>
        <th align="right">2Y</th>
        <th align="right">Curve</th>
    </tr>
    </thead>

    <tbody>
    """

    for r in rows:
        html += f"""
        <tr>
            <td><b>{r['country']}</b> ({r['role']})</td>
            <td align="right">{r['y10']:.2f}%</td>
            <td align="right">{r['y2'] if r['y2'] else '—'}</td>
            <td align="right">{r['curve'] if r['curve'] else '—'}</td>
        </tr>
        """

    html += "</tbody></table>"

    return html