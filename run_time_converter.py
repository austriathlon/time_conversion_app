#!/Users/wadehobbs/Python_VS/wades_venv/bin/python
# coding: utf-8

## Set working directory
#cd /Users/wadehobbs/Python_VS
## Set the kernel to the virtual environment
#source wades_venv/bin/activate

import pandas as pd
import streamlit as st

# Read the JSON file and convert it to a DataFrame
file_path = "iaaf-2025.json"  # Replace with your JSON file path
df = pd.read_json(file_path)

df = df.query("event in ['1500m', '3000m', '5000m', '10000m']")

# st.logo(
#     "AusTriathlon-Logo-500px.png",
#     link="https://www.triathlon.org.au/",
#     size="large"
# )

# Set page config to use the full width of the screen
#st.set_page_config(layout="wide")

pd.options.mode.copy_on_write = True


st.markdown(
    """
    <style>
    .custom-title {
        font-size: 18px; /* Adjust the size as needed */
        font-weight: bold;
        margin-bottom: 2px; /* Reduce the gap between the title and the widget */
    }
    .stRadio > div {
        margin-top: -10px; /* Reduce the gap above the radio buttons */
    }
    .stSelectbox > div {
        margin-top: -10px; /* Reduce the gap above the select box */
    }
    .stTextInput > div {
        margin-top: -10px; /* Reduce the gap above the text input */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create a layout with two columns
col1, col2 = st.columns([1, 8])

with col1:
    st.image("austriathlon_icon.png", width=100)

with col2:
    #st.title("AusTriathlon NPT App")
    st.markdown("<h1 style='text-align: center; '>AusTriathlon Run Time Converter</h1>", unsafe_allow_html=True)

st.markdown("</br>", unsafe_allow_html=True)

# Extract unique, sorted names
filtered_events = df[['event']].drop_duplicates().sort_values(by="event")['event'].tolist()
# Set default to first name in the filtered list (if any exist)
default_index = 0 if filtered_events else None  # Avoid errors if list is empty

# Radio button for selecting gender
st.markdown('<div class="custom-title">Select Gender</div>', unsafe_allow_html=True)
selected_gender = st.radio('', options=['Men', 'Women'], index=0)

st.markdown("</br>", unsafe_allow_html=True)

st.markdown('<div class="custom-title">Select Event</div>', unsafe_allow_html=True)
selected_event = st.selectbox('',filtered_events, index=default_index)

st.markdown("</br>", unsafe_allow_html=True)

# Text input for time in minutes:seconds
st.markdown('<div class="custom-title">Enter Time (MM:SS)</div>', unsafe_allow_html=True)
time_input = st.text_input("", value="00:00")

st.markdown("</br>", unsafe_allow_html=True)

# Convert time to seconds
# Convert time to seconds
try:
    minutes, seconds = map(int, time_input.split(":"))
    total_seconds = minutes * 60 + seconds
    # st.write(f"Time in seconds: {total_seconds}")
    
        # Find the closest value in the DataFrame
    points_df = df[df.gender == selected_gender.lower()]

    if 'mark' in points_df.columns:  # Ensure the 'mark' column exists
        # Filter points_df to only include rows for the selected event
        event_points_df = points_df[points_df['event'] == selected_event]

        # Calculate the absolute difference for the selected event
        event_points_df['abs_diff'] = abs(event_points_df['mark'] - total_seconds)  # Calculate absolute difference
        closest_row = event_points_df.loc[event_points_df['abs_diff'].idxmin()]  # Find the row with the smallest difference
        target_points = closest_row['points']

        # Filter the DataFrame based on the inputs, excluding the selected event
        filtered_df = df[
            (df['gender'] == selected_gender.lower()) &
            (df['points'] == target_points) &
            (df['event'] != selected_event)  # Exclude the selected event
        ]

        # Add the selected event back to the DataFrame for display
        selected_event_row = df[
            (df['gender'] == selected_gender.lower()) &
            (df['points'] == target_points) &
            (df['event'] == selected_event)
        ]
        filtered_df = pd.concat([filtered_df, selected_event_row])

        # Convert 'mark' column from seconds to MM:SS format
        filtered_df['mark'] = filtered_df['mark'].apply(lambda x: f"{int(x // 60):02}:{int(x % 60):02}")

        # Ensure the selected event's time is correctly displayed
        filtered_df = filtered_df.sort_values(by='event', key=lambda col: col != selected_event)

        # Transform the DataFrame to wide format
        wide_df = filtered_df.pivot(index='points', columns='event', values='mark')
        column_order = ['1500m', '3000m', '5000m', '10000m']
        wide_df = wide_df.reindex(columns=column_order)
        wide_df = wide_df.reset_index()
        wide_df = wide_df.rename(columns={'points': 'Points'})

        # Convert 'Points' column to string to ensure left alignment
        wide_df['Points'] = wide_df['Points'].astype(str)

        # Display the closest result
        st.markdown('<div class="custom-title">Equivalent Results:</div>', unsafe_allow_html=True)
        st.dataframe(wide_df, hide_index=True)  # Display as a single-row DataFrame
    else:
        st.error("The 'mark' column is missing in the DataFrame.")
except ValueError:
    st.error("Invalid time format. Please use MM:SS.")
