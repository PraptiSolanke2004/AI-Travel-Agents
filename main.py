"""
Aerogen — AI Travel Planner
Landing / Home Page
Run with: streamlit run main.py
"""

import streamlit as st
from db import register_user, login_user

st.set_page_config(
    page_title="Aerogen — AI Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Hide default sidebar nav & hamburger ──
st.markdown("""
<style>
[data-testid="collapsedControl"] { display:none; }
[data-testid="stSidebar"] { display:none; }
#MainMenu { visibility:hidden; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ── THEMES (shared with Planner.py via session_state) ──
if "theme" not in st.session_state:
    st.session_state["theme"] = "🌑 Dark Ocean"

THEMES_MAIN = {
    "🌑 Dark Ocean": {
        "app_bg":          "linear-gradient(135deg,#060d1f 0%,#0a1628 40%,#0d1a35 100%)",
        "text":            "rgba(255,255,255,.85)",
        "text_muted":      "rgba(255,255,255,.5)",
        "nav_bg":          "rgba(6,13,31,0.85)",
        "nav_border":      "rgba(255,255,255,0.07)",
        "nav_link":        "rgba(255,255,255,0.6)",
        "tag_bg":          "rgba(99,179,237,0.12)",
        "tag_border":      "rgba(99,179,237,0.3)",
        "tag_color":       "#90cdf4",
        "card_bg":         "rgba(255,255,255,0.04)",
        "card_border":     "rgba(255,255,255,0.09)",
        "card_hover":      "rgba(99,179,237,0.4)",
        "feat_title":      "white",
        "feat_desc":       "rgba(255,255,255,0.45)",
        "stat_label":      "rgba(255,255,255,0.4)",
        "divider":         "rgba(255,255,255,0.1)",
        "btn_bg":          "rgba(255,255,255,0.08)",
        "btn_border":      "rgba(255,255,255,0.2)",
        "btn_color":       "white",
        "brand_grad":      "linear-gradient(135deg,#63b3ed,#818cf8,#c4b5fd)",
        "accent_grad":     "linear-gradient(135deg,#63b3ed,#818cf8,#f472b6)",
        "stat_grad":       "linear-gradient(135deg,#63b3ed,#818cf8)",
        "footer_col":      "rgba(255,255,255,0.25)",
        "feat_sec":        "Everything you need to travel smarter",
        "feat_sec_c":      "white",
        "dialog_bg":       "#0a1628",
        "input_bg":        "rgba(255,255,255,0.07)",
        "input_border":    "rgba(255,255,255,0.15)",
        "input_color":     "white",
        "placeholder_col": "rgba(255,255,255,0.35)",
    },
    "☀️ Light Cloud": {
        "app_bg":          "linear-gradient(135deg,#f0f4ff 0%,#e8f0fe 40%,#f5f0ff 100%)",
        "text":            "#1e293b",
        "text_muted":      "#64748b",
        "nav_bg":          "rgba(240,244,255,0.92)",
        "nav_border":      "rgba(0,0,0,0.08)",
        "nav_link":        "#475569",
        "tag_bg":          "rgba(59,130,246,0.1)",
        "tag_border":      "rgba(59,130,246,0.3)",
        "tag_color":       "#1d4ed8",
        "card_bg":         "rgba(255,255,255,0.85)",
        "card_border":     "rgba(0,0,0,0.08)",
        "card_hover":      "rgba(59,130,246,0.35)",
        "feat_title":      "#1e293b",
        "feat_desc":       "#64748b",
        "stat_label":      "#64748b",
        "divider":         "rgba(0,0,0,0.1)",
        "btn_bg":          "rgba(0,0,0,0.07)",
        "btn_border":      "rgba(0,0,0,0.15)",
        "btn_color":       "#1e293b",
        "brand_grad":      "linear-gradient(135deg,#2563eb,#6366f1)",
        "accent_grad":     "linear-gradient(135deg,#2563eb,#6366f1,#8b5cf6)",
        "stat_grad":       "linear-gradient(135deg,#2563eb,#6366f1)",
        "footer_col":      "#94a3b8",
        "feat_sec":        "Everything you need to travel smarter",
        "feat_sec_c":      "#1e293b",
        "dialog_bg":       "#ffffff",
        "input_bg":        "#f8fafc",
        "input_border":    "rgba(0,0,0,0.18)",
        "input_color":     "#1e293b",
        "placeholder_col": "#94a3b8",
    },
    "🌌 Midnight Purple": {
        "app_bg":          "linear-gradient(135deg,#0f0a1e 0%,#1a0e35 40%,#0d0a2e 100%)",
        "text":            "rgba(255,255,255,.9)",
        "text_muted":      "rgba(196,181,253,0.6)",
        "nav_bg":          "rgba(15,10,30,0.88)",
        "nav_border":      "rgba(167,139,250,0.12)",
        "nav_link":        "rgba(196,181,253,0.65)",
        "tag_bg":          "rgba(167,139,250,0.12)",
        "tag_border":      "rgba(167,139,250,0.35)",
        "tag_color":       "#c4b5fd",
        "card_bg":         "rgba(255,255,255,0.04)",
        "card_border":     "rgba(167,139,250,0.18)",
        "card_hover":      "rgba(167,139,250,0.45)",
        "feat_title":      "white",
        "feat_desc":       "rgba(196,181,253,0.55)",
        "stat_label":      "rgba(196,181,253,0.45)",
        "divider":         "rgba(167,139,250,0.15)",
        "btn_bg":          "rgba(167,139,250,0.1)",
        "btn_border":      "rgba(167,139,250,0.3)",
        "btn_color":       "white",
        "brand_grad":      "linear-gradient(135deg,#a78bfa,#c4b5fd,#f472b6)",
        "accent_grad":     "linear-gradient(135deg,#a78bfa,#f472b6)",
        "stat_grad":       "linear-gradient(135deg,#a78bfa,#c4b5fd)",
        "footer_col":      "rgba(196,181,253,0.3)",
        "feat_sec":        "Everything you need to travel smarter",
        "feat_sec_c":      "rgba(255,255,255,0.9)",
        "dialog_bg":       "#1a0e35",
        "input_bg":        "rgba(167,139,250,0.07)",
        "input_border":    "rgba(167,139,250,0.22)",
        "input_color":     "white",
        "placeholder_col": "rgba(196,181,253,0.4)",
    },
}

tm = THEMES_MAIN[st.session_state["theme"]]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"] {{ font-family:'Inter',sans-serif; margin:0; padding:0; }}
.stApp {{ background:{tm['app_bg']}; min-height:100vh; }}
.brand {{ font-family:'Outfit',sans-serif; font-size:1.8rem; font-weight:900;
    background:{tm['brand_grad']}; -webkit-background-clip:text;
    -webkit-text-fill-color:transparent; background-clip:text; letter-spacing:-0.5px; }}
.hero-title {{ font-family:'Outfit',sans-serif; font-size:3.8rem; font-weight:900;
    color:{tm['text']}; line-height:1.12; margin-bottom:0.5rem; letter-spacing:-1.5px; }}
.hero-title .accent {{ background:{tm['accent_grad']};
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }}
.hero-sub {{ color:{tm['text_muted']}; font-size:1.15rem; max-width:560px;
    margin:1.2rem auto 2.5rem; line-height:1.7; }}
.hero-tag {{ display:inline-block; background:{tm['tag_bg']}; border:1px solid {tm['tag_border']};
    color:{tm['tag_color']}; padding:.35rem 1rem; border-radius:20px;
    font-size:.82rem; font-weight:600; letter-spacing:.5px; margin-bottom:1.5rem; }}
.hero-section {{ text-align:center; padding:5rem 2rem 4rem; max-width:860px; margin:0 auto; }}
.feat-card {{ flex:1; min-width:220px; max-width:300px; background:{tm['card_bg']};
    border:1px solid {tm['card_border']}; border-radius:18px; padding:2rem 1.5rem;
    text-align:center; transition:border-color .3s,transform .3s; }}
.feat-card:hover {{ border-color:{tm['card_hover']}; transform:translateY(-4px); }}
.feat-icon {{ font-size:2.2rem; margin-bottom:.75rem; }}
.feat-title {{ font-family:'Outfit',sans-serif; font-weight:700; font-size:1.05rem;
    color:{tm['feat_title']}; margin-bottom:.4rem; }}
.feat-desc {{ color:{tm['feat_desc']}; font-size:.88rem; line-height:1.6; }}
.features-row {{ display:flex; gap:1.5rem; max-width:1000px; margin:3rem auto;
    padding:0 2rem; flex-wrap:wrap; justify-content:center; }}
.stat-num {{ font-family:'Outfit',sans-serif; font-size:2.2rem; font-weight:800;
    background:{tm['stat_grad']}; -webkit-background-clip:text;
    -webkit-text-fill-color:transparent; background-clip:text; }}
.stat-label {{ color:{tm['stat_label']}; font-size:.85rem; margin-top:2px; }}
.stats-row {{ display:flex; justify-content:center; gap:4rem; padding:2rem 0 3rem; flex-wrap:wrap; }}
.divider {{ width:80%; max-width:700px; height:1px;
    background:linear-gradient(90deg,transparent,{tm['divider']},transparent); margin:1rem auto; }}
.stButton>button {{ background:{tm['btn_bg']}!important; border:1px solid {tm['btn_border']}!important;
    color:{tm['btn_color']}!important; border-radius:10px!important; font-weight:600!important;
    padding:.5rem 1.4rem!important; transition:all .2s!important; }}
.stButton>button:hover {{ background:rgba(99,102,241,.25)!important;
    border-color:rgba(99,102,241,.5)!important; }}

/* ── Sign In Dialog theming ── */
[data-testid="stDialog"] > div > div {{
    background:{tm['dialog_bg']}!important;
    border-radius:16px!important; }}
[data-testid="stDialog"] p,
[data-testid="stDialog"] label,
[data-testid="stDialog"] span {{
    color:{tm['text']}!important; }}
[data-testid="stDialog"] input {{
    background:{tm['input_bg']}!important;
    border:1px solid {tm['input_border']}!important;
    color:{tm['input_color']}!important;
    -webkit-text-fill-color:{tm['input_color']}!important;
    border-radius:8px!important; }}
[data-testid="stDialog"] input::placeholder {{
    color:{tm['placeholder_col']}!important;
    opacity:1!important; }}
[data-testid="stDialog"] .stTabs [data-baseweb="tab"] {{
    color:{tm['text']}!important; }}
[data-testid="stDialog"] .stButton>button {{
    background:linear-gradient(135deg,#3b82f6,#6366f1)!important;
    color:white!important; border:none!important; }}
</style>
""", unsafe_allow_html=True)


# ── SIGN IN DIALOG ──────────────────────────────────────
@st.dialog("💫 Welcome to Aerogen")
def sign_in_dialog():
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:1rem;">
        <span style="font-family:'Outfit',sans-serif;font-size:1.6rem;font-weight:800;
                     background:{tm['brand_grad']};
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                     background-clip:text;">Aerogen</span>
    </div>
    """, unsafe_allow_html=True)

    tab_in, tab_up = st.tabs(["Sign In", "Sign Up"])

    # ── SIGN IN ──
    with tab_in:
        email    = st.text_input("📧 Email", placeholder="you@example.com", key="si_email")
        password = st.text_input("🔒 Password", type="password", placeholder="••••••••", key="si_pass")
        if st.button("Sign In →", key="btn_signin", use_container_width=True):
            if email and password:
                result = login_user(email, password)
                if result["ok"]:
                    st.session_state["user"]    = result["user"]["email"]
                    st.session_state["user_id"] = result["user"]["id"]
                    st.session_state["user_name"] = result["user"]["name"]
                    st.success(f"✅ Welcome back, {result['user']['name']}!")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.warning("Please fill in both fields.")

    # ── SIGN UP ──
    with tab_up:
        name     = st.text_input("👤 Full Name", placeholder="Your Name", key="su_name")
        email2   = st.text_input("📧 Email", placeholder="you@example.com", key="su_email")
        pass2    = st.text_input("🔒 Password", type="password", placeholder="min 6 characters", key="su_pass")
        if st.button("Create Account →", key="btn_signup", use_container_width=True):
            if name and email2 and pass2:
                if len(pass2) < 6:
                    st.error("❌ Password must be at least 6 characters.")
                else:
                    result = register_user(name, email2, pass2)
                    if result["ok"]:
                        st.session_state["user"]      = result["user"]["email"]
                        st.session_state["user_id"]   = result["user"]["id"]
                        st.session_state["user_name"] = result["user"]["name"]
                        st.success(f"✅ Account created! Welcome, {name}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")
            else:
                st.warning("Please fill in all fields.")

# ── NAVBAR ──────────────────────────────────────────────
nav_col1, nav_col2, nav_col3 = st.columns([2, 4, 2])

with nav_col1:
    st.markdown('<div class="brand">Aero<span>gen</span></div>', unsafe_allow_html=True)

with nav_col2:
    st.markdown("""
    <div style="display:flex;justify-content:center;gap:2.5rem;padding-top:0.4rem;">
        <a href="#" style="color:rgba(255,255,255,0.6);text-decoration:none;font-weight:500;">Features</a>
        <a href="#" style="color:rgba(255,255,255,0.6);text-decoration:none;font-weight:500;">How it Works</a>
        <a href="#" style="color:rgba(255,255,255,0.6);text-decoration:none;font-weight:500;">Pricing</a>
        <a href="#" style="color:rgba(255,255,255,0.6);text-decoration:none;font-weight:500;">About</a>
    </div>
    """, unsafe_allow_html=True)

with nav_col3:
    ncol1, ncol2 = st.columns([1,1])
    with ncol1:
        theme_choice = st.selectbox("", list(THEMES_MAIN.keys()),
            index=list(THEMES_MAIN.keys()).index(st.session_state["theme"]),
            label_visibility="collapsed", key="main_theme")
        if theme_choice != st.session_state["theme"]:
            st.session_state["theme"] = theme_choice
            st.rerun()
    with ncol2:
        user = st.session_state.get("user", None)
        if user:
            name_display = st.session_state.get("user_name", user.split("@")[0])
            col_a, col_b = st.columns([2,1])
            with col_a:
                st.markdown(f"""
                <div style="padding-top:.3rem;">
                    <span style="background:{tm['brand_grad']};
                                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                                 font-weight:700;font-size:.9rem;">👤 {name_display}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                if st.button("🚪", key="signout", help="Sign Out"):
                    for k in ["user","user_id","user_name"]:
                        st.session_state.pop(k, None)
                    st.rerun()
        else:
            if st.button("Sign In", key="signin_nav"):
                sign_in_dialog()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── HERO ────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-section">
    <div class="hero-tag">✨ Powered by Groq AI & Real-time Data</div>
    <div class="hero-title">
        Plan Unforgettable<br>Trips with
        <span class="accent"> Aerogen</span>
    </div>
    <div class="hero-sub" style="color:{tm['text_muted']}">
        Your personal travel curator — real-time flights, hotels,
        live weather &amp; a full day-by-day itinerary crafted just for you.
    </div>
</div>
""", unsafe_allow_html=True)

# ── GET STARTED BUTTON ───────────────────────────────────
_, btn_col, _ = st.columns([2, 1.2, 2])
with btn_col:
    if st.button("🚀 Get Started — it's free", key="get_started", use_container_width=True):
        st.switch_page("pages/Planner.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── STATS ───────────────────────────────────────────────
st.markdown("""
<div class="stats-row">
    <div class="stat-item">
        <div class="stat-num">50+</div>
        <div class="stat-label">Countries Covered</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">10K+</div>
        <div class="stat-label">Trips Planned</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">< 30s</div>
        <div class="stat-label">Plan Generated</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">Free</div>
        <div class="stat-label">Always</div>
    </div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# ── FEATURE CARDS ───────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin:2rem 0 0.5rem;">
    <span style="font-family:'Outfit',sans-serif;font-size:1.8rem;font-weight:800;color:white;">
        Everything you need to travel smarter
    </span>
</div>
<div class="features-row">
    <div class="feat-card">
        <div class="feat-icon">✈️</div>
        <div class="feat-title">Real-time Flights</div>
        <div class="feat-desc">Live prices from Google Flights — compare, pick the best deal and book instantly.</div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">🏨</div>
        <div class="feat-title">Hotel Search</div>
        <div class="feat-desc">Top-rated hotels with live pricing. Book directly with one click.</div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">🌤️</div>
        <div class="feat-title">Trip Weather</div>
        <div class="feat-desc">Day-by-day forecast for your entire trip with AI precautions &amp; packing tips.</div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">🏛️</div>
        <div class="feat-title">Top Places</div>
        <div class="feat-desc">AI-curated list of must-visit landmarks, hidden gems, and local food spots.</div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">📅</div>
        <div class="feat-title">Full Itinerary</div>
        <div class="feat-desc">Complete day-by-day plan with timings, budget breakdown and download option.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── FOOTER ──────────────────────────────────────────────
st.markdown(f"""
<div class="divider" style="margin-top:3rem;"></div>
<div style="text-align:center;padding:1.5rem 0;color:{tm['footer_col']};font-size:0.82rem;">
    © 2025 <span style="font-family:'Outfit',sans-serif;font-weight:700;
    background:{tm['brand_grad']};
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    background-clip:text;">Aerogen</span>
    &nbsp;·&nbsp; Built with Groq AI &amp; SerpAPI
</div>
""", unsafe_allow_html=True)
