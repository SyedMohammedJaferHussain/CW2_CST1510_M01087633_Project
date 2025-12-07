import streamlit as st
import app.data.tickets as tickets
import plotly.express as exp


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
        

def RowColumnCnt(df):
    st.divider()
    rowCnt = tickets.TotalTickets(filterQuery)
    st.text(f"Row Count: {rowCnt}")
    

def BarChart(df):
    bar = exp.bar(df, x = "subject")
    Debug(df)
    st.subheader("IT Tickets")
    st.plotly_chart(bar)


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
            queries += (f"subject = '{title[0]}'", )
        else:
            queries += (f"subject IN {title}", )  
    if severity:
        if len(severity) == 1:
            queries += (f"priority = '{severity[0]}'", )
        else:
            queries += (f"priority IN {severity}", )
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
            
        with st.expander("**Subject**"):
            titleFil: tuple = tuple(st.multiselect("Subject", ("Printer not working", "Password reset request", "VPN connection issue", "Network outage", "Access request", "Software installation needed", "Malware alert", "Laptop not booting", "System Crash", "Email not syncing")))

        with st.expander("**Priority**"):
            sevFil: tuple = tuple(st.multiselect("Priority", ("low", "medium", "high", "urgent")))
            
        with st.expander("**Status**"):
            statusFil: tuple = tuple(st.multiselect("Status", ("open", "in progress", "resolved")))
        
        with st.expander("**Date**"):
            dateStart = st.date_input("Start Value", value = "2020-01-01")
            dateStop = st.date_input("Stop Value")
            
        if st.button("Apply Filters"):
            ApplyFilter(idStart, idStop, titleFil, sevFil, statusFil, str(dateStart), str(dateStop))
            global filterApply
            filterApply = True


def BarCheck():
    if filterApply:
        data = tickets.GetAllTickets(filterQuery)
        print(data)
        BarChart(data)
    else:
        data = tickets.GetAllTickets(filterQuery)
        print(data)
        BarChart(data)


def CreateTicket():
    """
        Provide labels and textboxes for user input
    """
    st.divider()
    st.subheader("Create Ticket")
    
    tId: str = st.text_input("Ticket ID")
    subjectType: str = st.selectbox("Incident Type", ("Printer not working", "Password reset request", "VPN connection issue", "Network outage", "Access request", "Software installation needed", "Malware alert", "Laptop not booting", "System Crash", "Email not syncing"))
    date: str = str(st.date_input("Date"))
    priority: str = st.selectbox("Severity", ("low", "medium", "high", "urgent"))
    status: str = st.selectbox("Status", ("open", "resolved", "in progress"))
    if st.button("Create Incident"):
        tickets.InsertTicket(tId, subjectType, priority, status, date)
        st.success("Incident Created!")
    

if __name__ == "__main__":
    CheckLogIn()
    st.title("IT TICKETS")
    filterApply = False
    filterQuery = ""
    Filters()
    RowColumnCnt(filterQuery)
    BarCheck()
    
    CreateTicket()