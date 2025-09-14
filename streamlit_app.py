import streamlit as st
import requests
import json

st.set_page_config(page_title="Indiav1 Enforcement Check API", layout="centered")

st.title("Indiav1 Enforcement Check API - Enforcement Record Search")
st.markdown("""
This Streamlit app allows you to query the Indiav1 Enforcement Check API for enforcement records.  
Add your JWT token and userId via Streamlit secrets as `indiav1_jwt_token` and `indiav1_user_id`.
""")

# Sidebar for API settings
st.sidebar.header("API Settings")
api_url = st.sidebar.text_input(
    "API Endpoint URL",
    value="https://ljnzkgwbtqoxpztwupli.supabase.co/functions/v1/indiav1",
    help="Enter the full API URL for Indiav1 Enforcement Check API"
)
jwt_token = st.secrets.get("indiav1_jwt_token", "")
user_id = st.secrets.get("indiav1_user_id", "")

if not jwt_token or not user_id:
    st.sidebar.warning("JWT Token or User ID not found in secrets. Please add them via Streamlit settings UI.")
else:
    st.sidebar.success("JWT Token and User ID loaded from secrets.")

# Main input form
with st.form(key="indiav1_search_form"):
    search_type = st.selectbox("Select Search Type", ["partial", "exact"])
    query = st.text_input("Enter search query (company name, CIN, PAN, etc.)")
    submit_btn = st.form_submit_button("Search")

if submit_btn:
    if not jwt_token or not user_id or not api_url:
        st.error("JWT token, user ID, or endpoint URL missing. Please check the sidebar.")
    elif not query:
        st.error("Please enter a search query.")
    else:
        payload = {
            "query": query,
            "searchType": search_type,
            "userId": user_id
        }
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            if response.ok:
                data = response.json()

                # DEBUG: Show full raw response for inspection
                st.subheader("Raw API Response")
                st.json(data)

                st.success(f"API call successful in {data.get('execution_time', 'N/A')}.")

                total_matches = data.get('total_matches', 'N/A')
                st.write(f"Total Matches: {total_matches}")
                st.write("---")

                results = data.get("matches", [])  # Updated key

                if results:
                    for record in results:
                        st.write(f"**Table Name:** {record.get('table', '')}")
                        st.write(f"**Matched Field:** {record.get('field', '')}")
                        st.write(f"**Matched Value:** {record.get('value', '')}")
                        st.json(record.get('record', {}))  # Pretty-print the detailed record
                        st.write("---")
                else:
                    st.warning("No enforcement matches found.")

            else:
                st.error(f"Request failed: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Error contacting API: {e}")

st.markdown("---")
st.markdown("#### API Docs Reference")
st.markdown("- [Indiav1 Enforcement Check API Documentation](#)")
