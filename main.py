import logging

# ✅ modules imports
from modules.macro_liquidity_builder import build_macro_table, generate_macro_html
from modules.yield_table_builder import build_yield_table, generate_yield_html
from modules.gemini_client import generate_gemini_report
from modules.data_fetcher import fetch_ticker_data
from modules.data_processor import process_and_store
from modules.signal_engine import compute_signals
from modules.report_builder import build_structured_snapshot, generate_html_table
from modules.email_sender import send_email

# ✅ core imports
from database import engine, Base
from settings import settings
from tickers import ASSET_STRUCTURE
from logger import setup_logger


# Create tables
Base.metadata.create_all(bind=engine)

# Setup logging
setup_logger()


def main():
    print("=== PIPELINE STARTED ===")
    logging.info("Pipeline started")

    try:
        # =========================
        # 1. FETCH + STORE DATA
        # =========================
        print("Step 1: Fetching data...")

        for category, value in ASSET_STRUCTURE.items():

            if isinstance(value, dict):
                for region, assets in value.items():
                    for asset in assets:
                        df = fetch_ticker_data(asset["symbol"])

                        if df is not None and not df.empty:
                            process_and_store(
                                display_name=asset["name"],
                                ticker_symbol=asset["symbol"],
                                category=category,
                                region=region,
                                df=df
                            )

            else:
                for asset in value:
                    df = fetch_ticker_data(asset["symbol"])

                    if df is not None and not df.empty:
                        process_and_store(
                            display_name=asset["name"],
                            ticker_symbol=asset["symbol"],
                            category=category,
                            region=None,
                            df=df
                        )

        # =========================
        # 2. MACRO + YIELD (FIXED)
        # =========================
        print("Step 2: Macro data...")
        macro_rows = build_macro_table()

        print("Step 3: Yield data...")
        yield_rows = build_yield_table()

        # =========================
        # 3. BUILD SNAPSHOT
        # =========================
        week_date, snapshot = build_structured_snapshot()

        # =========================
        # CASE 1: NO DATA
        # =========================
        if snapshot is None or len(snapshot) == 0:
            print("➡️ No data found → Sending fallback email")

            html_report = """
            <h2>No New Market Data Available Today</h2>
            <p>Market conditions unchanged from last update.</p>
            """

            send_email(
                subject="Daily Report - No New Data",
                html_content=html_report,
                report_id=1
            )

            return

        # =========================
        # CASE 2: DATA EXISTS
        # =========================
        print("➡️ Data found → Generating report")

        # Signals
        signals = compute_signals(snapshot)

        # AI Summary
        try:
            ai_summary = generate_gemini_report(signals)
        except Exception as e:
            print("AI failed:", e)
            ai_summary = "AI summary unavailable today."

        # =========================
        # FINAL REPORT (FIXED)
        # =========================
        html_report = f"""
        <h2>AI Market Summary</h2>
        <pre style="white-space: pre-wrap; font-family: Arial;">
        {ai_summary}
        </pre>

        <hr>

        {generate_html_table(snapshot, week_date)}

        {generate_macro_html(macro_rows)}

        {generate_yield_html(yield_rows)}
        """

        print("Sending full report email...")

        send_email(
            subject=f"Weekly Macro Report - {week_date}",
            html_content=html_report,
            report_id=1
        )

        print("✅ Full report email sent")
        logging.info("Pipeline completed successfully")

    except Exception as e:
        print("❌ ERROR:", e)
        logging.error(f"Pipeline failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()