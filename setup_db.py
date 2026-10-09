"""
Aerogen — Database Setup Script
Run ONCE to create the database and all tables.
Usage: python setup_db.py
"""

import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Connect WITHOUT specifying a database first
conn = pymysql.connect(
    host=os.getenv("MYSQL_HOST", "127.0.0.1"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", "20042004"),
    charset="utf8mb4",
)
cursor = conn.cursor()

# ── Create database ──────────────────────────────────────
cursor.execute("CREATE DATABASE IF NOT EXISTS aerogen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
cursor.execute("USE aerogen;")

# ── Users table ──────────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

# ── Saved trips table ────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS trips (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    destination     VARCHAR(255) NOT NULL,
    origin          VARCHAR(50),
    check_in        DATE NOT NULL,
    check_out       DATE NOT NULL,
    travelers       INT DEFAULT 1,
    budget          INT DEFAULT 0,
    travel_style    VARCHAR(100),
    interests       TEXT,
    itinerary       LONGTEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

# ── Search history table ─────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS search_history (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    destination VARCHAR(255) NOT NULL,
    searched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

conn.commit()
cursor.close()
conn.close()

print("✅ Database 'aerogen' created successfully!")
print("✅ Tables created: users, trips, search_history")
print("\nYou can now run: streamlit run main.py")
