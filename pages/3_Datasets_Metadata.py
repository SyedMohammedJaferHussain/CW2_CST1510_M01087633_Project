import streamlit as st
import app.data.datasets as datasets
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
    if "metaMsg" not in st.session_state:
        st.session_state.metaMsgs = list()

    if not st.session_state.logged_in:
        st.error("You must be logged in to view the dashboard.")
        if st.button("Go to login page"):
            st.switch_page("Home.py")   #Back to the home page
        st.stop()


def SelectCol() -> Literal["source", "category"]:
    """
        Creates a selectbox for user to select subject, priority, or status
        Returns: selectCol (_str_): Contains column selected by user
    """
    st.divider()
    selectedCol: str = st.selectbox("X Axis", ("source", "category"))
    return selectedCol
    
    
def RowColumnCnt() -> None:
    """
        Displays metric containing number of rows in filtered output
    """
    rowCnt = datasets.GetRowCnt(filterCons)
    st.metric("Row Count", rowCnt)
    

def BarChart(df, col: str):
    """
        Explanation: Creates a plotly.expressbar chart displaying column and number of occurances of column from df
        Args:
            df (_DataFrame_): DataFrame consisting of query output from IT_datasets Table
    """
    bar = exp.bar(df, x = col, y = "Count")
    st.plotly_chart(bar)


def AnalysisSummary() -> None:
    """
        Explanation: Creates 6 metrics for most and least amounts of datasets, priorities, and statuses
        Returns: None
    """
    ctgrys, sources = datasets.Metrics()  
    
    with st.container(horizontal = True):
        st.metric("Most Records of Categories", f"{ctgrys["MaxCol"].title()}:\n{ctgrys["MaxVal"]}", width = "content", border = True) #type: ignore 
        st.metric("Least Records of Categories", f"{ctgrys["MinCol"].title()}:\n{ctgrys["MinVal"]}", width = "content", border = True) #type: ignore 
        st.metric("Most Records of Sources", f"{sources["MaxCol"].title()}:\n{sources["MaxVal"]}", width = "content", border = True) #type: ignore 
        st.metric("Least Records of Sources", f"{sources["MinCol"].title()}:\n{sources["MinVal"]}", width = "content", border = True) #type: ignore 
        

def GetDate(dateVal: str) -> date:
    """
        Args: 
            dateVal (_str_): String in YYYY-MM-DD format
        Returns:
            date (_date_): Contains dateVal converted to datetime.date class
    """
    year, month, day = dateVal.split("-")
    return date(int(year), int(month), int(day))
    

def FilterConditions(idStart: str, idStop: str, ctgrys: tuple, srcs: tuple, sizeStart :str, sizeStop: str, dateStart :str, dateStop: str):
    """
        Args:
            idStart (str): Start value of id
            idStop (str): Stop value of id
            ctgrys (tuple): Tuple of categories to search in
            srcs (tuple): Tuple of sources to search in
            sizeStart (int): Start value of fileSize
            sizeStop (int): Stop value of fileSize
            dateStart (str): Start value of date
            dateStop (str): Stop value of date
    """    
    global filterCons
    if idStart and idStop: #Both selected by default
        filterCons["id"] = lambda id: int(idStart) <= id and id <= int(idStop)
    if ctgrys:
        filterCons["category"] = lambda ctgry: ctgry in ctgrys
    if srcs:
        filterCons["source"] = lambda source: source in srcs
    if sizeStart and sizeStop: #Both selected by default
        filterCons["file_size_mb"] = lambda size: float(sizeStart) <= size and size <= float(sizeStop)
    if dateStart: #Selected as today by default
        filterCons["last_updated"] = lambda date: GetDate(dateStart) <= GetDate(date) <= GetDate(dateStop)


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
            col1, col2 = st.columns(2)
            with col1:   
                idStart: str = str(st.text_input("Start Value"))
            with col2:
                idStop: str = str(st.text_input("Stop Value"))

        with st.expander("**Category**"):
            ctgryFil: tuple = tuple(st.multiselect("Category", categories))
            
        with st.expander("**Source**"):
            sourceFil: tuple = tuple(st.multiselect("Source", sources))
            
        with st.expander("**File Size**"):
            col1, col2 = st.columns(2)
            with col1:
                sizeStart: float = st.number_input("Start Value ", value = 0)
            with col2:     
                sizeStop: float = st.number_input("Stop Value ", value = 10000)

        with st.expander("**Date**"):
            col1, col2 = st.columns(2)
            with col1:     
                dateStart = st.date_input("Start Value  ", value = "2020-01-01")
            with col2:     
                dateStop = st.date_input("Stop Value  ")

        if st.button("Apply Filters"):
            FilterConditions(idStart, idStop, ctgryFil, sourceFil, str(sizeStart), str(sizeStop), str(dateStart), str(dateStop))
            global filterApply #Filter is currently being applied
            filterApply = True
            

def BarCheck(column: str) -> None:
    """
        Checks if filter has applied and updates chart everytime button is pressed
        It then calls BarChart() with 
    """
    if filterApply:
        data = datasets.GetColCount(filterCons, column)
        BarChart(data, column)
    else:
        data = datasets.GetColCount(None, column) #type: ignore
        BarChart(data, column)


def Table() -> None:
    """
        Creates table using st.dataframe() 
        Contains all filtered records
    """
    st.subheader("Table")
    data = datasets.GetRows(filterCons)
    st.dataframe(data)


def LineChart() -> None:
    """
        Creates line chart using st.line_chart
        Contains all dates grouped by amount of records in each date
    """
    st.divider()
    st.subheader("Line Chart (Dates)")
    data = datasets.GetColCount(filterCons, "last_updated")
    st.line_chart(data, x = "last_updated", y = "Count", color = "#4bd16f")


def PieChart(col: str) -> None:
    """
        Creates pie chart taking values from GetColCount() and matplotlib.subplots()
        
    """
    data = datasets.GetColCount(filterCons, col)
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
    id: str = st.text_input("Dataset ID")
    name: str = st.text_input("Dataset Name")
    category: str = st.selectbox("Category", categories) #type: ignore
    fileSize: float = st.number_input("File Size (MB)", min_value = 0, max_value = 100000)
    source: str = st.selectbox("Source", sources) #type: ignore
    lastUpd: str = str(st.date_input("Last Updated"))
    
    return id, name, category, fileSize, source, lastUpd


def CRUDTicket():
    """
        Contains functions for creating, updating, and deleting datasets
        Explanation:
            Allows user to choose selectbox between CRUD Operations
            Calls PromptTicketInfo() or displays necessary input prompt areas for getting user input
            When button pressed, take user input and call relevant function from datasetsClass.py
    """
    st.divider()
    with st.sidebar:
        st.header("CRUD Operations")
        cudChoice: str = st.selectbox("Operation", ("Create Dataset", "Read Datasets", "Update Dataset", "Delete Dataset"))
    
    st.subheader(cudChoice)
    if cudChoice == "Read Datasets":
        Table()
        return

    if cudChoice == "Create Dataset":
        id, name, category, fileSize, source, lastUpd = PromptTicketInfo()
    elif cudChoice != "Read Dataset":
        id: str = st.text_input("Dataset ID") #Only require id for delete and update
    
    if cudChoice == "Update Dataset": #Creating seperate widgets for update ticket since using PromptTicketInfo() raises streamlit.errors.StreamlitDuplicateElementId
        st.markdown("**Updated Values**")
        newId: int = int(st.number_input("Dataset ID "))
        newName: str = st.text_input("Dataset Name")
        newCtgry: str = st.selectbox("Category ", categories) #type: ignore
        newFileSize: float = st.number_input("File Size (MB)", min_value = 0, max_value = 10000)
        newSource: str = st.selectbox("Source", sources) #type: ignore
        newUpdate: str = str(st.date_input("Last Updated"))
        
    if st.button(cudChoice):
        #Calling necessary functions for each CUD Operation
        match cudChoice:
            case "Create Dataset":
                result = datasets.InsertDataset(int(id), name, category, fileSize, source, lastUpd) #type: ignore
                if not result:
                    st.error("Ticket ID Exists!")
                else:      
                    st.success("Ticket Created!")
            case "Update Dataset":
                datasets.UpdateDataset(id, newId, newName, newCtgry, newFileSize, newSource, newUpdate) #type: ignore
                st.success("Ticket Updated!")
            case "Delete Dataset":
                datasets.DeleteDataset(id) # type: ignore
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
        Displays all messages in st.session_state.metaMsgs except for messages by system 
        System message is initial prompt given to gpt for it to know its specific role
    """
    for message in st.session_state.metaMsgs:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def OpenAIConnect():
    """
        Implementing ChatGPT 4o mini to assist with IT related doubts
    """   
    st.divider()
    st.header("IT Expert")
    DisplayPrevMsgs()
    
    prompt = st.chat_input("Prompt our datasets expert (GPT 4.0mini)...")
    if prompt:
        st.session_state.metaMsgs.append({ "role": "user", "content": prompt })
        with st.chat_message("user"): 
            st.markdown(prompt)
        assistant = AIAssistant(
            "You are an datasets expert, you hold specialised knowledge in all things related to datasets. Make sure your responses are not too long", 
            client, 
            st.session_state.metaMsgs)
        
        completion = assistant.SendMessage(prompt)
        
        with st.chat_message("assistant"):
            fullReply = Streaming(completion)

        #Save AI response
        st.session_state.metaMsgs.append({ "role": "assistant", "content": fullReply })
        

def DisplayAllWidgets() -> None:
    """
        Handles all UI elements in this page
        Allows user to switch between Analysis, CRUD Operations, and AI Assistant
            Analysis: Contains Table, Barchart, Piechart, Linechart, Metrics, and Filters
            CRUD Operations: Contains Create, Read, Update, and Delete datasets
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
        Calls datasets.Commit() which saves all changes to DATA/intelligence_platform.db 
        Logs out user and switches page to Home.py
    """
    st.divider()
    if st.button("Log out", ):
        datasets.Commit()
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
    categories: tuple = ("Finance", "Education", "Environment", "Retail", "Transportation", "Technology", "Healthcare")
    sources: tuple = ("Government Open Data", "Internal Analytics Team", "Kaggle", "Public API", "Research Institute")
    
    #Preliminary Checks for login
    CheckLogIn()
    st.title("Datasets Metadata")
    
    #Widgets and UI
    DisplayAllWidgets()
    LogOut()