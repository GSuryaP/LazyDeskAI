"""Reusable, refined UI components for LazyDesk AI."""
import re
import textwrap
from typing import Optional, Dict, Any
import streamlit as st
from core.db import get_setting, set_setting
from core.llm_service import LLMService

LEAF_FOLDER_ICON = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 7C3 5.89543 3.89543 5 5 5H9.58579C10.1162 5 10.6249 5.21071 11 5.58579L12.4142 7H19C20.1046 7 21 7.89543 21 9V18C21 19.1046 20.1046 20 19 20H5C3.89543 20 3 19.1046 3 18V7Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M9 14C11.5 11.5 15 11 15 11C15 11 14.5 14.5 12 17C10.5 18.5 8 18 8 18C8 18 7.5 15.5 9 14Z" fill="currentColor" fill-opacity="0.22" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

def render_html(html_str: str):
    """Safely render HTML directly via st.html without markdown code block interference."""
    st.html(html_str)

def navigate_to(page_name: str):
    """Safely request programmatic navigation before the radio widget is instantiated."""
    st.session_state["pending_nav_target"] = page_name
    st.session_state["active_page"] = page_name
    st.query_params["page"] = page_name
    st.rerun()

def init_session_theme():
    """Initialize theme from URL query param, database setting, or session state."""
    # 1. Check query parameters
    query_theme = st.query_params.get("theme")
    if query_theme in ("light", "dark"):
        st.session_state["theme"] = query_theme
        set_setting("theme", query_theme)
        return

    # 2. Check session state
    if "theme" not in st.session_state:
        # 3. Check persistent database
        db_theme = get_setting("theme", "light")
        st.session_state["theme"] = db_theme if db_theme in ("light", "dark") else "light"

def render_sidebar_shell(active_page: str) -> str:
    """Render the refined sidebar navigation and persistent brand assets."""
    with st.sidebar:
        # Brand Wordmark & Leaf/Folder Icon
        render_html(f"""
        <div class="ld-sidebar-brand">
            <div style="color: var(--accent-primary);">{LEAF_FOLDER_ICON}</div>
            <div>
                <div class="ld-brand-title">LazyDesk AI</div>
                <div class="ld-brand-tagline">Local-first productivity</div>
            </div>
        </div>
        """)

        # Navigation Menu
        nav_options = [
            "Overview",
            "File Organizer",
            "Document Intelligence",
            "Duplicates",
            "Activity History",
            "Settings"
        ]

        # 1. Consume pending programmatic navigation BEFORE creating widget
        if "pending_nav_target" in st.session_state:
            target = st.session_state.pop("pending_nav_target")
            if target in nav_options:
                st.session_state["main_navigation_radio"] = target
                st.session_state["active_page"] = target
                st.query_params["page"] = target

        # 2. Check query param for direct navigation
        query_page = st.query_params.get("page")
        if query_page in nav_options:
            if "main_navigation_radio" not in st.session_state or st.session_state.get("active_page") != query_page:
                st.session_state["main_navigation_radio"] = query_page
                st.session_state["active_page"] = query_page

        if "main_navigation_radio" in st.session_state and st.session_state["main_navigation_radio"] in nav_options:
            current_idx = nav_options.index(st.session_state["main_navigation_radio"])
        else:
            current_idx = nav_options.index(active_page) if active_page in nav_options else 0

        selected_nav = st.radio(
            "Navigation",
            options=nav_options,
            index=current_idx,
            label_visibility="collapsed",
            key="main_navigation_radio"
        )
        st.session_state["active_page"] = selected_nav
        st.query_params["page"] = selected_nav

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        # Model Status Pill in Sidebar
        llm = LLMService()
        connected, models, status_msg, latency = llm.check_connection()
        pref_model = llm.get_preferred_model()

        if connected:
            dot_class = "ld-dot-green"
            model_label = f"{pref_model} • {latency}ms"
        else:
            dot_class = "ld-dot-amber"
            model_label = "Local Engine Standby"

        render_html(f"""
        <div style="padding: 10px 12px; background: var(--surface-secondary); border: 1px solid var(--border); border-radius: 6px;">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-secondary); margin-bottom: 5px;">Local Engine</div>
            <div style="display: flex; align-items: center; gap: 7px; font-size: 12.5px; font-weight: 500;">
                <span class="ld-dot {dot_class}"></span>
                <span style="font-family: var(--font-mono); font-size: 11.5px;">{model_label}</span>
            </div>
        </div>
        """)

        # Sidebar Footer
        render_html("""
        <div class="ld-sidebar-footer">
            Your files. Your machine.
        </div>
        """)

    return selected_nav

def render_top_header(title: str, description: str):
    """
    Render main view header with title, description, live model indicator,
    and the working Light/Dark theme toggle.
    """
    current_theme = st.session_state.get("theme", "light")
    is_dark = (current_theme == "dark")

    col_title, col_actions = st.columns([2.5, 1.9], vertical_alignment="center")

    with col_title:
        render_html(f"""
        <div class="ld-header-left">
            <h1 style="margin: 0 0 3px 0; padding: 0; line-height: 1.25;">{title}</h1>
            <p style="margin: 0; padding: 0;">{description}</p>
        </div>
        """)

    with col_actions:
        theme_col, model_col = st.columns([1.35, 0.85], vertical_alignment="center")

        with theme_col:
            toggle_label = "☀️ Light Theme" if is_dark else "🌙 Dark Theme"
            next_theme = "light" if is_dark else "dark"
            tooltip_msg = f"Switch to {next_theme.title()} theme"

            if st.button(toggle_label, key="theme_toggle_btn", help=tooltip_msg, use_container_width=True):
                st.session_state["theme"] = next_theme
                set_setting("theme", next_theme)
                st.query_params["theme"] = next_theme
                st.rerun()

        with model_col:
            llm = LLMService()
            connected, _, _, _ = llm.check_connection()
            status_text = "Ready" if connected else "Offline"
            badge_class = "ld-badge-sage" if connected else "ld-badge-warn"
            render_html(f"""
            <div style="text-align: right; padding-top: 1px;">
                <span class="ld-badge {badge_class}">AI: {status_text}</span>
            </div>
            """)

    render_html("<hr style='margin: 12px 0 20px 0; border: none; border-top: 1px solid var(--border);'>")

def render_metric_card(label: str, value: Any, subtext: str = ""):
    """Render a compact editorial metric block."""
    render_html(f"""
    <div style="background-color: var(--surface-primary); border: 1px solid var(--border); border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; box-shadow: var(--card-shadow);">
        <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 4px;">{label}</div>
        <div style="font-size: 24px; font-weight: 600; letter-spacing: -0.02em; color: var(--text-primary);">{value}</div>
        {f'<div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">{subtext}</div>' if subtext else ''}
    </div>
    """)

def render_empty_state(title: str, message: str) -> None:
    """Render a calm, content-first empty state."""
    render_html(f"""
    <div class="ld-empty-state">
        <div class="ld-empty-icon" style="color: var(--accent-primary);">
            {LEAF_FOLDER_ICON}
        </div>
        <div style="font-size: 15px; font-weight: 600; margin-bottom: 6px; color: var(--text-primary);">{title}</div>
        <div style="font-size: 13.5px; color: var(--text-secondary); max-width: 440px; margin: 0 auto 16px auto; line-height: 1.5;">{message}</div>
    </div>
    """)
