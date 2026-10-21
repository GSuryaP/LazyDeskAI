"""LazyDesk AI - Premium Local-First AI Productivity Assistant.

Main Streamlit Application Entry Point.
"""
import streamlit as st
from pathlib import Path
from core.config import APP_DIR
from core.db import init_db, get_setting, set_setting
from ui.styles import get_theme_css
from ui.components import init_session_theme, render_sidebar_shell
from ui.views.landing_view import render_landing_view
from ui.views.overview import render_overview_view
from ui.views.organizer_view import render_organizer_view
from ui.views.doc_view import render_doc_view
from ui.views.duplicates_view import render_duplicates_view
from ui.views.history_view import render_history_view
from ui.views.settings_view import render_settings_view
from generate_sample_data import create_sample_messy_folder

# 1. Page Configuration
st.set_page_config(
    page_title="LazyDesk AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Database Initialization
init_db()

# 3. Ensure sample workspace exists on first run
sample_dir = APP_DIR / "sample_messy_desktop"
if not sample_dir.exists():
    create_sample_messy_folder(sample_dir)

# 4. Resolve Theme State (Light: "Warm Paper" / Dark: "Forest Graphite")
init_session_theme()
active_theme = st.session_state.get("theme", "light")

# 5. Inject Theme Stylesheet
css_markup = get_theme_css(active_theme)
st.markdown(css_markup, unsafe_allow_html=True)

# 6. Page Routing & Application Shell
if "active_page" not in st.session_state:
    query_p = st.query_params.get("page")
    if query_p:
        if query_p.lower() == "welcome":
            st.session_state["active_page"] = "Welcome"
            st.session_state["has_entered"] = False
        else:
            st.session_state["active_page"] = query_p
            st.session_state["has_entered"] = True
    else:
        st.session_state["active_page"] = "Welcome"
        st.session_state["has_entered"] = False

is_landing = (st.session_state.get("active_page") == "Welcome" or not st.session_state.get("has_entered", False))

if is_landing:
    # Full 4-sided true viewport centering for minimalist front entrance
    st.markdown("""
    <style>
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    
    html, body, [data-testid="stAppViewContainer"], section[data-testid="stMain"] {
        height: 100% !important;
        min-height: 100vh !important;
    }
    
    [data-testid="stMain"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        min-height: 100vh !important;
        height: 100vh !important;
        overflow-y: auto !important;
    }
    
    div[data-testid="stAppViewContainer"] section.main .block-container,
    section[data-testid="stMain"] .block-container,
    .block-container,
    [data-testid="stMainBlockContainer"],
    .stMainBlockContainer {
        max-width: 900px !important;
        width: 100% !important;
        margin: auto !important;
        padding: 0 1.5rem !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        min-height: 86vh !important;
        height: 86vh !important;
    }

    div[data-testid="stAppViewContainer"] section.main .block-container > div,
    section[data-testid="stMain"] .block-container > div,
    .block-container > div {
        margin: auto !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
    }
    </style>
    """, unsafe_allow_html=True)
    render_landing_view()
else:
    # Render sidebar navigation
    selected_page = render_sidebar_shell(st.session_state["active_page"])
    st.session_state["active_page"] = selected_page
    current_page = selected_page

    # 7. View Dispatcher
    if current_page == "Overview":
        render_overview_view()
    elif current_page == "File Organizer":
        render_organizer_view()
    elif current_page == "Document Intelligence":
        render_doc_view()
    elif current_page == "Duplicates":
        render_duplicates_view()
    elif current_page == "Activity History":
        render_history_view()
    elif current_page == "Settings":
        render_settings_view()
    else:
        render_overview_view()
