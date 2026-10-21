"""Document Intelligence interface for LazyDesk AI."""
from pathlib import Path
import streamlit as st
from core.config import APP_DIR
from core.doc_intel import extract_text_from_file, analyze_document_file
from core.scanner import get_scanned_files
from ui.components import render_top_header, render_html, render_empty_state

def render_doc_view():
    """Render Document Intelligence editorial workspace."""
    render_top_header(
        title="Document Intelligence",
        description="Extract structured summaries, action items, and milestone dates from your local documents."
    )

    default_sample_dir = str(APP_DIR / "sample_messy_desktop")
    active_folder = st.session_state.get("active_folder", default_sample_dir)

    # 1. Document Selection Area in clean bordered container
    with st.container(border=True):
        sel_mode = st.radio("Source", ["Browse Folder Files", "Upload Document"], horizontal=True, label_visibility="collapsed")

        selected_file_path = None

        if sel_mode == "Browse Folder Files":
            candidates = []
            active_p = Path(active_folder).expanduser().resolve()
            if active_p.is_dir():
                for p in active_p.rglob("*"):
                    if p.is_file() and p.suffix.lower() in [".md", ".txt", ".pdf", ".csv", ".py", ".sql", ".json"]:
                        candidates.append(str(p))

            # Sort candidates so markdown and txt files appear first
            candidates.sort(key=lambda x: (0 if x.endswith(".md") else (1 if x.endswith(".txt") else 2), x))

            if candidates:
                selected_file_path = st.selectbox(
                    "Select a document to read and summarize",
                    options=candidates,
                    format_func=lambda x: f"{Path(x).name}  ({Path(x).parent.name}/)",
                    key="doc_select_box"
                )
            else:
                st.info(f"No text or PDF documents found in '{active_folder}'. Scan a folder first or upload a document below.")
        else:
            uploaded = st.file_uploader("Upload a local file (PDF, TXT, MD, Code, CSV)", type=["pdf", "txt", "md", "csv", "py", "sql", "json"])
            if uploaded:
                temp_dir = APP_DIR / "data" / "uploads"
                temp_dir.mkdir(parents=True, exist_ok=True)
                save_path = temp_dir / uploaded.name
                save_path.write_bytes(uploaded.getbuffer())
                selected_file_path = str(save_path)

    if not selected_file_path or not Path(selected_file_path).exists():
        render_empty_state(
            title="Select a document to begin",
            message="LazyDesk reads files locally, detects deadlines and todos, and synthesizes an executive summary."
        )
        return

    # 2. Document Analysis Trigger & Cache Check
    col_run, col_refresh = st.columns([3.8, 1.2], vertical_alignment="center")
    with col_refresh:
        force_reanalyze = st.button("Re-analyze", use_container_width=True, help="Rerun local model inference")

    with st.spinner("Analyzing document with local intelligence..."):
        result = analyze_document_file(selected_file_path, force_refresh=force_reanalyze)

    meta = result.get("metadata", {})

    # 3. Editorial Document Workspace (Reader Layout)
    render_html("""
    <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px;">
        Document Workspace
    </div>
    """)

    # Document Header & Metadata Bar in clean container
    with st.container(border=True):
        cached_badge = '<span class="ld-badge" style="margin-left: 6px;">Cached</span>' if result.get('cached') else ''
        page_count_html = f"<div><strong>Pages:</strong> {meta.get('page_count')}</div>" if meta.get('page_count') else ""
        render_html(f"""
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
            <div style="font-size: 16px; font-weight: 600; color: var(--text-primary);">{meta.get('file_name', Path(selected_file_path).name)}</div>
            <div style="display: flex; gap: 8px;">
                <span class="ld-badge ld-badge-sage">{meta.get('extension', '').upper()}</span>
                <span class="ld-badge">{result.get('model_used', 'Local Model')}</span>
                {cached_badge}
            </div>
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 16px; font-size: 12px; color: var(--text-secondary); border-top: 1px solid var(--border); padding-top: 8px;">
            <div><strong>Size:</strong> {meta.get('file_size', 0) / 1024:.1f} KB</div>
            <div><strong>Words:</strong> {meta.get('word_count', 0)}</div>
            <div><strong>Lines:</strong> {meta.get('line_count', 0)}</div>
            {page_count_html}
            <div><strong>Modified:</strong> {meta.get('last_modified', '-')}</div>
        </div>
        """)

    # Two column layout: Executive Summary & Action Items/Dates
    c_left, c_right = st.columns([1.7, 1.3])

    with c_left:
        with st.container(border=True):
            render_html(f"""
            <div class="ld-doc-section-title">
                <span>Executive Summary</span>
                <span class="ld-badge" style="font-size: 10px; font-weight: normal;">Model Synthesis</span>
            </div>
            <div style="font-size: 14px; line-height: 1.65; color: var(--text-primary); margin-top: 8px; margin-bottom: 14px;">
                {result.get('summary', 'No summary available.')}
            </div>
            """)

            summary_text = result.get('summary', '')
            if st.button("Copy Summary to Clipboard", key="copy_summary_btn"):
                st.code(summary_text, language="markdown")
                st.toast("Summary formatted for copying!")

    with c_right:
        with st.container(border=True):
            action_items = result.get("action_items", [])
            render_html("""
            <div class="ld-doc-section-title">
                <span>Extracted Action Items</span>
                <span class="ld-badge ld-badge-sage" style="font-size: 10px;">Extracted</span>
            </div>
            """)

            if action_items:
                for item in action_items:
                    render_html(f"""
                    <div class="ld-action-item">
                        <span style="color: var(--accent-primary); font-weight: bold;">•</span>
                        <span style="font-size: 13px; color: var(--text-primary);">{item}</span>
                    </div>
                    """)
            else:
                render_html("<div style='font-size: 12.5px; color: var(--text-secondary);'>No explicit action items found in this document.</div>")

        with st.container(border=True):
            key_dates = result.get("key_dates", [])
            render_html("""
            <div class="ld-doc-section-title">
                <span>Milestones & Deadlines</span>
                <span class="ld-badge" style="font-size: 10px;">Detected Dates</span>
            </div>
            """)

            if key_dates:
                for d in key_dates:
                    render_html(f"""
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span class="ld-badge ld-badge-warn" style="font-family: var(--font-mono); font-size: 11.5px;">{d}</span>
                        <span style="font-size: 12px; color: var(--text-secondary);">Timeline event</span>
                    </div>
                    """)
            else:
                render_html("<div style='font-size: 12.5px; color: var(--text-secondary);'>No explicit calendar dates detected.</div>")

    # 4. Raw Document Viewer in Collapsible Section
    with st.expander("View Full Extracted Document Text", expanded=False):
        raw_extraction = extract_text_from_file(selected_file_path)
        raw_text = raw_extraction.get("text", "")
        st.text_area("Extracted Text", value=raw_text, height=280, disabled=True, label_visibility="collapsed")
