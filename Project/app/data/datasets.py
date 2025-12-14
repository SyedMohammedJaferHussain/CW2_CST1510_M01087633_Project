from app.services.Database_Manager import DatabaseManager
from models.datasets import Dataset
from pathlib import Path
from typing import Any
import pandas as pd
import pickle
import csv


def TransferFromDB():
    """
        Gets all rows from IT_Datasets and creates a list of Dataset
        Returns: itDatasets (_list[Dataset]_): List containing all Datasets in database
    """
    
    dbMgr = DatabaseManager(str(Path("DATA") / "intelligence_platform.db"))
    df = dbMgr.FetchAll("SELECT * FROM Datasets_Metadata ORDER BY id")
    datasets: list[Dataset] = []
    ids: list[int] = df["id"].tolist()
    names: list[str] = df["dataset_name"].tolist()
    ctgrys: list[str] = df["category"].tolist()
    sizes: list[float] = df["file_size_mb"].tolist()
    sources: list[str] = df["source"].tolist()
    lastUpds: list[str] = df["last_update"].tolist()
    for i in range(len(df)):
        metadata: Dataset = Dataset(int(ids[i]), names[i], ctgrys[i], sizes[i], sources[i], lastUpds[i])
        datasets.append(metadata)
    
    return datasets


def GetColumn(col: str, dataset: Dataset):
    """
        Matches string to respective column value
        Args:
            col (_str_): Contains string form of column
            inc (_Dataset_): Dataset to get column value
        Returns:
            (_int_ | _str_): Value of Dataset[col]
    """
    match col:
        case "id":
            return dataset.GetID()
        case "dataset_name":
            return dataset.GetName()
        case "category":
            return dataset.GetCtgry()
        case "file_size_mb":
            return dataset.GetFileSize()
        case "source":
            return dataset.GetSource()
        case "last_updated":
            return dataset.GetLastUpd()
        case _: # * = "All"
            return dataset.GetAll()


def CheckFilters(filters: dict | None, metadata: Dataset):
    """
        Explanation: 
            Iterates through filters and checks if the function value returns True for all, if one returns False, break and return False
        Args:
            filters (_dict_): Dictionary of form dict[str, function]
            metadata (_Dataset_): Dataset which filter is being checked on
        Returns:
            check (_bool_): If True, passed all filters. If False, failed one filter
    """
    if not filters:
        return True
    check: bool = True
    for column in filters:
        if not filters[column](GetColumn(column, metadata)): #type: ignore
            check = False
            break
    
    return check


def AddCnt(hash: dict, col: Any, colName: str) -> None:
    """
        Explanation:
            Modifies hash to update col if found or not found
        Args: 
            hash (_dict_): Dictionary of type {column: count(column)}
            col (_Any_): Contains column value of Dataset
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
            Iterates through all rows of Datasets, if filter pass, it appends to dataframe
        Args:
            filters (_dict_): Contains filters of form dict[str, function]
        Returns:
            df (_df.DataFrame_): Contains DataFrame with all rows and labelled columns
    """
    datasets: list[Dataset] = GetDatasets()
    allRows: list = []
    for metadata in datasets:
        if CheckFilters(filters, metadata):
            allRows.append(GetColumn("*", metadata))
    
    df: pd.DataFrame = pd.DataFrame(allRows, columns = ["id", "dataset_name", "category", "file_size_mb", "source", "last_updated"])
    return df


def GetColCount(filters: dict, col: str) -> pd.DataFrame:
    """
        Explanation: 
            Iterates through all rows of Datasets, gets number of occurances of each value in col and returns respective dataframe
        Args:
            filters (_dict_): Contains filters of form dict[str, function]
            col (_str_): Contains column/attribute of Dataset to get DataFrame from
        Returns:
            df (_df.DataFrame_): Contains DataFrame with all rows and labelled columns
    """
    datasets: list[Dataset] = GetDatasets() #Create dictionaries
    sources: dict[str, list[str | int]] = {col: [], "Count": []}
    ctgrys: dict[str, list[str | int]] = {col: [], "Count": []}
    fileSizes: dict[str, list[str | int]] = {col: [], "Count": []}
    lastUpds: dict[str, list[str | int]] = {col: [], "Count": []}
    noDatasets: int = len(datasets)
    
    for i in range(noDatasets):
        metadata = datasets[i]
        if not CheckFilters(filters, metadata):
            continue
        
        #Get number of occurances of each value in col
        column = GetColumn(col, metadata) 
        match col:
            case "source":
                AddCnt(sources, column, col)
            case "category":
                AddCnt(ctgrys, column, col)
            case "file_size_mb":
                AddCnt(fileSizes, column, col)
            case "last_updated":
                AddCnt(lastUpds, column, col)
                
    dfToReturn: dict = {}           
    match col: #Return correct DataFrame
        case "source":
            dfToReturn = sources
        case "category":
            dfToReturn = ctgrys
        case "file_size_mb":
            dfToReturn = fileSizes
        case "last_updated":
            dfToReturn = lastUpds
    print(dfToReturn)
    return pd.DataFrame(dfToReturn)


def GetRowCnt(filters: dict) -> int:
    """
        Args:
            filters (_dict_): Contains filters of form dict[str, function]
        Returns:
            cnt (_int_): Contains number of rows that fulfill filters        
    """
    datasets: list[Dataset] = GetDatasets()
    cnt: int = 0
    for metadata in datasets:
        if CheckFilters(filters, metadata):
            cnt += 1
    
    return cnt


def GetIDs(datasets: list[Dataset]) -> list[int]:
    """
        Args:
            Datasets (_list[Dataset]_): List of all Datasets
        Returns:
            ids (_list[int]_): Contains list of all ids in Datasets
    """
    ids: list[int] = []
    for dataset in datasets:
        ids.append(dataset.GetID())
    return ids


def CheckID(datasets: list[Dataset], id: int) -> bool:
    return True if id in GetIDs(datasets) else False


def InsertDataset(id: int, name: str, ctgry: str, fileSize: float, source: str, lastUpd: str) -> bool:
    """
        Args:
            id (int): id of new dataset
            name (str): name of new dataset
            ctgry (str): category of new dataset
            fileSize (str): file size of new dataset
            source (str): source of new dataset
            lastUpd (str): date of last update of new dataset

        Returns:
            bool: Returns True if row added, False if not added
    """    
    datasets: list[Dataset] = GetDatasets()
    metadata: Dataset = Dataset(id, name, ctgry, float(fileSize), source, lastUpd)
    if CheckID(datasets, id):
        return False
    datasets.append(metadata)
    WriteDatasets(datasets)
    return True


def GetIndex(lst: list[Dataset], target: int) -> int:
    """
        Explanation:
            Uses BinarySearch algorithm to search for target in most efficient manner
            For more info go to https://www.geeksforgeeks.org/dsa/binary-search/
        Args:
            lst (list[Dataset]): Contains all Datasets
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


def UpdateDataset(id: int, newId: int, newName: str, newCtgry: str, newFileSize :str, newSource: str, newUpdate: str) -> None:
    """
        Args:
            id (int): Row containing this id will get updated
            newId (int): id of new row
            newName (str): name of new row
            newCtgry (str): category of new row
            newFileSize (str): file size of new row
    """       
    datasets: list[Dataset] = GetDatasets()
    index: int = GetIndex(datasets, int(id))
    datasets[index] = Dataset(newId, newName, newCtgry, float(newFileSize), newSource, newUpdate)
    WriteDatasets(datasets)


def DeleteDataset(id: str):
    """
        Explanation:
            Deletes Dataset after finding index of id and calls WriteDatasets()
        Args:
            id (str): Contains id of Dataset to be deleted
    """    
    datasets: list[Dataset] = GetDatasets()
    index: int = GetIndex(datasets, int(id))
    datasets.remove(datasets[index])
    WriteDatasets(datasets)


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
    

def Metrics() -> tuple[dict, dict]:
    """
        Explanation:  
            Creates a dictionary of form dict[str, str | int]
            The keys will be columnName/MaxVal/MaxCol/MinVal/MinCol
            The values will be Count/Values containing max and min values/Columns containing max and min values
        Returns:
            ctgrys (dict[str, str | int]): Contains columnName/MaxVal/MaxCol/MinVal/MinCol as keys and Count, values/columnName as values
    """
    datasets: list[Dataset] = GetDatasets()
    
    ctgrys: dict[str, str | int] = dict() #Dict of form subjectName : dict["Count": 0]
    sources: dict[str, str | int] = dict()

    for i in range(len(datasets)):
        dataset = datasets[i]
        ctgry: str = dataset.GetCtgry()
        source: str = dataset.GetSource()
        IncCount(ctgry, ctgrys) #type: ignore
        IncCount(source, sources) #type: ignore
    
    GetMaxMin(ctgrys)
    GetMaxMin(sources)
    return ctgrys, sources


def GetDatasets() -> list[Dataset]:
    """
        Explanation:
            Uses pickle module to read(Deserialise) Datasets.bin containing Datasets
        Returns: 
            Datasets (list[Dataset]): Contains all Datasets
    """
    with open(Path("DATA") / "datasets.bin", "rb") as datasetObj:
        datasets = pickle.load(datasetObj) 
    return datasets


def WriteDatasets(Datasets: list[Dataset]):
    """
        Args:
            Datasets (list[Dataset]): Contains all Datasets in Datasets.bin
    """    
    with open(Path("DATA") / "datasets.bin", "wb") as datasetObj:
        pickle.dump(Datasets, datasetObj)
        

def Commit():
    """
        Explanation:
            Commits all changes made to Datasets after logging out
            Iterates through every Dataset and adds Dataset to IT_Datasets in intelligence_platform.db
    """
    Datasets = GetDatasets()
    dbMgr = DatabaseManager(str(Path("DATA") / "intelligence_platform.db"))
    dbMgr.Exec("DELETE FROM Datasets_Metadata") #Truncating entire table
    for dataset in Datasets:
        dbMgr.Exec("INSERT INTO Datasets_Metadata (id, dataset_name, category, file_size_mb) VALUES (?, ?, ?, ?, ?)", (dataset.GetID(), dataset.GetName(), dataset.GetCtgry(), dataset.GetFileSize()) )
    
    dbMgr.Close()
    

def TransferCSV():
    DB_PATH: str = str(Path("DATA") / "intelligence_platform.db")
    dbMgr = DatabaseManager(DB_PATH)
    with open(Path("DATA/datasets_metadata.csv")) as itFile:
        reader = csv.reader(itFile)
        header: bool = False
        for row in reader:
            if header == False:
                header = True
                continue
            dbMgr.Exec("INSERT INTO Datasets_Metadata (id, dataset_name, category, file_size_mb, source, last_update) VALUES (?, ?, ?, ?, ?, ?)", (int(row[0]), row[1], row[2], float(row[3]), row[4], row[5]))
        
    dbMgr.Close()