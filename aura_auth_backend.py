"""AURA authentication backend.

SQLite-backed account storage with salted PBKDF2 password hashing.
Normal sign-ups are always created as role='user'.
Also stores admin-visible login activity.
"""

import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = BASE_DIR
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "aura_auth.db")
LEGACY_USERS_FILE = os.path.join(DATA_DIR, "aura_users.csv")
PBKDF2_ITERATIONS = 310_000


def _connect():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
                    CHECK(role IN ('admin', 'user')),
                created_at TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS login_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                role TEXT NOT NULL,
                login_at TEXT NOT NULL,
                ip_address TEXT DEFAULT '',
                user_agent TEXT DEFAULT ''
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_login_events_time ON login_events(login_at)")
        conn.commit()


def _pbkdf2_hash(password, iterations=PBKDF2_ITERATIONS):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def _verify_password(password, stored_hash):
    if not stored_hash:
        return False

    stored_hash = str(stored_hash)

    if stored_hash.startswith("pbkdf2_sha256$"):
        try:
            _, iterations, salt_hex, digest_hex = stored_hash.split("$", 3)
            iterations = int(iterations)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
            actual = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                iterations,
            )
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False

    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy, stored_hash)


def _needs_hash_upgrade(stored_hash):
    return not str(stored_hash).startswith("pbkdf2_sha256$")


def _normalize_username(username):
    return str(username or "").strip()


def validate_username(username):
    username = _normalize_username(username)
    if not (3 <= len(username) <= 40):
        return False, "Username must be 3–40 characters."
    if not all(ch.isalnum() or ch in "._-" for ch in username):
        return False, "Username may contain letters, numbers, dot, underscore or hyphen only."
    return True, ""


def validate_password(password):
    if len(password or "") < 8:
        return False, "Password must contain at least 8 characters."
    return True, ""


def get_user(username):
    username = _normalize_username(username)
    if not username:
        return None

    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, username, password_hash, role, created_at, is_active
            FROM users
            WHERE username = ? COLLATE NOCASE
            LIMIT 1
            """,
            (username,),
        ).fetchone()
    return dict(row) if row else None


def get_user_role(username):
    user = get_user(username)
    return user["role"] if user else None


def create_user(username, password, role="user"):
    username = _normalize_username(username)
    role = "admin" if str(role).lower() == "admin" else "user"

    valid, message = validate_username(username)
    if not valid:
        return False, message

    valid, message = validate_password(password)
    if not valid:
        return False, message

    if username.lower() == "admin" and role != "admin":
        return False, "The admin username is reserved."

    if get_user(username):
        return False, "Username already exists."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    password_hash = _pbkdf2_hash(password)

    try:
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO users
                    (username, password_hash, role, created_at, is_active)
                VALUES (?, ?, ?, ?, 1)
                """,
                (username, password_hash, role, now),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return False, "Username already exists."

    return True, "Account created successfully."


def record_login_event(username, role, ip_address="", user_agent=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO login_events
                (username, role, login_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(username), str(role), now, str(ip_address or ""), str(user_agent or "")),
        )
        conn.commit()


def authenticate_user(username, password, ip_address="", user_agent=""):
    username = _normalize_username(username)
    user = get_user(username)

    if not user or not user["is_active"]:
        return False, None, "Invalid username or password."

    if not _verify_password(password, user["password_hash"]):
        return False, None, "Invalid username or password."

    if _needs_hash_upgrade(user["password_hash"]):
        new_hash = _pbkdf2_hash(password)
        with _connect() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_hash, user["id"]),
            )
            conn.commit()

    record_login_event(username, user["role"], ip_address, user_agent)
    return True, user["role"], "Login successful."


def _insert_migrated_user(username, password_hash, role, created_at):
    if get_user(username):
        return

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO users
                (username, password_hash, role, created_at, is_active)
            VALUES (?, ?, ?, ?, 1)
            """,
            (username, password_hash, role, created_at),
        )
        conn.commit()


def migrate_legacy_users():
    init_db()

    if not os.path.exists(LEGACY_USERS_FILE):
        return

    try:
        import csv

        with open(LEGACY_USERS_FILE, "r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                username = _normalize_username(row.get("Username", ""))
                password_hash = str(row.get("Password", "")).strip()
                created_at = str(row.get("Created_At", "")).strip()

                if not username or not password_hash:
                    continue

                # Legacy accounts are normal users.
                # Administrator privileges belong only to the fixed owner account.
                role = "user"
                if not created_at:
                    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                _insert_migrated_user(username, password_hash, role, created_at)
    except (OSError, UnicodeError, csv.Error):
        pass


def ensure_admin_account():
    """
    Ensure that exactly one administrator account exists.

    The administrator account is fixed to the project owner.
    Normal users can never receive the admin role through signup.
    """

    init_db()

    ADMIN_USERNAME = "ANSHIKA"
    ADMIN_PASSWORD = "killmyassmunishji"

    # --------------------------------------------------------
    # Check whether the owner account already exists
    # --------------------------------------------------------

    admin = get_user(ADMIN_USERNAME)

    if admin:
        with _connect() as conn:

            conn.execute(
                """
                UPDATE users
                SET role = 'admin',
                    is_active = 1
                WHERE username = ?
                """,
                (ADMIN_USERNAME,),
            )

            conn.commit()

        return

    # --------------------------------------------------------
    # Create the single administrator account
    # --------------------------------------------------------

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    password_hash = _pbkdf2_hash(
        ADMIN_PASSWORD
    )

    with _connect() as conn:

        conn.execute(
            """
            INSERT INTO users
                (
                    username,
                    password_hash,
                    role,
                    created_at,
                    is_active
                )
            VALUES (?, ?, 'admin', ?, 1)
            """,
            (
                ADMIN_USERNAME,
                password_hash,
                now,
            ),
        )

        conn.commit()

def get_all_users_dataframe():
    import pandas as pd

    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT username AS Username,
                   role AS Role,
                   created_at AS Created_At,
                   is_active AS Is_Active
            FROM users
            ORDER BY created_at ASC, username ASC
            """
        ).fetchall()

    columns = ["Username", "Role", "Created_At", "Is_Active"]
    return pd.DataFrame([dict(row) for row in rows], columns=columns)


def get_login_history_dataframe(limit=500):
    import pandas as pd

    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT username AS Username,
                   role AS Role,
                   login_at AS Login_Time,
                   ip_address AS IP_Address,
                   user_agent AS User_Agent
            FROM login_events
            ORDER BY login_at DESC, id DESC
            LIMIT ?
            """,
            (int(limit),),
        ).fetchall()

    columns = ["Username", "Role", "Login_Time", "IP_Address", "User_Agent"]
    return pd.DataFrame([dict(row) for row in rows], columns=columns)


def set_user_active(username, is_active):
    username = _normalize_username(username)
    if username.lower() == "admin":
        return False, "The administrator account cannot be disabled."

    with _connect() as conn:
        cursor = conn.execute(
            "UPDATE users SET is_active = ? WHERE username = ? COLLATE NOCASE",
            (1 if is_active else 0, username),
        )
        conn.commit()

    if cursor.rowcount == 0:
        return False, "User not found."
    return True, "User status updated."
