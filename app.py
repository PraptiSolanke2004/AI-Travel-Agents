"""
AI Travel Planner — Unified Streamlit App
Powered by Groq AI (Llama 3.3) + SerpAPI (Flights, Hotels, Weather)
Single file — no FastAPI backend needed.
"""

import os
import time
import requests
import streamlit as st
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ──────────────────────────────────────────────────────
#  API KEYS  (from .env or hardcoded fallback)
# ──────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
SERP_API_KEY = os.getenv("SERPER_API_KEY", "dfdb6c7c6d99d957de3f4b799b6d13f5852e4dbb362055fbe7b5349623457ad9")

# ──────────────────────────────────────────────────────
#  PAGE CONFIG
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Travel Planner ✈️",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────
#  CUSTOM CSS
# ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1530 50%, #060d1f 100%);
}
.hero {
    background: linear-gradient(135deg,rgba(99,179,237,.15),rgba(129,140,248,.15));
    border: 1px solid rgba(99,179,237,.25);
    border-radius: 20px; padding: 2rem; text-align: center; margin-bottom: 1.5rem;
}
.hero-title {
    font-family:'Outfit',sans-serif; font-size:2.6rem; font-weight:800;
    background: linear-gradient(135deg,#63b3ed,#818cf8,#c4b5fd);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.hero-sub { color:rgba(255,255,255,.55); font-size:1rem; margin-top:.3rem; }

.card {
    background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.1);
    border-radius:14px; padding:1.2rem; margin-bottom:1rem;
    transition: border-color .3s;
}
.card:hover { border-color:rgba(99,179,237,.4); }

.section-title {
    font-family:'Outfit',sans-serif; font-size:1.3rem; font-weight:700;
    color:#63b3ed; margin:1rem 0 .6rem;
}
.badge {
    display:inline-block; background:rgba(99,179,237,.15);
    border:1px solid rgba(99,179,237,.3); border-radius:20px;
    padding:3px 12px; font-size:.8rem; color:#90cdf4; margin:2px;
}
.weather-day {
    background:rgba(255,255,255,.05); border:1px solid rgba(99,179,237,.2);
    border-radius:12px; padding:.8rem; text-align:center;
}
.plan-box {
    background:rgba(10,14,26,.85); border:1px solid rgba(99,179,237,.2);
    border-radius:14px; padding:1.5rem; color:rgba(255,255,255,.88);
    line-height:1.8; white-space:pre-wrap; max-height:600px; overflow-y:auto;
}
.stButton>button {
    background:linear-gradient(135deg,#3b82f6,#6366f1)!important;
    color:white!important; border:none!important; border-radius:10px!important;
    font-weight:600!important; width:100%;
}
.stButton>button:hover { transform:translateY(-2px)!important; box-shadow:0 8px 25px rgba(99,102,241,.5)!important; }
label, .stSelectbox label { color:rgba(255,255,255,.75)!important; font-weight:500!important; }
[data-testid="stSidebar"] { background:rgba(10,14,26,.95)!important; border-right:1px solid rgba(255,255,255,.08)!important; }
.stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>div>textarea {
    background:rgba(255,255,255,.07)!important; border:1px solid rgba(255,255,255,.15)!important;
    border-radius:8px!important; color:white!important;
}
.stDateInput>div>div>input { background:rgba(255,255,255,.07)!important; color:white!important; border-radius:8px!important; }
.success { background:rgba(16,185,129,.15); border:1px solid rgba(16,185,129,.4); border-radius:10px; padding:.8rem 1.2rem; color:#6ee7b7; margin:.5rem 0; }
.err { background:rgba(239,68,68,.15); border:1px solid rgba(239,68,68,.4); border-radius:10px; padding:.8rem 1.2rem; color:#fca5a5; margin:.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  SERPAPI HELPERS
# ══════════════════════════════════════════════════════

def serp_search(params: dict) -> dict:
    """Generic SerpAPI GET request."""
    params["api_key"] = SERP_API_KEY
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def search_flights(origin: str, destination: str, outbound: str, ret: str) -> list:
    """Fetch real-time flights via SerpAPI Google Flights engine."""
    params = {
        "engine": "google_flights",
        "hl": "en", "gl": "us",
        "departure_id": origin.strip().upper(),
        "arrival_id": destination.strip().upper(),
        "outbound_date": outbound,
        "return_date": ret,
        "currency": "INR",
    }
    data = serp_search(params)
    if "error" in data:
        st.warning(f"✈️ Flight search: {data['error']}")
        return []

    results = []
    for f in data.get("best_flights", [])[:6]:
        legs = f.get("flights", [])
        if not legs:
            continue
        leg = legs[0]
        results.append({
            "airline":      leg.get("airline", "Unknown"),
            "logo":         leg.get("airline_logo", ""),
            "price":        f.get("price", "N/A"),
            "duration":     f"{f.get('total_duration', 'N/A')} min",
            "stops":        "Nonstop" if len(legs) == 1 else f"{len(legs)-1} stop(s)",
            "departure":    f"{leg.get('departure_airport',{}).get('name','?')} at {leg.get('departure_airport',{}).get('time','?')}",
            "arrival":      f"{leg.get('arrival_airport',{}).get('name','?')} at {leg.get('arrival_airport',{}).get('time','?')}",
            "travel_class": leg.get("travel_class", "Economy"),
        })
    return results


def search_hotels(location: str, check_in: str, check_out: str) -> list:
    """Fetch real-time hotels via SerpAPI Google Hotels engine."""
    params = {
        "engine": "google_hotels",
        "q": location,
        "hl": "en", "gl": "us",
        "check_in_date": check_in,
        "check_out_date": check_out,
        "currency": "INR",
        "sort_by": 3,
        "rating": 7,
    }
    data = serp_search(params)
    if "error" in data:
        st.warning(f"🏨 Hotel search: {data['error']}")
        return []

    results = []
    for h in data.get("properties", [])[:6]:
        results.append({
            "name":     h.get("name", "Unknown"),
            "price":    h.get("rate_per_night", {}).get("lowest", "N/A"),
            "rating":   h.get("overall_rating", 0),
            "location": h.get("neighborhood", h.get("location", "N/A")),
            "link":     h.get("link", "#"),
        })
    return results


def search_weather(destination: str) -> str:
    """Fetch current weather via SerpAPI Google Search."""
    params = {
        "engine": "google",
        "q": f"weather in {destination}",
        "hl": "en",
    }
    data = serp_search(params)
    if "error" in data:
        return f"Weather unavailable: {data['error']}"

    w = data.get("answer_box", {})
    if w:
        temp     = w.get("temperature", "")
        unit     = w.get("unit", "")
        desc     = w.get("weather", "")
        humidity = w.get("humidity", "")
        wind     = w.get("wind", "")
        precip   = w.get("precipitation", "")
        location = w.get("location", destination)
        return (
            f"📍 **{location}**\n"
            f"🌡️ **{temp}{unit}** — {desc}\n"
            f"💧 Humidity: {humidity}  💨 Wind: {wind}  🌧️ Precip: {precip}"
        )
    return "Weather data not available for this destination."


def weather_code_to_emoji(code: int) -> tuple[str, str]:
    """Return (emoji, description) for WMO weather code."""
    mapping = {
        0: ("☀️", "Clear sky"),       1: ("🌤️", "Mainly clear"),
        2: ("⛅", "Partly cloudy"),   3: ("☁️", "Overcast"),
        45: ("🌫️", "Foggy"),          48: ("🌫️", "Icy fog"),
        51: ("🌦️", "Light drizzle"),  53: ("🌦️", "Drizzle"),
        55: ("🌧️", "Dense drizzle"),  61: ("🌧️", "Slight rain"),
        63: ("🌧️", "Moderate rain"),  65: ("🌧️", "Heavy rain"),
        71: ("🌨️", "Slight snow"),    73: ("❄️", "Moderate snow"),
        75: ("❄️", "Heavy snow"),     80: ("🌦️", "Rain showers"),
        81: ("🌧️", "Showers"),        82: ("⛈️", "Violent showers"),
        95: ("⛈️", "Thunderstorm"),   99: ("⛈️", "Thunderstorm+hail"),
    }
    return mapping.get(code, ("🌡️", f"Code {code}"))


def geocode_city(city: str):
    """Return (lat, lon) for a city name using Nominatim (free)."""
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "AITravelPlanner/2.0"},
            timeout=10,
        )
        results = r.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception:
        pass
    return None, None


def get_trip_weather_forecast(city: str, start_date: str, end_date: str) -> dict:
    """Fetch day-by-day weather forecast for the trip using Open-Meteo (free, no key)."""
    lat, lon = geocode_city(city)
    if lat is None:
        return {}
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max",
                "timezone": "auto",
                "start_date": start_date,
                "end_date": end_date,
            },
            timeout=15,
        )
        return r.json()
    except Exception:
        return {}


# ══════════════════════════════════════════════════════
#  GEMINI HELPERS
# ══════════════════════════════════════════════════════

GROQ_MODEL = "llama-3.3-70b-versatile"


def groq_call_with_retry(prompt: str, retries: int = 3) -> str:
    """Call Groq with exponential backoff on rate-limit errors."""
    client = Groq(api_key=GROQ_API_KEY)
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=8192,
            )
            return response.choices[0].message.content
        except Exception as e:
            err = str(e)
            if ("429" in err or "rate" in err.lower()) and attempt < retries - 1:
                wait = 15 * (attempt + 1)
                time.sleep(wait)
            else:
                return f"Groq error: {e}"
    return "Groq error: max retries reached."


def groq_full_plan(destination: str, check_in: str, check_out: str,
                     num_travelers: int, budget: int, style: str, interests: str,
                     flights: list, hotels: list, weather: str) -> dict:
    """
    Single Groq call that returns the full itinerary with top places to visit.
    Returns dict with keys: itinerary.
    """
    days = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days

    flight_txt = "\n".join(
        f"  Flight {i+1}: {f['airline']} | ₹{f['price']} | {f['duration']} | {f['stops']} | {f['departure']} → {f['arrival']} | {f['travel_class']}"
        for i, f in enumerate(flights[:5])
    ) or "  No flight data available."

    hotel_txt = "\n".join(
        f"  Hotel {i+1}: {h['name']} | ₹{h['price']}/night | ⭐{h['rating']} | {h['location']}"
        for i, h in enumerate(hotels[:5])
    ) or "  No hotel data available."

    prompt = f"""
You are an expert AI travel planner. Create a complete {days}-day travel plan for {destination}.

TRIP DETAILS:
- Destination : {destination}
- Dates       : {check_in} → {check_out} ({days} days)
- Travelers   : {num_travelers}
- Budget      : ₹{budget:,}
- Style       : {style}
- Interests   : {interests}

CURRENT WEATHER:
{weather}

FLIGHT OPTIONS:
{flight_txt}

HOTEL OPTIONS:
{hotel_txt}

Please generate the following sections using markdown with emojis:

## 🏛️ TOP PLACES TO VISIT IN {destination.upper()}
List the 10 most iconic and must-visit landmarks, attractions, and hidden gems in {destination}.
For each place include:
- Name and a one-line description
- Best time to visit and approximate entry fee (in ₹)
- Insider tip

## 📅 DAY-BY-DAY ITINERARY ({days} DAYS)
For each day provide:
- **Day X — Date**
- 🌅 Morning: specific activity with location name and timing (e.g. 9:00 AM – 11:00 AM)
- ☀️ Afternoon: specific activity with location
- 🌙 Evening: dinner or leisure recommendation with restaurant/venue name
- 💡 Pro tip of the day

## 💰 BUDGET BREAKDOWN
Estimated costs in ₹ for {num_travelers} traveler(s):
- Flights (round-trip)
- Accommodation ({days} nights)
- Food & Dining (per day × {days})
- Local Transport
- Activities & Entry Fees
- Miscellaneous
- **TOTAL ESTIMATED COST**
- Money-saving tips

## 🎒 PACKING & TRAVEL TIPS
- 5 essential items for this trip
- Local customs and etiquette
- Best apps / transport cards to use
- Safety tips

## 🍽️ FOOD GUIDE
- 5 must-try local dishes
- 3 recommended restaurants with cuisine type and price range
- Best street food areas

Be specific, practical, and helpful. Use real landmark and restaurant names.
""".strip()

    itinerary = groq_call_with_retry(prompt)
    return {"itinerary": itinerary}


# ══════════════════════════════════════════════════════
#  UI — HERO HEADER
# ══════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-title">🌍 AI Travel Planner ✈️</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  SIDEBAR — Trip Form
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="section-title">🗺️ Trip Details</div>', unsafe_allow_html=True)

    origin      = st.text_input("🛫 Origin Airport (IATA)", "BLR", help="e.g. BLR, DEL, BOM")
    destination_iata = st.text_input("🛬 Destination Airport (IATA)", "DEL", help="e.g. NYC, DXB, SIN")
    destination_city = st.text_input("🏙️ Destination City (full name)", "New Delhi, India", help="For hotels & weather search")

    col1, col2 = st.columns(2)
    with col1:
        outbound_date = st.date_input("📅 Departure", date.today() + timedelta(days=15))
    with col2:
        return_date   = st.date_input("📅 Return",    date.today() + timedelta(days=22))

    st.markdown("---")
    num_travelers = st.number_input("👥 Travelers", 1, 20, 2)
    budget_inr    = st.number_input("💰 Budget (₹)", 5000, 10000000, 80000, step=5000)

    travel_style = st.selectbox("🎒 Travel Style", [
        "Budget Backpacker", "Mid-range Explorer", "Luxury Traveler",
        "Family-friendly", "Adventure Seeker", "Cultural Immersion"
    ], index=1)

    interests = st.text_area("❤️ Interests", "food, history, sightseeing", height=70)

    st.markdown("---")
    search_mode = st.radio("🔍 Search Mode", [
        "Complete (Flights + Hotels + Itinerary)",
        "Flights Only",
        "Hotels Only",
    ])

    st.markdown("---")
    go = st.button("✨ Plan My Trip")
    st.markdown('<p style="color:rgba(255,255,255,.3);font-size:.75rem;text-align:center;">Groq AI (Llama 3.3) · SerpAPI · Google Search</p>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  MAIN — Run on button click
# ══════════════════════════════════════════════════════
if go:
    # Validation
    if return_date <= outbound_date:
        st.markdown('<div class="err">⚠️ Return date must be after departure date.</div>', unsafe_allow_html=True)
        st.stop()

    out_str  = outbound_date.strftime("%Y-%m-%d")
    ret_str  = return_date.strftime("%Y-%m-%d")
    days     = (return_date - outbound_date).days

    # ── Summary bar ──
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🌍 Destination", destination_city.split(",")[0])
    c2.metric("📅 Days", days)
    c3.metric("👥 Travelers", num_travelers)
    c4.metric("💰 Budget", f"₹{budget_inr:,}")
    c5.metric("🎒 Style", travel_style)
    st.markdown("---")

    flights, hotels = [], []
    flight_rec, hotel_rec, itinerary, weather = "", "", "", ""

    # ── Flights ──
    if search_mode != "Hotels Only":
        with st.spinner("✈️ Fetching live flights from Google..."):
            flights = search_flights(origin, destination_iata, out_str, ret_str)

    # ── Hotels ──
    if search_mode != "Flights Only":
        with st.spinner("🏨 Fetching live hotels from Google..."):
            hotels = search_hotels(destination_city, out_str, ret_str)

    # ── Weather ──
    with st.spinner("🌤️ Fetching weather from Google..."):
        weather = search_weather(destination_city)

    # ── AI — Groq itinerary call ──
    if search_mode == "Complete (Flights + Hotels + Itinerary)":
        with st.spinner("🤖 Groq AI is crafting your itinerary & top places..."):
            ai = groq_full_plan(
                destination_city, out_str, ret_str,
                num_travelers, budget_inr, travel_style, interests,
                flights, hotels, weather
            )
            itinerary = ai["itinerary"]

    # ══════════════════════════════════════════════════════
    #  TABS  (no AI Picks tab)
    # ══════════════════════════════════════════════════════
    if search_mode == "Complete (Flights + Hotels + Itinerary)":
        tabs = st.tabs(["✈️ Flights", "🏨 Hotels", "🌤️ Weather", "📅 Itinerary"])
    elif search_mode == "Flights Only":
        tabs = st.tabs(["✈️ Flights", "🌤️ Weather"])
    else:
        tabs = st.tabs(["🏨 Hotels", "🌤️ Weather"])

    # ── Flights Tab ──
    if search_mode != "Hotels Only":
        tab_idx = 0
        with tabs[tab_idx]:
            st.markdown(f'<div class="section-title">✈️ Flights: {origin} → {destination_iata}</div>', unsafe_allow_html=True)
            if flights:
                cols = st.columns(2)
                for i, f in enumerate(flights):
                    with cols[i % 2]:
                        logo_html = f'<img src="{f["logo"]}" style="height:28px;margin-bottom:6px;">' if f["logo"] else ""
                        # Google Flights deep-link
                        gf_url = (
                            f"https://www.google.com/travel/flights?q=Flights+from+"
                            f"{origin}+to+{destination_iata}+on+{out_str}"
                        )
                        st.markdown(f"""
                        <div class="card">
                            {logo_html}
                            <b>{f['airline']}</b> &nbsp;·&nbsp; <span class="badge">{f['stops']}</span><br>
                            🕒 {f['departure']}<br>
                            🕘 {f['arrival']}<br>
                            ⏱️ {f['duration']} &nbsp;·&nbsp; 💺 {f['travel_class']}<br>
                            <span style="font-size:1.3rem;font-weight:700;color:#63b3ed;">₹{f['price']}</span><br>
                            <a href="{gf_url}" target="_blank"
                               style="display:inline-block;margin-top:8px;padding:6px 18px;
                                      background:linear-gradient(135deg,#3b82f6,#6366f1);
                                      color:white;border-radius:8px;font-weight:600;
                                      font-size:.85rem;text-decoration:none;">
                               ✈️ Book Now
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No flights found. Check IATA codes and dates.")

    # ── Hotels Tab ──
    if search_mode != "Flights Only":
        tab_idx = 0 if search_mode == "Hotels Only" else 1
        with tabs[tab_idx]:
            st.markdown(f'<div class="section-title">🏨 Hotels in {destination_city}</div>', unsafe_allow_html=True)
            if hotels:
                cols = st.columns(3)
                for i, h in enumerate(hotels):
                    with cols[i % 3]:
                        stars = "⭐" * min(int(h["rating"]), 5) if h["rating"] else ""
                        # Google Hotels deep-link
                        gh_url = (
                            f"https://www.google.com/travel/hotels/{requests.utils.quote(destination_city)}"
                            f"?dates={out_str},{ret_str}"
                        )
                        book_url = h["link"] if h["link"] != "#" else gh_url
                        st.markdown(f"""
                        <div class="card">
                            <b>{h['name']}</b><br>
                            {stars} {h['rating']}<br>
                            📍 {h['location']}<br>
                            <span style="font-size:1.2rem;font-weight:700;color:#63b3ed;">₹{h['price']}/night</span><br>
                            <div style="display:flex;gap:8px;margin-top:8px;">
                              <a href="{h['link']}" target="_blank"
                                 style="color:#818cf8;font-size:.82rem;text-decoration:none;">🔗 Details</a>
                              <a href="{book_url}" target="_blank"
                                 style="padding:5px 14px;
                                        background:linear-gradient(135deg,#10b981,#059669);
                                        color:white;border-radius:8px;font-weight:600;
                                        font-size:.82rem;text-decoration:none;">
                                 🏨 Book Now
                              </a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No hotels found. Try a different city name.")

    # ── Weather Tab ──
    weather_tab_idx = 1
    if search_mode == "Complete (Flights + Hotels + Itinerary)":
        weather_tab_idx = 2
    with tabs[weather_tab_idx]:
        st.markdown('<div class="section-title">🌤️ Trip Weather Forecast</div>', unsafe_allow_html=True)

        # Current weather (SerpAPI)
        st.markdown(f'<div class="card">🌍 <b>Current Conditions</b><br>{weather}</div>', unsafe_allow_html=True)

        # Full trip forecast (Open-Meteo)
        with st.spinner("📅 Fetching day-by-day forecast..."):
            forecast = get_trip_weather_forecast(destination_city, out_str, ret_str)

        daily = forecast.get("daily", {})
        dates     = daily.get("time", [])
        max_t     = daily.get("temperature_2m_max", [])
        min_t     = daily.get("temperature_2m_min", [])
        precip_d  = daily.get("precipitation_sum", [])
        codes     = daily.get("weathercode", [])
        wind_d    = daily.get("windspeed_10m_max", [])

        if dates:
            st.markdown("**📅 Day-by-Day Forecast (Open-Meteo)**")
            # Show max 7 per row
            chunk = 7
            for row_start in range(0, len(dates), chunk):
                row_dates = dates[row_start:row_start+chunk]
                cols = st.columns(len(row_dates))
                for j, col in enumerate(cols):
                    idx = row_start + j
                    emoji, desc = weather_code_to_emoji(codes[idx] if idx < len(codes) else 0)
                    rain = precip_d[idx] if idx < len(precip_d) else 0
                    wind = wind_d[idx] if idx < len(wind_d) else 0
                    rain_color = "#f87171" if rain > 5 else "#6ee7b7"
                    with col:
                        st.markdown(f"""
                        <div class="card" style="text-align:center;padding:.8rem .4rem;">
                            <div style="font-size:1.8rem">{emoji}</div>
                            <div style="color:#63b3ed;font-weight:600;font-size:.75rem;">{dates[idx]}</div>
                            <div style="color:#f87171;font-size:.85rem;">↑ {max_t[idx]:.0f}°C</div>
                            <div style="color:#93c5fd;font-size:.85rem;">↓ {min_t[idx]:.0f}°C</div>
                            <div style="color:{rain_color};font-size:.75rem;">🌧 {rain:.1f}mm</div>
                            <div style="color:#94a3b8;font-size:.72rem;">💨 {wind:.0f}km/h</div>
                            <div style="font-size:.68rem;color:rgba(255,255,255,.45);margin-top:2px">{desc}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # AI weather summary + precautions
            st.markdown("---")
            weather_data_text = "\n".join(
                f"Day {i+1} ({dates[i]}): {weather_code_to_emoji(codes[i] if i < len(codes) else 0)[1]}, "
                f"Max {max_t[i]:.0f}°C, Min {min_t[i]:.0f}°C, Rain {precip_d[i]:.1f}mm, Wind {wind_d[i]:.0f}km/h"
                for i in range(len(dates))
            )
            with st.spinner("🤖 Groq AI generating weather summary & precautions..."):
                weather_summary = groq_call_with_retry(
                    f"""Analyze this {len(dates)}-day weather forecast for a trip to {destination_city} """
                    f"""and provide:\n1. A brief overall weather summary (2-3 sentences)\n"""
                    f"""2. Specific travel precautions and packing tips based on the conditions\n"""
                    f"""3. Best days for outdoor activities\n4. Any weather warnings if applicable\n\n"""
                    f"""Forecast data:\n{weather_data_text}\n\nUse markdown with emojis. Be concise and practical."""
                )
            st.markdown('<div class="section-title">🤖 AI Weather Summary & Precautions</div>', unsafe_allow_html=True)
            st.markdown(weather_summary)
        else:
            st.info("Day-by-day forecast unavailable. Try dates within the next 16 days.")

    # ── Itinerary Tab ──
    if search_mode == "Complete (Flights + Hotels + Itinerary)":
        with tabs[3]:
            st.markdown('<div class="section-title">📅 AI Itinerary & Top Places to Visit</div>', unsafe_allow_html=True)
            if itinerary:
                st.markdown(itinerary)
                fname = f"itinerary_{destination_iata}_{out_str}.md"
                st.download_button("💾 Download Itinerary (.md)", itinerary, fname, "text/markdown")
            else:
                st.info("Itinerary generation failed. Check your Groq API key.")

else:
    # ── Landing page ──
    st.markdown("""
    <div class="card" style="text-align:center;padding:3rem 2rem;">
        <div style="font-size:3.5rem;">🗺️</div>
        <div style="font-family:'Outfit',sans-serif;font-size:1.5rem;font-weight:700;color:#63b3ed;margin:.5rem 0;">
            Your Dream Trip Awaits
        </div>
        <div style="color:rgba(255,255,255,.5);max-width:480px;margin:auto;">
            Fill in your trip details in the sidebar and click
            <b style="color:#818cf8;">✨ Plan My Trip</b> to get real-time flights,
            hotels, live weather, and a full AI-crafted itinerary.
        </div>
        <div style="margin-top:1.5rem;">
            <span class="badge">✈️ Real-time Flights</span>
            <span class="badge">🏨 Live Hotels</span>
            <span class="badge">🌤️ Google Weather</span>
            <span class="badge">🤖 Groq AI (Llama 3.3)</span>
            <span class="badge">🏛️ Top Places to Visit</span>
            <span class="badge">📅 Day-by-Day Plan</span>
            <span class="badge">💾 Download</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
