import streamlit as st
import requests

API_URL = "https://foodies-yl76.onrender.com"

st.set_page_config(page_title="FoodieS 🍽️", layout="centered")

# 🍽️ Style & Background
st.markdown("""
    <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1600891964599-f61ba0e24092");
            background-size: cover;
            background-attachment: fixed;
        }
        .block-container {
            backdrop-filter: blur(4px);
            background-color: rgba(255,255,255,0.85);
            padding: 2rem;
            border-radius: 1rem;
        }
        #chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #ffffffcc;
            border: 2px solid #fca311;
            padding: 16px;
            width: 300px;
            border-radius: 1rem;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
            z-index: 9999;
        }
        #chat-widget h4 {
            margin-top: 0;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🍽️ FoodieS Restaurant Reservation")

# Load restaurant list for dropdown
@st.cache_data
def fetch_restaurants():
    try:
        return [f"Restaurant {i+1}" for i in range(20)]
    except:
        return []

restaurant_names = fetch_restaurants()

# 🔍 Cuisine Recommendation
st.header("🌮 Find a Restaurant")
cuisine = st.selectbox("🍛 Select Cuisine", ["Indian", "Italian", "Japanese", "Chinese", "Mexican", "French", "Thai", "American"])
if st.button("✨ Get Recommendation"):
    res = requests.get(f"{API_URL}/recommend/{cuisine}")
    if res.ok:
        st.success(f"✅ {res.json()['message']}")
    else:
        st.error("❌ No available restaurants.")

# 📅 Book Table
st.header("📅 Book a Table")
restaurant_name = st.selectbox("🏷️ Choose Restaurant", restaurant_names)
tables = st.number_input("🪑 Tables", min_value=1, step=1)
if st.button("📌 Book Now"):
    data = {"restaurant_name": restaurant_name, "tables": tables}
    res = requests.post(f"{API_URL}/book", json=data)
    if res.ok:
        st.success(res.json()["message"])
    else:
        st.error(res.json()["detail"])

# 📈 Business Metrics
st.header("📊 Business Insights")
if st.button("📉 View Metrics"):
    res = requests.get(f"{API_URL}/metrics")
    if res.ok:
        m = res.json()
        st.success(f"✅ Total Bookings: {m['total_bookings']}, Restaurants: {m['total_restaurants']}")

# 📌 Strategy Insight Section
with st.expander("💡 Strategy & Expansion Insights"):
    st.markdown("""
        - **Success Metrics**: Track bookings, table utilization, customer preferences.
        - **ROI Model**: More filled seats = increased revenue. Avg table = ₹1500.
        - **Expansion**: Adapt this system for food courts, cafes, and hotel chains.
        - **Competitive Edge**:
            1. Real-time AI-backed recommendations.
            2. Seat optimization logic.
            3. Backend ready for scaling to 100+ locations.
    """)


# 🧠 AI Assistant Chat (Bottom Floating Style via Streamlit Layout)
with st.container():
    st.markdown("---")
    st.markdown("### 🤖 Ask the AI Assistant")

    user_input = st.text_input("💬 Type your question to the assistant", key="chat_input")

    if st.button("🚀 Ask"):
        if user_input.strip() != "":
            try:
                res = requests.post(f"{API_URL}/chat", json={"message": user_input})
                if res.ok:
                    response = res.json()["ai_response"]
                    st.success(f"🧠 {response}")
                else:
                    st.error("❌ Assistant failed to respond.")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")

