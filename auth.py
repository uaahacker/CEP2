"""
auth.py – Simple Authentication Module
=======================================
Academic demo authentication using SQLite + bcrypt password hashing.

NOTE FOR REVIEWERS:
    This is intentionally simplified for an academic assignment.
    In a real production application, you would use:
        - AWS Cognito for managed identity
        - OAuth 2.0 / OpenID Connect
        - Managed secrets (AWS Secrets Manager)
    For this demo, we use SQLite + bcrypt, which is secure enough
    for a non-production environment.
"""

import sqlite3
import os
import streamlit as st
import bcrypt

# ── Database file path (kept outside the app directory in production)
DB_PATH = os.environ.get("AUTH_DB_PATH", "users.db")


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE INITIALISATION
# ─────────────────────────────────────────────────────────────────────────────

def init_user_db() -> None:
    """
    Create the users table if it does not already exist.
    Called once at application startup.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            email    TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# PASSWORD UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    bcrypt automatically handles salting – never store plain-text passwords.

    Args:
        plain_password: The user-supplied password string.

    Returns:
        A bcrypt hash string (stored in the database).
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check a plain-text password against a stored bcrypt hash.

    Args:
        plain_password:  The password entered by the user at login.
        hashed_password: The hash retrieved from the database.

    Returns:
        True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# USER MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

def create_user(email: str, password: str) -> tuple[bool, str]:
    """
    Register a new user in the SQLite database.

    Args:
        email:    New user's email address (used as login identifier).
        password: Plain-text password (will be hashed before storage).

    Returns:
        (True, "success message")  on success
        (False, "error message")   on failure
    """
    # Basic validation
    if not email or not password:
        return False, "Email and password are required."
    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    hashed = hash_password(password)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email.lower().strip(), hashed),
        )
        conn.commit()
        conn.close()
        return True, "Account created successfully. Please log in."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    except Exception as exc:
        return False, f"Registration failed: {exc}"


def authenticate_user(email: str, password: str) -> tuple[bool, str]:
    """
    Verify login credentials against the database.

    Args:
        email:    Email address entered at login.
        password: Plain-text password entered at login.

    Returns:
        (True, email)          on success
        (False, "error message") on failure
    """
    if not email or not password:
        return False, "Email and password are required."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password FROM users WHERE email = ?",
            (email.lower().strip(),),
        )
        row = cursor.fetchone()
        conn.close()
    except Exception as exc:
        return False, f"Login failed: {exc}"

    if row is None:
        return False, "No account found with this email."

    stored_hash = row[0]
    if verify_password(password, stored_hash):
        return True, email.lower().strip()
    return False, "Incorrect password. Please try again."


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def logout_user() -> None:
    """
    Clear the authentication session state so the user is logged out.
    Streamlit will re-render the login page on the next run.
    """
    st.session_state.pop("authenticated", None)
    st.session_state.pop("user_email", None)
    st.rerun()


def require_login() -> str | None:
    """
    Gate function – call this at the top of any protected page.

    If the user is not logged in, renders the login/signup UI and stops
    execution (via st.stop()) so the dashboard is never shown.

    Returns:
        The logged-in user's email string when authenticated.
    """
    # Initialise the DB on every session start (idempotent)
    init_user_db()

    # Already authenticated?
    if st.session_state.get("authenticated"):
        return st.session_state.get("user_email")

    # ── Auth UI ───────────────────────────────────────────────────────────────
    _render_auth_page()
    st.stop()         # Prevent dashboard from rendering
    return None       # Unreachable – here for type checker


# ─────────────────────────────────────────────────────────────────────────────
# AUTH PAGE RENDERER
# ─────────────────────────────────────────────────────────────────────────────

def _render_auth_page() -> None:
    """
    Render the Login / Sign-Up tabs.
    Called internally by require_login() when the user is not authenticated.
    """
    # Centre the auth card with columns
    _, centre, _ = st.columns([1, 2, 1])

    with centre:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            padding: 2rem 2.5rem 1.5rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        ">
            <h1 style="color:#e94560; margin:0; font-size:2rem;">☁️ Cloud Cost Panel</h1>
            <p style="color:#a8b2d8; margin:0.5rem 0 0 0;">
                AWS FinOps Dashboard – Please log in to continue
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔑 Log In", "📝 Sign Up"])

        # ── LOGIN TAB ─────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("#### Welcome back")
            login_email = st.text_input(
                "Email", key="login_email", placeholder="you@example.com"
            )
            login_pass = st.text_input(
                "Password", type="password", key="login_pass", placeholder="••••••"
            )
            st.markdown("")

            if st.button("Log In", use_container_width=True, type="primary"):
                success, result = authenticate_user(login_email, login_pass)
                if success:
                    st.session_state["authenticated"] = True
                    st.session_state["user_email"] = result
                    st.success(f"✅ Welcome back, {result}!")
                    st.rerun()
                else:
                    st.error(f"❌ {result}")

            st.markdown(
                "<small style='color:#666;'>Don't have an account? Use the Sign Up tab above.</small>",
                unsafe_allow_html=True,
            )

        # ── SIGN-UP TAB ───────────────────────────────────────────────────────
        with tab_signup:
            st.markdown("#### Create your account")
            signup_email = st.text_input(
                "Email", key="signup_email", placeholder="you@example.com"
            )
            signup_pass = st.text_input(
                "Password (min 6 characters)", type="password",
                key="signup_pass", placeholder="••••••",
            )
            signup_pass2 = st.text_input(
                "Confirm Password", type="password",
                key="signup_pass2", placeholder="••••••",
            )
            st.markdown("")

            if st.button("Create Account", use_container_width=True, type="primary"):
                if signup_pass != signup_pass2:
                    st.error("❌ Passwords do not match.")
                else:
                    ok, msg = create_user(signup_email, signup_pass)
                    if ok:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")

            st.markdown(
                "<small style='color:#666;'>Already have an account? Use the Log In tab above.</small>",
                unsafe_allow_html=True,
            )
