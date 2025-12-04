import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as exp
import app.data.incidents as CyberFuncs

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


def BarGraph():
    CyberFuncs.GetAllIncidents("placeholder")
    cyberBar = exp.bar({1: "1"}, x = "title")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cyber Incidents")
        st.plotly_chart(cyberBar, x = "title")
        

def CreateIncident():
    """
        Provide labels and textboxes for user input
    """
    st.subheader("Create Incident")
    
    date: str = st.text_input("Date", key = "date")
    incidentType: str = st.selectbox("Incident Type", ("DDoS attack", "Phishing email detected", "Data breach", "Zero-day exploit activity", "Firewall breach", "Suspicious login", "Malware infection", "SQL injection attempt", "Ransomware detected", "Unauthorized access attempt"))
    severity: str = st.selectbox("Severity", ("Low", "Medium", "High", "Critical"))
    status: str = st.selectbox("Status", ("Open", "Resolved", "Investigating"))
    description: str = st.text_input("Description", key = "description")
    
    

if __name__ == "__main__":
    CheckLogIn()
    st.title("Data Analysis")
    st.divider()