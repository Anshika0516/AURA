import os
import hashlib
from datetime import datetime

import joblib
import pandas as pd
import streamlit as st

from aura_auth_backend import (
    authenticate_user,
    create_user as backend_create_user,
    ensure_admin_account,
    get_all_users_dataframe,
    get_user,
    migrate_legacy_users,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AURA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# GLOBAL UI THEME
# ============================================================

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

THEME = st.session_state.theme_mode

if THEME == "Dark":
    theme_vars = {
        "bg": "#11111A",
        "surface": "#1B1A28",
        "surface2": "#242238",
        "border": "#38354D",
        "text": "#F7F7FB",
        "muted": "#B9B7C8",
        "primary": "#8B7CF6",
        "primary_hover": "#9B8DFF",
        "primary_text": "#FFFFFF",
        "accent": "#F4C95D",
        "pink": "#E86AA5",
        "input_bg": "#211F31",
    }

else:
    theme_vars = {
        "bg": "#F7F5FF",
        "surface": "#FFFFFF",
        "surface2": "#F0EDFF",
        "border": "#E2DDF5",
        "text": "#171522",
        "muted": "#686579",
        "primary": "#6750C9",
        "primary_hover": "#5842B5",
        "primary_text": "#FFFFFF",
        "accent": "#F3C84B",
        "pink": "#E65C9C",
        "input_bg": "#FFFFFF",
    }


st.markdown(
    f"""
<style>

/* ============================================================
   AURA GLOBAL COLOR VARIABLES
   ============================================================ */

:root {{
    --aura-bg: {theme_vars['bg']};
    --aura-surface: {theme_vars['surface']};
    --aura-surface-2: {theme_vars['surface2']};
    --aura-border: {theme_vars['border']};

    --aura-text: {theme_vars['text']};
    --aura-muted: {theme_vars['muted']};

    --aura-primary: {theme_vars['primary']};
    --aura-primary-hover: {theme_vars['primary_hover']};
    --aura-primary-text: {theme_vars['primary_text']};

    --aura-accent: {theme_vars['accent']};
    --aura-pink: {theme_vars['pink']};

    --aura-input: {theme_vars['input_bg']};
}}


/* ============================================================
   GLOBAL APP
   ============================================================ */

.stApp,
[data-testid="stAppViewContainer"] {{
    background: var(--aura-bg) !important;
    color: var(--aura-text) !important;
}}

[data-testid="stHeader"] {{
    background: transparent !important;
}}

html,
body,
[class*="css"],
.stMarkdown,
.stText,
p,
label,
span,
div {{
    color: var(--aura-text);
}}

h1,
h2,
h3,
h4,
h5,
h6 {{
    color: var(--aura-text) !important;
    letter-spacing: -0.02em;
}}

.stCaption,
[data-testid="stCaptionContainer"] {{
    color: var(--aura-muted) !important;
}}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div:first-child {{
    background: var(--aura-surface) !important;
    border-right: 1px solid var(--aura-border);
}}

section[data-testid="stSidebar"] * {{
    color: var(--aura-text);
}}


/* ============================================================
   SIDEBAR APPEARANCE / THEME BUTTON
   ============================================================ */

.sidebar-section-label {{
    font-size: 11px;
    font-weight: 750;
    color: var(--aura-muted) !important;

    text-transform: uppercase;
    letter-spacing: 0.8px;

    margin: 8px 0 8px 2px;
}}


/* Theme button */

[data-testid="stSidebar"] .theme-toggle-button button {{
    width: 100% !important;

    min-height: 44px !important;

    border-radius: 12px !important;

    border: 1px solid var(--aura-border) !important;

    background: var(--aura-surface-2) !important;

    color: var(--aura-text) !important;

    font-size: 14px !important;
    font-weight: 700 !important;

    text-align: left !important;

    padding: 0 15px !important;

    box-shadow: none !important;

    transition:
        background 0.18s ease,
        border-color 0.18s ease,
        color 0.18s ease,
        transform 0.18s ease !important;
}}


/* Theme button text */

[data-testid="stSidebar"] .theme-toggle-button button p,
[data-testid="stSidebar"] .theme-toggle-button button span,
[data-testid="stSidebar"] .theme-toggle-button button div {{
    color: var(--aura-text) !important;
}}


/* Theme button hover */

[data-testid="stSidebar"] .theme-toggle-button button:hover {{
    background: var(--aura-primary) !important;

    border-color: var(--aura-primary) !important;

    color: #FFFFFF !important;

    transform: translateY(-1px);

    box-shadow:
        0 5px 15px rgba(103, 80, 201, 0.18) !important;
}}


[data-testid="stSidebar"] .theme-toggle-button button:hover p,
[data-testid="stSidebar"] .theme-toggle-button button:hover span,
[data-testid="stSidebar"] .theme-toggle-button button:hover div {{
    color: #FFFFFF !important;
}}


/* ============================================================
   PAGE HEADER
   ============================================================ */

.page-header {{
    display: flex;
    align-items: center;
    gap: 16px;

    padding: 22px 24px;
    margin: 6px 0 18px;

    border: 1px solid var(--aura-border);
    border-radius: 20px;

    background: var(--aura-surface);

    box-shadow:
        0 8px 30px rgba(60, 45, 120, 0.07);
}}

.page-header-icon {{
    width: 54px;
    height: 54px;
    min-width: 54px;

    border-radius: 16px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 27px;

    background: var(--aura-surface-2);

    border: 1px solid var(--aura-border);
}}

.page-header h1 {{
    margin: 0 !important;
    font-size: 30px !important;
}}

.page-header p {{
    margin: 4px 0 0 !important;

    color: var(--aura-muted) !important;

    font-size: 14px;
}}


/* ============================================================
   ANALYSIS INTRO / SECTIONS
   ============================================================ */

.analysis-intro,
.analysis-section {{
    border: 1px solid var(--aura-border);

    background: var(--aura-surface);

    border-radius: 16px;
}}

.analysis-intro {{
    padding: 16px 20px;

    margin-bottom: 16px;

    background: var(--aura-surface-2);
}}

.analysis-intro span,
.section-subtitle {{
    color: var(--aura-muted) !important;
}}

.analysis-section {{
    padding: 16px 18px;

    margin: 8px 0 12px;
}}

.section-title {{
    font-size: 17px;
    font-weight: 750;

    color: var(--aura-text) !important;
}}

.section-subtitle {{
    margin-top: 3px;
    font-size: 13px;
}}


/* ============================================================
   CTA
   ============================================================ */

.analysis-cta {{
    display: flex;
    align-items: center;
    gap: 18px;

    padding: 22px 24px;
    margin: 10px 0 16px;

    border: 1px solid var(--aura-border);

    border-radius: 18px;

    background:
        linear-gradient(
            135deg,
            var(--aura-surface-2),
            var(--aura-surface)
        );

    box-shadow:
        0 8px 26px rgba(60, 45, 120, 0.06);
}}

.cta-icon {{
    width: 52px;
    height: 52px;
    min-width: 52px;

    border-radius: 14px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 25px;

    background: var(--aura-primary);

    color: #FFFFFF !important;
}}

.cta-content {{
    flex: 1;
}}

.cta-title {{
    font-size: 20px;
    font-weight: 750;

    margin-bottom: 5px;

    color: var(--aura-text) !important;
}}

.cta-description {{
    font-size: 14px;
    line-height: 1.6;

    color: var(--aura-muted) !important;

    opacity: 1 !important;
}}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button,
.stDownloadButton > button {{
    border-radius: 12px !important;

    min-height: 42px !important;

    font-weight: 650 !important;

    border: 1px solid var(--aura-border) !important;

    transition:
        all 0.18s ease !important;
}}


/* Primary */

.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {{
    background: var(--aura-primary) !important;

    color: #FFFFFF !important;

    border-color: var(--aura-primary) !important;

    box-shadow:
        0 5px 16px rgba(103, 80, 201, 0.20);
}}

.stButton > button[kind="primary"]:hover,
.stDownloadButton > button[kind="primary"]:hover {{
    background: var(--aura-primary-hover) !important;

    color: #FFFFFF !important;

    border-color: var(--aura-primary-hover) !important;

    transform: translateY(-1px);
}}


/* Secondary */

.stButton > button[kind="secondary"],
.stDownloadButton > button[kind="secondary"] {{
    background: var(--aura-surface) !important;

    color: var(--aura-text) !important;

    border-color: var(--aura-border) !important;
}}

.stButton > button[kind="secondary"]:hover,
.stDownloadButton > button[kind="secondary"]:hover {{
    background: var(--aura-surface-2) !important;

    color: var(--aura-text) !important;

    border-color: var(--aura-primary) !important;
}}


/* All button contents */

.stButton > button *,
.stDownloadButton > button * {{
    color: inherit !important;
}}


/* ============================================================
   INPUTS
   ============================================================ */

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {{
    background: var(--aura-input) !important;

    color: var(--aura-text) !important;

    border-color: var(--aura-border) !important;
}}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color: var(--aura-muted) !important;

    opacity: 1 !important;
}}


/* Dropdown */

[data-baseweb="popover"],
[data-baseweb="menu"] {{
    background: var(--aura-surface) !important;
}}

[role="option"] {{
    color: var(--aura-text) !important;def render_about_page():
}}
/* ============================================================
   DISABLED INPUTS
   Fix visibility of Username / Role / Status / Created fields
   ============================================================ */

.stTextInput input:disabled,
.stNumberInput input:disabled,
.stTextArea textarea:disabled {{
    background: var(--aura-input) !important;

    color: var(--aura-text) !important;

    -webkit-text-fill-color: var(--aura-text) !important;

    border-color: var(--aura-border) !important;

    opacity: 1 !important;

    cursor: default !important;
}}


/* Disabled input wrapper */

.stTextInput:has(input:disabled) label,
.stNumberInput:has(input:disabled) label,
.stTextArea:has(textarea:disabled) label {{
    color: var(--aura-text) !important;
}}


/* Disabled input internal text */

.stTextInput input:disabled *,
.stNumberInput input:disabled *,
.stTextArea textarea:disabled * {{
    color: var(--aura-text) !important;

    -webkit-text-fill-color: var(--aura-text) !important;
}}
/* ============================================================
   METRICS
   ============================================================ */

[data-testid="stMetric"] {{
    background: var(--aura-surface) !important;

    border: 1px solid var(--aura-border);

    border-radius: 16px;

    padding: 14px 16px;
}}

[data-testid="stMetricLabel"] {{
    color: var(--aura-muted) !important;
}}

[data-testid="stMetricValue"] {{
    color: var(--aura-text) !important;
}}


/* ============================================================
   DATAFRAME
   ============================================================ */

[data-testid="stDataFrame"] {{
    border: 1px solid var(--aura-border);

    border-radius: 14px;

    overflow: hidden;
}}


/* ============================================================
   DIVIDERS
   ============================================================ */

hr {{
    border-color: var(--aura-border) !important;
}}


/* ============================================================
   MOBILE
   ============================================================ */

@media(max-width: 768px) {{

    .page-header {{
        padding: 18px;
        gap: 12px;
        border-radius: 16px;
    }}

    .page-header-icon {{
        width: 44px;
        height: 44px;
        min-width: 44px;
        font-size: 22px;
    }}

    .page-header h1 {{
        font-size: 24px !important;
    }}

    .analysis-cta {{
        padding: 18px;
        gap: 12px;
    }}

    .cta-title {{
        font-size: 17px;
    }}

    .cta-description {{
        font-size: 13px;
    }}

    .stButton > button {{
        min-height: 46px !important;
    }}

    [data-testid="stSidebar"] .theme-toggle-button button {{
        min-height: 46px !important;
    }}
}}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# PATHS
# ============================================================

APP_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(
    APP_DIR,
    "models"
)

DATA_DIR = os.path.join(
    APP_DIR,
    "data"
)

PRODUCTIVITY_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "productivity_model.pkl"
)

BURNOUT_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "burnout_model.pkl"
)

HISTORY_FILE = os.path.join(
    DATA_DIR,
    "aura_history.csv"
)

os.makedirs(DATA_DIR, exist_ok=True)

# ============================================================
# FEATURE DEFINITIONS
# ============================================================

FEATURE_NAMES = [
    "Sleep_Hours",
    "Stress_Level",
    "Screen_Time",
    "Workload",
    "Break_Frequency",
    "Mood_Score",
    "Physical_Activity",
    "Water_Intake",
    "Study_Hours",
    "Focus_Sessions",
    "Social_Media_Time",
    "Deadline_Pressure",
    "Heart_Rate",
    "Energy_Level",
    "Task_Completion_Rate",
]

DISPLAY_FEATURE_NAMES = [
    "Sleep Hours",
    "Stress Level",
    "Screen Time",
    "Workload",
    "Break Frequency",
    "Mood Score",
    "Physical Activity",
    "Water Intake",
    "Study Hours",
    "Focus Sessions",
    "Social Media Time",
    "Deadline Pressure",
    "Heart Rate",
    "Energy Level",
    "Task Completion Rate",
]

PRODUCTIVITY_SCORES = {
    "High": 100,
    "Medium": 70,
    "Low": 40,
}

BURNOUT_SCORES = {
    "Safe": 100,
    "Warning": 60,
    "Critical": 20,
}


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_SESSION_STATE = {
    "authenticated": False,
    "current_user": None,
    "current_role": None,
    "page": "Dashboard",
    "analysis_done": False,
    "analysis_result": None,
    "whatif_result": None,
    "theme_mode": "Light",
}

for key, value in DEFAULT_SESSION_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# LOGIN-SCREEN SIDEBAR PROTECTION
# ============================================================
# Streamlit can retain widget/layout state briefly between reruns.
# Hide the sidebar completely until authentication succeeds.
if not st.session_state.authenticated:
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
            }
            button[data-testid="collapsedControl"] {
                display: none !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# AUTHENTICATION / USER MANAGEMENT
# ============================================================

# Authentication is persisted in a SQLite backend. Existing AURA CSV
# accounts are migrated automatically so the project does not lose users.
migrate_legacy_users()
ensure_admin_account()


def load_users():
    """Return safe user metadata for the app/admin UI.

    Password hashes are intentionally never returned to the UI.
    """
    return get_all_users_dataframe()


def create_user(username, password):
    """Create a normal user account; role assignment is backend-controlled."""
    return backend_create_user(username, password, role="user")


def authenticate(username, password):
    """Authenticate and return (success, role)."""
    success, role, _message = authenticate_user(username, password)
    return success, role


def logout_user():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_role = None
    st.session_state.page = "Home"
    st.session_state.analysis_done = False
    st.session_state.analysis_result = None
    st.session_state.whatif_result = None

    # Clear navigation/widget state so it cannot persist into the
    # unauthenticated login screen.
    st.session_state.pop("aura_navigation", None)
    st.rerun()


# ============================================================
# MODEL LOADING
# ============================================================

@st.cache_resource
def load_models():

    if not os.path.exists(PRODUCTIVITY_MODEL_PATH):
        raise FileNotFoundError(
            f"Productivity model not found:\n"
            f"{PRODUCTIVITY_MODEL_PATH}"
        )

    if not os.path.exists(BURNOUT_MODEL_PATH):
        raise FileNotFoundError(
            f"Burnout model not found:\n"
            f"{BURNOUT_MODEL_PATH}"
        )

    productivity = joblib.load(
        PRODUCTIVITY_MODEL_PATH
    )

    burnout = joblib.load(
        BURNOUT_MODEL_PATH
    )

    return productivity, burnout


# ============================================================
# HISTORY MANAGEMENT
# ============================================================

HISTORY_COLUMNS = [
    "Username",
    "Timestamp",
    *FEATURE_NAMES,
    "Productivity",
    "Burnout",
    "AURA_Score",
]


def load_all_history():
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    try:
        history = pd.read_csv(HISTORY_FILE)
    except Exception:
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    # Older versions may not have Username/Timestamp.
    # We keep the records readable, but never silently expose
    # them to another account through the user-specific loader.
    for col in HISTORY_COLUMNS:
        if col not in history.columns:
            history[col] = None

    return history


def load_history(username=None):
    """
    Return history belonging only to the logged-in user.

    If username is omitted, an empty DataFrame is returned so that
    accidental global-history access cannot happen.
    """
    if not username:
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    history = load_all_history()

    if history.empty:
        return history

    if "Username" not in history.columns:
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    user_history = history[
        history["Username"]
        .astype(str)
        .str.strip()
        .str.lower()
        == str(username).strip().lower()
    ].copy()

    if "Timestamp" in user_history.columns:
        user_history["Timestamp"] = user_history[
            "Timestamp"
        ].astype(str)

    return user_history.reset_index(drop=True)


def save_history(result):
    username = st.session_state.current_user

    if not username:
        return

    row = {
        "Username": username,
        "Timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "Sleep_Hours": result["sleep_hours"],
        "Stress_Level": result["stress_level"],
        "Screen_Time": result["screen_time"],
        "Workload": result["workload"],
        "Break_Frequency": result["break_frequency"],
        "Mood_Score": result["mood_score"],
        "Physical_Activity": result["physical_activity"],
        "Water_Intake": result["water_intake"],
        "Study_Hours": result["study_hours"],
        "Focus_Sessions": result["focus_sessions"],
        "Social_Media_Time": result["social_media_time"],
        "Deadline_Pressure": result["deadline_pressure"],
        "Heart_Rate": result["heart_rate"],
        "Energy_Level": result["energy_level"],
        "Task_Completion_Rate": result["task_completion_rate"],
        "Productivity": result["productivity_prediction"],
        "Burnout": result["burnout_prediction"],
        "AURA_Score": round(result["aura_score"], 2),
    }

    row_df = pd.DataFrame([row])

    if not os.path.exists(HISTORY_FILE):
        row_df.to_csv(HISTORY_FILE, index=False)
        return

    try:
        existing = pd.read_csv(HISTORY_FILE)
    except Exception:
        existing = pd.DataFrame()

    # Migrate an old history file safely.
    # Old rows without Username are NOT assigned to the current user.
    # This prevents one user's old records from leaking to another.
    for col in HISTORY_COLUMNS:
        if col not in existing.columns:
            existing[col] = None

    existing = existing[HISTORY_COLUMNS]

    combined = pd.concat(
        [existing, row_df],
        ignore_index=True,
    )

    combined.to_csv(
        HISTORY_FILE,
        index=False,
    )


# ============================================================
# AURA CALCULATIONS
# ============================================================

def calculate_aura_score(productivity, burnout):
    productivity_score = PRODUCTIVITY_SCORES.get(
        str(productivity),
        70,
    )

    burnout_score = BURNOUT_SCORES.get(
        str(burnout),
        60,
    )

    aura_score = (
        productivity_score * 0.60
        + burnout_score * 0.40
    )

    return (
        productivity_score,
        burnout_score,
        aura_score,
    )


def get_aura_status(aura_score):
    if aura_score >= 75:
        return (
            "Stable",
            "Your overall resilience looks stable.",
        )

    if aura_score >= 50:
        return (
            "Watch",
            "Your current pattern needs some attention.",
        )

    return (
        "Needs Attention",
        "Your current pattern needs attention and recovery.",
    )


def generate_recommendations(
    stress,
    sleep,
    screen,
    workload,
    breaks,
    mood,
    energy,
    completion,
    burnout,
    productivity,
):
    recommendations = []

    if stress >= 7:
        recommendations.append(
            "High stress detected. Consider reducing workload "
            "and adding recovery breaks."
        )

    if sleep < 6:
        recommendations.append(
            "Sleep duration is relatively low. Improving sleep "
            "consistency may support energy and productivity."
        )

    if screen >= 9:
        recommendations.append(
            "Screen time is high. Consider adding short "
            "screen-free intervals."
        )

    if workload >= 8:
        recommendations.append(
            "Workload is high. Prioritize important tasks "
            "and break larger tasks into smaller steps."
        )

    if breaks <= 2:
        recommendations.append(
            "Break frequency is low. Consider taking regular "
            "short breaks between focused sessions."
        )

    if mood <= 4:
        recommendations.append(
            "Mood score is relatively low. Consider balancing "
            "demanding tasks with restorative activities."
        )

    if energy <= 4:
        recommendations.append(
            "Energy level is low. Review sleep, activity, "
            "hydration and workload patterns."
        )

    if completion < 50:
        recommendations.append(
            "Task completion is low. Try prioritizing fewer "
            "high-impact tasks at a time."
        )

    if burnout == "Critical":
        recommendations.append(
            "ML model indicates critical burnout risk. Focus "
            "on recovery, workload balance and regular breaks."
        )
    elif burnout == "Warning":
        recommendations.append(
            "ML model indicates warning-level burnout risk. "
            "Monitor stress, workload and recovery patterns."
        )

    if productivity == "Low":
        recommendations.append(
            "ML model predicts low productivity. Try reducing "
            "distractions and prioritizing important tasks."
        )
    elif productivity == "High":
        recommendations.append(
            "ML model predicts high productivity. Maintain the "
            "habits that are supporting your performance."
        )

    if not recommendations:
        recommendations.append(
            "Your current metrics look relatively balanced. "
            "Keep monitoring your daily patterns."
        )

    return recommendations


# ============================================================
# ANALYSIS HELPERS
# ============================================================

def make_model_input(
    sleep_hours,
    stress_level,
    screen_time,
    workload,
    break_frequency,
    mood_score,
    physical_activity,
    water_intake,
    study_hours,
    focus_sessions,
    social_media_time,
    deadline_pressure,
    heart_rate,
    energy_level,
    task_completion_rate,
):
    values = [[
        sleep_hours,
        stress_level,
        screen_time,
        workload,
        break_frequency,
        mood_score,
        physical_activity,
        water_intake,
        study_hours,
        focus_sessions,
        social_media_time,
        deadline_pressure,
        heart_rate,
        energy_level,
        task_completion_rate,
    ]]

    return pd.DataFrame(
        values,
        columns=FEATURE_NAMES,
    )


def run_prediction(input_df, productivity_model, burnout_model):
    productivity_prediction = productivity_model.predict(
        input_df
    )[0]

    productivity_probabilities = (
        productivity_model.predict_proba(input_df)[0]
    )

    productivity_probability = (
        productivity_probabilities.max() * 100
    )

    burnout_prediction = burnout_model.predict(
        input_df
    )[0]

    burnout_probabilities = (
        burnout_model.predict_proba(input_df)[0]
    )

    burnout_probability = (
        burnout_probabilities.max() * 100
    )

    productivity_score, burnout_score, aura_score = (
        calculate_aura_score(
            productivity_prediction,
            burnout_prediction,
        )
    )

    aura_status, score_message = get_aura_status(
        aura_score
    )

    return {
        "productivity_prediction": productivity_prediction,
        "productivity_probabilities": productivity_probabilities,
        "productivity_probability": productivity_probability,
        "burnout_prediction": burnout_prediction,
        "burnout_probabilities": burnout_probabilities,
        "burnout_probability": burnout_probability,
        "productivity_score": productivity_score,
        "burnout_score": burnout_score,
        "aura_score": aura_score,
        "aura_status": aura_status,
        "score_message": score_message,
    }


# ============================================================
# LOGIN PAGE
# ============================================================

def render_login_page():
    # This function is called ONLY before authentication.
    # No dashboard, analysis, history or sidebar is rendered here.

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:4rem 0 1rem;
        ">
            <div style="font-size:4.5rem;">🧠</div>
            <h1 style="
                font-size:3.5rem;
                margin:0;
                font-weight:800;
            ">
                AURA
            </h1>
            <h3>
                Adaptive User Resilience & Analytics
            </h3>
            <p>
                AI-powered behavioral intelligence for
                productivity, resilience and workload awareness.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    left, center, right = st.columns([1, 2, 1])

    with center:
        login_tab, signup_tab = st.tabs(
            ["🔐 Login", "📝 Sign Up"]
        )

        with login_tab:
            st.markdown("### 🔐 Login to AURA")

            username = st.text_input(
                "Username",
                key="login_username",
                placeholder="Enter your username",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
                placeholder="Enter your password",
            )

            if st.button(
                "🚀 Login",
                use_container_width=True,
                type="primary",
            ):
                if not username.strip() or not password:
                    st.error(
                        "Please enter both username and password."
                    )
                else:
                    login_ok, login_role = authenticate(
                        username,
                        password,
                    )

                    if login_ok:
                        st.session_state.authenticated = True
                        st.session_state.current_user = username.strip()
                        st.session_state.current_role = login_role
                        st.session_state.page = "Home"
                        st.session_state.analysis_done = False
                        st.session_state.analysis_result = None
                        st.session_state.whatif_result = None
                        st.session_state.pop("aura_navigation", None)
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

            st.caption(
                "AURA uses a persistent authentication backend. New sign-ups are standard users."
            )

        with signup_tab:
            st.markdown(
                "### 📝 Create your AURA account"
            )

            new_username = st.text_input(
                "Choose Username",
                key="signup_username",
                placeholder="Minimum 3 characters",
            )

            new_password = st.text_input(
                "Create Password",
                type="password",
                key="signup_password",
                placeholder="Minimum 8 characters",
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                key="signup_confirm",
            )

            if st.button(
                "✨ Create Account",
                use_container_width=True,
                type="primary",
            ):
                if len(new_username.strip()) < 3:
                    st.error(
                        "Username must contain at least 3 characters."
                    )

                elif len(new_password) < 8:
                    st.error(
                        "Password must contain at least 8 characters."
                    )

                elif new_password != confirm_password:
                    st.error(
                        "Passwords do not match."
                    )

                else:
                    ok, message = create_user(
                        new_username,
                        new_password,
                    )

                    if ok:
                        st.success(
                            message + " Please log in."
                        )
                    else:
                        st.error(message)

# ============================================================
# ADMIN ACCESS
# ============================================================

current_role = st.session_state.get("current_role")
is_admin = str(current_role or "").strip().lower() == "admin"

# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    with st.sidebar:
        st.markdown("<div style=\"font-size:25px;font-weight:800;letter-spacing:-.5px;\">🧠 AURA</div><div style=\"font-size:12px;color:var(--aura-muted);margin-bottom:14px;\">Adaptive User Resilience & Analytics</div>", unsafe_allow_html=True)

        # ============================================================
        # APPEARANCE / THEME BUTTON
        # ============================================================

        st.markdown(
            """
            <div class="sidebar-section-label">
                🎨 Appearance
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.theme_mode == "Light":

            if st.button(
                "🌙  Dark Mode",
                use_container_width=True,
                key="theme_dark_button",
            ):
                st.session_state.theme_mode = "Dark"
                st.rerun()

        else:

            if st.button(
                "☀️  Light Mode",
                use_container_width=True,
                key="theme_light_button",
            ):
                st.session_state.theme_mode = "Light"
                st.rerun()
        st.divider()

        st.markdown(f"<div style=\"padding:13px 14px;border:1px solid var(--aura-border);border-radius:14px;background:var(--aura-surface-2);margin-bottom:12px;\"><div style=\"font-weight:700;\">👤 {st.session_state.current_user}</div><div style=\"color:var(--aura-muted);font-size:12px;margin-top:3px;\">{'Administrator' if is_admin else 'Active user'}</div></div>", unsafe_allow_html=True)

        pages=["Home","AURA Analysis","Treatment","History","About"]
        if is_admin:
            if st.button("👑 Admin Panel",key="nav_admin_panel",use_container_width=True,type="primary" if st.session_state.page=="Admin Panel" else "secondary"):
                st.session_state.page="Admin Panel"; st.session_state.whatif_result=None; st.rerun()
        for page in pages:
            is_current=st.session_state.page==page
            if st.button(f"● {page}" if is_current else page,key=f"nav_{page.replace(' ','_').replace('&','and')}",use_container_width=True,type="primary" if is_current else "secondary"):
                st.session_state.page=page
                if page != "AURA Analysis": st.session_state.whatif_result=None
                st.rerun()
        st.divider()
        if st.button("🚪 Logout",key="sidebar_logout",use_container_width=True,type="secondary"):
            logout_user()
        st.divider()
        st.caption("Your analysis history is separated by account.")

# ============================================================
# DAILY ANALYSIS PAGE
# ============================================================

def render_daily_page(
    productivity_model,
    burnout_model,
):
    # ============================================================
    # PROFESSIONAL DAILY ANALYSIS HEADER
    # ============================================================

    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-icon">🧠</div>
            <div>
                <h1>Daily Analysis</h1>
                <p>
                    Analyze your daily behavioral patterns and generate
                    personalized AURA insights.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>📊 Today's Behavioral Assessment</strong>
                <br>
                <span>
                    Enter your current lifestyle, productivity and
                    behavioral metrics below.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ============================================================
    # DAILY METRICS — PROFESSIONAL 4-SECTION LAYOUT
    # ============================================================

    st.markdown("### 📋 Daily Metrics")

    # ============================================================
    # SECTION 1 — RECOVERY & WELLNESS
    # ============================================================

    st.markdown(
        """
        <div class="analysis-section">
            <div class="section-title">🛌 Recovery & Wellness</div>
            <div class="section-subtitle">
                Sleep, stress and daily recovery indicators
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        sleep_hours = st.number_input(
            "Sleep Hours",
            min_value=0.0,
            max_value=12.0,
            value=7.0,
            step=0.5,
            key="daily_sleep",
        )

    with col2:
        stress_level = st.slider(
            "Stress Level",
            0.0,
            10.0,
            5.0,
            key="daily_stress",
        )

    with col3:
        screen_time = st.number_input(
            "Screen Time (Hours)",
            min_value=0.0,
            max_value=24.0,
            value=6.0,
            step=0.5,
            key="daily_screen",
        )

    col1, col2 = st.columns(2)

    with col1:
        workload = st.slider(
            "Workload",
            0.0,
            10.0,
            5.0,
            key="daily_workload",
        )

    with col2:
        break_frequency = st.slider(
            "Break Frequency",
            0.0,
            10.0,
            5.0,
            key="daily_breaks",
        )

    st.divider()

    # ============================================================
    # SECTION 2 — PRODUCTIVITY & FOCUS
    # ============================================================

    st.markdown(
        """
        <div class="analysis-section">
            <div class="section-title">🎯 Productivity & Focus</div>
            <div class="section-subtitle">
                Mood, study habits and task performance
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        mood_score = st.slider(
            "Mood Score",
            0.0,
            10.0,
            5.0,
            key="daily_mood",
        )

    with col2:
        study_hours = st.number_input(
            "Study Hours",
            min_value=0.0,
            max_value=16.0,
            value=5.0,
            step=0.5,
            key="daily_study",
        )

    with col3:
        focus_sessions = st.number_input(
            "Focus Sessions",
            min_value=0,
            max_value=20,
            value=5,
            key="daily_focus",
        )

    col1, col2 = st.columns(2)

    with col1:
        energy_level = st.slider(
            "Energy Level",
            0.0,
            10.0,
            5.0,
            key="daily_energy",
        )

    with col2:
        task_completion_rate = st.slider(
            "Task Completion Rate (%)",
            0.0,
            100.0,
            70.0,
            key="daily_completion",
        )

    st.divider()

    # ============================================================
    # SECTION 3 — DIGITAL & LIFESTYLE
    # ============================================================

    st.markdown(
        """
        <div class="analysis-section">
            <div class="section-title">📱 Digital & Lifestyle</div>
            <div class="section-subtitle">
                Digital activity, physical activity and hydration
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        social_media_time = st.number_input(
            "Social Media Time (Hours)",
            min_value=0.0,
            max_value=24.0,
            value=2.0,
            step=0.5,
            key="daily_social",
        )

    with col2:
        physical_activity = st.number_input(
            "Physical Activity (Hours)",
            min_value=0.0,
            max_value=10.0,
            value=1.0,
            step=0.5,
            key="daily_activity",
        )

    with col3:
        water_intake = st.number_input(
            "Water Intake (Litres)",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            key="daily_water",
        )

    st.divider()

    # ============================================================
    # SECTION 4 — PRESSURE & PERFORMANCE
    # ============================================================

    st.markdown(
        """
        <div class="analysis-section">
            <div class="section-title">⚡ Pressure & Performance</div>
            <div class="section-subtitle">
                Deadline pressure and physiological performance
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        deadline_pressure = st.slider(
            "Deadline Pressure",
            0.0,
            10.0,
            5.0,
            key="daily_deadline",
        )

    with col2:
        heart_rate = st.number_input(
            "Heart Rate",
            min_value=40.0,
            max_value=180.0,
            value=75.0,
            step=1.0,
            key="daily_heart",
        )

    st.divider()

    # ============================================================
    # AURA ANALYSIS — PROFESSIONAL CTA
    # ============================================================

    st.markdown(
        """
        <div class="analysis-cta">
            <div class="cta-icon">🤖</div>
            <div class="cta-content">
                <div class="cta-title">Ready to analyze your day?</div>
                <div class="cta-description">
                    AURA will evaluate your behavioral patterns, estimate
                    productivity and burnout levels, calculate your overall
                    AURA score, and generate personalized recommendations.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "🔍  Analyze My AURA",
        use_container_width=True,
        type="primary",
        key="daily_analyze_aura",
    ):

        input_df = make_model_input(
            sleep_hours,
            stress_level,
            screen_time,
            workload,
            break_frequency,
            mood_score,
            physical_activity,
            water_intake,
            study_hours,
            focus_sessions,
            social_media_time,
            deadline_pressure,
            heart_rate,
            energy_level,
            task_completion_rate,
        )

        prediction = run_prediction(
            input_df,
            productivity_model,
            burnout_model,
        )

        recommendations = generate_recommendations(
            stress_level,
            sleep_hours,
            screen_time,
            workload,
            break_frequency,
            mood_score,
            energy_level,
            task_completion_rate,
            prediction["burnout_prediction"],
            prediction["productivity_prediction"],
        )

        analysis_result = {
            "input_df": input_df,
            "sleep_hours": sleep_hours,
            "stress_level": stress_level,
            "screen_time": screen_time,
            "workload": workload,
            "break_frequency": break_frequency,
            "mood_score": mood_score,
            "physical_activity": physical_activity,
            "water_intake": water_intake,
            "study_hours": study_hours,
            "focus_sessions": focus_sessions,
            "social_media_time": social_media_time,
            "deadline_pressure": deadline_pressure,
            "heart_rate": heart_rate,
            "energy_level": energy_level,
            "task_completion_rate": task_completion_rate,

            **prediction,

            "recommendations": recommendations,
            "recommendations_count": len(recommendations),
        }

        st.session_state.analysis_done = True
        st.session_state.analysis_result = analysis_result
        st.session_state.whatif_result = None

        save_history(analysis_result)

        st.success(
            "✅ AURA analysis completed and saved to your history."
        )

    # ============================================================
    # DISPLAY CURRENT ANALYSIS
    # ============================================================

    if st.session_state.analysis_done:
        result = st.session_state.analysis_result

        if result is not None:
            render_current_analysis(
                result,
                productivity_model,
                burnout_model,
            )

# ============================================================
# CURRENT ANALYSIS RESULT
# ============================================================

def render_current_analysis(
    result,
    productivity_model,
    burnout_model,
):
    productivity = result["productivity_prediction"]
    burnout = result["burnout_prediction"]

    productivity_probability = (
        result["productivity_probability"]
    )
    burnout_probability = (
        result["burnout_probability"]
    )

    productivity_score = result["productivity_score"]
    burnout_score = result["burnout_score"]

    aura_score = result["aura_score"]
    aura_status = result["aura_status"]
    score_message = result["score_message"]

    recommendations = result["recommendations"]

    # --------------------------------------------------------
    # OVERALL SCORE
    # --------------------------------------------------------

    st.divider()
    st.subheader("🧠 AURA Overall Score")

    score_col1, score_col2 = st.columns([2, 1])

    with score_col1:
        st.metric(
            "AURA Resilience Score",
            f"{aura_score:.0f}/100",
        )

        st.progress(
            min(max(int(aura_score), 0), 100)
        )

        st.caption(score_message)

    with score_col2:
        if aura_score >= 75:
            st.success(
                f"✅ Status: {aura_status}"
            )
        elif aura_score >= 50:
            st.warning(
                f"⚠️ Status: {aura_status}"
            )
        else:
            st.error(
                f"⚠️ Status: {aura_status}"
            )

    # --------------------------------------------------------
    # ASSESSMENT
    # --------------------------------------------------------

    st.divider()
    st.subheader("🎯 AURA Assessment")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Productivity",
            productivity,
            f"{productivity_probability:.1f}% confidence",
        )

    with c2:
        st.metric(
            "Burnout Risk",
            burnout,
            f"{burnout_probability:.1f}% confidence",
        )

    with c3:
        st.metric(
            "AURA Score",
            f"{aura_score:.0f}/100",
        )

    # --------------------------------------------------------
    # SCORE BREAKDOWN
    # --------------------------------------------------------

    st.divider()
    st.subheader("📊 AURA Score Breakdown")

    productivity_contribution = (
        productivity_score * 0.60
    )
    burnout_contribution = (
        burnout_score * 0.40
    )

    b1, b2 = st.columns(2)

    with b1:
        st.markdown(
            "### 🎯 Productivity Contribution"
        )

        st.metric(
            "Productivity Score",
            f"{productivity_score}/100",
        )

        st.progress(
            min(max(int(productivity_score), 0), 100)
        )

        st.caption(
            f"60% weight → "
            f"{productivity_contribution:.0f} points"
        )

    with b2:
        st.markdown(
            "### 🛡️ Burnout Resilience"
        )

        st.metric(
            "Burnout Score",
            f"{burnout_score}/100",
        )

        st.progress(
            min(max(int(burnout_score), 0), 100)
        )

        st.caption(
            f"40% weight → "
            f"{burnout_contribution:.0f} points"
        )

    st.info(
        f"🧠 Final AURA Score = "
        f"{productivity_contribution:.0f} + "
        f"{burnout_contribution:.0f} = "
        f"{aura_score:.0f}/100"
    )

    # --------------------------------------------------------
    # INSIGHTS
    # --------------------------------------------------------

    st.divider()
    st.subheader("🔍 AURA Insights")

    st.write(
        "The trained machine learning models identified the "
        "following features as the most influential factors."
    )

    productivity_importance = pd.DataFrame({
        "Feature": DISPLAY_FEATURE_NAMES,
        "Importance": productivity_model.feature_importances_,
    }).sort_values(
        "Importance",
        ascending=False,
    ).head(5)

    burnout_importance = pd.DataFrame({
        "Feature": DISPLAY_FEATURE_NAMES,
        "Importance": burnout_model.feature_importances_,
    }).sort_values(
        "Importance",
        ascending=False,
    ).head(5)

    i1, i2 = st.columns(2)

    with i1:
        st.markdown("### 📈 Productivity Drivers")

        for _, row in productivity_importance.iterrows():
            importance = float(row["Importance"])

            st.write(
                f"**{row['Feature']}** — "
                f"{importance * 100:.1f}% importance"
            )

            st.progress(
                min(max(int(importance * 100), 0), 100)
            )

    with i2:
        st.markdown("### ⚠️ Burnout Drivers")

        for _, row in burnout_importance.iterrows():
            importance = float(row["Importance"])

            st.write(
                f"**{row['Feature']}** — "
                f"{importance * 100:.1f}% importance"
            )

            st.progress(
                min(max(int(importance * 100), 0), 100)
            )

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    st.divider()
    st.subheader(
        "💡 Personalized AURA Recommendations"
    )

    for recommendation in recommendations:
        st.info("💡 " + recommendation)

    # --------------------------------------------------------
    # PROBABILITIES
    # --------------------------------------------------------

    st.divider()
    st.subheader("📊 Prediction Probability")

    productivity_probability_df = pd.DataFrame({
        "Class": productivity_model.classes_,
        "Probability": (
            result["productivity_probabilities"] * 100
        ),
    })

    burnout_probability_df = pd.DataFrame({
        "Class": burnout_model.classes_,
        "Probability": (
            result["burnout_probabilities"] * 100
        ),
    })

    p1, p2 = st.columns(2)

    with p1:
        st.markdown(
            "### 📈 Productivity Probability"
        )

        st.bar_chart(
            productivity_probability_df.set_index(
                "Class"
            )
        )

        display_df = productivity_probability_df.copy()

        display_df["Probability"] = (
            display_df["Probability"]
            .round(1)
            .astype(str)
            + "%"
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

    with p2:
        st.markdown(
            "### ⚠️ Burnout Probability"
        )

        st.bar_chart(
            burnout_probability_df.set_index(
                "Class"
            )
        )

        display_df = burnout_probability_df.copy()

        display_df["Probability"] = (
            display_df["Probability"]
            .round(1)
            .astype(str)
            + "%"
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

# ============================================================
# PHASE 7 — STEP 1
# 🤖 AURA SMART INSIGHTS ENGINE
# ============================================================

def generate_smart_insights(result):
    """
    Generate rule-based smart insights from the latest
    AURA analysis result.

    This engine converts behavioral metrics into
    understandable, personalized insights.
    """

    insights = []

    # --------------------------------------------------------
    # GET VALUES SAFELY
    # --------------------------------------------------------

    sleep = float(result.get("sleep_hours", 0))
    stress = float(result.get("stress_level", 0))
    screen_time = float(result.get("screen_time", 0))
    workload = float(result.get("workload", 0))
    breaks = float(result.get("break_frequency", 0))
    mood = float(result.get("mood_score", 0))
    activity = float(result.get("physical_activity", 0))
    water = float(result.get("water_intake", 0))
    study = float(result.get("study_hours", 0))
    focus = float(result.get("focus_sessions", 0))
    social_media = float(result.get("social_media_time", 0))
    deadline = float(result.get("deadline_pressure", 0))
    heart_rate = float(result.get("heart_rate", 0))
    energy = float(result.get("energy_level", 0))
    completion = float(
        result.get("task_completion_rate", 0)
    )

    productivity = str(
        result.get(
            "productivity_prediction",
            "Unknown",
        )
    )

    burnout = str(
        result.get(
            "burnout_prediction",
            "Unknown",
        )
    )

    aura_score = float(
        result.get(
            "aura_score",
            0,
        )
    )

    # ========================================================
    # RECOVERY INSIGHTS
    # ========================================================

    if sleep < 6:
        insights.append({
            "category": "Recovery",
            "icon": "😴",
            "title": "Sleep Recovery",
            "message": (
                "Your recorded sleep duration is relatively low. "
                "Consistent recovery may help support energy, focus "
                "and daily performance."
            ),
            "priority": "High",
        })

    elif sleep >= 7:
        insights.append({
            "category": "Recovery",
            "icon": "😴",
            "title": "Sleep Pattern",
            "message": (
                "Your recorded sleep duration is supporting a "
                "stronger recovery pattern."
            ),
            "priority": "Positive",
        })

    # ========================================================
    # STRESS INSIGHTS
    # ========================================================

    if stress >= 8:
        insights.append({
            "category": "Stress",
            "icon": "😰",
            "title": "High Stress",
            "message": (
                "Stress is currently elevated. Reducing unnecessary "
                "pressure and including recovery breaks may help "
                "maintain daily balance."
            ),
            "priority": "High",
        })

    elif stress >= 6:
        insights.append({
            "category": "Stress",
            "icon": "⚠️",
            "title": "Moderate Stress",
            "message": (
                "Your stress level is moderately elevated. "
                "Monitoring workload and recovery can help prevent "
                "further strain."
            ),
            "priority": "Medium",
        })

    elif stress <= 3:
        insights.append({
            "category": "Stress",
            "icon": "😌",
            "title": "Low Stress",
            "message": (
                "Your current stress level is relatively low, "
                "which supports a more balanced behavioral pattern."
            ),
            "priority": "Positive",
        })

    # ========================================================
    # WORKLOAD INSIGHTS
    # ========================================================

    if workload >= 8:
        insights.append({
            "category": "Workload",
            "icon": "💼",
            "title": "High Workload",
            "message": (
                "Your workload is currently high. Prioritizing "
                "essential tasks and avoiding unnecessary workload "
                "may improve balance."
            ),
            "priority": "High",
        })

    elif workload <= 4:
        insights.append({
            "category": "Workload",
            "icon": "⚖️",
            "title": "Manageable Workload",
            "message": (
                "Your current workload appears relatively manageable, "
                "providing room for focused and consistent work."
            ),
            "priority": "Positive",
        })

    # ========================================================
    # ENERGY INSIGHTS
    # ========================================================

    if energy <= 3:
        insights.append({
            "category": "Energy",
            "icon": "🔋",
            "title": "Low Energy",
            "message": (
                "Energy levels are currently low. Recovery, adequate "
                "rest and manageable workload may support better "
                "daily performance."
            ),
            "priority": "High",
        })

    elif energy >= 8:
        insights.append({
            "category": "Energy",
            "icon": "⚡",
            "title": "Strong Energy",
            "message": (
                "Your energy level is relatively strong, providing "
                "a favorable foundation for focused activities."
            ),
            "priority": "Positive",
        })

    # ========================================================
    # TASK PERFORMANCE
    # ========================================================

    if completion < 40:
        insights.append({
            "category": "Performance",
            "icon": "📉",
            "title": "Low Task Completion",
            "message": (
                "Task completion is currently low. Breaking larger "
                "tasks into smaller achievable steps may make progress "
                "more manageable."
            ),
            "priority": "High",
        })

    elif completion >= 80:
        insights.append({
            "category": "Performance",
            "icon": "✅",
            "title": "Strong Task Completion",
            "message": (
                "You completed a high proportion of your planned "
                "tasks, indicating strong execution during this period."
            ),
            "priority": "Positive",
        })

    # ========================================================
    # FOCUS INSIGHTS
    # ========================================================

    if focus <= 2:
        insights.append({
            "category": "Focus",
            "icon": "🎯",
            "title": "Limited Focus Sessions",
            "message": (
                "Your number of focused work sessions is relatively "
                "low. Short, distraction-free sessions may help "
                "improve consistency."
            ),
            "priority": "Medium",
        })

    elif focus >= 8:
        insights.append({
            "category": "Focus",
            "icon": "🎯",
            "title": "Strong Focus Activity",
            "message": (
                "You recorded several focused sessions, suggesting "
                "good engagement with planned activities."
            ),
            "priority": "Positive",
        })

    # ========================================================
    # SCREEN TIME
    # ========================================================

    if screen_time >= 10:
        insights.append({
            "category": "Digital",
            "icon": "📱",
            "title": "High Screen Time",
            "message": (
                "Screen time is relatively high. Adding short "
                "screen-free intervals may support better daily balance."
            ),
            "priority": "Medium",
        })

    # ========================================================
    # SOCIAL MEDIA
    # ========================================================

    if social_media >= 4:
        insights.append({
            "category": "Digital",
            "icon": "📱",
            "title": "High Social Media Exposure",
            "message": (
                "Social media usage is relatively high compared with "
                "a balanced daily routine. Consider protecting focused "
                "work periods from unnecessary digital interruptions."
            ),
            "priority": "Medium",
        })

    # ========================================================
    # BREAKS
    # ========================================================

    if breaks <= 2:
        insights.append({
            "category": "Recovery",
            "icon": "☕",
            "title": "Limited Breaks",
            "message": (
                "You recorded relatively few breaks. Regular short "
                "pauses can help maintain focus during demanding tasks."
            ),
            "priority": "Medium",
        })

    # ========================================================
    # MOOD
    # ========================================================

    if mood <= 3:
        insights.append({
            "category": "Wellbeing",
            "icon": "🌧️",
            "title": "Low Mood Score",
            "message": (
                "Your recorded mood score is relatively low. "
                "Balancing workload with recovery and enjoyable "
                "activities may support a healthier routine."
            ),
            "priority": "Medium",
        })

    elif mood >= 8:
        insights.append({
            "category": "Wellbeing",
            "icon": "🌟",
            "title": "Positive Mood",
            "message": (
                "Your current mood score is strong, which contributes "
                "to a more positive overall behavioral pattern."
            ),
            "priority": "Positive",
        })

    # ========================================================
    # DEADLINE PRESSURE
    # ========================================================

    if deadline >= 8:
        insights.append({
            "category": "Pressure",
            "icon": "⏰",
            "title": "High Deadline Pressure",
            "message": (
                "Deadline pressure is elevated. Prioritizing the most "
                "important tasks first may help reduce unnecessary pressure."
            ),
            "priority": "High",
        })

    # ========================================================
    # HYDRATION
    # ========================================================

    if water < 1:
        insights.append({
            "category": "Lifestyle",
            "icon": "💧",
            "title": "Low Recorded Water Intake",
            "message": (
                "Your recorded water intake is relatively low. "
                "Maintaining regular hydration throughout the day "
                "may support your general routine."
            ),
            "priority": "Medium",
        })

    # ========================================================
    # PHYSICAL ACTIVITY
    # ========================================================

    if activity >= 1:
        insights.append({
            "category": "Lifestyle",
            "icon": "🏃",
            "title": "Physical Activity",
            "message": (
                "You recorded physical activity today, adding a "
                "positive lifestyle component to your behavioral profile."
            ),
            "priority": "Positive",
        })

    # ========================================================
    # PRODUCTIVITY + BURNOUT COMBINATION
    # ========================================================

    if productivity == "High" and burnout == "Safe":
        insights.append({
            "category": "Overall",
            "icon": "🌟",
            "title": "Balanced Performance",
            "message": (
                "Your current prediction shows strong productivity "
                "alongside a safer burnout profile."
            ),
            "priority": "Positive",
        })

    elif productivity == "High" and burnout in {
        "Warning",
        "Critical",
    }:
        insights.append({
            "category": "Overall",
            "icon": "⚠️",
            "title": "Performance–Recovery Imbalance",
            "message": (
                "Productivity is currently strong, but the burnout "
                "prediction suggests that maintaining recovery and "
                "workload balance is important."
            ),
            "priority": "High",
        })

    elif productivity == "Low" and burnout == "Critical":
        insights.append({
            "category": "Overall",
            "icon": "🚨",
            "title": "Multiple Pressure Signals",
            "message": (
                "Both productivity and burnout indicators require "
                "attention. Recovery, workload balance and realistic "
                "task planning should be prioritized."
            ),
            "priority": "High",
        })

    elif productivity == "Low":
        insights.append({
            "category": "Overall",
            "icon": "🎯",
            "title": "Productivity Opportunity",
            "message": (
                "The current productivity prediction suggests that "
                "task planning, focus and recovery patterns may be "
                "useful areas to review."
            ),
            "priority": "Medium",
        })

    # ========================================================
    # AURA SCORE INSIGHT
    # ========================================================

    if aura_score >= 80:
        insights.append({
            "category": "AURA",
            "icon": "🏆",
            "title": "Strong AURA Score",
            "message": (
                f"Your current AURA score is {aura_score:.0f}/100, "
                "indicating a strong overall behavioral profile."
            ),
            "priority": "Positive",
        })

    elif aura_score >= 60:
        insights.append({
            "category": "AURA",
            "icon": "📊",
            "title": "Moderate AURA Score",
            "message": (
                f"Your current AURA score is {aura_score:.0f}/100. "
                "Consistent improvements in key behavioral areas "
                "may strengthen your overall score."
            ),
            "priority": "Medium",
        })

    else:
        insights.append({
            "category": "AURA",
            "icon": "🔎",
            "title": "AURA Needs Attention",
            "message": (
                f"Your current AURA score is {aura_score:.0f}/100. "
                "Recovery, workload balance and daily consistency "
                "are useful areas to review."
            ),
            "priority": "High",
        })

    # ========================================================
    # FALLBACK
    # ========================================================

    if not insights:
        insights.append({
            "category": "Overall",
            "icon": "🧠",
            "title": "Balanced Pattern",
            "message": (
                "No major behavioral concerns were identified "
                "from the current recorded metrics."
            ),
            "priority": "Positive",
        })

    return insights

# ============================================================
# PHASE 7 — SMART INSIGHTS DISPLAY
# ============================================================

def render_smart_insights(result):
    """Render the rule-based AURA Smart Insights Engine."""
    st.divider()
    st.markdown("### 🤖 AURA Smart Insights Engine")
    st.caption(
        "Automatically generated insights based on your latest "
        "behavioral and AURA analysis."
    )

    smart_insights = generate_smart_insights(result)

    high_priority = [
        item for item in smart_insights if item["priority"] == "High"
    ]
    medium_priority = [
        item for item in smart_insights if item["priority"] == "Medium"
    ]
    positive_insights = [
        item for item in smart_insights if item["priority"] == "Positive"
    ]

    if high_priority:
        st.markdown("#### ⚠️ Priority Insights")
        for insight in high_priority:
            st.warning(
                f"{insight['icon']} **{insight['title']}**\n\n"
                f"{insight['message']}"
            )

    if medium_priority:
        st.markdown("#### 🔎 Areas to Monitor")
        insight_cols = st.columns(2)
        for index, insight in enumerate(medium_priority):
            with insight_cols[index % 2]:
                st.info(
                    f"{insight['icon']} **{insight['title']}**\n\n"
                    f"{insight['message']}"
                )

    if positive_insights:
        st.markdown("#### 🌟 Positive Signals")
        for insight in positive_insights:
            st.success(
                f"{insight['icon']} **{insight['title']}**\n\n"
                f"{insight['message']}"
            )

    st.caption(
        f"🧠 AURA identified {len(smart_insights)} behavioral "
        f"insight(s) from this analysis."
    )
    st.caption(
        "ℹ️ Smart Insights are rule-based interpretations of recorded "
        "behavioral metrics and are not medical or psychological diagnoses."
    )


# ============================================================
# PHASE 8 — PROFESSIONAL REPORT & EXPORT
# ============================================================

def render_aura_report(result):
    """Render and export a structured report for the current analysis."""
    st.divider()

    st.markdown("### 📄 AURA Report")
    st.caption(
        "Structured summary of your behavioral inputs, machine-learning "
        "predictions, AURA score and personalized recommendations."
    )

    productivity = result["productivity_prediction"]
    burnout = result["burnout_prediction"]
    productivity_probability = float(result["productivity_probability"])
    burnout_probability = float(result["burnout_probability"])
    productivity_score = result["productivity_score"]
    burnout_score = result["burnout_score"]
    aura_score = float(result["aura_score"])
    aura_status = result["aura_status"]
    recommendations = result.get("recommendations", [])

    report_data = {
        "Metric": [
            "Sleep Hours", "Stress Level", "Screen Time", "Workload",
            "Break Frequency", "Mood Score", "Physical Activity",
            "Water Intake", "Study Hours", "Focus Sessions",
            "Social Media Time", "Deadline Pressure", "Heart Rate",
            "Energy Level", "Task Completion Rate",
            "Productivity Prediction", "Productivity Confidence",
            "Burnout Prediction", "Burnout Confidence",
            "Productivity Score", "Burnout Resilience Score",
            "AURA Score", "AURA Status", "Analysis Type",
            "Recommendations Generated",
        ],
        "Value": [
            result.get("sleep_hours"), result.get("stress_level"),
            result.get("screen_time"), result.get("workload"),
            result.get("break_frequency"), result.get("mood_score"),
            result.get("physical_activity"), result.get("water_intake"),
            result.get("study_hours"), result.get("focus_sessions"),
            result.get("social_media_time"), result.get("deadline_pressure"),
            result.get("heart_rate"), result.get("energy_level"),
            result.get("task_completion_rate"), productivity,
            f"{productivity_probability:.1f}%", burnout,
            f"{burnout_probability:.1f}%", productivity_score,
            burnout_score, f"{aura_score:.0f}/100", aura_status,
            "Machine Learning Analysis", len(recommendations),
        ],
    }

    report_df = pd.DataFrame(report_data)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🧠 AURA Score", f"{aura_score:.0f}/100")
    c2.metric("🎯 Productivity", productivity)
    c3.metric("🛡️ Burnout", burnout)
    c4.metric("📌 Status", aura_status)

    st.markdown("#### 📋 Detailed Analysis Report")
    st.dataframe(report_df, use_container_width=True, hide_index=True)

    st.markdown("#### 💡 Personalized Recommendations")
    if recommendations:
        for index, recommendation in enumerate(recommendations, start=1):
            st.info(f"**{index}.** {recommendation}")
    else:
        st.success("✅ No additional recommendations were generated.")

    st.download_button(
        label="📥 Download AURA Report (CSV)",
        data=report_df.to_csv(index=False),
        file_name=f"AURA_Report_{st.session_state.current_user}.csv",
        mime="text/csv",
        use_container_width=True,
        key="download_aura_report",
    )


# ============================================================
# EXPLAINABILITY
# ============================================================

def render_explainability(result):
    st.divider()
    st.subheader(
        "🧠 Why did AURA make this prediction?"
    )

    productivity = result["productivity_prediction"]
    burnout = result["burnout_prediction"]

    stress = result["stress_level"]
    sleep = result["sleep_hours"]
    workload = result["workload"]
    energy = result["energy_level"]
    completion = result["task_completion_rate"]
    screen = result["screen_time"]

    st.markdown("### 🎯 Productivity Prediction")

    productivity_reasons = []

    if productivity == "Low":
        if completion < 50:
            productivity_reasons.append(
                "Task completion rate is relatively low."
            )

        if energy <= 4:
            productivity_reasons.append(
                "Energy level is relatively low."
            )

        if stress >= 7:
            productivity_reasons.append(
                "Stress level is relatively high."
            )

        if workload >= 8:
            productivity_reasons.append(
                "Workload is relatively high."
            )

        if sleep < 6:
            productivity_reasons.append(
                "Sleep duration is relatively low."
            )

    elif productivity == "Medium":
        if completion >= 50:
            productivity_reasons.append(
                "Task completion rate is supporting moderate productivity."
            )

        if energy > 4:
            productivity_reasons.append(
                "Energy level is supporting productivity."
            )

        if stress >= 7:
            productivity_reasons.append(
                "Higher stress may be limiting productivity."
            )

        if workload >= 8:
            productivity_reasons.append(
                "Higher workload may be affecting productivity."
            )

    else:
        if completion >= 70:
            productivity_reasons.append(
                "Strong task completion is supporting productivity."
            )

        if energy >= 7:
            productivity_reasons.append(
                "Higher energy level is supporting productivity."
            )

        if stress <= 4:
            productivity_reasons.append(
                "Lower stress level is supporting productivity."
            )

        if sleep >= 7:
            productivity_reasons.append(
                "Adequate sleep duration is supporting productivity."
            )

    if not productivity_reasons:
        productivity_reasons.append(
            "The current combination of behavioral metrics "
            "contributed to this productivity prediction."
        )

    for reason in productivity_reasons:
        st.info("🔹 " + reason)

    st.markdown("### 🛡️ Burnout Risk Prediction")

    burnout_reasons = []

    if burnout == "Critical":
        if stress >= 7:
            burnout_reasons.append(
                "Stress level is relatively high."
            )

        if workload >= 8:
            burnout_reasons.append(
                "Workload is relatively high."
            )

        if sleep < 6:
            burnout_reasons.append(
                "Sleep duration is relatively low."
            )

        if energy <= 4:
            burnout_reasons.append(
                "Energy level is relatively low."
            )

        if screen >= 9:
            burnout_reasons.append(
                "Screen time is relatively high."
            )

    elif burnout == "Warning":
        if stress >= 6:
            burnout_reasons.append(
                "Elevated stress may be contributing to burnout risk."
            )

        if workload >= 7:
            burnout_reasons.append(
                "Higher workload may be contributing to burnout risk."
            )

        if sleep < 6:
            burnout_reasons.append(
                "Lower sleep duration may affect recovery."
            )

        if energy <= 4:
            burnout_reasons.append(
                "Lower energy may indicate reduced recovery."
            )

    else:
        if stress <= 4:
            burnout_reasons.append(
                "Lower stress is supporting a safer burnout profile."
            )

        if sleep >= 7:
            burnout_reasons.append(
                "Adequate sleep is supporting recovery."
            )

        if energy >= 7:
            burnout_reasons.append(
                "Higher energy level is supporting resilience."
            )

        if workload <= 5:
            burnout_reasons.append(
                "Moderate workload is supporting a safer profile."
            )

    if not burnout_reasons:
        burnout_reasons.append(
            "The current combination of behavioral metrics "
            "contributed to this burnout prediction."
        )

    for reason in burnout_reasons:
        st.warning("🔹 " + reason)

    st.caption(
        "ℹ️ These explanations are rule-based interpretations "
        "of recorded metrics. They describe contributing patterns "
        "and do not represent medical or psychological diagnosis."
    )


# ============================================================
# WHAT-IF SIMULATOR PAGE
# ============================================================

def render_whatif_page(
    productivity_model,
    burnout_model,
):

    # ============================================================
    # PROFESSIONAL WHAT-IF SIMULATOR HEADER
    # ============================================================

    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-icon">🧪</div>
            <div>
                <h1>What-If Simulator</h1>
                <p>
                    Explore how changes in your daily habits may influence
                    productivity, burnout resilience and your overall AURA score.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>🔮 Simulate Behavioral Changes</strong>
                <br>
                <span>
                    Adjust selected lifestyle and performance indicators to
                    compare your current state with a hypothetical scenario.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    baseline = st.session_state.analysis_result

    if baseline is None:
        history_df = load_history(
            st.session_state.current_user
        )

        if history_df.empty:
            st.info(
                "Run a Daily Analysis first. "
                "The What-If Simulator needs a baseline."
            )
            return

        latest = history_df.iloc[-1]

        baseline = {
            "sleep_hours": float(latest["Sleep_Hours"]),
            "stress_level": float(latest["Stress_Level"]),
            "screen_time": float(latest["Screen_Time"]),
            "workload": float(latest["Workload"]),
            "energy_level": float(latest["Energy_Level"]),
            "task_completion_rate": float(
                latest["Task_Completion_Rate"]
            ),
        }

    # ============================================================
    # WHAT-IF INPUT COMPARISON
    # ============================================================

    st.markdown("### 🎛️ Scenario Builder")

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>🔄 Current State → What-If Scenario</strong>
                <br>
                <span>
                    Your current values are shown as a baseline. Adjust the
                    scenario values to explore how different habits may affect
                    your AURA outcome.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    current_col, scenario_col = st.columns(2)

    # ============================================================
    # CURRENT STATE
    # ============================================================

    with current_col:

        st.markdown("#### 📌 Current State")

        st.metric(
            "😴 Sleep",
            f"{float(baseline['sleep_hours']):.1f} hrs",
        )

        st.metric(
            "😰 Stress",
            f"{float(baseline['stress_level']):.1f}/10",
        )

        st.metric(
            "💼 Workload",
            f"{float(baseline['workload']):.1f}/10",
        )

        st.metric(
            "⚡ Energy",
            f"{float(baseline['energy_level']):.1f}/10",
        )

        st.metric(
            "📱 Screen Time",
            f"{float(baseline['screen_time']):.1f} hrs",
        )

        st.metric(
            "✅ Task Completion",
            f"{float(baseline['task_completion_rate']):.1f}%",
        )

    # ============================================================
    # WHAT-IF SCENARIO
    # ============================================================

    with scenario_col:

        st.markdown("#### 🔮 What-If Scenario")

        whatif_sleep = st.slider(
            "😴 Sleep Hours",
            0.0,
            12.0,
            float(baseline["sleep_hours"]),
            0.5,
            key="whatif_sleep",
        )

        whatif_stress = st.slider(
            "😰 Stress Level",
            0.0,
            10.0,
            float(baseline["stress_level"]),
            0.5,
            key="whatif_stress",
        )

        whatif_workload = st.slider(
            "💼 Workload",
            0.0,
            10.0,
            float(baseline["workload"]),
            0.5,
            key="whatif_workload",
        )

        whatif_energy = st.slider(
            "⚡ Energy Level",
            0.0,
            10.0,
            float(baseline["energy_level"]),
            0.5,
            key="whatif_energy",
        )

        whatif_screen = st.slider(
            "📱 Screen Time",
            0.0,
            24.0,
            float(baseline["screen_time"]),
            0.5,
            key="whatif_screen",
        )

        whatif_completion = st.slider(
            "✅ Task Completion Rate",
            0.0,
            100.0,
            float(baseline["task_completion_rate"]),
            1.0,
            key="whatif_completion",
        )

    st.divider()

    if st.button(
        "🧪 Run What-If Simulation",
        use_container_width=True,
        type="primary",
    ):
        if (
    st.session_state.analysis_result is not None
    and "input_df" in st.session_state.analysis_result
):
            simulated_input = (
                st.session_state.analysis_result[
                    "input_df"
                ].copy()
            )
        else:
            # Build a baseline from history when the user entered
            # this page without running a fresh analysis.
            history_df = load_history(
                st.session_state.current_user
            )

            if history_df.empty:
                st.error(
                    "No baseline data is available."
                )
                return

            latest = history_df.iloc[-1]

            simulated_input = pd.DataFrame([{
                feature: latest[feature]
                for feature in FEATURE_NAMES
            }])

        simulated_input.loc[
            0, "Sleep_Hours"
        ] = whatif_sleep

        simulated_input.loc[
            0, "Stress_Level"
        ] = whatif_stress

        simulated_input.loc[
            0, "Workload"
        ] = whatif_workload

        simulated_input.loc[
            0, "Energy_Level"
        ] = whatif_energy

        simulated_input.loc[
            0, "Screen_Time"
        ] = whatif_screen

        simulated_input.loc[
            0, "Task_Completion_Rate"
        ] = whatif_completion

        prediction = run_prediction(
            simulated_input,
            productivity_model,
            burnout_model,
        )

        simulated_aura_score = prediction[
            "aura_score"
        ]

        baseline_aura = None

        if st.session_state.analysis_result is not None:
            baseline_aura = float(
                st.session_state.analysis_result[
                    "aura_score"
                ]
            )
        else:
            history_df = load_history(
                st.session_state.current_user
            )

            if not history_df.empty:
                baseline_aura = float(
                    history_df.iloc[-1]["AURA_Score"]
                )

        st.session_state.whatif_result = {
            **prediction,
            "simulated_input": simulated_input,
            "baseline_aura": baseline_aura,
        }

    if st.session_state.whatif_result is not None:
        sim = st.session_state.whatif_result

# ============================================================
# PROFESSIONAL WHAT-IF RESULT
# ============================================================

if st.session_state.whatif_result is not None:

    st.divider()

    st.markdown("### 🔮 Simulation Result")

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>📊 Baseline vs Simulated Outcome</strong>
                <br>
                <span>
                    See how your selected behavioral changes may influence
                    productivity, burnout resilience and your overall AURA score.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sim = st.session_state.whatif_result

    baseline_aura = sim["baseline_aura"]
    simulated_aura = float(sim["aura_score"])

    # ========================================================
    # AURA SCORE COMPARISON
    # ========================================================

    if baseline_aura is not None:

        score_difference = (
            simulated_aura - float(baseline_aura)
        )

        comparison_col1, comparison_col2, comparison_col3 = st.columns(3)

        with comparison_col1:
            st.metric(
                "📌 Current AURA",
                f"{float(baseline_aura):.0f}/100",
            )

        with comparison_col2:
            st.metric(
                "🔮 Simulated AURA",
                f"{simulated_aura:.0f}/100",
                f"{score_difference:+.0f} points",
            )

        with comparison_col3:

            if score_difference > 0:
                status_text = "📈 Improvement"

            elif score_difference < 0:
                status_text = "📉 Decrease"

            else:
                status_text = "➡️ No Change"

            st.metric(
                "Scenario Impact",
                status_text,
            )

    else:

        st.metric(
            "🔮 Simulated AURA",
            f"{simulated_aura:.0f}/100",
        )

    # ========================================================
    # AI PREDICTION
    # ========================================================

    st.markdown("#### 🤖 AI Prediction")

    result_col1, result_col2 = st.columns(2)

    with result_col1:
        st.metric(
            "🎯 Productivity",
            sim["productivity_prediction"],
            f"{sim['productivity_probability']:.1f}% confidence",
        )

    with result_col2:
        st.metric(
            "🛡️ Burnout Risk",
            sim["burnout_prediction"],
            f"{sim['burnout_probability']:.1f}% confidence",
        )

    # ========================================================
    # SCENARIO INTERPRETATION
    # ========================================================

    if baseline_aura is not None:

        st.markdown("#### 💡 Scenario Interpretation")

        score_difference = (
            simulated_aura - float(baseline_aura)
        )

        if score_difference > 0:

            st.success(
                f"📈 This scenario shows a potential AURA improvement "
                f"of {score_difference:.0f} points compared with your "
                f"current baseline."
            )

        elif score_difference < 0:

            st.warning(
                f"📉 This scenario shows a potential AURA decrease "
                f"of {abs(score_difference):.0f} points compared with "
                f"your current baseline."
            )

        else:

            st.info(
                "➡️ This scenario produces the same AURA score as "
                "your current baseline."
            )

    # ============================================================
    # BEFORE vs AFTER COMPARISON
    # ============================================================

    if baseline_aura is not None:

        st.markdown("#### 🔄 Before vs After")

        comparison_df = pd.DataFrame(
            {
                "State": [
                    "Current",
                    "What-If",
                ],
                "AURA Score": [
                    float(baseline_aura),
                    simulated_aura,
                ],
            }
        )

        st.bar_chart(
            comparison_df.set_index("State"),
            use_container_width=True,
        )

    st.caption(
        "ℹ️ What-If simulations are hypothetical and are not saved to history."
    )

# ============================================================
# DASHBOARD PAGE
# ============================================================

def render_dashboard_page():
    """Render the professional AURA dashboard."""

    st.title("🧠 AURA Home")
    st.caption(
        f"Welcome back, {st.session_state.current_user} 👋"
    )

    # IMPORTANT: dashboard data is always restricted to the
    # currently authenticated account.
    history_df = load_history(
        st.session_state.current_user
    )

    # ========================================================
    # EMPTY DASHBOARD
    # ========================================================

    if history_df.empty:
        st.info(
            "No AURA analysis has been recorded yet. "
            "Start your first Daily Analysis to build your dashboard."
        )

        st.divider()
        st.subheader("🚀 Get Started with AURA")

        st.markdown(
            """
            AURA analyzes your behavioral and productivity patterns
            using machine learning to generate:

            - 🎯 Productivity predictions
            - 🛡️ Burnout risk assessment
            - 🧠 AURA resilience score
            - 💡 Personalized recommendations
            - 📈 Long-term behavioral insights
            """
        )

        st.divider()
        st.subheader("⚡ Quick Start")

        q1, q2, q3 = st.columns(3)

        with q1:
            st.markdown("### 📊 Daily Analysis")
            st.caption(
                "Enter your current behavioral and productivity metrics."
            )
            if st.button(
                "Start AURA Analysis →",
                key="dashboard_start_analysis",
                use_container_width=True,
                type="primary",
            ):
                st.session_state.page = "AURA Analysis"
                st.rerun()

        with q2:
            st.markdown("### 📈 History & Trends")
            st.caption(
                "Track your AURA performance over time."
            )
            if st.button(
                "View History →",
                key="dashboard_empty_history",
                use_container_width=True,
            ):
                st.session_state.page = "History"
                st.rerun()

        with q3:
            st.markdown("### ℹ️ About AURA")
            st.caption(
                "View your account and personal AURA summary."
            )
            if st.button(
                "Open About →",
                key="dashboard_empty_profile",
                use_container_width=True,
            ):
                st.session_state.page = "About"
                st.rerun()

        return

    # ========================================================
    # LATEST RECORD
    # ========================================================

    latest = history_df.iloc[-1]
    latest_aura = float(latest["AURA_Score"])
    productivity = str(latest["Productivity"])
    burnout = str(latest["Burnout"])

    # ========================================================
    # TOP METRICS
    # ========================================================

    st.markdown("### 📌 Current Performance")

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("🧠 AURA Score", f"{latest_aura:.0f}/100")

    with m2:
        st.metric("🎯 Productivity", productivity)

    with m3:
        st.metric("🛡️ Burnout Risk", burnout)

    with m4:
        st.metric("📊 Total Analyses", len(history_df))

    # ========================================================
    # STATUS CARD
    # ========================================================

    st.divider()
    st.subheader("🌟 Current AURA Status")

    status_col1, status_col2 = st.columns([2, 1])

    if latest_aura >= 75:
        status = "Stable"
        status_message = (
            "Your current AURA pattern indicates a relatively "
            "stable balance between productivity and resilience."
        )
    elif latest_aura >= 50:
        status = "Watch"
        status_message = (
            "Your current AURA pattern shows areas that may "
            "benefit from attention and consistent monitoring."
        )
    else:
        status = "Needs Attention"
        status_message = (
            "Your current AURA pattern indicates that recovery, "
            "workload balance and daily habits deserve attention."
        )

    with status_col1:
        if status == "Stable":
            st.success(f"### 🟢 {status}\n\n{status_message}")
        elif status == "Watch":
            st.warning(f"### 🟡 {status}\n\n{status_message}")
        else:
            st.error(f"### 🔴 {status}\n\n{status_message}")

    with status_col2:
        st.metric("Latest Score", f"{latest_aura:.0f}/100")
        st.progress(min(max(latest_aura / 100, 0.0), 1.0))

    # ========================================================
    # PERFORMANCE SUMMARY
    # ========================================================

    st.divider()
    st.subheader("📊 Performance Summary")

    average_aura = float(history_df["AURA_Score"].mean())
    highest_aura = float(history_df["AURA_Score"].max())
    lowest_aura = float(history_df["AURA_Score"].min())

    s1, s2, s3 = st.columns(3)
    s1.metric("Average AURA", f"{average_aura:.0f}/100")
    s2.metric("Highest AURA", f"{highest_aura:.0f}/100")
    s3.metric("Lowest AURA", f"{lowest_aura:.0f}/100")

    # ========================================================
    # AURA TREND
    # ========================================================

    st.divider()
    st.subheader("📈 AURA Score Trend")

    if len(history_df) >= 2:
        trend_df = history_df[["AURA_Score"]].copy()
        trend_df.index = range(1, len(trend_df) + 1)
        st.line_chart(trend_df, use_container_width=True)
        st.caption("Your AURA score across completed analyses.")
    else:
        st.info(
            "Run at least two analyses to generate your AURA score trend."
        )

    # ========================================================
    # LATEST ANALYSIS SNAPSHOT
    # ========================================================

    st.divider()
    st.subheader("🔎 Latest Analysis Snapshot")

    snapshot_columns = [
        "Stress_Level",
        "Sleep_Hours",
        "Workload",
        "Energy_Level",
        "Task_Completion_Rate",
        "Screen_Time",
        "Study_Hours",
        "Focus_Sessions",
    ]

    available_snapshot_columns = [
        col for col in snapshot_columns if col in history_df.columns
    ]

    snapshot_labels = {
        "Stress_Level": "😰 Stress",
        "Sleep_Hours": "😴 Sleep",
        "Workload": "💼 Workload",
        "Energy_Level": "⚡ Energy",
        "Task_Completion_Rate": "✅ Task Completion",
        "Screen_Time": "📱 Screen Time",
        "Study_Hours": "📚 Study Hours",
        "Focus_Sessions": "🎯 Focus Sessions",
    }

    snapshot_cols = st.columns(4)

    for index, column in enumerate(available_snapshot_columns[:8]):
        current_col = snapshot_cols[index % 4]
        value = latest[column]

        with current_col:
            if column in {"Sleep_Hours", "Screen_Time", "Study_Hours"}:
                display_value = f"{float(value):.1f} hrs"
            elif column == "Task_Completion_Rate":
                display_value = f"{float(value):.1f}%"
            elif column == "Focus_Sessions":
                display_value = f"{float(value):.0f}"
            else:
                display_value = f"{float(value):.1f}"

            st.metric(
                snapshot_labels.get(column, column),
                display_value,
            )

    # ========================================================
    # QUICK ACTIONS
    # ========================================================

    st.divider()
    st.subheader("⚡ Quick Actions")
    st.caption("Navigate directly to the main AURA modules.")

    action1, action2, action3, action4 = st.columns(4)

    # IMPORTANT: Do NOT modify the `aura_navigation` widget key here.
    # The sidebar radio has already been created in this run. Only
    # update the page state and rerun; the sidebar will follow it.
    with action1:
        if st.button(
            "📊 Daily Analysis",
            key="dashboard_daily_analysis",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.page = "AURA Analysis"
            st.rerun()

    with action2:
        if st.button(
            "📜 History",
            key="dashboard_history",
            use_container_width=True,
        ):
            st.session_state.page = "History"
            st.rerun()

    with action3:
        if st.button(
            "💊 Treatment",
            key="dashboard_treatment",
            use_container_width=True,
        ):
            st.session_state.page = "Treatment"
            st.rerun()

    with action4:
        if st.button(
            "ℹ️ About AURA",
            key="dashboard_about",
            use_container_width=True,
        ):
            st.session_state.page = "About"
            st.rerun()

    # ========================================================
    # RECENT ANALYSES
    # ========================================================

    st.divider()
    st.subheader("🗂️ Recent Analyses")

    recent_columns = [
        "Timestamp",
        "Productivity",
        "Burnout",
        "AURA_Score",
        "Stress_Level",
        "Sleep_Hours",
        "Energy_Level",
        "Task_Completion_Rate",
    ]

    available_recent_columns = [
        col for col in recent_columns if col in history_df.columns
    ]

    recent_df = history_df[available_recent_columns].tail(5).copy()

    st.dataframe(
        recent_df,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "🧠 AURA continuously analyzes your recorded behavioral "
        "patterns to help you monitor productivity, resilience "
        "and workload balance."
    )


# ============================================================
# HISTORY & TRENDS PAGE
# ============================================================

def render_history_dashboard():
    history_df = load_history(
        st.session_state.current_user
    )

    # ============================================================
    # PROFESSIONAL HISTORY & TRENDS HEADER
    # ============================================================

    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-icon">📈</div>
            <div>
                <h1>History & Trends</h1>
                <p>
                    Track your behavioral patterns, AURA scores and
                    progress over time.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>📊 Your Personal Analytics Timeline</strong>
                <br>
                <span>
                    Review previous assessments and understand how your
                    productivity, burnout and AURA score change over time.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    if history_df.empty:
        st.info(
            "No AURA history available yet. "
            "Run your first AURA analysis."
        )
        return

    # ============================================================
    # NUMERIC DATA PREPARATION
    # ============================================================

    numeric_columns = [
        "AURA_Score",
        "Sleep_Hours",
        "Stress_Level",
        "Workload",
        "Energy_Level",
        "Task_Completion_Rate",
        "Screen_Time",
        "Study_Hours",
        "Focus_Sessions",
    ]

    for col in numeric_columns:
        if col in history_df.columns:
            history_df[col] = pd.to_numeric(
                history_df[col],
                errors="coerce",
            )

    productivity_numeric = (
        history_df["Productivity"]
        .map(PRODUCTIVITY_SCORES)
    )

    burnout_numeric = (
        history_df["Burnout"]
        .map(BURNOUT_SCORES)
    )

    # ============================================================
    # PROFESSIONAL HISTORY OVERVIEW
    # ============================================================

    st.markdown("### 📊 Overall AURA Analytics")

    average_aura = history_df["AURA_Score"].mean()
    highest_aura = history_df["AURA_Score"].max()
    lowest_aura = history_df["AURA_Score"].min()

    average_productivity = productivity_numeric.mean()
    average_burnout = burnout_numeric.mean()

    latest_aura = float(
        history_df["AURA_Score"].iloc[-1]
    )

    previous_aura = None

    if len(history_df) >= 2:
        previous_aura = float(
            history_df["AURA_Score"].iloc[-2]
        )

    # ============================================================
    # PRIMARY ANALYTICS
    # ============================================================

    a1, a2, a3 = st.columns(3)

    with a1:
        if previous_aura is not None:
            aura_delta = latest_aura - previous_aura

            st.metric(
                "🧠 Current AURA",
                f"{latest_aura:.0f}/100",
                f"{aura_delta:+.1f} vs previous",
            )
        else:
            st.metric(
                "🧠 Current AURA",
                f"{latest_aura:.0f}/100",
            )

    with a2:
        st.metric(
            "🎯 Average Productivity",
            f"{average_productivity:.0f}/100",
        )

    with a3:
        st.metric(
            "🛡️ Burnout Resilience",
            f"{average_burnout:.0f}/100",
        )

    # ============================================================
    # SECONDARY ANALYTICS
    # ============================================================

    a4, a5, a6 = st.columns(3)

    with a4:
        st.metric(
            "⭐ Best AURA Score",
            f"{highest_aura:.0f}/100",
        )

    with a5:
        st.metric(
            "📉 Lowest AURA Score",
            f"{lowest_aura:.0f}/100",
        )

    with a6:
        st.metric(
            "📅 Total Analyses",
            len(history_df),
        )

    # ============================================================
    # OVERALL STATUS
    # ============================================================

    st.markdown("#### 💡 Overall Status")

    if average_aura >= 75:
        st.success(
            "🌟 Your overall AURA pattern is stable. "
            "Your recorded productivity, resilience and behavioral "
            "balance are currently performing well."
        )

    elif average_aura >= 50:
        st.warning(
            "⚠️ Your overall AURA pattern is moderate. "
            "Monitoring stress, recovery and workload balance may "
            "help improve your overall score."
        )

    else:
        st.error(
            "🔴 Your overall AURA pattern currently needs attention. "
            "Consider focusing on recovery, workload management and "
            "consistent daily routines."
        )

    # ============================================================
    # PROFESSIONAL AURA TRENDS
    # ============================================================

    st.divider()

    st.markdown("### 📈 AURA Trends")

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>📊 Progress Over Time</strong>
                <br>
                <span>
                    Monitor how your AURA score, productivity and burnout
                    resilience change across your previous assessments.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if len(history_df) >= 2:

        # ========================================================
        # AURA SCORE TREND
        # ========================================================

        st.markdown("#### 🧠 AURA Score Trend")

        aura_trend_df = history_df[
            ["AURA_Score"]
        ].reset_index(drop=True)

        aura_trend_df.index = (
            aura_trend_df.index + 1
        )

        st.line_chart(
            aura_trend_df,
            use_container_width=True,
        )

        # ========================================================
        # PRODUCTIVITY & BURNOUT TRENDS
        # ========================================================

        trend_col1, trend_col2 = st.columns(2)

        with trend_col1:

            st.markdown("#### 🎯 Productivity Trend")

            productivity_trend_df = pd.DataFrame(
                {
                    "Productivity": productivity_numeric
                    .reset_index(drop=True)
                }
            )

            productivity_trend_df.index = (
                productivity_trend_df.index + 1
            )

            st.line_chart(
                productivity_trend_df,
                use_container_width=True,
            )

        with trend_col2:

            st.markdown(
                "#### 🛡️ Burnout Resilience Trend"
            )

            burnout_trend_df = pd.DataFrame(
                {
                    "Burnout Resilience": burnout_numeric
                    .reset_index(drop=True)
                }
            )

            burnout_trend_df.index = (
                burnout_trend_df.index + 1
            )

            st.line_chart(
                burnout_trend_df,
                use_container_width=True,
            )

    else:

        st.info(
            "📊 Run at least two AURA analyses to generate meaningful "
            "trend visualizations."
        )

    # --------------------------------------------------------
    # PROFESSIONAL LATEST ANALYSIS SUMMARY
    # --------------------------------------------------------

    st.divider()

    st.markdown("### 📋 Latest Analysis Summary")

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>🔎 Most Recent Assessment</strong>
                <br>
                <span>
                    A quick overview of the results from your latest
                    AURA behavioral analysis.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    latest = history_df.iloc[-1]

    l1, l2, l3, l4 = st.columns(4)

    with l1:
        st.metric(
            "🧠 AURA Score",
            f"{float(latest['AURA_Score']):.0f}/100",
        )

    with l2:
        st.metric(
            "🎯 Productivity",
            str(latest["Productivity"]),
        )

    with l3:
        st.metric(
            "🛡️ Burnout Risk",
            str(latest["Burnout"]),
        )

    with l4:
        st.metric(
            "😰 Stress Level",
            f"{float(latest['Stress_Level']):.1f}/10",
        )

    # --------------------------------------------------------
    # PROFESSIONAL RECENT HISTORY
    # --------------------------------------------------------

    st.divider()

    st.markdown("### 🗂️ Recent Analysis History")

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>📅 Previous Assessments</strong>
                <br>
                <span>
                    Review your most recent AURA assessments and compare
                    important behavioral indicators.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    display_columns = [
        "Timestamp",
        "Productivity",
        "Burnout",
        "AURA_Score",
        "Stress_Level",
        "Sleep_Hours",
        "Energy_Level",
        "Task_Completion_Rate",
    ]

    display_columns = [
        col
        for col in display_columns
        if col in history_df.columns
    ]

    recent_history = history_df[
        display_columns
    ].tail(10).copy()

    # Round numeric values for cleaner presentation
    for col in [
        "AURA_Score",
        "Stress_Level",
        "Sleep_Hours",
        "Energy_Level",
        "Task_Completion_Rate",
    ]:
        if col in recent_history.columns:
            recent_history[col] = recent_history[col].round(1)

    st.dataframe(
        recent_history,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # PROFESSIONAL BEHAVIORAL ANALYTICS
    # --------------------------------------------------------

    st.divider()

    st.markdown("### 🧠 Behavioral Analytics")

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>📊 Latest Behavioral Indicators</strong>
                <br>
                <span>
                    These metrics summarize the behavioral profile from your
                    most recent AURA assessment.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    latest = history_df.iloc[-1]

    # ==========================
    # ROW 1
    # ==========================

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "😴 Sleep",
            f"{float(latest['Sleep_Hours']):.1f} hrs",
        )

    with c2:
        st.metric(
            "😰 Stress",
            f"{float(latest['Stress_Level']):.1f}/10",
        )

    with c3:
        st.metric(
            "💼 Workload",
            f"{float(latest['Workload']):.1f}/10",
        )

    with c4:
        st.metric(
            "⚡ Energy",
            f"{float(latest['Energy_Level']):.1f}/10",
        )

    # ==========================
    # ROW 2
    # ==========================

    c5, c6, c7, c8 = st.columns(4)

    with c5:
        st.metric(
            "✅ Completion",
            f"{float(latest['Task_Completion_Rate']):.1f}%",
        )

    with c6:
        st.metric(
            "📱 Screen",
            f"{float(latest['Screen_Time']):.1f} hrs",
        )

    with c7:
        st.metric(
            "📚 Study",
            f"{float(latest['Study_Hours']):.1f} hrs",
        )

    with c8:
        st.metric(
            "🎯 Focus",
            f"{float(latest['Focus_Sessions']):.0f}",
        )

    # ==========================
    # TREND
    # ==========================

    if len(history_df) >= 2:

        st.markdown("#### 📈 Behavioral Trend")

        trend_df = history_df[
            [
                "Stress_Level",
                "Energy_Level",
                "Task_Completion_Rate",
            ]
        ].copy()

        st.line_chart(
            trend_df,
            use_container_width=True,
        )

    # ============================================================
    # SMART ACTION PLAN
    # ============================================================

    st.divider()
    st.subheader("🧠 AURA Smart Action Plan")

    smart_actions = []

    if (
        latest["Stress_Level"] >= 7
        and latest["Workload"] >= 7
    ):
        smart_actions.append(
            "⚠️ Stress and workload are both elevated. "
            "Prioritize essential tasks and include regular recovery breaks."
        )

    if (
        latest["Sleep_Hours"] < 6
        and latest["Energy_Level"] <= 4
    ):
        smart_actions.append(
            "😴 Lower sleep and energy levels were recorded together. "
            "Improving rest and maintaining a consistent routine may "
            "support daily performance."
        )

    if latest["Productivity"] == "Low":
        smart_actions.append(
            "🎯 Productivity is currently Low. Try focusing on a "
            "smaller number of high-priority tasks."
        )

    elif latest["Productivity"] == "Medium":
        smart_actions.append(
            "📈 Productivity is currently Medium. Consistent focus "
            "sessions and balanced workload may help improve performance."
        )

    if latest["Burnout"] == "Critical":
        smart_actions.append(
            "🛡️ Burnout risk is currently Critical. Consider reducing "
            "excessive workload and prioritizing recovery."
        )

    elif latest["Burnout"] == "Warning":
        smart_actions.append(
            "⚠️ Burnout risk is currently Warning. Monitor stress, "
            "workload and recovery patterns."
        )

    if latest["Task_Completion_Rate"] < 50:
        smart_actions.append(
            "✅ Task completion is relatively low. Breaking large tasks "
            "into smaller achievable steps may make progress easier."
        )

    if latest["Screen_Time"] >= 9:
        smart_actions.append(
            "📱 Screen time is high. Consider adding short "
            "screen-free intervals."
        )

    if not smart_actions:
        smart_actions.append(
            "🌟 Your current behavioral pattern looks relatively "
            "balanced. Continue monitoring your AURA trends."
        )

    for action in smart_actions:
        st.info(action)

    # ============================================================
    # RISK INDICATOR
    # ============================================================

    st.divider()
    st.subheader("🚦 AURA Risk Indicator")

    r1, r2, r3, r4 = st.columns(4)

    with r1:

        if latest["Sleep_Hours"] < 6:
            st.error("🔴 Recovery Risk: High")
        elif latest["Sleep_Hours"] < 7:
            st.warning("🟡 Recovery Risk: Moderate")
        else:
            st.success("🟢 Recovery Risk: Low")

    with r2:

        if latest["Stress_Level"] >= 7:
            st.error("🔴 Stress Risk: High")
        elif latest["Stress_Level"] >= 4:
            st.warning("🟡 Stress Risk: Moderate")
        else:
            st.success("🟢 Stress Risk: Low")

    with r3:

        if latest["Workload"] >= 8:
            st.error("🔴 Workload Risk: High")
        elif latest["Workload"] >= 5:
            st.warning("🟡 Workload Risk: Moderate")
        else:
            st.success("🟢 Workload Risk: Low")

    with r4:

        if latest["Energy_Level"] <= 4:
            st.error("🔴 Energy Risk: High")
        elif latest["Energy_Level"] <= 7:
            st.warning("🟡 Energy Risk: Moderate")
        else:
            st.success("🟢 Energy Risk: Low")

    # ============================================================
    # PERFORMANCE DISTRIBUTIONS
    # ============================================================

    st.divider()
    st.subheader("📊 AURA Performance Dashboard")

    aura_distribution = pd.cut(
        history_df["AURA_Score"],
        bins=[-1, 49, 74, 100],
        labels=[
            "Needs Attention",
            "Watch",
            "Stable",
        ],
    )

    aura_distribution_counts = (
        aura_distribution
        .value_counts()
        .reindex([
            "Stable",
            "Watch",
            "Needs Attention",
        ])
        .fillna(0)
    )

    st.markdown("### 🧠 AURA Score Distribution")

    st.bar_chart(
        aura_distribution_counts,
        use_container_width=True,
    )

    d1, d2 = st.columns(2)

    with d1:

        st.markdown(
            "### 🎯 Productivity Distribution"
        )

        productivity_distribution = (
            history_df["Productivity"]
            .value_counts()
            .reindex([
                "High",
                "Medium",
                "Low",
            ])
            .fillna(0)
        )

        st.bar_chart(
            productivity_distribution,
            use_container_width=True,
        )

    with d2:

        st.markdown(
            "### 🛡️ Burnout Risk Distribution"
        )

        burnout_distribution = (
            history_df["Burnout"]
            .value_counts()
            .reindex([
                "Safe",
                "Warning",
                "Critical",
            ])
            .fillna(0)
        )

        st.bar_chart(
            burnout_distribution,
            use_container_width=True,
        )

    # ============================================================
    # TREND INSIGHTS
    # ============================================================

    st.divider()
    st.subheader("🔎 AURA Trend Insights")

    if len(history_df) >= 2:

        first = history_df.iloc[0]
        latest = history_df.iloc[-1]

        aura_change = (
            latest["AURA_Score"]
            - first["AURA_Score"]
        )

        if aura_change > 5:
            st.success(
                f"📈 Your AURA score has improved by "
                f"{aura_change:.1f} points since the first analysis."
            )

        elif aura_change < -5:
            st.warning(
                f"📉 Your AURA score has decreased by "
                f"{abs(aura_change):.1f} points since the first analysis."
            )

        else:
            st.info(
                "➡️ Your AURA score has remained relatively stable."
            )

        sleep_change = (
            latest["Sleep_Hours"]
            - first["Sleep_Hours"]
        )

        if sleep_change > 0.5:
            st.info(
                f"😴 Sleep duration increased by "
                f"{sleep_change:.1f} hours."
            )

        elif sleep_change < -0.5:
            st.warning(
                f"😴 Sleep duration decreased by "
                f"{abs(sleep_change):.1f} hours."
            )

        stress_change = (
            latest["Stress_Level"]
            - first["Stress_Level"]
        )

        if stress_change > 0.5:
            st.warning(
                f"😰 Stress level increased by "
                f"{stress_change:.1f} points."
            )

        elif stress_change < -0.5:
            st.success(
                f"😌 Stress level decreased by "
                f"{abs(stress_change):.1f} points."
            )

        energy_change = (
            latest["Energy_Level"]
            - first["Energy_Level"]
        )

        if energy_change > 0.5:
            st.success(
                f"⚡ Energy level increased by "
                f"{energy_change:.1f} points."
            )

        elif energy_change < -0.5:
            st.warning(
                f"⚡ Energy level decreased by "
                f"{abs(energy_change):.1f} points."
            )

        completion_change = (
            latest["Task_Completion_Rate"]
            - first["Task_Completion_Rate"]
        )

        if completion_change > 5:
            st.success(
                f"✅ Task completion rate improved by "
                f"{completion_change:.1f}%."
            )

        elif completion_change < -5:
            st.warning(
                f"📉 Task completion rate decreased by "
                f"{abs(completion_change):.1f}%."
            )

    else:

        st.info(
            "Run at least two AURA analyses to generate trend insights."
        )

    # ============================================================
    # PROFESSIONAL AURA GOAL TRACKING
    # ============================================================

    st.divider()

    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-icon">🎯</div>
            <div>
                <h1>AURA Goal Tracking</h1>
                <p>
                    Set a personal AURA target and monitor your progress
                    toward achieving a stronger behavioral balance.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>🏆 Personal AURA Goal</strong>
                <br>
                <span>
                    Define your target AURA score and track how close you are
                    to reaching your personal goal.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ============================================================
    # GOAL SETUP
    # ============================================================

    goal_col1, goal_col2 = st.columns(2)

    with goal_col1:

        st.markdown("#### 🎯 Set Your Target")

        aura_goal = st.slider(
            "Target AURA Score",
            min_value=50,
            max_value=100,
            value=80,
            step=5,
            key="aura_goal",
        )

    with goal_col2:

        current_aura_goal = float(
            history_df["AURA_Score"].iloc[-1]
        )

        st.markdown("#### 📊 Current Performance")

        st.metric(
            "Current AURA Score",
            f"{current_aura_goal:.0f}/100",
            f"Target: {aura_goal}/100",
        )

    goal_progress = min(
        max(current_aura_goal / aura_goal, 0.0),
        1.0,
    )

    # ============================================================
    # GOAL PROGRESS
    # ============================================================

    st.markdown("### 📈 Goal Progress")

    progress_col1, progress_col2 = st.columns([3, 1])

    with progress_col1:

        st.progress(goal_progress)

    with progress_col2:

        st.metric(
            "Progress",
            f"{goal_progress * 100:.0f}%",
        )

    if current_aura_goal >= aura_goal:

        st.success(
            "🏆 Congratulations! You have reached your AURA goal."
        )

    else:

        points_remaining = aura_goal - current_aura_goal

        st.info(
            f"💪 You are {points_remaining:.0f} points "
            f"away from your AURA goal."
        )

    # ============================================================
    # GOAL SCORE BREAKDOWN
    # ============================================================

    st.markdown("#### 🎯 Goal Score Breakdown")

    g1, g2, g3 = st.columns(3)

    with g1:
        st.metric(
            "Current Score",
            f"{current_aura_goal:.0f}",
        )

    with g2:
        st.metric(
            "Target Score",
            f"{aura_goal:.0f}",
        )

    with g3:
        if current_aura_goal >= aura_goal:
            remaining_text = "Goal Reached"
        else:
            remaining_text = f"{aura_goal - current_aura_goal:.0f} pts"

        st.metric(
            "Remaining",
            remaining_text,
        )

    # ============================================================
    # SMART GOAL INSIGHTS
    # ============================================================

    st.markdown("#### 💡 Smart Goal Insights")

    if current_aura_goal >= aura_goal:

        st.success(
            "🏆 Goal achieved! Your current AURA score has reached "
            "or exceeded your selected target."
        )

    elif goal_progress >= 0.85:

        st.info(
            "🚀 You are very close to your target. Small improvements "
            "in your daily behavioral patterns may help you reach the goal."
        )

    elif goal_progress >= 0.60:

        st.info(
            "📈 You are making steady progress toward your target. "
            "Focus on maintaining consistent daily habits."
        )

    else:

        st.warning(
            "💪 Your target is still some distance away. "
            "Use Daily Analysis and What-If Simulator to identify "
            "behavioral changes that may improve your AURA score."
        )

    # ============================================================
    # PROFESSIONAL CORRELATION ANALYSIS
    # ============================================================

    st.divider()

    st.markdown("### 🧩 Behavioral Correlation Analysis")

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>🔗 Understand Your Behavioral Patterns</strong>
                <br>
                <span>
                    Explore how sleep, stress, workload, energy and task
                    completion are associated with your AURA score.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    correlation_columns = [
        "Sleep_Hours",
        "Stress_Level",
        "Workload",
        "Energy_Level",
        "Task_Completion_Rate",
        "AURA_Score",
    ]

    correlation_df = (
        history_df[correlation_columns]
        .corr()
        .round(2)
    )

    # ============================================================
    # CORRELATION MATRIX
    # ============================================================

    st.markdown("#### 📊 Correlation Matrix")

    st.caption(
        "Values closer to +1 indicate a positive association, "
        "while values closer to -1 indicate a negative association."
    )

    st.dataframe(
        correlation_df,
        use_container_width=True,
    )

    # ============================================================
    # PATTERN SUMMARY
    # ============================================================

    st.divider()
    st.subheader("🧠 AURA Pattern Summary")

    correlations = {
        "sleep": history_df["Sleep_Hours"].corr(
            history_df["AURA_Score"]
        ),
        "stress": history_df["Stress_Level"].corr(
            history_df["AURA_Score"]
        ),
        "workload": history_df["Workload"].corr(
            history_df["AURA_Score"]
        ),
        "energy": history_df["Energy_Level"].corr(
            history_df["AURA_Score"]
        ),
        "completion": history_df[
            "Task_Completion_Rate"
        ].corr(
            history_df["AURA_Score"]
        ),
    }

    # ============================================================
    # STRONGEST BEHAVIORAL RELATIONSHIPS
    # ============================================================

    valid_correlations = {
        key: value
        for key, value in correlations.items()
        if pd.notna(value)
    }

    if valid_correlations:

        strongest_positive = max(
            valid_correlations,
            key=valid_correlations.get,
        )

        strongest_negative = min(
            valid_correlations,
            key=valid_correlations.get,
        )

        correlation_labels = {
            "sleep": "😴 Sleep",
            "stress": "😰 Stress",
            "workload": "💼 Workload",
            "energy": "⚡ Energy",
            "completion": "✅ Task Completion",
        }

        st.markdown("#### 🔍 Key Behavioral Relationships")

        r1, r2 = st.columns(2)

        with r1:
            st.info(
                f"📈 **Strongest Positive:** "
                f"{correlation_labels[strongest_positive]} "
                f"({valid_correlations[strongest_positive]:+.2f})"
            )

        with r2:
            st.warning(
                f"📉 **Strongest Negative:** "
                f"{correlation_labels[strongest_negative]} "
                f"({valid_correlations[strongest_negative]:+.2f})"
            )

    # ============================================================
    # CORRELATION STRENGTH INTERPRETATION
    # ============================================================

    def correlation_strength(value):

        value = abs(float(value))

        if value >= 0.7:
            return "Strong"

        elif value >= 0.4:
            return "Moderate"

        elif value >= 0.3:
            return "Weak"

        else:
            return "Very Weak"

    if valid_correlations:

        positive_value = valid_correlations[
            strongest_positive
        ]

        negative_value = valid_correlations[
            strongest_negative
        ]

        st.markdown("#### 📐 Relationship Strength")

        s1, s2 = st.columns(2)

        with s1:

            st.metric(
                "📈 Positive Relationship",
                correlation_strength(positive_value),
                f"{positive_value:+.2f}",
            )

        with s2:

            st.metric(
                "📉 Negative Relationship",
                correlation_strength(negative_value),
                f"{negative_value:+.2f}",
            )

    pattern_messages = []

    if pd.notna(correlations["sleep"]):

        if correlations["sleep"] > 0.3:
            pattern_messages.append(
                "😴 Higher sleep duration is associated with higher "
                "AURA scores in your history."
            )

        elif correlations["sleep"] < -0.3:
            pattern_messages.append(
                "😴 Higher sleep duration is associated with lower "
                "AURA scores in your recorded history."
            )

    if pd.notna(correlations["stress"]):

        if correlations["stress"] < -0.3:
            pattern_messages.append(
                "😰 Higher stress levels are associated with lower "
                "AURA scores."
            )

        elif correlations["stress"] > 0.3:
            pattern_messages.append(
                "😰 Stress and AURA score show a positive association "
                "in your recorded history."
            )

    if (
        pd.notna(correlations["workload"])
        and correlations["workload"] < -0.3
    ):
        pattern_messages.append(
            "💼 Higher workload is associated with lower AURA scores."
        )

    if (
        pd.notna(correlations["energy"])
        and correlations["energy"] > 0.3
    ):
        pattern_messages.append(
            "⚡ Higher energy levels are associated with higher "
            "AURA scores."
        )

    if (
        pd.notna(correlations["completion"])
        and correlations["completion"] > 0.3
    ):
        pattern_messages.append(
            "✅ Higher task completion rates are associated with "
            "higher AURA scores."
        )

    if not pattern_messages:
        pattern_messages.append(
            "📊 No strong behavioral relationship was detected "
            "in the current history. More analyses may provide "
            "more meaningful patterns."
        )

    # ============================================================
    # PROFESSIONAL PATTERN SUMMARY
    # ============================================================

    st.markdown("#### 🧠 Personalized Pattern Insights")

    if pattern_messages:

        for message in pattern_messages:

            if (
                "higher" in message.lower()
                and "lower" not in message.lower()
            ):
                st.success(message)

            elif (
                "lower" in message.lower()
                or "stress" in message.lower()
            ):
                st.warning(message)

            else:
                st.info(message)

    else:

        st.info(
            "📊 No strong behavioral relationship was detected "
            "in the current history. More analyses may provide "
            "more meaningful patterns."
        )

    # ============================================================
    # ANALYTICS CONTEXT NOTE
    # ============================================================

    st.caption(
        f"📌 These behavioral insights are calculated from "
        f"{len(history_df)} recorded AURA analyses. "
        "Correlation indicates association, not causation."
    )

# ============================================================
# TREATMENT / GUIDANCE PAGE
# ============================================================

def render_treatment_page():
    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-icon">💊</div>
            <div>
                <h1>Treatment & Guidance</h1>
                <p>Practical lifestyle guidance based on your latest AURA analysis.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history_df = load_history(st.session_state.current_user)

    if history_df.empty:
        st.info("Run an AURA Analysis first to receive personalized guidance.")
        return

    latest = history_df.iloc[-1]
    burnout = str(latest.get("Burnout", "—"))
    productivity = str(latest.get("Productivity", "—"))
    aura = float(pd.to_numeric(latest.get("AURA_Score", 0), errors="coerce") or 0)

    st.markdown(
        f"""
        <div class="analysis-intro">
            <strong>🧠 Latest AURA Snapshot</strong><br>
            <span>Productivity: {productivity} &nbsp; • &nbsp; Burnout Risk: {burnout} &nbsp; • &nbsp; AURA Score: {aura:.0f}/100</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    guidance = []
    if burnout == "Critical":
        guidance.append(("🛡️ Recovery Priority", "Reduce unnecessary workload, schedule regular breaks and prioritize recovery before adding more demanding tasks."))
    elif burnout == "Warning":
        guidance.append(("🛡️ Burnout Prevention", "Monitor stress and workload closely and keep consistent recovery breaks throughout the day."))
    else:
        guidance.append(("🛡️ Maintain Resilience", "Continue the habits that are supporting your current balance and monitor changes over time."))

    if float(latest.get("Sleep_Hours", 7)) < 6:
        guidance.append(("😴 Sleep", "Your recorded sleep is low. Work toward a more consistent sleep routine."))
    if float(latest.get("Stress_Level", 5)) >= 7:
        guidance.append(("😰 Stress", "Consider shorter focused work blocks, planned breaks and reducing avoidable workload pressure."))
    if float(latest.get("Screen_Time", 6)) >= 9:
        guidance.append(("📱 Screen Time", "Add short screen-free intervals between longer periods of device use."))
    if float(latest.get("Energy_Level", 5)) <= 4:
        guidance.append(("⚡ Energy", "Review sleep, hydration, physical activity and workload patterns when energy remains low."))
    if float(latest.get("Task_Completion_Rate", 50)) < 50:
        guidance.append(("🎯 Task Planning", "Prioritize a smaller number of high-impact tasks and break large tasks into manageable steps."))

    st.markdown("### 🌿 Personalized Guidance")
    for title, message in guidance:
        st.markdown(
            f"""<div class="analysis-section"><div class="section-title">{title}</div><div class="section-subtitle">{message}</div></div>""",
            unsafe_allow_html=True,
        )

    st.caption("AURA provides behavioral guidance based on recorded data; it is not a medical or psychological diagnostic system.")


# ============================================================
# ABOUT AURA PAGE
# ============================================================

def render_about_page():

    st.markdown("# ℹ️ About AURA")

    st.caption(
        "Adaptive User Resilience & Analytics"
    )

    st.divider()

    # ========================================================
    # ABOUT AURA
    # ========================================================

    st.subheader("🧠 What is AURA?")

    st.write(
        """
        **AURA — Adaptive User Resilience & Analytics** is an
        AI-powered behavioral intelligence application designed
        to help users understand patterns related to productivity,
        stress, workload, energy, recovery and burnout risk.

        AURA combines behavioral data with Machine Learning models
        to generate productivity predictions, burnout-risk insights
        and an overall AURA Score.

        The platform is designed to turn everyday behavioral data
        into understandable insights that users can monitor over
        time and explore through interactive analysis tools.
        """
    )

    # ========================================================
    # KEY FEATURES
    # ========================================================

    st.divider()

    st.subheader("✨ What AURA Offers")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 🧠 AURA Analysis")
        st.write(
            "Analyze daily behavioral and lifestyle indicators "
            "using Machine Learning models."
        )

    with c2:
        st.markdown("### 🧪 What-If Simulator")
        st.write(
            "Explore hypothetical changes in your daily factors "
            "and compare their predicted impact."
        )

    with c3:
        st.markdown("### 📊 Smart Insights")
        st.write(
            "Convert analysis results and behavioral patterns "
            "into simple and understandable insights."
        )

    c4, c5, c6 = st.columns(3)

    with c4:
        st.markdown("### 📈 History & Trends")
        st.write(
            "Track previous analyses and monitor changes in "
            "your AURA score over time."
        )

    with c5:
        st.markdown("### 💊 Treatment & Guidance")
        st.write(
            "Receive general wellness and behavioral guidance "
            "based on your latest AURA analysis."
        )

    with c6:
        st.markdown("### 🔐 Secure Accounts")
        st.write(
            "AURA supports user authentication and protected "
            "administrator functionality."
        )

    # ========================================================
    # HOW AURA WORKS
    # ========================================================

    st.divider()

    st.subheader("🔄 How AURA Works")

    step1, step2, step3, step4 = st.columns(4)

    with step1:
        st.markdown("### 01")
        st.markdown("📝 **Daily Input**")
        st.write(
            "Users record lifestyle, productivity and "
            "behavioral indicators."
        )

    with step2:
        st.markdown("### 02")
        st.markdown("🤖 **AI Analysis**")
        st.write(
            "Machine Learning models process the recorded "
            "behavioral information."
        )

    with step3:
        st.markdown("### 03")
        st.markdown("📊 **AURA Insights**")
        st.write(
            "The system generates productivity, burnout "
            "and AURA score results."
        )

    with step4:
        st.markdown("### 04")
        st.markdown("🎯 **Track & Explore**")
        st.write(
            "Users can review history, identify patterns "
            "and explore What-If scenarios."
        )

    # ========================================================
    # TECHNOLOGY
    # ========================================================

    st.divider()

    st.subheader("🛠️ Technology Behind AURA")

    st.write(
        "AURA combines several technologies to provide its "
        "analysis and interactive web experience:"
    )

    tech1, tech2, tech3 = st.columns(3)

    with tech1:
        st.markdown("🐍 **Python**")
        st.markdown("Core application and data-processing language.")

        st.markdown("🤖 **Machine Learning**")
        st.markdown("Predictive models for productivity and burnout.")

        st.markdown("🧠 **Scikit-learn**")
        st.markdown("Machine Learning model implementation.")

    with tech2:
        st.markdown("🎈 **Streamlit**")
        st.markdown("Interactive web application interface.")

        st.markdown("📊 **Pandas & NumPy**")
        st.markdown("Data processing and numerical analysis.")

        st.markdown("📈 **Data Visualization**")
        st.markdown("Charts and visual analytics for behavioral trends.")

    with tech3:
        st.markdown("💾 **SQLite / CSV**")
        st.markdown("Local storage for account and analysis data.")

        st.markdown("🔐 **Authentication**")
        st.markdown("Login, signup and role-based access.")

        st.markdown("🧪 **What-If Analysis**")
        st.markdown("Scenario-based behavioral simulation.")

    # ========================================================
    # PROJECT CREATOR
    # ========================================================

    st.divider()

    st.subheader("👩‍💻 About the Creator")

    st.write(
        """
        **Created by Anshika**

        AURA was developed as a Computer Science project with
        a focus on Artificial Intelligence, Machine Learning,
        behavioral analytics and interactive web application
        development.

        The project brings predictive analytics, historical
        tracking, behavioral insights, What-If simulation and
        secure account functionality together in one platform.

        The objective of AURA is to transform behavioral data
        into meaningful information that is easier for users
        to understand and monitor.
        """
    )

    # ========================================================
    # PROJECT INFORMATION
    # ========================================================

    st.divider()

    st.subheader("📌 Project Information")

    info1, info2 = st.columns(2)

    with info1:
        st.markdown("**Project Name**")
        st.write("AURA AI")

        st.markdown("**Full Name**")
        st.write("Adaptive User Resilience & Analytics")

        st.markdown("**Project Type**")
        st.write("AI-powered behavioral analytics web application")

    with info2:
        st.markdown("**Primary Focus**")
        st.write(
            "Artificial Intelligence, Machine Learning, "
            "Data Analytics and Web Application Development"
        )

        st.markdown("**Core Functionality**")
        st.write(
            "Productivity Prediction, Burnout Analysis, "
            "AURA Score, History Tracking and What-If Simulation"
        )

        st.markdown("**Platform**")
        st.write("Interactive Web Application")

    # ========================================================
    # DISCLAIMER
    # ========================================================

    st.divider()

    st.subheader("ℹ️ Important Note")

    st.info(
        "AURA is a behavioral analytics and wellness-support "
        "application. Its predictions and recommendations are "
        "informational and should not be considered medical or "
        "psychological diagnosis."
    )

# ============================================================
# AUTHENTICATION GATE
# ============================================================

# IMPORTANT:
# Everything below this point is protected.
# If the user is not authenticated, ONLY the login page
# is rendered and Streamlit execution stops immediately.

if not st.session_state.authenticated:
    render_login_page()
    st.stop()

# Re-check the account in the backend on every authenticated rerun.
# This keeps the role authoritative in the database instead of trusting
# a stale client-side role value.
active_account = get_user(st.session_state.current_user)
if not active_account or not active_account.get("is_active"):
    logout_user()

st.session_state.current_role = active_account.get("role", "user")


# ============================================================
# PROTECTED APPLICATION
# ============================================================

try:
    productivity_model, burnout_model = load_models()
except Exception as model_error:
    st.error(
        "❌ AURA models could not be loaded."
    )
    st.code(str(model_error))
    st.stop()

# ============================================================
# ADMIN DASHBOARD
# ============================================================

def render_admin_dashboard():

    # --------------------------------------------------------
    # ADMIN ACCESS PROTECTION
    # --------------------------------------------------------

    current_role = str(
        st.session_state.get("current_role", "")
    ).strip().lower()

    if current_role != "admin":
        st.error(
            "🚫 Access Denied"
        )

        st.info(
            "The Admin Panel is available only to the administrator account."
        )

        if st.button(
            "← Back to Dashboard",
            use_container_width=True,
            key="admin_access_denied_back",
        ):
            st.session_state.page = "Home"
            st.rerun()

        return

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="page-header">
            <div class="page-header-icon">🛡️</div>
            <div>
                <h1>Admin Panel</h1>
                <p>
                    Monitor AURA users, analyses and overall system activity.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>⚙️ AURA System Administration</strong>
                <br>
                <span>
                    Review registered accounts, analysis activity and
                    overall AURA system performance.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------------------------------------------------
    # LOAD ADMIN DATA
    # --------------------------------------------------------

    users_df = load_users()
    history_df = load_all_history()

    # --------------------------------------------------------
    # SYSTEM OVERVIEW
    # --------------------------------------------------------

    st.subheader("📊 System Overview")

    total_users = len(users_df)

    total_analyses = len(history_df)

    # --------------------------------------------------------
    # AURA SCORE STATISTICS
    # --------------------------------------------------------

    if (
        not history_df.empty
        and "AURA_Score" in history_df.columns
    ):

        aura_scores = pd.to_numeric(
            history_df["AURA_Score"],
            errors="coerce",
        ).dropna()

        if not aura_scores.empty:

            average_aura = aura_scores.mean()
            highest_aura = aura_scores.max()

        else:

            average_aura = None
            highest_aura = None

    else:

        average_aura = None
        highest_aura = None

    # --------------------------------------------------------
    # SYSTEM OVERVIEW METRICS
    # --------------------------------------------------------

    m1, m2, m3, m4 = st.columns(4)

    with m1:

        st.metric(
            "👥 Total Users",
            total_users,
        )

    with m2:

        st.metric(
            "📊 Total Analyses",
            total_analyses,
        )

    with m3:

        st.metric(
            "📈 Average AURA Score",
            (
                f"{average_aura:.0f}/100"
                if average_aura is not None
                else "—"
            ),
        )

    with m4:

        st.metric(
            "🏆 Highest AURA Score",
            (
                f"{highest_aura:.0f}/100"
                if highest_aura is not None
                else "—"
            ),
        )

    # --------------------------------------------------------
    # AVERAGE AURA ANALYTICS
    # --------------------------------------------------------

    st.subheader("📈 Average AURA Score")

    if not history_df.empty:

        aura_scores = pd.to_numeric(
            history_df["AURA_Score"],
            errors="coerce"
        ).dropna()

        if not aura_scores.empty:

            avg_aura = aura_scores.mean()

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "📈 Overall Average AURA",
                    f"{avg_aura:.1f}/100"
                )

            with col2:
                st.metric(
                    "📊 Analyses Used",
                    len(aura_scores)
                )

        else:
            st.info("No valid AURA scores available yet.")

    else:
        st.info("No analysis data available yet.")

    # --------------------------------------------------------
    # PRODUCTIVITY DISTRIBUTION
    # --------------------------------------------------------

    st.subheader("🧠 Productivity Distribution")

    if not history_df.empty and "Productivity_Level" in history_df.columns:

        productivity_data = (
            history_df["Productivity_Level"]
            .astype(str)
            .str.strip()
            .value_counts()
        )

        if not productivity_data.empty:

            col1, col2 = st.columns([2, 1])

            with col1:
                st.bar_chart(productivity_data)

            with col2:
                st.write("### 📋 Breakdown")

                for level, count in productivity_data.items():
                    st.write(f"**{level}:** {count}")

        else:
            st.info("No productivity data available yet.")

    else:
        st.info("No productivity analysis data available yet.")

    # ========================================================
    # USER ACCOUNTS
    # ========================================================

    st.divider()

    st.subheader("👥 Registered Users")

    if users_df.empty:

        st.info(
            "No registered users found."
        )

    else:

        user_display = users_df.copy()

        # Never display password hashes
        if "Password" in user_display.columns:

            user_display = user_display.drop(
                columns=["Password"]
            )

        # Add analysis count for each user
        if (
            not history_df.empty
            and "Username" in history_df.columns
            and "Username" in user_display.columns
        ):

            analysis_counts = (
                history_df["Username"]
                .astype(str)
                .str.strip()
                .str.lower()
                .value_counts()
            )

            user_display["Analyses"] = (
                user_display["Username"]
                .astype(str)
                .str.strip()
                .str.lower()
                .map(analysis_counts)
                .fillna(0)
                .astype(int)
            )

        else:

            user_display["Analyses"] = 0

        st.dataframe(
            user_display,
            use_container_width=True,
            hide_index=True,
        )

    # ========================================================
    # USER / ACTIVITY OVERVIEW
    # ========================================================

    st.divider()

    st.markdown("### 👥 User Activity Overview")

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>📊 User-Level AURA Activity</strong>
                <br>
                <span>
                    Review analysis frequency, AURA performance and
                    recent activity across registered users.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if users_df.empty:

        st.info(
            "No registered users are available."
        )

    else:

        # ----------------------------------------------------
        # PREPARE USER ACTIVITY DATA
        # ----------------------------------------------------

        user_activity = users_df.copy()

        # Never expose password information.
        if "Password" in user_activity.columns:
            user_activity = user_activity.drop(
                columns=["Password"]
            )

        # Default activity columns.
        user_activity["Total Analyses"] = 0
        user_activity["Average AURA"] = 0.0
        user_activity["Best AURA"] = 0.0
        user_activity["Last Analysis"] = "—"
        user_activity["Latest Productivity"] = "—"
        user_activity["Latest Burnout"] = "—"

        # ----------------------------------------------------
        # CALCULATE USER-WISE ACTIVITY
        # ----------------------------------------------------

        if (
            not history_df.empty
            and "Username" in history_df.columns
        ):

            activity_data = history_df.copy()

            if "Timestamp" in activity_data.columns:
                activity_data["Timestamp_Parsed"] = pd.to_datetime(
                    activity_data["Timestamp"], errors="coerce"
                )
                activity_data = activity_data.sort_values(
                    "Timestamp_Parsed", na_position="last"
                )

            activity_data["Username_Normalized"] = (
                activity_data["Username"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            activity_data["AURA_Score"] = pd.to_numeric(
                activity_data["AURA_Score"],
                errors="coerce",
            )

            # ----------------------------------------------
            # GROUP USER ACTIVITY
            # ----------------------------------------------

            user_summary = (
                activity_data
                .groupby(
                    "Username_Normalized",
                    dropna=False,
                )
                .agg(
                    Total_Analyses=(
                        "AURA_Score",
                        "count",
                    ),
                    Average_AURA=(
                        "AURA_Score",
                        "mean",
                    ),
                    Best_AURA=(
                        "AURA_Score",
                        "max",
                    ),
                )
                .reset_index()
            )

            # ----------------------------------------------
            # MAP SUMMARY TO USERS
            # ----------------------------------------------

            user_activity["Username_Normalized"] = (
                user_activity["Username"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            user_activity = user_activity.merge(
                user_summary,
                on="Username_Normalized",
                how="left",
                suffixes=("", "_summary"),
            )

            user_activity["Total Analyses"] = (
                user_activity["Total_Analyses"]
                .fillna(0)
                .astype(int)
            )

            user_activity["Average AURA"] = (
                user_activity["Average_AURA"]
                .fillna(0)
            )

            user_activity["Best AURA"] = (
                user_activity["Best_AURA"]
                .fillna(0)
            )

            # ----------------------------------------------
            # LATEST USER RECORD
            # ----------------------------------------------

            for username in user_activity[
                "Username"
            ].astype(str):

                username_key = (
                    username.strip().lower()
                )

                user_records = activity_data[
                    activity_data[
                        "Username_Normalized"
                    ] == username_key
                ]

                if user_records.empty:
                    continue

                latest_record = user_records.iloc[-1]

                mask = (
                    user_activity[
                        "Username_Normalized"
                    ] == username_key
                )

                user_activity.loc[
                    mask,
                    "Latest Productivity"
                ] = str(
                    latest_record.get(
                        "Productivity",
                        "—",
                    )
                )

                user_activity.loc[
                    mask,
                    "Latest Burnout"
                ] = str(
                    latest_record.get(
                        "Burnout",
                        "—",
                    )
                )

                # ------------------------------------------
                # LAST ANALYSIS TIMESTAMP
                # ------------------------------------------

                if "Timestamp" in user_records.columns:

                    timestamps = pd.to_datetime(
                        user_records["Timestamp"],
                        errors="coerce",
                    )

                    valid_timestamps = (
                        timestamps.dropna()
                    )

                    if not valid_timestamps.empty:

                        latest_timestamp = (
                            valid_timestamps.max()
                        )

                        user_activity.loc[
                            mask,
                            "Last Analysis"
                        ] = (
                            latest_timestamp
                            .strftime(
                                "%d %b %Y, %I:%M %p"
                            )
                        )

        # ----------------------------------------------------
        # ACTIVITY STATUS
        # ----------------------------------------------------

        def get_activity_status(
            analysis_count
        ):

            if analysis_count >= 5:
                return "🟢 Active"

            elif analysis_count >= 1:
                return "🟡 Occasional"

            return "⚪ No Activity"

        user_activity["Activity Status"] = (
            user_activity[
                "Total Analyses"
            ]
            .apply(get_activity_status)
        )

        # ----------------------------------------------------
        # CLEAN DISPLAY TABLE
        # ----------------------------------------------------

        activity_display_columns = [
            "Username",
            "Total Analyses",
            "Average AURA",
            "Best AURA",
            "Latest Productivity",
            "Latest Burnout",
            "Last Analysis",
            "Activity Status",
        ]

        activity_display_columns = [
            col
            for col in activity_display_columns
            if col in user_activity.columns
        ]

        activity_display = user_activity[
            activity_display_columns
        ].copy()

        # Format AURA values.
        if "Average AURA" in activity_display.columns:
            activity_display[
                "Average AURA"
            ] = activity_display[
                "Average AURA"
            ].round(1)

        if "Best AURA" in activity_display.columns:
            activity_display[
                "Best AURA"
            ] = activity_display[
                "Best AURA"
            ].round(1)

        # ----------------------------------------------------
        # USER ACTIVITY TABLE
        # ----------------------------------------------------

        st.dataframe(
            activity_display,
            use_container_width=True,
            hide_index=True,
        )

        # ----------------------------------------------------
        # ACTIVITY SUMMARY
        # ----------------------------------------------------

        st.markdown("### 📌 Activity Summary")

        active_users = (
            user_activity[
                "Total Analyses"
            ] > 0
        ).sum()

        highly_active_users = (
            user_activity[
                "Total Analyses"
            ] >= 5
        ).sum()

        inactive_users = (
            user_activity[
                "Total Analyses"
            ] == 0
        ).sum()

        s1, s2, s3 = st.columns(3)

        with s1:
            st.metric(
                "🟢 Users With Activity",
                int(active_users),
            )

        with s2:
            st.metric(
                "🔥 Highly Active Users",
                int(highly_active_users),
            )

        with s3:
            st.metric(
                "⚪ Users With No Analysis",
                int(inactive_users),
            )

    # ========================================================
    # PRODUCTIVITY DISTRIBUTION
    # ========================================================

    st.divider()

    st.subheader("🎯 Productivity Overview")

    if (
        history_df.empty
        or "Productivity" not in history_df.columns
    ):

        st.info(
            "No productivity data available."
        )

    else:

        productivity_distribution = (
            history_df["Productivity"]
            .value_counts()
            .reindex(
                [
                    "High",
                    "Medium",
                    "Low",
                ]
            )
            .fillna(0)
        )

        st.bar_chart(
            productivity_distribution
        )

    # ========================================================
    # BURNOUT DISTRIBUTION
    # ========================================================

    st.divider()

    st.subheader("🛡️ Burnout Risk Overview")

    if (
        history_df.empty
        or "Burnout" not in history_df.columns
    ):

        st.info(
            "No burnout data available."
        )

    else:

        burnout_distribution = (
            history_df["Burnout"]
            .value_counts()
            .reindex(
                [
                    "Safe",
                    "Warning",
                    "Critical",
                ]
            )
            .fillna(0)
        )

        st.bar_chart(
            burnout_distribution
        )

    # ========================================================
    # ADMIN ANALYTICS
    # ========================================================

    st.divider()

    st.markdown("### 📊 Admin Analytics")

    st.markdown(
        """
        <div class="analysis-intro">
            <div>
                <strong>📈 Platform-Wide Behavioral Analytics</strong>
                <br>
                <span>
                    Monitor AURA performance trends, user activity volume,
                    and key behavioral indicators across all analyses.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if history_df.empty:
        st.info("No analysis data is available for admin analytics.")

    else:
        analytics_df = history_df.copy()

        # ----------------------------------------------------
        # CLEAN NUMERIC COLUMNS
        # ----------------------------------------------------

        numeric_columns = [
            "AURA_Score",
            "Stress_Level",
            "Sleep_Hours",
            "Energy_Level",
            "Task_Completion_Rate",
            "Workload",
            "Screen_Time",
        ]

        for col in numeric_columns:
            if col in analytics_df.columns:
                analytics_df[col] = pd.to_numeric(
                    analytics_df[col],
                    errors="coerce",
                )

        # ----------------------------------------------------
        # OVERALL ANALYTICS METRICS
        # ----------------------------------------------------

        st.markdown("### 📌 Overall Performance")

        avg_aura = (
            analytics_df["AURA_Score"].mean()
            if "AURA_Score" in analytics_df.columns
            else 0
        )

        median_aura = (
            analytics_df["AURA_Score"].median()
            if "AURA_Score" in analytics_df.columns
            else 0
        )

        best_aura = (
            analytics_df["AURA_Score"].max()
            if "AURA_Score" in analytics_df.columns
            else 0
        )

        total_analyses = len(analytics_df)

        a1, a2, a3, a4 = st.columns(4)

        with a1:
            st.metric(
                "📊 Total Analyses",
                int(total_analyses),
            )

        with a2:
            st.metric(
                "⭐ Average AURA",
                f"{avg_aura:.1f}",
            )

        with a3:
            st.metric(
                "📍 Median AURA",
                f"{median_aura:.1f}",
            )

        with a4:
            st.metric(
                "🏆 Best AURA",
                f"{best_aura:.1f}",
            )

        # ----------------------------------------------------
        # AURA TREND
        # ----------------------------------------------------

        st.markdown("### 📈 AURA Performance Trend")

        trend_df = analytics_df.copy()

        if "Timestamp" in trend_df.columns:

            trend_df["Timestamp"] = pd.to_datetime(
                trend_df["Timestamp"],
                errors="coerce",
            )

            trend_df = trend_df.dropna(
                subset=["Timestamp"]
            )

            trend_df = trend_df.sort_values(
                "Timestamp"
            )

        if (
            not trend_df.empty
            and "AURA_Score" in trend_df.columns
        ):

            trend_chart = trend_df[
                ["AURA_Score"]
            ].copy()

            if "Timestamp" in trend_df.columns:
                trend_chart.index = trend_df[
                    "Timestamp"
                ]

            else:
                trend_chart.index = range(
                    1,
                    len(trend_chart) + 1,
                )

            trend_chart = trend_chart.rename(
                columns={
                    "AURA_Score": "AURA Score"
                }
            )

            st.line_chart(
                trend_chart
            )

        else:
            st.info(
                "AURA trend data is not available."
            )

        # ----------------------------------------------------
        # DAILY ANALYSIS ACTIVITY
        # ----------------------------------------------------

        if (
            "Timestamp" in analytics_df.columns
        ):

            activity_df = analytics_df.copy()

            activity_df["Timestamp"] = pd.to_datetime(
                activity_df["Timestamp"],
                errors="coerce",
            )

            activity_df = activity_df.dropna(
                subset=["Timestamp"]
            )

            if not activity_df.empty:

                st.markdown(
                    "### 🗓️ Daily Analysis Volume"
                )

                activity_df["Date"] = (
                    activity_df["Timestamp"]
                    .dt.date
                )

                daily_activity = (
                    activity_df
                    .groupby("Date")
                    .size()
                    .reset_index(
                        name="Analyses"
                    )
                )

                daily_activity = (
                    daily_activity.set_index(
                        "Date"
                    )
                )

                st.bar_chart(
                    daily_activity
                )

        # ----------------------------------------------------
        # BEHAVIORAL AVERAGES
        # ----------------------------------------------------

        st.markdown(
            "### 🧠 Behavioral Indicator Averages"
        )

        indicator_map = {
            "Stress_Level": "Stress",
            "Sleep_Hours": "Sleep Hours",
            "Energy_Level": "Energy",
            "Task_Completion_Rate": "Task Completion",
            "Workload": "Workload",
            "Screen_Time": "Screen Time",
        }

        indicator_data = []

        for column, label in indicator_map.items():

            if column in analytics_df.columns:

                value = analytics_df[
                    column
                ].mean()

                if pd.notna(value):

                    indicator_data.append(
                        {
                            "Indicator": label,
                            "Average": round(
                                value,
                                2,
                            ),
                        }
                    )

        if indicator_data:

            indicator_df = pd.DataFrame(
                indicator_data
            ).set_index(
                "Indicator"
            )

            st.bar_chart(
                indicator_df
            )

        else:
            st.info(
                "Behavioral indicator data is not available."
            )

        # ----------------------------------------------------
        # AURA CORRELATION ANALYSIS
        # ----------------------------------------------------

        st.markdown(
            "### 🔗 Relationship With AURA Score"
        )

        correlation_columns = [
            "AURA_Score",
            "Stress_Level",
            "Sleep_Hours",
            "Energy_Level",
            "Task_Completion_Rate",
            "Workload",
            "Screen_Time",
        ]

        available_correlation_columns = [
            col
            for col in correlation_columns
            if col in analytics_df.columns
        ]

        if (
            "AURA_Score"
            in available_correlation_columns
            and len(
                available_correlation_columns
            ) > 1
        ):

            correlation_matrix = (
                analytics_df[
                    available_correlation_columns
                ]
                .corr(
                    numeric_only=True
                )
            )

            aura_correlations = (
                correlation_matrix[
                    "AURA_Score"
                ]
                .drop(
                    "AURA_Score"
                )
                .dropna()
                .sort_values(
                    ascending=False
                )
                .reset_index()
            )

            aura_correlations.columns = [
                "Behavioral Factor",
                "Correlation With AURA",
            ]

            aura_correlations[
                "Behavioral Factor"
            ] = aura_correlations[
                "Behavioral Factor"
            ].replace(
                {
                    "Stress_Level": "Stress Level",
                    "Sleep_Hours": "Sleep Hours",
                    "Energy_Level": "Energy Level",
                    "Task_Completion_Rate":
                        "Task Completion Rate",
                    "Workload": "Workload",
                    "Screen_Time": "Screen Time",
                }
            )

            aura_correlations[
                "Correlation With AURA"
            ] = aura_correlations[
                "Correlation With AURA"
            ].round(3)

            st.dataframe(
                aura_correlations,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                "Correlation shows statistical association only and "
                "does not prove that one factor causes another."
            )

        else:
            st.info(
                "Not enough numeric data is available "
                "for correlation analysis."
            )

    # ========================================================
    # ALL ANALYSIS RECORDS
    # ========================================================

    st.divider()

    st.subheader("🗂️ All Analysis Records")

    if history_df.empty:

        st.info(
            "No analysis records available."
        )

    else:

        admin_columns = [
            "Username",
            "Timestamp",
            "Productivity",
            "Burnout",
            "AURA_Score",
            "Stress_Level",
            "Sleep_Hours",
            "Energy_Level",
            "Task_Completion_Rate",
        ]

        admin_columns = [
            col
            for col in admin_columns
            if col in history_df.columns
        ]

        st.dataframe(
            history_df[admin_columns],
            use_container_width=True,
            hide_index=True,
        )

        # ----------------------------------------------------
        # DOWNLOAD ADMIN REPORT
        # ----------------------------------------------------

        st.download_button(
            label="📥 Download Complete Analysis Data",
            data=history_df.to_csv(
                index=False
            ),
            file_name="AURA_Admin_Analysis_Report.csv",
            mime="text/csv",
            use_container_width=True,
            key="admin_download_analysis",
        )

    # ========================================================
    # ADMIN SYSTEM STATUS
    # ========================================================

    st.divider()

    st.subheader("⚙️ System Status")

    s1, s2, s3 = st.columns(3)

    with s1:

        st.success(
            "🟢 Authentication System\n\nOperational"
        )

    with s2:

        st.success(
            "🟢 ML Analysis System\n\nOperational"
        )

    with s3:

        st.success(
            "🟢 History Storage\n\nOperational"
        )

    # ========================================================
    # BACK TO DASHBOARD
    # ========================================================

    st.divider()

    if st.button(
        "← Back to Dashboard",
        use_container_width=True,
        key="admin_back_dashboard",
    ):

        st.session_state.page = "Home"
        st.rerun()

# ============================================================
# SIDEBAR
# ============================================================

render_sidebar()


# ============================================================
# PAGE ROUTING
# ============================================================

if st.session_state.page == "Home":

    render_dashboard_page()


elif st.session_state.page == "AURA Analysis":

    render_daily_page(
        productivity_model,
        burnout_model,
    )

    st.divider()
    render_whatif_page(
        productivity_model,
        burnout_model,
    )


elif st.session_state.page == "Treatment":

    render_treatment_page()


elif st.session_state.page == "History":

    render_history_dashboard()


elif st.session_state.page == "About":

    render_about_page()


elif st.session_state.page == "Admin Panel":

    render_admin_dashboard()


else:
    st.session_state.page = "Home"
    st.rerun()

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🧠 AURA — Adaptive User Resilience & Analytics | "
    "Machine Learning based behavioral analytics system"
)

st.caption(
    "ℹ️ AURA provides data-driven behavioral insights and "
    "is not a medical or psychological diagnostic system."
)
