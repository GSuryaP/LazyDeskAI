"""Theme-aware design-token system and refined stylesheet for LazyDesk AI."""
from core.config import THEMES

def get_theme_css(theme_mode: str = "light") -> str:
    """Generate complete CSS injecting exact tokens and styling native Streamlit components."""
    mode = "dark" if theme_mode == "dark" else "light"
    t = THEMES[mode]

    # Contrast color for primary button text
    btn_text_color = "#FAF8F2" if mode == "light" else "#18231F"
    accent_surface_text = "#252C25" if mode == "light" else "#E8E8DB"

    return f"""
<style>
/* ==========================================================================
   LazyDesk AI Theme Tokens: {t['name']} ({mode.upper()})
   ========================================================================== */
:root {{
    --bg-app: {t['app_bg']};
    --surface-primary: {t['primary_surface']};
    --surface-secondary: {t['secondary_surface']};
    --accent-primary: {t['primary_accent']};
    --accent-hover: {t['accent_hover']};
    --accent-soft: {t['soft_accent_surface']};
    --accent-soft-text: {accent_surface_text};
    --text-primary: {t['main_text']};
    --text-secondary: {t['secondary_text']};
    --border: {t['borders']};
    --success: {t['success']};
    --warning: {t['warning']};
    --error: {t['error']};
    --card-shadow: {t['card_shadow']};
    --btn-text-primary: {btn_text_color};
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --font-mono: ui-monospace, "SF Mono", "Menlo", "Consolas", "Liberation Mono", monospace;
}}

/* Base Page and Streamlit Containers */
html, body, [data-testid="stAppViewContainer"], .stApp {{
    background-color: var(--bg-app) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-sans) !important;
    font-size: 14.5px !important;
    line-height: 1.55 !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* Top Header Bar - Eliminate fixed bar occlusion and prevent any button clipping */
header[data-testid="stHeader"],
[data-testid="stHeader"] {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    border-bottom: none !important;
    box-shadow: none !important;
    pointer-events: none !important;
    height: 0px !important;
    min-height: 0px !important;
    z-index: 10 !important;
}}

/* Hide all extraneous Streamlit header chrome (e.g. Deploy button, menus) */
header[data-testid="stHeader"] > * {{
    visibility: hidden !important;
}}

/* Allow interaction with sidebar collapse control */
header[data-testid="stHeader"] [data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapsedControl"] * {{
    visibility: visible !important;
    pointer-events: auto !important;
}}

/* Main Block Layout - Generous Whitespace, Guaranteed Clearance for Buttons & Titles */
.block-container,
[data-testid="stMainBlockContainer"],
.stMainBlockContainer,
div[data-testid="stAppViewContainer"] section.main .block-container,
section[data-testid="stMain"] .block-container {{
    max-width: 1080px !important;
    padding-top: 5.5rem !important;
    padding-bottom: 4rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}}

/* Sidebar Overrides */
[data-testid="stSidebar"] {{
    background-color: var(--surface-primary) !important;
    border-right: 1px solid var(--border) !important;
}}

[data-testid="stSidebar"] .block-container {{
    padding: 1.5rem 1rem !important;
}}

[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
    background-color: var(--surface-primary) !important;
    color: var(--text-primary) !important;
}}

/* Native Bordered Container as Editorial Card */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: var(--surface-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: var(--card-shadow) !important;
    padding: 18px 22px !important;
    margin-bottom: 14px !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    background-color: transparent !important;
}}

/* Headings Typography */
h1, h2, h3, h4, h5, h6 {{
    font-family: var(--font-sans) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    letter-spacing: -0.015em !important;
    margin-top: 0.5rem !important;
    margin-bottom: 0.4rem !important;
}}

h1 {{
    font-size: 1.6rem !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
}}

h2 {{
    font-size: 1.3rem !important;
    font-weight: 600 !important;
}}

h3 {{
    font-size: 1.08rem !important;
    font-weight: 600 !important;
}}

p, span, label, div {{
    color: var(--text-primary);
}}

/* Buttons Styling - Comprehensive Coverage */
div.stButton button,
div.stButton > button,
button[data-testid="baseButton-secondary"],
div[data-testid="stTooltipHoverTarget"] button {{
    font-family: var(--font-sans) !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    padding: 7px 16px !important;
    border-radius: 6px !important;
    border: 1px solid var(--border) !important;
    background-color: var(--surface-primary) !important;
    color: var(--text-primary) !important;
    box-shadow: var(--card-shadow) !important;
    transition: all 0.15s ease-in-out !important;
    white-space: nowrap !important;
    min-height: 38px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

/* Ensure button text and nested spans inherit the correct theme color */
div.stButton button *,
div.stButton > button *,
div[data-testid="stTooltipHoverTarget"] button * {{
    color: var(--text-primary) !important;
}}

div.stButton button:hover,
div.stButton > button:hover,
div[data-testid="stTooltipHoverTarget"] button:hover {{
    border-color: var(--accent-primary) !important;
    color: var(--accent-primary) !important;
    background-color: var(--surface-secondary) !important;
}}

div.stButton button:hover *,
div.stButton > button:hover *,
div[data-testid="stTooltipHoverTarget"] button:hover * {{
    color: var(--accent-primary) !important;
}}

div.stButton button:active,
div.stButton > button:active {{
    transform: translateY(1px);
}}

/* Dedicated Theme Toggle Button Styling */
.st-key-theme_toggle_btn button,
div.st-key-theme_toggle_btn button,
.st-key-landing_theme_toggle_btn button,
div.st-key-landing_theme_toggle_btn button {{
    background-color: var(--surface-primary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    padding: 7px 18px !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    box-shadow: var(--card-shadow) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

.st-key-theme_toggle_btn button *,
.st-key-theme_toggle_btn button p,
.st-key-theme_toggle_btn button span,
.st-key-landing_theme_toggle_btn button *,
.st-key-landing_theme_toggle_btn button p,
.st-key-landing_theme_toggle_btn button span {{
    color: var(--text-primary) !important;
}}

.st-key-theme_toggle_btn button:hover,
div.st-key-theme_toggle_btn button:hover,
.st-key-landing_theme_toggle_btn button:hover,
div.st-key-landing_theme_toggle_btn button:hover {{
    border-color: var(--accent-primary) !important;
    background-color: var(--surface-secondary) !important;
    color: var(--accent-primary) !important;
}}

.st-key-theme_toggle_btn button:hover *,
.st-key-theme_toggle_btn button:hover p,
.st-key-theme_toggle_btn button:hover span,
.st-key-landing_theme_toggle_btn button:hover *,
.st-key-landing_theme_toggle_btn button:hover p,
.st-key-landing_theme_toggle_btn button:hover span {{
    color: var(--accent-primary) !important;
}}

/* Primary Buttons */
div.stButton button[kind="primary"],
div.stButton > button[kind="primary"],
button[data-testid="baseButton-primary"] {{
    background-color: var(--accent-primary) !important;
    color: var(--btn-text-primary) !important;
    border: 1px solid var(--accent-primary) !important;
    font-weight: 600 !important;
}}

div.stButton button[kind="primary"] *,
button[data-testid="baseButton-primary"] * {{
    color: var(--btn-text-primary) !important;
}}

div.stButton button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {{
    background-color: var(--accent-hover) !important;
    border-color: var(--accent-hover) !important;
    color: var(--btn-text-primary) !important;
}}

div.stButton button[kind="primary"]:hover *,
button[data-testid="baseButton-primary"]:hover * {{
    color: var(--btn-text-primary) !important;
}}

/* Tooltips */
div[data-baseweb="tooltip"],
div[data-testid="stTooltipContent"],
div[role="tooltip"] {{
    background-color: var(--surface-secondary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-size: 12px !important;
    box-shadow: var(--card-shadow) !important;
}}

div[data-baseweb="tooltip"] *,
div[data-testid="stTooltipContent"] *,
div[role="tooltip"] * {{
    color: var(--text-primary) !important;
}}

div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="baseButton-primary"]:hover {{
    background-color: var(--accent-hover) !important;
    border-color: var(--accent-hover) !important;
    color: var(--btn-text-primary) !important;
}}

/* Input Fields */
div[data-baseweb="input"] > div,
input.stTextInput,
.stTextInput > div > div > input {{
    background-color: var(--surface-primary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-size: 14px !important;
    padding: 6px 12px !important;
    transition: border-color 0.15s ease !important;
}}

.stTextInput > div > div > input:focus {{
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 1px var(--accent-primary) !important;
}}

/* Selectbox & Dropdowns */
div[data-baseweb="select"] > div {{
    background-color: var(--surface-primary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}}

div[data-baseweb="popover"] ul,
div[data-baseweb="menu"] {{
    background-color: var(--surface-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}}

li[role="option"] {{
    color: var(--text-primary) !important;
}}

li[role="option"]:hover, li[aria-selected="true"] {{
    background-color: var(--accent-soft) !important;
    color: var(--accent-soft-text) !important;
}}

/* Radio Buttons */
div[data-testid="stRadio"] label {{
    font-size: 14px !important;
    color: var(--text-primary) !important;
    cursor: pointer;
}}

/* Tabs Styling */
button[data-baseweb="tab"] {{
    font-family: var(--font-sans) !important;
    color: var(--text-secondary) !important;
    font-size: 14px !important;
    padding: 8px 16px !important;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    color: var(--accent-primary) !important;
    font-weight: 600 !important;
    border-bottom-color: var(--accent-primary) !important;
}}

div[data-baseweb="tab-highlight"] {{
    background-color: var(--accent-primary) !important;
}}

div[data-baseweb="tab-border"] {{
    background-color: var(--border) !important;
}}

/* Expanders */
div[data-testid="stExpander"] {{
    background-color: var(--surface-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: var(--card-shadow) !important;
}}

div[data-testid="stExpander"] summary {{
    color: var(--text-primary) !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
}}

/* Streamlit Native Metrics */
[data-testid="stMetric"] {{
    background-color: var(--surface-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 14px 18px !important;
    box-shadow: var(--card-shadow) !important;
}}

[data-testid="stMetricLabel"] p {{
    font-size: 11px !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

[data-testid="stMetricValue"] div {{
    font-size: 24px !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}}

/* Alerts / Notifications */
div[data-testid="stAlert"] {{
    background-color: var(--surface-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}}

div[data-testid="stAlert"] p {{
    color: var(--text-primary) !important;
}}

/* DataFrames / Tables */
div[data-testid="stDataFrame"] {{
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    background-color: var(--surface-primary) !important;
}}

/* Custom Editorial Classes */
.ld-card {{
    background-color: var(--surface-primary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 14px;
    box-shadow: var(--card-shadow);
}}

.ld-card-muted {{
    background-color: var(--surface-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 14px;
}}

.ld-header-left h1 {{
    margin: 0 0 2px 0 !important;
    font-size: 1.55rem !important;
    letter-spacing: -0.02em;
}}

.ld-header-left p {{
    margin: 0 !important;
    color: var(--text-secondary);
    font-size: 13.5px;
}}

.ld-badge {{
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11.5px;
    font-weight: 600;
    letter-spacing: 0.02em;
    border: 1px solid var(--border);
    background: var(--surface-secondary);
    color: var(--text-primary);
}}

.ld-badge-sage {{
    background-color: var(--accent-soft);
    color: var(--accent-soft-text);
    border-color: var(--border);
    font-weight: 600;
}}

.ld-badge-warn {{
    background-color: rgba(165, 107, 43, 0.15);
    color: var(--warning);
    border-color: rgba(165, 107, 43, 0.35);
    font-weight: 600;
}}

.ld-badge-error {{
    background-color: rgba(180, 78, 69, 0.15);
    color: var(--error);
    border-color: rgba(180, 78, 69, 0.35);
    font-weight: 600;
}}

.ld-mono {{
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--text-primary);
    background: var(--surface-secondary);
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid var(--border);
}}

.ld-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
}}

.ld-dot-green {{
    background-color: var(--success);
}}

.ld-dot-amber {{
    background-color: var(--warning);
}}

.ld-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 13.5px;
    background-color: var(--surface-primary);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 16px;
}}

.ld-table th {{
    background-color: var(--surface-secondary);
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    text-align: left;
}}

.ld-table td {{
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    color: var(--text-primary);
    vertical-align: middle;
}}

.ld-table tr:last-child td {{
    border-bottom: none;
}}

.ld-table tr:hover td {{
    background-color: var(--accent-soft);
}}

.ld-action-item {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 7px 0;
    border-bottom: 1px dashed var(--border);
    font-size: 13.5px;
}}

.ld-action-item:last-child {{
    border-bottom: none;
}}

.ld-doc-section-title {{
    font-size: 11.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}}

.ld-empty-state {{
    text-align: center;
    padding: 40px 24px;
    background-color: var(--surface-primary);
    border: 1px dashed var(--border);
    border-radius: 8px;
    margin: 16px 0;
}}

.ld-empty-icon {{
    margin-bottom: 10px;
    opacity: 0.8;
}}

.ld-sidebar-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 16px;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--border);
}}

.ld-brand-title {{
    font-weight: 700;
    font-size: 16px;
    letter-spacing: -0.02em;
    color: var(--text-primary);
}}

.ld-brand-tagline {{
    font-size: 11px;
    color: var(--text-secondary);
}}

.ld-sidebar-footer {{
    margin-top: 32px;
    padding-top: 14px;
    border-top: 1px solid var(--border);
    font-size: 11px;
    color: var(--text-secondary);
    letter-spacing: 0.02em;
}}

/* ==========================================================================
   Minimalist Landing / Front Page Styles
   ========================================================================== */
.ld-landing-wrapper {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding-top: 4rem;
    padding-bottom: 2rem;
}}

.ld-landing-icon {{
    font-size: 68px;
    line-height: 1;
    margin-bottom: 20px;
    display: inline-block;
    filter: drop-shadow(0 6px 16px rgba(73, 107, 80, 0.22));
    animation: ld-float 3.5s ease-in-out infinite;
}}

@keyframes ld-float {{
    0%, 100% {{
        transform: translateY(0px) rotate(0deg);
    }}
    50% {{
        transform: translateY(-8px) rotate(-1.5deg);
    }}
}}

.ld-landing-title {{
    font-size: clamp(2.8rem, 6vw, 4.2rem);
    font-weight: 750;
    letter-spacing: -0.035em;
    color: var(--text-primary);
    margin: 0 0 16px 0 !important;
    padding: 0 !important;
    line-height: 1.15;
}}

.ld-landing-subline {{
    font-size: clamp(1.1rem, 2.2vw, 1.3rem);
    color: var(--text-secondary);
    max-width: 620px;
    margin: 0 auto;
    line-height: 1.6;
    font-weight: 400;
}}

.ld-landing-footer {{
    text-align: center;
    margin-top: 48px;
    font-size: 12px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--text-secondary);
    opacity: 0.75;
}}

/* Continue CTA Button Styling */
.st-key-landing_continue_btn button,
div.st-key-landing_continue_btn button {{
    padding: 13px 32px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    letter-spacing: -0.01em !important;
    box-shadow: 0 4px 14px rgba(73, 107, 80, 0.25) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}

.st-key-landing_continue_btn button:hover,
div.st-key-landing_continue_btn button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(73, 107, 80, 0.35) !important;
}}

/* Sidebar Landing Return Button */
.st-key-sidebar_landing_return_btn button,
div.st-key-sidebar_landing_return_btn button {{
    background-color: var(--surface-primary) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 6px 12px !important;
    border-radius: 6px !important;
    margin-bottom: 4px !important;
    transition: all 0.15s ease !important;
}}

.st-key-sidebar_landing_return_btn button *,
div.st-key-sidebar_landing_return_btn button * {{
    color: var(--text-secondary) !important;
}}

.st-key-sidebar_landing_return_btn button:hover,
div.st-key-sidebar_landing_return_btn button:hover {{
    border-color: var(--accent-primary) !important;
    color: var(--accent-primary) !important;
    background-color: var(--accent-soft) !important;
}}

.st-key-sidebar_landing_return_btn button:hover *,
div.st-key-sidebar_landing_return_btn button:hover * {{
    color: var(--accent-primary) !important;
}}

/* Custom Scrollbars */
::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
}}

::-webkit-scrollbar-track {{
    background: var(--bg-app);
}}

::-webkit-scrollbar-thumb {{
    background: var(--border);
    border-radius: 3px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: var(--text-secondary);
}}
</style>
"""
