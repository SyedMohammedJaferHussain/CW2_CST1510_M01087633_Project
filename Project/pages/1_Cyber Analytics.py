import streamlit as st
import plotly.express as exp
import app.data.incidents as CyberFuncs

def Debug(*args) -> None:
    #For easy debugging, using f-string formatting
    for arg in args:
        print(f"{arg=}")


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


def BarGraph(cyberData):
    global filterApply
    filterApply = False
    cyberBar = exp.bar(cyberData, x = "incident_type")

    st.subheader("Cyber Incidents")
    st.plotly_chart(cyberBar)
    

def ApplyFilter(idStart: str, idStop: str, title: tuple, severity :tuple, status: tuple, dateStart :str, dateStop: str):
    """_summary_

    Args:
        idStart (_str_): Start range of ID
        idStop (_str_): Stop range of ID
        title (_tuple_): Titles to check for
        severity (_tuple_): Severity to check for
        status (_tuple_): Status to check for
        dateStart (_str_): Start range of date
        dateStop (_str_): Stop range of date

    Returns:
        None
    """
    queries: tuple = tuple()
    if idStart and idStop: #Both selected by default
        queries += (f"id BETWEEN {idStart} AND {idStop}", )
    if title:
        if len(title) == 1:
            queries += (f"incident_type = '{title[0]}'", )
        else:
            queries += (f"incident_type IN {title}", )  
    if severity:
        if len(severity) == 1:
            queries += (f"severity = '{severity[0]}'", )
        else:
            queries += (f"severity IN {severity}", )
    if status:
        if len(severity) == 1:
            queries += (f"status = '{status[0]}'", )
        else:
            queries += (f"status IN {status}", )
    #if dateStart: #Selected as today by default
        #queries += (f"date BETWEEN '{dateStart}' AND '{dateStop}'", )

    query: str = ""
    noQueries: int = len(queries)
    Debug(queries)
    if len(queries) == 1:
        query = queries[0]
    for i in range(noQueries - 1): #To make sure last query doesn't have "AND" at the end
        query += queries[i] + " AND "
    if len(queries) > 1:
        query += queries[-1]
    
    Debug(query)
    global filterQuery
    filterQuery = query
    

def Filters() -> None:
    """
        Gets user input for filters and passes data to ApplyFilter()
        Returns: None
    """
    with st.sidebar:
        st.title("Filters")
        
        with st.expander("**ID**"):
            idStart: str = str(st.text_input("Start Value"))
            idStop: str = str(st.text_input("Stop Value"))
            
        with st.expander("**Title**"):
            titleFil: tuple = tuple(st.multiselect("Title", ("DDoS attack", "Phishing email detected", "Data breach","Zero-day exploit activity", "Firewall breach", "Suspicious login", "Malware infection", "Unauthorized access attempt", "Firewall breach", "SQL injection attempt", "Ransomeware detected")))

        with st.expander("**Severity**"):
            sevFil: tuple = tuple(st.multiselect("Severity", ("low", "medium", "high", "critical")))
            
        with st.expander("**Status**"):
            statusFil: tuple = tuple(st.multiselect("Status", ("open", "investigating", "resolved", "closed")))
        
        with st.expander("**Date**"):
            dateStart = st.date_input("Start Value", value = "2020-01-01")
            dateStop = st.date_input("Stop Value")
            
        if st.button("Apply Filters"):
            ApplyFilter(idStart, idStop, titleFil, sevFil, statusFil, str(dateStart), str(dateStop))
            global filterApply
            filterApply = True
            

def CreateIncident():
    """
        Provide labels and textboxes for user input
    """
    st.subheader("Create Incident")
    
    date: str = st.text_input("Date", key = "date")
    incidentType: str = st.selectbox("Incident Type", ("DDoS attack", "Phishing email detected", "Data breach", "Zero-day exploit activity", "Firewall breach", "Suspicious login", "Malware infection", "SQL injection attempt", "Ransomware detected", "Unauthorized access attempt"))
    severity: str = st.selectbox("Severity", ("Low", "Medium", "High", "Critical"))
    status: str = st.selectbox("Status", ("Open", "Resolved", "Investigating"))
    desc: str = st.text_input("Description", key = "description")
    reportedBy: str = st.session_state.username
    if st.button("Create Incident"):
        CyberFuncs.InsertIncident(date, incidentType, severity, status, desc, reportedBy)
        st.success("Incident Created!")
    
    
if __name__ == "__main__":
    CheckLogIn()
    st.title("Data Analysis")
    CyberFuncs.TransferCSV()
    filterApply: bool = False
    filterQuery: str = ""
    INCIDENTS: tuple = ("DDoS attack", "Phishing email detected", "Data breach", "Zero-day exploit activity", "Firewall breach", "Suspicious login", "Malware infection", "SQL injection attempt", "Ransomware detected", "Unauthorized access attempt")
    Filters()
    if filterApply:
        data = CyberFuncs.GetAllIncidents(filterQuery)
        print(data)
        BarGraph(data)
    else:
        data = CyberFuncs.GetAllIncidents("")
        print(data)
        BarGraph(data)
        
    st.divider()
    
    CreateIncident()
    