import sqlite3
import json
import os
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "satquery.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

class DatabaseManager:
    """
    SQLite persistence for SatQuery AI / Terrascope AI analysis history and replay storage.
    """
    def __init__(self):
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT UNIQUE NOT NULL,
                    query TEXT NOT NULL,
                    specialist TEXT NOT NULL,
                    location_label TEXT NOT NULL,
                    bbox TEXT NOT NULL,
                    date_a TEXT NOT NULL,
                    date_b TEXT NOT NULL,
                    actual_date_a TEXT,
                    actual_date_b TEXT,
                    satellite TEXT NOT NULL,
                    change_percentage REAL,
                    affected_area_sq_km REAL,
                    earth_change_score REAL,
                    confidence_pct REAL,
                    result_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT DEFAULT 'Senior Analyst',
                    organization TEXT DEFAULT 'TerraScope Intelligence Lab',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
        
        # Seed initial default demo analyst account if users table is empty
        self._seed_default_user()

    def _hash_password(self, password: str, salt: bytes = None) -> tuple[str, str]:
        if salt is None:
            salt = os.urandom(16)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return hashed.hex(), salt.hex()

    def _verify_password(self, password: str, stored_hash: str, stored_salt: str) -> bool:
        try:
            salt = bytes.fromhex(stored_salt)
            hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return hashed.hex() == stored_hash
        except Exception:
            return False

    def _seed_default_user(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM users;")
                count = cursor.fetchone()[0]
                if count == 0:
                    self.create_user(
                        email="cibinjool08@gmail.com",
                        password="password123",
                        full_name="cibinjool08",
                        role="Senior Analyst",
                        organization="TerraScope Intelligence Lab"
                    )
                    self.create_user(
                        email="sarah.vance@terrascope.ai",
                        password="password123",
                        full_name="Dr. Sarah Vance",
                        role="Senior Earth Observation Specialist",
                        organization="Copernicus Intelligence Lab"
                    )
        except Exception as e:
            print(f"Error seeding default user: {e}")

    def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        role: str = "Senior Analyst",
        organization: str = "TerraScope Intelligence Lab"
    ) -> Optional[Dict[str, Any]]:
        clean_email = email.strip().lower()
        pwd_hash, salt_hex = self._hash_password(password)
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO users (email, password_hash, salt, full_name, role, organization)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (clean_email, pwd_hash, salt_hex, full_name, role, organization))
                conn.commit()
                user_id = cursor.lastrowid
                return {
                    "id": user_id,
                    "email": clean_email,
                    "full_name": full_name,
                    "role": role,
                    "organization": organization
                }
        except sqlite3.IntegrityError:
            return None
        except Exception as e:
            print(f"User creation error: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        clean_email = email.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE email = ?;", (clean_email,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.get_user_by_email(email)
        if not user:
            return None
        if self._verify_password(password, user["password_hash"], user["salt"]):
            return {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "name": user["full_name"],
                "role": user["role"],
                "organization": user["organization"]
            }
        return None

    def save_analysis(
        self,
        analysis_id: str,
        query: str,
        specialist: str,
        location_label: str,
        bbox: List[float],
        date_a: str,
        date_b: str,
        actual_date_a: str,
        actual_date_b: str,
        satellite: str,
        change_percentage: float,
        affected_area_sq_km: float,
        earth_change_score: float,
        confidence_pct: float,
        result_json: Dict[str, Any]
    ) -> bool:
        """Saves a completed satellite analysis record into database."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO analyses (
                        analysis_id, query, specialist, location_label, bbox,
                        date_a, date_b, actual_date_a, actual_date_b, satellite,
                        change_percentage, affected_area_sq_km, earth_change_score,
                        confidence_pct, result_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    analysis_id, query, specialist, location_label, json.dumps(bbox),
                    date_a, date_b, actual_date_a, actual_date_b, satellite,
                    change_percentage, affected_area_sq_km, earth_change_score,
                    confidence_pct, json.dumps(result_json), datetime.utcnow().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Database save error: {e}")
            return False

    def get_recent_analyses(self, limit: int = 20, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists recent analyses with optional specialist filter."""
        with self._get_connection() as conn:
            if filter_type and filter_type.lower() != "all":
                cursor = conn.execute("""
                    SELECT id, analysis_id, query, specialist, location_label, bbox,
                           date_a, date_b, satellite, change_percentage, affected_area_sq_km,
                           earth_change_score, confidence_pct, created_at
                    FROM analyses WHERE LOWER(specialist) LIKE ? OR LOWER(query) LIKE ?
                    ORDER BY id DESC LIMIT ?;
                """, (f"%{filter_type.lower()}%", f"%{filter_type.lower()}%", limit))
            else:
                cursor = conn.execute("""
                    SELECT id, analysis_id, query, specialist, location_label, bbox,
                           date_a, date_b, satellite, change_percentage, affected_area_sq_km,
                           earth_change_score, confidence_pct, created_at
                    FROM analyses ORDER BY id DESC LIMIT ?;
                """, (limit,))
            
            rows = cursor.fetchall()
            results = []
            for row in rows:
                item = dict(row)
                item["bbox"] = json.loads(item["bbox"]) if item["bbox"] else []
                results.append(item)
            return results

    def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves full analysis record by ID (case-insensitive)."""
        if not analysis_id:
            return None
        clean_id = analysis_id.strip()
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM analyses WHERE UPPER(analysis_id) = UPPER(?);", (clean_id,))
            row = cursor.fetchone()
            if row:
                res = dict(row)
                res["bbox"] = json.loads(res["bbox"])
                res["result_json"] = json.loads(res["result_json"])
                return res
            return None

    def get_total_analyses_count(self) -> int:
        """Returns total count of saved analyses in SQLite database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM analyses;")
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            print(f"Database count query error: {e}")
            return 0

db_manager = DatabaseManager()
