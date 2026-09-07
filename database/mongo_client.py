"""
Async MongoDB Motor client for BLRNav.
Manages a single connection pool across the FastAPI lifespan.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from core.config import MONGODB_URI

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    """Call once at app startup (inside FastAPI lifespan)."""
    global _client, _db
    if not MONGODB_URI:
        print("⚠️  MONGODB_URI not set — MongoDB storage disabled.")
        return
    try:
        _client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        _db = _client["blrnav"]
        # Confirm the connection is alive
        await _client.admin.command("ping")
        # Ensure indexes exist (idempotent)
        await _ensure_indexes()
        print("✅ Connected to MongoDB Atlas → blrnav")
    except Exception as exc:
        print(f"❌ MongoDB connection failed: {exc}")
        _client = None
        _db = None


async def close_db() -> None:
    """Call once at app shutdown."""
    global _client
    if _client:
        _client.close()
        print("MongoDB connection closed.")


def is_connected() -> bool:
    return _db is not None


def get_col(name: str):
    """Return a collection handle. Raises if not connected."""
    if _db is None:
        raise RuntimeError("MongoDB not connected — check MONGODB_URI in .env")
    return _db[name]


async def _ensure_indexes() -> None:
    """Create indexes on first connect. Safe to run multiple times."""
    db = _db
    # journeys: fast lookup by session and status
    await db["journeys"].create_index("session_id")
    await db["journeys"].create_index("status")
    await db["journeys"].create_index("context.time_of_day_hour")
    await db["journeys"].create_index("created_at")
    # route_decisions: compound index for O(1) aggregation
    await db["route_decisions"].create_index(
        [("hour_bucket", 1), ("grid_lat", 1), ("grid_lng", 1)]
    )
