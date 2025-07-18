import streamlit as st
import requests
import json

st.set_page_config(page_title="SniffR API - Individual Record Search", layout="centered")

st.title("SniffR API - Individual Record Search")
st.markdown("""
This Streamlit app allows you to query the SniffR API for individual records.  
Enter your search details below.  
**Add your API key via Streamlit secrets (in the cloud or settings UI) as `sniffr_api_key`.**
""")

# Search type options from the API doc
SEARCH_TYPES = {
    "All fields": "all",
    "PAN number": "pan",
    "CIN number": "cin",
    "DIN number": "din",
    "Company name": "company_name",
    "Director name": "director_name",
}

# Sidebar for API settings
st.sidebar.header("API Settings")
api_url = st.sidebar.text_input(
    "API Endpoint URL",
    value="https://your-api-domain/functions/v1/sniffR",
    help="Enter the full API URL for SniffR endpoint"
)
api_key = st.secrets.get("sniffr_api_key", "")

if not api_key:
    st.sidebar.warning("API key not found in secrets. Please add it via Streamlit settings UI.")
else:
    st.sidebar.success("API key loaded from secrets.")

# Main input form
with st.form(key="sniffr_search_form"):
    search_type_label = st.selectbox("Select Search Type", list(SEARCH_TYPES.keys()))
    search_type = SEARCH_TYPES[search_type_label]
    search_term = st.text_input(f"Enter {search_type_label}")
    submit_btn = st.form_submit_button("Search")

if submit_btn:
    if not api_key or not api_url:
        st.error("API key or endpoint URL missing. Please check the sidebar.")
    elif not search_term:
        st.error("Please enter a search term.")
    else:
        payload = {
            "search_term": search_term,
            "search_type": search_type
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            if response.ok:
                data = response.json()
                if data.get("success") and data.get("results"):
                    st.success(f"Found {data.get('total_results', 0)} result(s) for '{search_term}'")
                    for record in data["results"]:
                        st.write("---")
                        st.write(f"**Type:** {record.get('type', '')}")
                        st.write(f"**Company Name:** {record.get('company_name', '')}")
                        st.write(f"**Director Name:** {record.get('director_name', '')}")
                        st.write(f"**PAN:** {record.get('pan', '')}")
                        st.write(f"**DIN:** {record.get('din', '')}")
                        st.write(f"**CIN:** {record.get('cin', '')}")
                        st.write(f"**Address:** {record.get('address', '')}")
                        st.write(f"**Severity Level:** {record.get('severity_level', '')}")
                        st.write(f"**Description:** {record.get('description', '')}")
                        st.write(f"**Created At:** {record.get('created_at', '')}")
                        st.write(f"**Source:** {record.get('source', '')}")
                        st.write(f"**ID:** {record.get('id', '')}")
                else:
                    st.warning("No results found or API did not return the expected response.")
            else:
                st.error(f"Request failed: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Error contacting API: {e}")

st.markdown("---")
st.markdown("#### API Docs Reference")
st.markdown("- [SniffR API Endpoint and Request Body](#)")
st.markdown("- [SniffR API Response Example](#)")
