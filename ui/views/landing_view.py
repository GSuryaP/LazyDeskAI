"""Minimalist, refined front landing page for LazyDesk AI."""
import streamlit as st

def render_landing_view():
    """
    Render a clean, focused front entrance page featuring the app name,
    a one-line tagline, and a prominent continue button leading into the workspace.
    """
    # 1. Main Centered Brand Hero
    st.markdown("""
    <div style="text-align: center; padding-top: 5rem; padding-bottom: 1.5rem; max-width: 680px; margin: 0 auto;">
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 22px;">
            <div style="width: 86px; height: 86px; border-radius: 50%; background: var(--accent-soft); border: 2px solid var(--border); display: flex; align-items: center; justify-content: center; font-size: 44px; box-shadow: 0 8px 24px rgba(73, 107, 80, 0.16); animation: ld-float 3.5s ease-in-out infinite;">
                🦥
            </div>
        </div>
        <h1 style="font-size: clamp(2.8rem, 5.5vw, 4rem); font-weight: 800; letter-spacing: -0.035em; color: var(--text-primary); text-align: center; margin: 0 0 16px 0; padding: 0; line-height: 1.15;">
            LazyDesk AI
        </h1>
        <p style="font-size: clamp(1.1rem, 2vw, 1.3rem); color: var(--text-secondary); text-align: justify; text-justify: inter-word; text-align-last: center; max-width: 580px; margin: 0 auto 36px auto; line-height: 1.6; font-weight: 400;">
            Channel your inner sloth. Let local AI organize your digital clutter.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Prominent, Centered "Continue" Call to Action
    col_l, col_btn, col_r = st.columns([1.3, 1.1, 1.3])
    with col_btn:
        if st.button("Continue →", key="landing_continue_btn", type="primary", use_container_width=True):
            st.session_state["has_entered"] = True
            st.session_state["active_page"] = "Overview"
            st.session_state["main_navigation_radio"] = "Overview"
            st.query_params["page"] = "Overview"
            st.rerun()

    # 3. Understated Privacy & Model Subtext
    st.markdown("""
    <div style="text-align: center; margin-top: 42px; font-size: 12px; letter-spacing: 0.05em; text-transform: uppercase; color: var(--text-secondary); opacity: 0.75;">
        100% Local &amp; Private • Google Gemma 2 • Zero Cloud Fees
    </div>
    """, unsafe_allow_html=True)
