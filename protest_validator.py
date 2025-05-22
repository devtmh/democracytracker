import streamlit as st
import pandas as pd
import urllib.parse
import io
import os

from datetime import datetime

# Date parser
def parse_date(date_string: str) -> datetime | None:
    # Try interpreting as MM/DD/YY
    try:
        interpret_mmddyy = datetime.strptime(date_string, "%x")
        return interpret_mmddyy

    except ValueError:
        return None

# -------------------------------
# 1️⃣ APP SETUP
# -------------------------------

st.set_page_config(page_title="Protest Validator", layout="wide")
st.title("Protest Validator")

# Display Event Type Classification Key
st.markdown("### Event Type Classification")
st.markdown("""
**National** - 50501, Indivisible, or other multi-state pre-announced event \\
**Tesla** - Tesla Takedown \\
**Statewide** - Organized action within one state or a small group of neighboring states \\
**One-off** - Organized one-time events, e.g., at officials' offices or responding to specific events \\
**Other** - All others, including spontaneous small groups, wildcat events
""")

# -------------------------------
# 2️⃣ SESSION STATE INITIALIZATION
# -------------------------------

# Initialize session state variables if they don't exist
## Record index to identify the record in the set
if "record_index" not in st.session_state:
    st.session_state.record_index = 0

if "data" not in st.session_state:
    st.session_state.data = None

## Identify name of source file
if "original_filename" not in st.session_state:
    st.session_state.original_filename = None

## create a last_saved value for continuity?
if "last_saved" not in st.session_state:
    st.session_state.last_saved = None

# -------------------------------
# 3️⃣ FILE LOADING
# -------------------------------

# File uploader in sidebar
## Note:  we would like to have a file type so it will accept csv files
with st.sidebar:
    st.header("File Operations")
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

    # Process uploaded file
    if uploaded_file is not None and (st.session_state.data is None or uploaded_file.name != st.session_state.original_filename):
        try:
            # Read the Excel file
            df = pd.read_excel(uploaded_file, sheet_name="Records")

            # Ensure required columns exist
            if "Valid" not in df.columns:
                df["Valid"] = None
            if "Type" not in df.columns:
                df["Type"] = None

            # Store the data and filename in session state
            st.session_state.data = df
            st.session_state.original_filename = uploaded_file.name
            st.session_state.record_index = 0
            st.session_state.last_saved = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            st.success(f"✅ File '{uploaded_file.name}' loaded successfully!")
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")

# -------------------------------
# 4️⃣ NAVIGATION CONTROLS
# -------------------------------

# Add navigation controls in sidebar
with st.sidebar:
    st.header("Navigation")

    if st.session_state.data is not None:
        total_records = len(st.session_state.data)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("◀️ Previous", disabled=st.session_state.record_index <= 0):
                st.session_state.record_index -= 1
                st.rerun()

        with col2:
            if st.button("Next ▶️", disabled=st.session_state.record_index >= total_records - 1):
                st.session_state.record_index += 1
                st.rerun()

        # Direct record navigation
        selected_index = st.number_input(
            f"Go to record (1-{total_records})",
            min_value=1,
            max_value=total_records,
            value=st.session_state.record_index + 1
        )

        if st.button("Go"):
            st.session_state.record_index = selected_index - 1
            st.rerun()

        # Progress indicator
        progress = (st.session_state.record_index + 1) / total_records
        st.progress(progress)
        st.write(f"Record {st.session_state.record_index + 1} of {total_records}")

        # Count of validated records
        if st.session_state.data is not None:
            valid_count = st.session_state.data["Valid"].fillna(0).astype(bool).sum()
            invalid_count = (st.session_state.data["Valid"] == 0).sum()
            pending_count = total_records - valid_count - invalid_count

            st.write(f"✅ Valid: {valid_count}")
            st.write(f"❌ Invalid: {invalid_count}")
            st.write(f"⏳ Pending: {pending_count}")

# -------------------------------
# 5️⃣ DOWNLOAD FUNCTIONALITY
# -------------------------------

# Add download button in sidebar
with st.sidebar:
    st.header("Save Progress")

    if st.session_state.data is not None:
        # Create download button for the current progress
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            # Write main sheet with all records
            st.session_state.data.to_excel(writer, sheet_name="Records", index=False)

            # Create valid records sheet
            valid_records = st.session_state.data[st.session_state.data["Valid"] == 1]
            if not valid_records.empty:
                valid_records.to_excel(writer, sheet_name="Valid Records", index=False)

        # Get the value of the buffer
        buffer.seek(0)

        # Create a filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = st.session_state.original_filename.split('.')[0]
        download_filename = f"{original_name}_validated_{timestamp}.xlsx"

        # Add download button
        st.download_button(
            label="📥 Download Progress",
            data=buffer,
            file_name=download_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        if st.session_state.last_saved:
            st.write(f"Last auto-saved in memory: {st.session_state.last_saved}")

# -------------------------------
# 6️⃣ MAIN CONTENT - RECORD DISPLAY
# -------------------------------

# Check if data is loaded
if st.session_state.data is None:
    st.warning("⚠ Please upload an Excel file using the sidebar to begin validation.")
    exit()

# Get current record
if st.session_state.record_index < len(st.session_state.data):
    row = st.session_state.data.iloc[st.session_state.record_index]

    # Display record information
    st.header(f"Record #{st.session_state.record_index + 1}")

    # Create two columns for record details and iframe
    col1, col2 = st.columns([1, 1])

    with col1:
        # Display record details
        # TODO: change writes to forms in order to facilitate correcting invalid data
        st.subheader("Record Details")
        info_cols = st.columns(3)
        with info_cols[0]:
            st.write(f"**City:** {row['City']}")
        with info_cols[1]:
            st.write(f"**State:** {row['State']}")
        with info_cols[2]:
            st.write(f"**Date:** {row['Date']}")
            # If date is valid but from before 2025, display warning
            if row['Date'].year < 2025:
                st.warning("Provided date is before 2025.")

        # Display URL and extract domain
        try:
            parsed_url = urllib.parse.urlparse(row["URL"])
            domain = parsed_url.netloc
            st.write(f"**Source:** [{domain}]({row['URL']})")
        except:
            st.write(f"**URL:** {row.get('URL', 'No URL provided')}")

        # Display current status
        current_status = "⏳ Pending"
        if row["Valid"] == 1:
            current_status = "✅ Valid"
        elif row["Valid"] == 0:
            current_status = "❌ Invalid"

        st.write(f"**Status:** {current_status}")

        if row["Type"] is not None and row["Valid"] == 1:
            st.write(f"**Type:** {row['Type']}")

        # Validation controls
        st.subheader("Validation")

        # Event type selection (only shown if not marked as invalid)
        if row["Valid"] != 0:
            event_type = st.selectbox(
                "Select Event Type:",
                options=["National", "Tesla", "Statewide", "One-off", "Other"],
                index=None if row["Type"] is None else ["National", "Tesla", "Statewide", "One-off", "Other"].index(row["Type"]),
                key=f"type_select_{st.session_state.record_index}"
            )

        # Validation buttons
        col_valid, col_invalid = st.columns(2)

        with col_valid:
            if st.button("✅ Mark as Valid", key=f"valid_btn_{st.session_state.record_index}",
                        use_container_width=True, type="primary"):
                # Check if event type is selected
                if event_type is None:
                    st.error("Please select an event type before marking as valid.")
                else:
                    # Update the dataframe
                    st.session_state.data.at[st.session_state.record_index, "Valid"] = 1
                    st.session_state.data.at[st.session_state.record_index, "Type"] = event_type

                    # Update last saved timestamp
                    st.session_state.last_saved = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Move to next record if not at the end
                    if st.session_state.record_index < len(st.session_state.data) - 1:
                        st.session_state.record_index += 1

                    st.rerun()

        with col_invalid:
            if st.button("❌ Mark as Invalid", key=f"invalid_btn_{st.session_state.record_index}",
                        use_container_width=True):
                # Update the dataframe
                st.session_state.data.at[st.session_state.record_index, "Valid"] = 0
                st.session_state.data.at[st.session_state.record_index, "Type"] = None

                # Update last saved timestamp
                st.session_state.last_saved = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Move to next record if not at the end
                if st.session_state.record_index < len(st.session_state.data) - 1:
                    st.session_state.record_index += 1

                st.rerun()

    with col2:
        # Display URL in iframe
        st.subheader("Preview")
        try:
            if pd.notna(row["URL"]):
                st.components.v1.html(
                    f'<iframe src="{row["URL"]}" width="100%" height="500" style="border: 1px solid #ddd; border-radius: 5px;"></iframe>',
                    height=520
                )
            else:
                st.warning("No URL available for this record.")
        except:
            st.warning("Unable to load URL in an iframe. Please use the link above to view the source.")
else:
    st.success("✅ All records processed! You can download your results using the sidebar.")
