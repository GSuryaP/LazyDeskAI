"""Minimalist, refined front landing page for LazyDesk AI."""
import streamlit as st

def render_landing_view():
    """
    Render a magnified, perfectly centered front entrance page featuring
    the app name, tagline, and prominent continue button.
    """
    # 1. Main Centered Brand Hero
    st.markdown("""
    <div style="text-align: center; margin: 0 auto; width: 100%; max-width: 780px; padding: 0 1rem;">
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 26px;">
            <div style="width: 136px; height: 136px; border-radius: 50%; background: var(--accent-soft); border: 2.5px solid var(--border); display: flex; align-items: center; justify-content: center; font-size: 70px; box-shadow: 0 14px 36px rgba(73, 107, 80, 0.22); animation: ld-float 4s ease-in-out infinite;">
                🦥
            </div>
        </div>
        <h1 class="ld-landing-title">
            LazyDesk AI
        </h1>
        <p class="ld-landing-subline">
            Channel your inner sloth. Let local AI organize your digital clutter.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Prominent, Centered "Continue" Call to Action
    col_l, col_btn, col_r = st.columns([1, 1.4, 1])
    with col_btn:
        if st.button("Continue →", key="landing_continue_btn", type="primary", use_container_width=True):
            st.session_state["has_entered"] = True
            st.session_state["active_page"] = "Overview"
            st.session_state["main_navigation_radio"] = "Overview"
            st.query_params["page"] = "Overview"
            st.rerun()

    # 3. Understated Privacy & Model Subtext
    st.markdown("""
    <div class="ld-landing-footer">
        100% Local &amp; Private • Google Gemma 2 • Zero Cloud Fees
    </div>
    """, unsafe_allow_html=True)
