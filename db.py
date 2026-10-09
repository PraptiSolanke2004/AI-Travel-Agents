"""
Aerogen — Database Helper
All DB connection + CRUD functions used across the app.
"""

import pymysql
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()


# ── Connection ───────────────────────────────────────────
def get_conn():
    """Return a fresh MySQL connection to the aerogen database."""
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "20042004"),
        database="aerogen",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


# ══════════════════════════════════════════════════════
#  USER AUTH
# ══════════════════════════════════════════════════════

def register_user(name: str, email: str, password: str) -> dict:
    """
    Create a new user. Returns {"ok": True, "user": {...}} or {"ok": False, "error": "..."}.
    """
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name.strip(), email.strip().lower(), hashed),
            )
        conn.commit()
        conn.close()
        return login_user(email, password)
    except pymysql.err.IntegrityError:
        return {"ok": False, "error": "Email already registered. Please sign in."}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def login_user(email: str, password: str) -> dict:
    """
    Verify credentials. Returns {"ok": True, "user": {...}} or {"ok": False, "error": "..."}.
    """
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email, password FROM users WHERE email = %s",
                (email.strip().lower(),),
            )
            row = cur.fetchone()
        conn.close()
        if not row:
            return {"ok": False, "error": "No account found with this email."}
        if bcrypt.checkpw(password.encode(), row["password"].encode()):
            return {"ok": True, "user": {"id": row["id"], "name": row["name"], "email": row["email"]}}
        return {"ok": False, "error": "Incorrect password."}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ══════════════════════════════════════════════════════
#  TRIPS
# ══════════════════════════════════════════════════════

def save_trip(user_id: int, destination: str, origin: str,
              check_in: str, check_out: str, travelers: int,
              budget: int, travel_style: str, interests: str,
              itinerary: str) -> dict:
    """Save a generated itinerary to the trips table."""
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO trips
                    (user_id, destination, origin, check_in, check_out,
                     travelers, budget, travel_style, interests, itinerary)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (user_id, destination, origin, check_in, check_out,
                  travelers, budget, travel_style, interests, itinerary))
        conn.commit()
        conn.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_user_trips(user_id: int) -> list:
    """Fetch all saved trips for a user, newest first."""
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, destination, origin, check_in, check_out,
                       travelers, budget, travel_style, interests,
                       itinerary, created_at
                FROM trips
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def delete_trip(trip_id: int, user_id: int) -> dict:
    """Delete a trip (only if it belongs to the user)."""
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM trips WHERE id = %s AND user_id = %s",
                (trip_id, user_id),
            )
        conn.commit()
        conn.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ══════════════════════════════════════════════════════
#  SEARCH HISTORY
# ══════════════════════════════════════════════════════

def log_search(user_id: int, destination: str):
    """Log a destination search for the user."""
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO search_history (user_id, destination) VALUES (%s, %s)",
                (user_id, destination),
            )
        conn.commit()
        conn.close()
    except Exception:
        pass  # Non-critical — don't crash the app


def get_search_history(user_id: int, limit: int = 10) -> list:
    """Fetch recent search history for a user."""
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT destination, searched_at FROM search_history
                WHERE user_id = %s
                ORDER BY searched_at DESC LIMIT %s
            """, (user_id, limit))
            rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []
