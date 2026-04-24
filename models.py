from sqlalchemy import Column, Integer, String, Float, Date, Text, Boolean
from database import Base


class RawMarketData(Base):
    __tablename__ = "raw_market_data"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(50))   # ✅ FIX
    date = Column(Date)

    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)


class ProcessedMetrics(Base):
    __tablename__ = "processed_metrics"

    id = Column(Integer, primary_key=True)

    ticker = Column(String(100))      # ✅ FIX
    category = Column(String(100))    # ✅ FIX
    region = Column(String(100))      # ✅ FIX

    latest_close = Column(Float)
    pct_change_1d = Column(Float)
    pct_change_5d = Column(Float)
    pct_change_10d = Column(Float)
    volatility_10d = Column(Float)

    high_10d = Column(Float)
    low_10d = Column(Float)

    week_timestamp = Column(Date)


class EmailLog(Base):
    __tablename__ = "email_log"

    id = Column(Integer, primary_key=True)
    report_id = Column(Integer)
    recipient = Column(String(100))   # ✅ FIX
    status = Column(String(20))       # ✅ FIX
    error_message = Column(Text)


class MacroIndicator(Base):
    __tablename__ = "macro_indicators"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    latest = Column(Float)
    delta_3m = Column(Float)
    delta_6m = Column(Float)
    timestamp = Column(Date)


class YieldCurve(Base):
    __tablename__ = "yield_curve"

    id = Column(Integer, primary_key=True)

    country = Column(String(100))
    role = Column(String(100))

    y10 = Column(Float)
    y10_3m = Column(Float)
    y10_6m = Column(Float)

    y2 = Column(Float)
    y2_3m = Column(Float)
    y2_6m = Column(Float)

    spread = Column(Float)
    curve = Column(String(50))

    timestamp = Column(Date)