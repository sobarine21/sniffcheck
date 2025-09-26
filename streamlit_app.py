import streamlit as st
import requests
import json
import pandas as pd

# ---------------- UI Setup ----------------
st.set_page_config(page_title="SniffR 🐾 by Ever Tech", layout="wide")

st.markdown(
    "<h1 style='text-align: center; color: #4CAF50;'>🐾 SniffR by Ever Tech</h1>",
    unsafe_allow_html=True
)

# Sidebar for API settings
st.sidebar.header("⚙️ API Settings")
api_url = st.sidebar.text_input(
    "API Endpoint URL",
    value="https://ljnzkgwbtqoxpztwupli.supabase.co/functions/v1/indiav1"
)
jwt_token = st.secrets.get("indiav1_jwt_token", "")
user_id = st.secrets.get("indiav1_user_id", "")

if not jwt_token or not user_id:
    st.sidebar.error("❌ JWT Token or User ID not found in secrets.")
else:
    st.sidebar.success("✅ Secrets loaded successfully")

# ---------------- Search Form ----------------
with st.form(key="indiav1_search_form"):
    query = st.text_input("🔍 Enter company name, CIN, PAN, etc.")
    submit_btn = st.form_submit_button("Search 🚀")

# ---------------- API Call ----------------
if submit_btn:
    if not jwt_token or not user_id or not api_url:
        st.error("JWT token, user ID, or endpoint URL missing. Please check the sidebar.")
    elif not query.strip():
        st.error("Please enter a search query.")
    else:
        payload = {"query": query, "userId": user_id}
        headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}

        try:
            with st.spinner("Sniffing records... 🐕"):
                response = requests.post(api_url, headers=headers, data=json.dumps(payload))

            if response.ok:
                data = response.json()

                # Show quick stats
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                stats_col1.metric("Execution Time (ms)", data.get("executionTimeMs", "N/A"))
                stats_col2.metric("Total Matches", data.get("totalMatches", "N/A"))
                stats_col3.metric("Tables With Matches", len(data.get("tablesWithMatches", [])))

                st.markdown("---")

                results = data.get("results", [])
                results_with_matches = [t for t in results if t.get("matches")]

                if results_with_matches:
                    for table_result in results_with_matches:
                        table_name = table_result.get("table", "Unknown")
                        matches = table_result.get("matches", [])

                        st.subheader(f"📂 Table: {table_name}")

                        # Convert matches into dataframe for faster, cleaner rendering
                        df = pd.DataFrame(matches)
                        st.dataframe(df, use_container_width=True)
                else:
                    st.warning("⚠️ No enforcement matches found in any table.")
            else:
                st.error(f"Request failed: {response.status_code} - {response.text}")

        except Exception as e:
            st.error(f"🚨 Error contacting API: {e}")
