import time
import sqlite3
from core.config import DECISIONS_DB

GRID_DEGREES = 0.01          # ~1.1km grid cells
MIN_SAMPLES_TO_TRUST = 15
SKIP_THRESHOLD = 0.15

def init_db():
    with sqlite3.connect(DECISIONS_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hour_bucket INTEGER,
                grid_lat INTEGER,
                grid_lng INTEGER,
                strategy TEXT,
                ts REAL
            )
        """)
        conn.execute("PRAGMA journal_mode=WAL;")

def _context_key(lat: float, lng: float, ts: float = None):
    ts = ts if ts is not None else time.time()
    hour_bucket = time.localtime(ts).tm_hour
    grid_lat = round(lat / GRID_DEGREES)
    grid_lng = round(lng / GRID_DEGREES)
    return hour_bucket, grid_lat, grid_lng

def log_route_decision(lat: float, lng: float, strategy: str):
    hour_bucket, grid_lat, grid_lng = _context_key(lat, lng)
    try:
        with sqlite3.connect(DECISIONS_DB) as conn:
            conn.execute(
                "INSERT INTO decisions (hour_bucket, grid_lat, grid_lng, strategy, ts) VALUES (?, ?, ?, ?, ?)",
                (hour_bucket, grid_lat, grid_lng, strategy, time.time()),
            )
    except Exception as exc:
        print(f"  Could not log route decision to {DECISIONS_DB}: {exc}")

def strategy_win_rates(lat: float, lng: float):
    hour_bucket, grid_lat, grid_lng = _context_key(lat, lng)
    try:
        with sqlite3.connect(DECISIONS_DB) as conn:
            rows = conn.execute(
                "SELECT strategy, COUNT(*) FROM decisions WHERE hour_bucket=? AND grid_lat=? AND grid_lng=? GROUP BY strategy",
                (hour_bucket, grid_lat, grid_lng),
            ).fetchall()
    except Exception as exc:
        print(f"  Could not read route decision history: {exc}")
        return {}

    total = sum(count for _, count in rows)
    return {strategy: (count, total) for strategy, count in rows}

def should_skip_live_check(strategy: str, lat: float, lng: float) -> bool:
    rates = strategy_win_rates(lat, lng)
    if strategy not in rates:
        return False
    win_count, total = rates[strategy]
    if total < MIN_SAMPLES_TO_TRUST:
        return False
    return (win_count / total) < SKIP_THRESHOLD