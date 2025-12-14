from app.services.database_manager import DatabaseManager
from models.incidents import Incident
from pathlib import Path
from typing import Any
import pandas as pd
import pickle


def TransferFromDB():
    """
        Gets all rows from IT_incidents and creates a list of Incident
        Returns: itincidents (_list[Incident]_): List containing all incidents in database
    """
    dbMgr = DatabaseManager(str(Path("DATA") / "intelligence_platform.db"))
    df = dbMgr.FetchAll("SELECT * FROM Cyber_Incidents ORDER BY id")
    cyberIncidents: list[Incident] = []
    ids: list[int] = df["id"].tolist()
    incType: list[str] = df["incident_type"].tolist()
    sevs: list[str] = df["severity"].tolist()
    stats: list[str] = df["status"].tolist()
    crDates: list[str] = df["date"].tolist()
    for i in range(len(df)):
        incident: Incident = Incident(int(ids[i]), incType[i], sevs[i], stats[i], crDates[i])
        cyberIncidents.append(incident)
    
    return cyberIncidents


def GetColumn(col: str, incident: Incident):
    """
        Matches string to respective column value
        Args:
            col (_str_): Contains string form of column
            inc (_Incident_): Incident to get column value
        Returns:
            (_int_ | _str_): Value of incident[col]
    """
    match col:
        case "id":
            return incident.GetID()
        case "incident_type":
            return incident.GetIncident()
        case "severity":
            return incident.GetSev()
        case "status":
            return incident.GetStatus()
        case "date":
            return incident.GetCrDate()
        case _: # * = "All"
            return incident.GetAll()


def CheckFilters(filters: dict | None, incident: Incident):
    """
        Explanation: 
            Iterates through filters and checks if the function value returns True for all, if one returns False, break and return False
        Args:
            filters (_dict_): Dictionary of form dict[str, function]
            incident (_Incident_): Incident which filter is being checked on
        Returns:
            check (_bool_): If True, passed all filters. If False, failed one filter
    """
    if not filters:
        return True
    check: bool = True
    for column in filters:
        if not filters[column](GetColumn(column, incident)): #type: ignore
            check = False
            break
    
    return check


def AddCnt(hash: dict, col: Any, colName: str) -> None:
    """
        Explanation:
            Modifies hash to update col if found or not found
        Args: 
            hash (_dict_): Dictionary of type {column: count(column)}
            col (_Any_): Contains column value of incident
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
    incidents: list[Incident] = GetIncidents()
    allRows: list = []
    for incident in incidents:
        if CheckFilters(filters, incident):
            allRows.append(GetColumn("*", incident))
    
    df: pd.DataFrame = pd.DataFrame(allRows, columns = ["id", "incident_type", "severity", "status", "date"])
    return df


def GetColCount(filters: dict, col: str) -> pd.DataFrame:
    """
        Explanation: 
            Iterates through all rows of incidents, gets number of occurances of each value in col and returns respective dataframe
        Args:
            filters (_dict_): Contains filters of form dict[str, function]
            col (_str_): Contains column/attribute of Incident to get DataFrame from
        Returns:
            df (_df.DataFrame_): Contains DataFrame with all rows and labelled columns
    """
    incidents: list[Incident] = GetIncidents() #Create dictionaries
    incidentTypes: dict[str, list[str | int]] = {col: [], "Count": []}
    severities: dict[str, list[str | int]] = {col: [], "Count": []}
    statusS: dict[str, list[str | int]] = {col: [], "Count": []}
    dates: dict[str, list[str | int]] = {col: [], "Count": []}
    noIncidents: int = len(incidents)
    
    for i in range(noIncidents):
        incident = incidents[i]
        if not CheckFilters(filters, incident):
            continue
        
        column = GetColumn(col, incident) #Get number of occurances of each value in col
        match col:
            case "incident_type":
                AddCnt(incidentTypes, column, col)
            case "severity":
                AddCnt(severities, column, col)
            case "status":
                AddCnt(statusS, column, col)
            case "date":
                AddCnt(dates, column, col)
                
    dfToReturn: dict = {}           
    match col: #Return correct DataFrame
        case "incident_type":
                dfToReturn = incidentTypes
        case "priority":
                dfToReturn = severities
        case "status":
                dfToReturn = statusS
        case "date":
                dfToReturn = dates
    
    return pd.DataFrame(dfToReturn)


def GetRowCnt(filters: dict) -> int:
    """
        Args:
            filters (_dict_): Contains filters of form dict[str, function]
        Returns:
            cnt (_int_): Contains number of rows that fulfill filters        
    """
    incidents: list[Incident] = GetIncidents()
    cnt: int = 0
    for incident in incidents:
        if CheckFilters(filters, incident):
            cnt += 1
    
    return cnt


def GetIDs(incidents: list[Incident]) -> list[int]:
    """
        Args:
            incidents (_list[Incident]_): List of all incidents
        Returns:
            ids (_list[int]_): Contains list of all ids in incidents
    """
    ids: list[int] = []
    for incident in incidents:
        ids.append(incident.GetID())
    return ids


def CheckID(incidents: list[Incident], id: int) -> bool:
    return True if id in GetIDs(incidents) else False


def InsertIncident(tID: int, sub: str, prio: str, status: str, crDate: str) -> bool:
    """
        Args:
            tID (int): Contains new incident id
            sub (str): Contains new incident subject
            prio (str): Contains new incident priority
            status (str): Contains new incident status
            crDate (str): Contains new incident createdDate

        Returns:
            None | bool: False if ID exists in incidents, else None
    """    

    
    incidents: list[Incident] = GetIncidents()
    incident: Incident = Incident(tID, sub, prio, status, crDate)
    if not CheckID(incidents, tID):
        return False
    incidents.append(incident)
    Writeincidents(incidents)
    return True


def GetIndex(lst: list[Incident], target: int) -> int:
    """
        Explanation:
            Uses BinarySearch algorithm to search for target in most efficient manner
            For more info go to https://www.geeksforgeeks.org/dsa/binary-search/
        Args:
            lst (list[Incident]): Contains all incidents
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


def UpdateIncident(id: int, newId: int, newInc: str, newSev: str, newStat :str, newDate: str) -> None:
    """
        Explanation:
            Updates incident after finding index of id and calls WriteIncidents()
        Args:
            id (int): ID to update
            newId (int): ID of new incident
            newInc (str): incident_type of new incident
            newSev (str): severity of new incident
            newStat (str): status of new incident
            newDate (str): date of new incident
    """    
    incidents: list[Incident] = GetIncidents()
    index: int = GetIndex(incidents, int(id))
    incidents[index] = Incident(newId, newInc, newSev, newStat, newDate)
    Writeincidents(incidents)


def DeleteIncident(id: str):
    """
        Explanation:
            Deletes incident after finding index of id and calls Writeincidents()
        Args:
            id (str): Contains id of incident to be deleted
    """    
    incidents: list[Incident] = GetIncidents()
    index: int = GetIndex(incidents, int(id))
    incidents.remove(incidents[index])
    Writeincidents(incidents)


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
    

def Metrics():
    """
        Explanation:  
            Creates 3 dictionaries (incidents, severities, statusS) of form dict[str, str | int]
            The keys will be columnName/MaxVal/MaxCol/MinVal/MinCol
            The values will be Count/Values containing max and min values/Columns containing max and min values
        Returns:
            tuple[dict[str, str | int]]: Contains 3 dictionaries containing maximum/minimum column name and value
    """
    incidents: list[Incident] = GetIncidents()
    
    incidentTypes: dict[str, str | int] = dict() #Dict of form subjectName : dict["Count": 0]
    severities: dict[str, str | int]  = dict()
    statusS: dict[str, str | int]  = dict()

    for i in range(len(incidents)):
        incident = incidents[i]
        incType: str = incident.GetIncident()
        severity: str = incident.GetSev()
        status: str = incident.GetStatus()
        IncCount(incType, incidentTypes) #type: ignore
        IncCount(severity, severities) #type: ignore
        IncCount(status, statusS) #type: ignore
    
    GetMaxMin(incidentTypes)
    GetMaxMin(severities)
    GetMaxMin(statusS)

    return incidentTypes, severities, statusS


def GetIncidents() -> list[Incident]:
    """
        Explanation:
            Uses pickle module to read(Deserialise) incidents.bin containing incidents
        Returns: 
            incidents (list[Incident]): Contains all incidents
    """
    with open(Path("DATA") / "incidents.bin", "rb") as incidentsObjs:
        incidents = pickle.load(incidentsObjs) 
    return incidents


def Writeincidents(incidents: list[Incident]):
    """
        Args:
            incidents (list[Incident]): Contains all incidents in incidents.bin
    """    
    with open(Path("DATA") / "incidents.bin", "wb") as incidentsObjs:
        pickle.dump(incidents, incidentsObjs)
        

def Commit():
    """
        Explanation:
            Commits all changes made to incidents after logging out
            Iterates through every incident and adds incident to IT_incidents in intelligence_platform.db
    """
    incidents = GetIncidents()
    dbMgr = DatabaseManager(str(Path("DATA") / "intelligence_platform.db"))
    dbMgr.Exec("DELETE FROM Cyber_Incidents")
    for incident in incidents:
        dbMgr.Exec("INSERT INTO Cyber_Incidents (id, incident_type, severity, status, date) VALUES (?, ?, ?, ?, ?)", (str(incident.GetID()), incident.GetIncident(), incident.GetSev(), incident.GetStatus(), incident.GetCrDate()) )
    
    dbMgr.Close()