import streamlit as st
import app.data.ticketsClass as tickets
import plotly.express as exp
from openai import OpenAI
from matplotlib.pyplot import subplots
from datetime import date
from typing import Literal


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
    if "messages" not in st.session_state:
        st.session_state.messages = list()

    if not st.session_state.logged_in:
        st.error("You must be logged in to view the dashboard.")
        if st.button("Go to login page"):
            st.switch_page("Home.py")   #Back to the home page
        st.stop()


def SelectCol() -> Literal['subject', 'priority', 'status']:
    """
        Creates a selectbox for user to select subject, priority, or status
        Returns: selectCol (_str_): Contains column selected by user
    """
    st.divider()
    selectedCol: str = st.selectbox("X Axis", ("subject", "priority", "status"))
    return selectedCol
    
    
def RowColumnCnt() -> None:
    """
        Displays metric containing number of rows in filtered output
    """
    rowCnt = tickets.GetRowCnt(filterCons)
    st.metric("Row Count", rowCnt)
    

def BarChart(df, col: str):
    """
        Explanation: Creates a plotly.expressbar chart displaying column and number of occurances of column from df
        Args:
            df (_DataFrame_): DataFrame consisting of query output from IT_Tickets Table
    """
    bar = exp.bar(df, x = col, y = "Count")
    st.plotly_chart(bar)


def AnalysisSummary() -> None:
    """
        Explanation: Creates 6 metrics for most and least amounts of tickets, priorities, and statuses
        Returns: None
    """
    subjects, priorities, statusS = tickets.Metrics()  
    
    with st.container(horizontal = True):
        st.metric("Most Records of Tickets", f"{subjects["MaxCol"].title()}:\n{subjects["MaxVal"]}", width = "content", border = True) #type: ignore 
        st.metric("Least Records of Tickets", f"{subjects["MinCol"].title()}:\n{subjects["MinVal"]}", width = "content", border = True) #type: ignore 
        st.metric("Most Records of Priorities", f"{priorities["MaxCol"].title()}:\n{priorities["MaxVal"]}", width = "content", border = True) #type: ignore 
        st.metric("Least Records of Priorities", f"{priorities["MinCol"].title()}:\n{priorities["MinVal"]}", width = "content", border = True) #type: ignore 
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
    

def FilterConditions(idStart: str, idStop: str, titles: tuple, priorities :tuple, status: tuple, dateStart :str, dateStop: str):
    """
        Explanation: 
            Checks every filter variable. If filled: adds key: value pair to filterCons of form {column: lambda function}
        Args:
            idStart (_str_): Start range of ID
            idStop (_str_): Stop range of ID
            titles (_tuple_): Titles to check for
            priorities (_tuple_): Priorities to check for
            status (_tuple_): Status to check for
            dateStart (_str_): Start range of date
            dateStop (_str_): Stop range of date
    """
    global filterCons
    if idStart and idStop: #Both selected by default
        filterCons["ticket_id"] = lambda tId: int(idStart) <= tId <= int(idStop)
    if titles:
        filterCons["subject"] = lambda sub: sub in titles
    if priorities:
        filterCons["priority"] = lambda prio: prio in priorities
    if status:
        filterCons["status"] = lambda stat: stat in status
    if dateStart: #Selected as today by default
        filterCons["created_date"] = lambda date: GetDate(dateStart) <= GetDate(date) <= GetDate(dateStop)


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
            
        with st.expander("**Subject**"):
            titleFil: tuple = tuple(st.multiselect("Subject", ("Printer not working", "Password reset request", "VPN connection issue", "Network outage", "Access request", "Software installation needed", "Malware alert", "Laptop not booting", "System Crash", "Email not syncing")))

        with st.expander("**Priority**"):
            prioFil: tuple = tuple(st.multiselect("Priority", ("low", "medium", "high", "urgent")))
            
        with st.expander("**Status**"):
            statusFil: tuple = tuple(st.multiselect("Status", ("open", "in progress", "resolved")))
        
        with st.expander("**Date**"):
            dateStart = st.date_input("Start Value", value = "2020-01-01")
            dateStop = st.date_input("Stop Value")
            
        if st.button("Apply Filters"):
            FilterConditions(idStart, idStop, titleFil, prioFil, statusFil, str(dateStart), str(dateStop))
            global filterApply #Filter is currently being applied
            filterApply = True
            

def BarCheck(column: str) -> None:
    """
        Checks if filter has applied and updates chart everytime button is pressed
        It then calls BarChart() with 
    """
    if filterApply:
        data = tickets.GetColCount(filterCons, column)
        BarChart(data, column)
    else:
        data = tickets.GetColCount(None, column) #type: ignore
        BarChart(data, column)


def Table() -> None:
    """
        Creates table using st.dataframe() 
        Contains all filtered records
    """
    st.subheader("Table")
    data = tickets.GetRows(filterCons)
    st.dataframe(data)


def LineChart() -> None:
    """
        Creates line chart using st.line_chart
        Contains all dates grouped by amount of records in each date
    """
    st.divider()
    st.subheader("Line Chart (Dates)")
    data = tickets.GetColCount(filterCons, "created_date")
    st.line_chart(data, x = "created_date", y = "Count", color = "#4bd16f")


def PieChart(col: str) -> None:
    """
        Creates pie chart taking values from GetColCount() and matplotlib.subplots()
        
    """
    data = tickets.GetColCount(filterCons, col)
    labels = data[col].tolist()
    sizes = data["Count"].tolist()
    
    fig, ax = subplots() #fig is figure, ax is array of axes
    ax.pie(sizes, labels = labels, autopct = "%1.1f%%", startangle = 90)
    ax.axis("equal")
    st.pyplot(fig)
    

def PromptTicketInfo() -> tuple:
    """
        Creates text input widgets for id, subject, date, priority, and status
        Returns: (_tuple_): Variables containing user input for each column
    """
    tId: str = st.text_input("Ticket ID")
    subjectType: str = st.selectbox("Incident Type", ("Printer not working", "Password reset request", "VPN connection issue", "Network outage", "Access request", "Software installation needed", "Malware alert", "Laptop not booting", "System Crash", "Email not syncing"))
    date: str = str(st.date_input("Date"))
    priority: str = st.selectbox("Priority", ("low", "medium", "high", "urgent"))
    status: str = st.selectbox("Status", ("open", "resolved", "in progress"))
    
    return tId, subjectType, priority, status, date


def CRUDTicket():
    """
        Contains functions for creating, updating, and deleting tickets
        Explanation:
            Allows user to choose selectbox between CRUD Operations
            Calls PromptTicketInfo() or displays necessary input prompt areas for getting user input
            When button pressed, take user input and call relevant function from ticketsClass.py
    """
    st.divider()
    with st.sidebar:
        st.header("CRUD Operations")
        cudChoice: str = st.selectbox("Operation", ("Create Ticket", "Read Tickets", "Update Ticket", "Delete Ticket"))
    
    st.subheader(cudChoice)
    if cudChoice == "Read Tickets":
        Table()
        return

    if cudChoice == "Create Ticket":
        tId, subjectType, priority, status, date = PromptTicketInfo()
    elif cudChoice != "Read Tickets":
        tId: str = st.text_input("Ticket ID") #Only require id for delete and update
    
    if cudChoice == "Update Ticket": #Creating seperate widgets for update ticket since using PromptTicketInfo() raises streamlit.errors.StreamlitDuplicateElementId
        st.markdown("**Updated Values**")
        newId: str = st.text_input("Ticket ID ")
        newSub: str = st.selectbox("Incident Type ", ("Printer not working", "Password reset request", "VPN connection issue", "Network outage", "Access request", "Software installation needed", "Malware alert", "Laptop not booting", "System Crash", "Email not syncing"))
        newDate: str = str(st.date_input("Date "))
        newPrio: str = st.selectbox("Priority ", ("low", "medium", "high", "urgent"))
        newStat: str = st.selectbox("Status ", ("open", "resolved", "in progress"))
    
    if st.button(cudChoice):
        #Calling necessary functions for each CUD Operation
        match cudChoice:
            case "Create Ticket":
                result = tickets.InsertTicket(tId, subjectType, priority, status, date) # type: ignore
                if type(result) is not None:
                    st.error("Ticket ID Exists!")
                else:      
                    st.success("Ticket Created!")
            case "Update Ticket":
                tickets.UpdateTicket(tId, newId, newSub, newPrio, newStat, newDate)# type: ignore
                st.success("Ticket Updated!")
            case "Delete Ticket":
                tickets.DeleteTicket(tId) # type: ignore
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
        Displays all messages in st.session_state.messages except for messages by system 
        System message is initial prompt given to gpt for it to know its specific role
    """
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def AIAssistant():
    """
        Implementing ChatGPT 4o mini to assist with IT related doubts
    """   
    st.divider()
    st.header("IT Expert")
    DisplayPrevMsgs()
    
    prompt = st.chat_input("Prompt our IT expert (GPT 4.0mini)...")
    gptMsg = [{"role": "system", "content": "You are an IT expert, you hold knowledge specialising in office related IT incidents. Make sure your responses are not too long"}]
    if prompt:
        #Save user response
        st.session_state.messages.append({ "role": "user", "content": prompt })
        with st.chat_message("user"): 
            st.markdown(prompt)
        
        # Call OpenAI API with streaming
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create( 
                model = "gpt-4o-mini",
                messages = gptMsg + st.session_state.messages,
                stream = True,
            )
            
        with st.chat_message("assistant"):
            fullReply = Streaming(completion)
        
        #Save AI response
        st.session_state.messages.append({ "role": "assistant", "content": fullReply })
       

def DisplayAllWidgets() -> None:
    """
        Handles all UI elements in this page
        Allows user to switch between Analysis, CRUD Operations, and AI Assistant
            Analysis: Contains Table, Barchart, Piechart, Linechart, Metrics, and Filters
            CRUD Operations: Contains Create, Read, Update, and Delete tickets
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
            AIAssistant()


def LogOut():
    """
        Creates logout button for user
        Calls tickets.Commit() which saves all changes to DATA/intelligence_platform.db 
        Logs out user and switches page to Home.py
    """
    st.divider()
    if st.button("Log out", ):
        tickets.Commit()
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
    st.title("IT TICKETS")
    
    #Widgets and UI
    DisplayAllWidgets()
    LogOut()