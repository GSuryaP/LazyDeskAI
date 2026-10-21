"""Settings and Configuration interface for LazyDesk AI."""
import streamlit as st
from core.config import DEFAULT_OLLAMA_HOST, CATEGORY_MAP
from core.db import get_setting, set_setting, get_db_connection
from core.llm_service import LLMService
from ui.components import render_top_header, render_html

def render_settings_view():
    """Render application settings and model configuration."""
    render_top_header(
        title="Settings",
        description="Configure your local inference engine, directory rules, and system storage."
    )

    llm = LLMService()
    connected, installed_models, conn_status, latency = llm.check_connection()

    # 1. Local AI Engine Configuration
    render_html("""
    <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px;">
        Local AI Engine (Ollama / Gemma)
    </div>
    """)

    with st.container(border=True):
        current_host = get_setting("ollama_host", DEFAULT_OLLAMA_HOST)
        new_host = st.text_input("Ollama Host API Endpoint", value=current_host, help="URL of your running Ollama instance")

        if new_host != current_host:
            set_setting("ollama_host", new_host)
            st.toast("Updated Ollama host endpoint.")
            st.rerun()

        # Model selection
        options = installed_models if installed_models else ["qwen3:8b", "gemma:2b", "gemma2:2b"]
        current_pref = get_setting("preferred_model", options[0])
        pref_idx = options.index(current_pref) if current_pref in options else 0

        selected_model = st.selectbox(
            "Selected Local Model",
            options=options,
            index=pref_idx,
            help="Choose the model used for document summarization and action item parsing."
        )

        if selected_model != current_pref:
            set_setting("preferred_model", selected_model)
            st.toast(f"Preferred model changed to {selected_model}")
            st.rerun()

        # Engine diagnostic details
        dot = "ld-dot-green" if connected else "ld-dot-amber"
        render_html(f"""
        <div style="display: flex; gap: 20px; font-size: 12px; color: var(--text-secondary); border-top: 1px solid var(--border); padding-top: 10px; margin-top: 10px;">
            <div><span class="ld-dot {dot}"></span> <strong>Daemon:</strong> {conn_status}</div>
            <div><strong>Latency:</strong> {latency} ms</div>
            <div><strong>Models detected:</strong> {len(installed_models)}</div>
        </div>
        """)

    # 2. Category Extension Rules
    render_html("""
    <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; margin-top: 16px;">
        Categorization & Filing Rules
    </div>
    """)

    with st.container(border=True):
        render_html("<div style='font-size: 13px; color: var(--text-secondary); margin-bottom: 10px;'>Files are organized into subfolders according to file extension signatures:</div>")

        for cat, exts in CATEGORY_MAP.items():
            ext_str = ", ".join(exts)
            render_html(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 13px;">
                <span style="font-weight: 600; width: 140px;">{cat}</span>
                <span class="ld-mono" style="font-size: 11.5px; color: var(--text-secondary);">{ext_str}</span>
            </div>
            """)

    # 3. System Reset & Maintenance
    render_html("""
    <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px; margin-top: 16px;">
        Database Maintenance
    </div>
    """)

    with st.container(border=True):
        c_reset1, c_reset2 = st.columns([3.4, 1.2], vertical_alignment="center")
        with c_reset1:
            render_html("""
            <div style="font-weight: 600; font-size: 13.5px;">Reset Activity and Scan Cache</div>
            <div style="font-size: 12px; color: var(--text-secondary);">Clears cached scan items and undo history from the local SQLite database. Does not alter your physical files.</div>
            """)
        with c_reset2:
            if st.button("Reset DB Cache", help="Purge database tables", use_container_width=True):
                conn = get_db_connection()
                with conn:
                    conn.execute("DELETE FROM scanned_files;")
                    conn.execute("DELETE FROM activity_log;")
                    conn.execute("DELETE FROM document_summaries;")
                conn.close()
                st.success("Cache cleared successfully.")
                st.rerun()
