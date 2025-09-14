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

                # Properly display execution time and total matches
                execution_time_ms = data.get('executionTimeMs', 'N/A')
                total_matches = data.get('totalMatches', 'N/A')

                st.success(f"API call successful in {execution_time_ms} ms.")
                st.write(f"Total Matches: {total_matches}")
                st.write(f"Tables Searched: {data.get('tablesSearched', 'N/A')}")
                st.write(f"Tables With Matches: {data.get('tablesWithMatches', 'N/A')}")
                st.write("---")

                results = data.get("results", [])

                # Filter out any tables with no matches
                results_with_matches = [table for table in results if table.get('matches')]

                if results_with_matches:
                    for table_result in results_with_matches:
                        table_name = table_result.get('table', 'N/A')
                        matches = table_result.get('matches', [])

                        st.write(f"### Table: {table_name}")
                        for idx, match in enumerate(matches, start=1):
                            st.write(f"#### Match #{idx}")
                            for key, value in match.items():
                                st.write(f"**{key}:** {value}")
                            st.write("---")
                else:
                    st.warning("No enforcement matches found in any table.")

            else:
                st.error(f"Request failed: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Error contacting API: {e}")

st.markdown("---")
st.markdown("#### API Docs Reference")
st.markdown("- [Indiav1 Enforcement Check API Documentation](#)")
