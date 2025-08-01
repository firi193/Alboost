# ui/components/time_selector.py

import streamlit as st
from datetime import date, timedelta

def time_range_selector(label="📅 Select Time Range", key=None):
    today = date.today()
    max_past_date = today - timedelta(days=90)

    range_options = {
        "Past Day": (today - timedelta(days=1), today),
        "This Week": (today - timedelta(days=today.weekday()), today),
        "Last 7 Days": (today - timedelta(days=7), today),
        "Last 30 Days": (today - timedelta(days=30), today),
        "Last 60 Days": (today - timedelta(days=60), today),
        "Last 90 Days": (today - timedelta(days=90), today),
        "Custom Range": None
    }

    # Use the key parameter to make selectbox unique
    selectbox_key = f"time_range_select_{key}" if key else "time_range_select"
    selected_option = st.selectbox(label, list(range_options.keys()), key=selectbox_key)

    if selected_option == "Custom Range":
        # Use the key parameter to make date_input unique
        date_input_key = f"time_range_date_{key}" if key else "time_range_date"
        start_date, end_date = st.date_input(
            "Select date range (max past 90 days)",
            value=(today - timedelta(days=7), today),
            min_value=max_past_date,
            max_value=today,
            key=date_input_key
        )
    else:
        start_date, end_date = range_options[selected_option]

    return start_date, end_date
