import streamlit as st
import pandas as pd
import numpy as np

def CheckLogIn() -> None: 
        # Ensure state keys exist (in case user opens this page first)
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    # Guard: if not logged in, send user back
    if not st.session_state.logged_in:
        st.error("You must be logged in to view the dashboard.")
        if st.button("Go to login page"):
            st.switch_page("Home.py")   # back to the first page
        st.stop()

CheckLogIn()
st.title("Data Analysis")

cyberData = pd.read_csv("DATA/cyber_incidents.csv")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Cyber Incidents")
    st.bar_chart(cyberData, y = "id", x = "title")
    
st.divider()