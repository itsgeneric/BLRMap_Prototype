import os
import json
import threading
import time
from core.config import EDGE_BLACKLIST_FILE, BLACKLIST_PENALTY_MULTIPLIER

class EdgeBlacklist:
    def __init__(self, filepath=EDGE_BLACKLIST_FILE):
        self.filepath = filepath
        self.lock = threading.Lock()
        # In-memory penalty lookup: "u_v" -> penalty multiplier
        self.penalties: dict[str, float] = {}
        # Detailed metadata for debugging / tracking
        self.last_check_time: float = 0.0
        self.load()

    def _key(self, u, v) -> str:
        return f"{u}_{v}"

    def load(self):
        """Loads blacklisted edges from disk."""
        with self.lock:
            if not os.path.exists(self.filepath):
                self.penalties = {}
                self.records = {}
                self.last_mtime = 0.0
                return

            try:
                mtime = os.path.getmtime(self.filepath)
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.records = data.get("edges", {})
                self.penalties = {}
                for edge_key, info in self.records.items():
                    penalty = float(info.get("penalty", BLACKLIST_PENALTY_MULTIPLIER))
                    self.penalties[edge_key] = penalty
                self.last_mtime = mtime
                print(f"[EdgeBlacklist] Loaded {len(self.records)} blacklisted segments from {self.filepath}")
            except Exception as e:
                print(f"[EdgeBlacklist] Error loading {self.filepath}: {e}")
                self.penalties = {}
                self.records = {}

    def _check_auto_reload(self):
        now = time.time()
        if now - self.last_check_time < 2.0:
            return
        self.last_check_time = now
        if os.path.exists(self.filepath):
            try:
                mtime = os.path.getmtime(self.filepath)
                if mtime > self.last_mtime:
                    self.load()
            except Exception:
                pass

    def save(self):
        """Saves blacklisted edges to disk."""
        with self.lock:
            try:
                payload = {
                    "updated_at": time.time(),
                    "count": len(self.records),
                    "edges": self.records,
                }
                temp_file = f"{self.filepath}.tmp"
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2)
                os.replace(temp_file, self.filepath)
            except Exception as e:
                print(f"[EdgeBlacklist] Error saving to {self.filepath}: {e}")

    def mark_edge_bad(self, u, v, penalty=BLACKLIST_PENALTY_MULTIPLIER, deviation_m=None, reason="gmaps_snap_deviation", metadata=None):
        """
        Marks an edge as non-existent or impassable.
        Records both forward (u, v) and reverse (v, u) to prevent travel in either direction.
        """
        now = time.time()
        record_data = {
            "u": u,
            "v": v,
            "penalty": penalty,
            "deviation_m": round(deviation_m, 2) if deviation_m is not None else None,
            "reason": reason,
            "flagged_at": now,
        }
        if metadata:
            record_data.update(metadata)

        k_fwd = self._key(u, v)
        k_rev = self._key(v, u)

        with self.lock:
            self.records[k_fwd] = record_data
            self.records[k_rev] = record_data
            self.penalties[k_fwd] = penalty
            self.penalties[k_rev] = penalty

        self.save()

    def get_edge_penalty(self, u, v) -> float:
        """Returns the multiplier penalty for this edge. Defaults to 1.0 (no penalty)."""
        self._check_auto_reload()
        k_fwd = self._key(u, v)
        if k_fwd in self.penalties:
            return self.penalties[k_fwd]
        k_rev = self._key(v, u)
        if k_rev in self.penalties:
            return self.penalties[k_rev]
        return 1.0

    def count(self) -> int:
        return len(self.records) // 2 if self.records else 0

    def clear(self):
        with self.lock:
            self.records = {}
            self.penalties = {}
        self.save()

edge_blacklist = EdgeBlacklist()
