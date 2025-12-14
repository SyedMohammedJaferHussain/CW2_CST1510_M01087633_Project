from app.services.database_manager import DatabaseManager
from models.it_ticket import ITTicket
from pathlib import Path
from typing import Any
import pandas as pd
import pickle


def TransferFromDB():
    """
        Gets all rows from IT_Tickets and creates a list of ITTicket
        Returns: itTickets (_list[ITTicket]_): List containing all tickets in database
    """
    dbMgr = DatabaseManager(str(Path("DATA") / "intelligence_platform.db"))
    df = dbMgr.FetchAll("SELECT * FROM IT_Tickets ORDER BY ticket_id")
    itTickets: list[ITTicket] = []
    ids: list[str] = df["ticket_id"].tolist() #Converted to int later
    subs: list[str] = df["subject"].tolist()
    prios: list[str] = df["priority"].tolist()
    stats: list[str] = df["status"].tolist()
    crDates: list[str] = df["created_date"].tolist()
    for i in range(len(df)):
        ticket: ITTicket = ITTicket(int(ids[i]), subs[i], prios[i], stats[i], crDates[i])
        itTickets.append(ticket)
    
    return itTickets


def GetColumn(col: str, ticket: ITTicket):
    """
        Matches string to respective column value
        Args:
            col (_str_): Contains string form of column
            ticket (_ITTicket_): Ticket to get column value
        Returns:
            (_int_ | _str_): Value of ticket[col]
    """
    match col:
        case "ticket_id":
            return ticket.GetID()
        case "subject":
            return ticket.GetSub()
        case "priority":
            return ticket.GetPrio()
        case "status":
            return ticket.GetStatus()
        case "created_date":
            return ticket.GetCrDate()
        case _: # * = "All"
            return ticket.GetAll()


def CheckFilters(filters: dict | None, ticket: ITTicket):
    """
        Explanation: 
            Iterates through filters and checks if the function value returns True for all, if one returns False, break and return False
        Args:
            filters (_dict_): Dictionary of form dict[str, function]
            ticket (_ITTicket_): Ticket which filter is being checked on
        Returns:
            check (_bool_): If True, passed all filters. If False, failed one filter
    """
    if not filters:
        return True
    check: bool = True
    for column in filters:
        if not filters[column](GetColumn(column, ticket)): #type: ignore
            check = False
            break
    
    return check


def AddCnt(hash: dict, col: Any, colName: str) -> None:
    """
        Explanation:
            Modifies hash to update col if found or not found
        Args: 
            hash (_dict_): Dictionary of type {column: count(column)}
            col (_Any_): Contains column value of ticket
            colName (_str_): Contains value of x-axis to be shown in charts
    """
    if col in hash[colName]:
        index: int = hash[colName].index(col)
        hash["Count"][index] += 1
    else:
        hash[colName].append(col)
        hash["Count"].append(1)


def GetRows(filters: dict) -> pd.DataFrame:
    """
        Explanation: 
            Iterates through all rows of incidents, if filter pass, it appends to dataframe
        Args:
            filters (_dict_): Contains filters of form dict[str, function]
        Returns:
            df (_df.DataFrame_): Contains DataFrame with all rows and labelled columns
    """
    tickets: list[ITTicket] = GetTickets()
    allRows: list = []
    for ticket in tickets:
        if CheckFilters(filters, ticket):
            allRows.append(GetColumn("*", ticket))
    
    df: pd.DataFrame = pd.DataFrame(allRows, columns = ["ticket_id", "subject", "priority", "status", "created_date"])
    return df


def GetColCount(filters: dict, col: str) -> pd.DataFrame:
    """
        Explanation: 
            Iterates through all rows of tickets, gets number of occurances of each value in col and returns respective dataframe
        Args:
            filters (_dict_): Contains filters of form dict[str, function]
            col (_str_): Contains column/attribute of ITTicket to get DataFrame from
        Returns:
            df (_df.DataFrame_): Contains DataFrame with all rows and labelled columns
    """
    tickets: list[ITTicket] = GetTickets() #Create dictionaries
    subjects: dict[str, list[str | int]] = {col: [], "Count": []}
    priorities: dict[str, list[str | int]] = {col: [], "Count": []}
    statusS: dict[str, list[str | int]] = {col: [], "Count": []}
    dates: dict[str, list[str | int]] = {col: [], "Count": []}
    noTickets: int = len(tickets)
    
    for i in range(noTickets):
        ticket = tickets[i]
        if not CheckFilters(filters, ticket):
            continue
        
        column = GetColumn(col, ticket) #Get number of occurances of each value in col
        match col:
            case "subject":
                AddCnt(subjects, column, col)
            case "priority":
                AddCnt(priorities, column, col)
            case "status":
                AddCnt(statusS, column, col)
            case "created_date":
                AddCnt(dates, column, col)
                
    dfToReturn = {}           
    match col: #Return correct DataFrame
        case "subject":
                dfToReturn = subjects
        case "priority":
                dfToReturn = priorities
        case "status":
                dfToReturn = statusS
        case "created_date":
                dfToReturn = dates
    
    return pd.DataFrame(dfToReturn)


def GetRowCnt(filters: dict) -> int:
    """
        Args:
            filters (_dict_): Contains filters of form dict[str, function]
        Returns:
            cnt (_int_): Contains number of rows that fulfill filters        
    """
    tickets: list[ITTicket] = GetTickets()
    cnt: int = 0
    for ticket in tickets:
        if CheckFilters(filters, ticket):
            cnt += 1
    
    return cnt


def GetIDs(tickets: list[ITTicket]) -> list[int]:
    """
        Args:
            tickets (_list[ITTIcket]_): List of all tickets
        Returns:
            ids (_list[int]_): Contains list of all ids in tickets
    """
    ids: list[int] = []
    for ticket in tickets:
        ids.append(ticket.GetID())
    return ids


def CheckID(tickets: list[ITTicket], id: int) -> bool:
    """If found return True, if not found return false"""
    return True if id in GetIDs(tickets) else False


def InsertTicket(tID: int, sub: str, prio: str, status: str, crDate: str) -> bool:
    """
        Args:
            tID (int): Contains new ticket id
            sub (str): Contains new ticket subject
            prio (str): Contains new ticket priority
            status (str): Contains new ticket status
            crDate (str): Contains new ticket createdDate

        Returns:
            bool: True if ticket added, False if not added
    """    
    tickets: list[ITTicket] = GetTickets()
    ticket: ITTicket = ITTicket(tID, sub, prio, status, crDate)
    check = CheckID(tickets, tID)
    if check:
        return False
    tickets.append(ticket)
    WriteTickets(tickets)
    return True


def GetIndex(lst: list[ITTicket], target: int) -> int:
    """
        Explanation:
            Uses BinarySearch algorithm to search for target in most efficient manner
            For more info go to https://www.geeksforgeeks.org/dsa/binary-search/
        Args:
            lst (list[ITTicket]): Contains all tickets
            target (int): Target to be searched for
        Returns:
            int: Index location of target
    """    
    low: int = 0
    high: int = len(lst) - 1
    while low <= high:
        mid: int = low + (high - low) // 2
        if lst[mid].GetID() == target:
            return mid
        elif int(lst[mid].GetID()) < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


def UpdateTicket(id: int, newId: int, newSub: str, newPrio: str, newStat :str, newDate: str) -> None:
    """
        Explanation:
            Updates ticket after finding index of id and calls WriteTickets()
        Args:
            id (int): Contains ticket id to update
            newId (int): Contains new ticket id
            newSub (str): Contains new ticket subject
            newPrio (str): Contains new ticket priority
            newStat (str): Contains new ticket status
            newDate (str): Contains new ticket created_date
    """    
    tickets: list[ITTicket] = GetTickets()
    index: int = GetIndex(tickets, int(id))
    tickets[index] = ITTicket(newId, newSub, newPrio, newStat, newDate)
    WriteTickets(tickets)


def DeleteTicket(id: str):
    """
        Explanation:
            Deletes ticket after finding index of id and calls WriteTickets()
        Args:
            id (str): Contains id of ticket to be deleted
    """    
    tickets: list[ITTicket] = GetTickets()
    index: int = GetIndex(tickets, int(id))
    tickets.remove(tickets[index])
    WriteTickets(tickets)


def IncCount(column: str, dictionary: dict) -> None:
    """
        Explanation:
            Increments dictionary[column] value by 1 if exists, else sets value to 1
        Args:
            column (str): Value in dictionary to increment/set
            dictionary (dict): Dictionary containing various columns
    """    
    if column in dictionary:
        dictionary[column] += 1 #type: ignore
    else:
        dictionary[column] = 1 #type: ignore


def GetMaxMin(dictionary: dict[str, str | int]) -> None: 
    """
        Explanation: 
            Goes through every column in dictionary and finds maximum and minimum value and column name. 
            Puts maximum and minimum value and column names as keys in dictionary
        Args:
            dictionary (dict[str, str  |  int]): Dictionary containing columns and Max/Min Column names and values
    """    
    firstKey: str = list(dictionary.keys())[0]
    dictionary["MaxCol"] = firstKey
    dictionary["MinCol"] = firstKey
    dictionary["MaxVal"] = dictionary[firstKey]
    dictionary["MinVal"] = dictionary[firstKey]
    for col in dictionary:
        if col in ("MaxVal", "MaxCol", "MinVal", "MinCol"):
            break
        count: int = dictionary[col] #type: ignore
        if count > dictionary["MaxVal"]: #type: ignore
            dictionary["MaxVal"] = count
            dictionary["MaxCol"] = col
        elif count < dictionary["MinVal"]: #type: ignore
            dictionary["MinVal"] = count
            dictionary["MinCol"] = col
    

def Metrics(filters: dict):
    """
        Explanation:  
            Creates 3 dictionaries (subjects, priorities, statusS) of form dict[str, str | int]
            The keys will be columnName/MaxVal/MaxCol/MinVal/MinCol
            The values will be Count/Values containing max and min values/Columns containing max and min values
        Returns:
            tuple[dict[str, str | int]]: Contains 3 dictionaries containing maximum/minimum column name and value
    """
    tickets: list[ITTicket] = GetTickets()
    
    subjects: dict[str, str | int] = dict() #Dict of form subjectName : dict["Count": 0]
    priorities: dict[str, str | int]  = dict()
    statusS: dict[str, str | int]  = dict()

    for i in range(len(tickets)):
        if not CheckFilters(filters, tickets[i]):
            continue 
        ticket = tickets[i]
        
        subject: str = ticket.GetSub()
        priority: str = ticket.GetPrio()
        status: str = ticket.GetStatus()
        IncCount(subject, subjects) #type: ignore
        IncCount(priority, priorities) #type: ignore
        IncCount(status, statusS) #type: ignore
    
    GetMaxMin(subjects)
    GetMaxMin(priorities)
    GetMaxMin(statusS)

    return subjects, priorities, statusS


def GetTickets() -> list[ITTicket]:
    """
        Explanation:
            Uses pickle module to read(Deserialise) tickets.bin containing tickets
        Returns: 
            tickets (list[ITTicket]): Contains all tickets
    """
    with open(Path("DATA") / "tickets.bin", "rb") as ticketsObjs:
        tickets = pickle.load(ticketsObjs) 
    return tickets


def WriteTickets(tickets: list[ITTicket]):
    """
        Args:
            tickets (list[ITTicket]): Contains all tickets in tickets.bin
    """    
    with open(Path("DATA") / "tickets.bin", "wb") as ticketsObjs:
        pickle.dump(tickets, ticketsObjs)
        

def Commit():
    """
        Explanation:
            Commits all changes made to tickets after logging out
            Iterates through every ticket and adds ticket to IT_Tickets in intelligence_platform.db
    """
    tickets = GetTickets()
    dbMgr = DatabaseManager(str(Path("DATA") / "intelligence_platform.db"))
    dbMgr.Exec("DELETE FROM IT_Tickets")
    for ticket in tickets:
        dbMgr.Exec("INSERT INTO IT_Tickets (ticket_id, subject, priority, status, created_date) VALUES (?, ?, ?, ?, ?)", (str(ticket.GetID()), ticket.GetSub(), ticket.GetPrio(), ticket.GetStatus(), ticket.GetCrDate()) )
    
    dbMgr.Close()