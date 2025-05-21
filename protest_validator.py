import streamlit as st
import pandas as pd
import urllib.parse
import datetime

# Date parser
def parse_date(date_string: str) -> datetime.datetime | None:
    # Try interpreting as MM/DD/YY
    try:
        interpret_mmddyy = datetime.datetime.strptime(date_string, "%x")
        return interpret_mmddyy

    except ValueError:
        return None

# -------------------------------
# 1️⃣ APP SETUP
# -------------------------------

st.title("Protest Validator")

# Display Event Type Classification Key (Reduced Spacing)
st.markdown("### Event Type Classification")
st.markdown("""
**National** - 50501, Indivisible, or other multi-state pre-announced event
**Tesla** - Tesla Takedown
**Statewide** - Organized action within one state or a small group of neighboring states
**One-off** - Organized one-time events, e.g., at officials' offices or responding to specific events
**Other** - All others, including spontaneous small groups, wildcat events
""")

# File uploader to select Excel file
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

# -------------------------------
# 2️⃣ FILE LOADING DEBUG CHECK (Ensures File Upload Works)
# -------------------------------

if uploaded_file is None:
    st.warning("⚠ Please upload an Excel file to begin validation.")
else:
    st.success("✅ File loaded successfully!")

# Check if user uploaded a file
if not uploaded_file:
    exit()

# -------------------------------
# 3️⃣ LOAD EXCEL DATA
# -------------------------------

try:
    df = pd.read_excel(uploaded_file, sheet_name="Records")
except Exception as e:
    st.error(f"❌ Error loading file: {e}")
    st.stop()  # Prevent app from running further if file fails to load

# Ensure the 'Valid' column exists in the dataset
if "Valid" not in df.columns:
    df["Valid"] = None  # Initialize validation column

# Ensure the 'Type' column exists
if "Type" not in df.columns:
    df["Type"] = None  # Initialize Type column

# -------------------------------
# 4️⃣ SESSION STATE SETUP (Fix for Persistence)
# -------------------------------

if "record_index" not in st.session_state:
    st.session_state["record_index"] = 0

record_index = st.session_state["record_index"]

if record_index < len(df):
    row = df.iloc[record_index]

    # -------------------------------
    # 5️⃣ DISPLAY RECORD DETAILS (Added Debug Output)
    # -------------------------------

    st.write(f"🆔 Currently Showing Record Index: {record_index}")

    # TODO: Warn user if date is not from 2025
    st.write(f"**City:** {row['City']}")
    st.write(f"**State:** {row['State']}")
    st.write(f"**Date:** {row['Date']}")

    parsed_url = urllib.parse.urlparse(row["URL"])
    domain = parsed_url.netloc  # Extract domain name

    st.write(f"[Open {domain}]({row['URL']})")

    # -------------------------------
    # 6️⃣ EMBED URL IN IFRAME (Reduced Height by 20%)
    # -------------------------------

    with st.container():
        try:
            st.components.v1.html(
                f'<iframe src="{row["URL"]}" width="100%" height="384"></iframe>',
                height=404  # Adjusted to match the reduced iframe height
            )
        except:
            st.warning("Unable to load URL in an iframe. Please use the link above.")

    # -------------------------------
    # 7️⃣ TYPE SELECTION (Fix: Prevent Auto-Advancing)
    # -------------------------------

    if "selected_type" not in st.session_state:
        st.session_state["selected_type"] = None

    event_type = st.selectbox(
        "Select Type:", ["National", "Tesla", "Statewide", "One-off", "Other"],
        index=None,
        key="selected_type"  # ✅ Fix for avoiding reruns due to dropdown selection
    )

    # -------------------------------
    # 8️⃣ USER INPUT: VALID OR INVALID (Corrected Button Logic)
    # -------------------------------

    if st.button("Valid + Next"):
        df.at[record_index, "Valid"] = 1
        df.at[record_index, "Type"] = st.session_state["selected_type"]
        st.session_state["record_index"] += 1
        st.rerun()  # ✅ Force Streamlit to refresh & show next record

    if st.button("Invalid + Next"):
        df.at[record_index, "Valid"] = 0
        st.session_state["record_index"] += 1
        st.rerun()  # ✅ Force Streamlit to refresh & show next record

    # -------------------------------
    # 9️⃣ SAVE PROGRESS & VALID RECORDS
    # -------------------------------

    st.session_state["record_index"] = record_index  # Ensure index persists

    with pd.ExcelWriter(uploaded_file, mode="a", engine="openpyxl") as writer:
        valid_records = df[df["Valid"] == 1]
        valid_records.to_excel(writer, sheet_name="valid records", index=False)

    # -------------------------------
    # 🚀 SAVE UPDATED RECORDS TO SOURCE FILE (Enable after development)
    # -------------------------------

    # When ready to save changes directly to the source file, uncomment the following:
    with pd.ExcelWriter(uploaded_file, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name="Records", index=False)

    # This will ensure all changes (Valid status & Type selections) persist after closing the app.
