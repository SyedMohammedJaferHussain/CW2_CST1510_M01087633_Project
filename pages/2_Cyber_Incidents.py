import streamlit as st
import app.data.incidents as incidents
import plotly.express as exp
from openai import OpenAI
from matplotlib.pyplot import subplots
from datetime import date
from typing import Literal
from app.services.ai_assistant import AIAssistant


def Debug(*args) -> None:
    """
        ONLY USED FOR DEVELOPMENT
        For easy debugging, using f-string formatting. 
    """
    for arg in args:
        print(f"{arg=}")


def CheckLogIn() -> None: 
    """
        Check if user is in logged in state
        If not display appropriate error and switch to Home page
    """
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "cyberMsgs" not in st.session_state:
        st.session_state.cyberMsgs = list()

    if not st.session_state.logged_in:
        st.error("You must be logged in to view the dashboard.")
        if st.button("Go to login page"):
            st.switch_page("Home.py")   #Back to the home page
        st.stop()


def SelectCol() -> Literal["incident_type", "severity", "status"]:
    """
        Creates a selectbox for user to select subject, priority, or status
        Returns: selectCol (_str_): Contains column selected by user
    """
    st.divider()
    selectedCol: str = st.selectbox("X Axis", ("incident_type", "severity", "status"))
    return selectedCol
    
    
def RowColumnCnt() -> None:
    """
        Displays metric containing number of rows in filtered output
    """
    rowCnt = incidents.GetRowCnt(filterCons)
    st.metric("Row Count", rowCnt)
    

def BarChart(df, col: str):
    """
        Explanation: Creates a plotly.expressbar chart displaying column and number of occurances of column from df
        Args:
            df (_DataFrame_): DataFrame consisting of query output from Cyber_Incidents Table
    """
    bar = exp.bar(df, x = col, y = "Count")
    st.plotly_chart(bar)


def AnalysisSummary() -> None:
    """
        Explanation: Creates 6 metrics for most and least amounts of incidents, priorities, and statuses
        Returns: None
    """
    incidentTypes, severities, statusS = incidents.Metrics()  
    
    with st.container(horizontal = True):
        st.metric("Most Records of Incidents", f"{incidentTypes["MaxCol"].title()}:\n{incidentTypes["MaxVal"]}", width = "content", border = True) #type: ignore 
        st.metric("Least Records of Incidents", f"{incidentTypes["MinCol"].title()}:\n{incidentTypes["MinVal"]}", width = "content", border = True) #type: ignore 
        st.metric("Most Records of Priorities", f"{severities["MaxCol"].title()}:\n{severities["MaxVal"]}", width = "content", border = True) #type: ignore 
        st.metric("Least Records of Priorities", f"{severities["MinCol"].title()}:\n{severities["MinVal"]}", width = "content", border = True) #type: ignore 
        st.metric("Most Records of Statuses", f"{statusS["MaxCol"].title()}:\n{statusS["MaxVal"]}", width = "content", border = True) #type: ignore 
        st.metric("Least Records of Statuses", f"{statusS["MinCol"].title()}:\n{statusS["MinVal"]}", width = "content", border = True) #type: ignore 


def GetDate(dateVal: str) -> date:
    """
        Args: 
            dateVal (_str_): String in YYYY-MM-DD format
        Returns:
            date (_date_): Contains dateVal converted to datetime.date class
    """
    year, month, day = dateVal.split("-")
    return date(int(year), int(month), int(day))
    

def FilterConditions(idStart: str, idStop: str, incTypes: tuple, severities :tuple, status: tuple, dateStart :str, dateStop: str):
    """
        Explanation: 
            Checks every filter variable. If filled: adds key: value pair to filterCons of form {column: lambda function}
        Args:
            idStart (_str_): Start range of ID
            idStop (_str_): Stop range of ID
            incTypes (_tuple_): Incidents to check for
            severities (_tuple_): Severities to check for
            status (_tuple_): Status to check for
            dateStart (_str_): Start range of date
            dateStop (_str_): Stop range of date
    """
    global filterCons
    if idStart and idStop: #Both selected by default
        filterCons["id"] = lambda tId: int(idStart) <= tId <= int(idStop)
    if incTypes:
        filterCons["incident_type"] = lambda sub: sub in incTypes
    if severities:
        filterCons["severity"] = lambda prio: prio in severities
    if status:
        filterCons["status"] = lambda stat: stat in status
    if dateStart: #Selected as today by default
        filterCons["date"] = lambda date: GetDate(dateStart) <= GetDate(date) <= GetDate(dateStop)


def Filters() -> None:
    """
        Creates widgets for filters which include textboxes, checkboxes, and date inputs
        When apply filters button clicked, pass user input values to FilterConditions()
    """
    if curTab != "Analysis": #Only show when on analysis tab
        return
    
    with st.sidebar:
        st.title("Filters")
        
        with st.expander("**ID**"):
            idStart: str = str(st.text_input("Start Value"))
            idStop: str = str(st.text_input("Stop Value"))
            
        with st.expander("**Incident Type**"):
            incFil: tuple = tuple(st.multiselect("Incident Type", ("DDos Attack", "Phishing email detected", "Data breach", "Zero-day exploit activity", "Firewall breach", "Suspicious login", "Malware infection", "Unauthorized access attempt", "SQL injection attempt")) )

        with st.expander("**Severity**"):
            sevFil: tuple = tuple(st.multiselect("Severity", ("low", "medium", "high", "critical")))
            
        with st.expander("**Status**"):
            statusFil: tuple = tuple(st.multiselect("Status", ("open", "investigating", "resolved")))
        
        with st.expander("**Date**"):
            dateStart = st.date_input("Start Value", value = "2020-01-01")
            dateStop = st.date_input("Stop Value")
            
        if st.button("Apply Filters"):
            FilterConditions(idStart, idStop, incFil, sevFil, statusFil, str(dateStart), str(dateStop))
            global filterApply #Filter is currently being applied
            filterApply = True
            

def BarCheck(column: str) -> None:
    """
        Checks if filter has applied and updates chart everytime button is pressed
        It then calls BarChart() with 
    """
    if filterApply:
        print(1)
        data = incidents.GetColCount(filterCons, column)
        print(data)
        BarChart(data, column)
    else:
        
        data = incidents.GetColCount(None, column) #type: ignore
        print(data)
        BarChart(data, column)


def Table() -> None:
    """
        Creates table using st.dataframe() 
        Contains all filtered records
    """
    st.subheader("Table")
    data = incidents.GetRows(filterCons)
    st.dataframe(data)


def LineChart() -> None:
    """
        Creates line chart using st.line_chart
        Contains all dates grouped by amount of records in each date
    """
    st.divider()
    st.subheader("Line Chart (Dates)")
    data = incidents.GetColCount(filterCons, "date")
    st.line_chart(data, x = "date", y = "Count", color = "#4bd16f")


def PieChart(col: str) -> None:
    """
        Creates pie chart taking values from GetColCount() and matplotlib.subplots()
        
    """
    data = incidents.GetColCount(filterCons, col)
    labels = data[col].tolist()
    sizes = data["Count"].tolist()
    
    fig, ax = subplots() #fig is figure, ax is array of axes
    ax.pie(sizes, labels = labels, autopct = "%1.1f%%", startangle = 90)
    ax.axis("equal")
    st.pyplot(fig)
    

def PromptTicketInfo() -> tuple:
    """
        Creates text input widgets for id, incident_type, date, severity, and status
        Returns: (_tuple_): Variables containing user input for each column
    """
    tId: str = st.text_input("Ticket ID")
    incidentType: str = st.selectbox("Incident Type", ("DDos Attack", "Phishing email detected", "Data breach", "Zero-day exploit activity", "Firewall breach", "Suspicious login", "Malware infection", "Unauthorized access attempt", "SQL injection attempt"))
    date: str = str(st.date_input("Date"))
    severity: str = st.selectbox("Severity", ("low", "medium", "high", "critical"))
    status: str = st.selectbox("Status", ("open", "resolved", "investigating"))
    
    return tId, incidentType, severity, status, date


def CRUDTicket():
    """
        Contains functions for creating, updating, and deleting incidents
        Explanation:
            Allows user to choose selectbox between CRUD Operations
            Calls PromptTicketInfo() or displays necessary input prompt areas for getting user input
            When button pressed, take user input and call relevant function from incidentsClass.py
    """
    st.divider()
    with st.sidebar:
        st.header("CRUD Operations")
        cudChoice: str = st.selectbox("Operation", ("Create Incident", "Read Incident", "Update Incident", "Delete Incident"))
    
    st.subheader(cudChoice)
    if cudChoice == "Read Incident":
        Table()
        return

    if cudChoice == "Create Incident":
        tId, incType, severity, status, date = PromptTicketInfo()
    elif cudChoice != "Read Incident":
        tId: str = st.text_input("Incident ID") #Only require id for delete and update
    
    if cudChoice == "Update Incident": #Creating seperate widgets for update ticket since using PromptTicketInfo() raises streamlit.errors.StreamlitDuplicateElementId
        st.markdown("**Updated Values**")
        newId: str = st.text_input("Incident ID ")
        newInc: str = st.selectbox("Incident Type ", ("DDos Attack", "Phishing email detected", "Data breach", "Zero-day exploit activity", "Firewall breach", "Suspicious login", "Malware infection", "Unauthorized access attempt", "SQL injection attempt"))
        newDate: str = str(st.date_input("Date "))
        newSev: str = st.selectbox("Priority ", ("low", "medium", "high", "critical"))
        newStat: str = st.selectbox("Status ", ("open", "resolved", "investigating"))
    
    if st.button(cudChoice):
        #Calling necessary functions for each CRUD Operation
        match cudChoice:
            case "Create Incident":
                result = incidents.InsertIncident(tId, incType, severity, status, date) #type: ignore
                if not result:
                    st.error("Ticket ID Exists!")
                else:      
                    st.success("Ticket Created!")
            case "Update Incident":
                incidents.UpdateIncident(tId, newId, newInc, newSev, newStat, newDate) #type: ignore
                st.success("Ticket Updated!")
            case "Delete Incident":
                incidents.DeleteIncident(tId)
                st.success("Ticket Deleted!")


def Streaming(completion):
    """
        Explanation: Takes delta time and displays ChatGPT response in small chunks
        
        Args: 
            completion (_Stream[ChatCompletionChunk]_): Contains entire response in small chunks to allow for streaming
        Returns:
            fullReply (_str_): Contains the full response by ChatGPT
    """
    container = st.empty()
    fullReply = ""
    
    for chunk in completion:
        delta = chunk.choices[0].delta
        if delta.content:
            fullReply += delta.content
            container.markdown(fullReply + "▌") # Add cursor effect, character is "Left Hand Block"
    
    # Remove cursor and show final response
    container.markdown(fullReply)
    return fullReply


def DisplayPrevMsgs():
    """
        Displays all messages in st.session_state.cyberMsgs except for messages by system 
        System message is initial prompt given to gpt for it to know its specific role
    """
    for message in st.session_state.cyberMsgs:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def OpenAIConnect():
    """
        Implementing ChatGPT 4o mini to assist with IT related doubts
    """   
    st.divider()
    st.header("Cyber Incidents Expert")
    DisplayPrevMsgs()
    
    prompt = st.chat_input("Prompt our cyber incidents expert (GPT 4.0mini)...")
    if prompt:
        #Save user response
        st.session_state.cyberMsgs.append({ "role": "user", "content": prompt })
        with st.chat_message("user"): 
            st.markdown(prompt)
            
        assistant = AIAssistant(
            "You are an expert in office related cyber incidents. Make sure your responses are not too long", 
            client, 
            st.session_state.metaMsgs)
        
        completion = assistant.SendMessage(prompt)
            
        with st.chat_message("assistant"):
            fullReply = Streaming(completion)
        
        #Save AI response
        st.session_state.cyberMsgs.append({ "role": "assistant", "content": fullReply })
       

def DisplayAllWidgets() -> None:
    """
        Handles all UI elements in this page
        Allows user to switch between Analysis, CRUD Operations, and AI Assistant
            Analysis: Contains Table, Barchart, Piechart, Linechart, Metrics, and Filters
            CRUD Operations: Contains Create, Read, Update, and Delete incidents
            AI Assistant: Contains OpenAI API Interface with specialised chatbot for IT Related help
    """
    global curTab
    curTab = st.selectbox("Tabs", ["Analysis", "CRUD Operations", "AI Assistant"], placeholder = "Analysis")
    match curTab:
        case "Analysis":
            Filters()
            AnalysisSummary()
            Table()
            col: str = SelectCol()
            RowColumnCnt()
            col1, col2 = st.columns(2)
            with col1: 
                st.subheader("Bar Chart")
                BarCheck(col)
            with col2:
                st.subheader("Pie Chart")
                PieChart(col)
            LineChart()
        case "CRUD Operations":
            CRUDTicket()
        case "AI Assistant":    
            OpenAIConnect()


def LogOut():
    """
        Creates logout button for user
        Calls incidents.Commit() which saves all changes to DATA/intelligence_platform.db 
        Logs out user and switches page to Home.py
    """
    st.divider()
    if st.button("Log out", ):
        incidents.Commit()
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.info("You have been logged out.")
        st.switch_page("Home.py")
    
    
if __name__ == "__main__": #Main function
    #Global Variables
    filterApply = False 
    filterCons: dict = {} #Of form: {"ticket_id": lambda id: 100 <= id <= 200}
    client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])
    curTab: str = ""
    
    #Preliminary Checks for login
    CheckLogIn()
    st.title("Cyber Incidents")
    
    #Widgets and UI
    DisplayAllWidgets()
    LogOut()