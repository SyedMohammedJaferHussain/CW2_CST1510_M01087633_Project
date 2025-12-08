import pandas as pd
from app.data.db import connect_database


def InsertIncident(date, incident_type, severity, status, description, reported_by=None):
    """Insert new incident."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO cyber_incidents 
        (date, incident_type, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, incident_type, severity, status, description, reported_by))
    
    conn.commit()
    incident_id = cursor.lastrowid
    conn.close()
    return incident_id


def GetIncidentsQuery(filter):
    """
        Returns query with filter if filter exist
    """
    if filter:
        return f"SELECT incident_type FROM cyber_incidents WHERE {filter}"
    
    return "SELECT incident_type FROM cyber_incidents"


def GetAllIncidents(filter):
    """
        Get all incidents as DataFrame.
        Takes filter: str as parameter and filters incidents
    """
    conn = connect_database()
    query = GetIncidentsQuery(filter)
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df


def TotalIncidents(filter: str) -> int:
    conn = connect_database()
    query = GetIncidentsQuery(filter)
    totalInc = pd.read_sql_query(query, conn)
    
    return len(totalInc)


def TransferCSV():
    import csv
    from pathlib import Path
    conn = connect_database()
    cursor = conn.cursor()
    with open(Path("DATA/cyber_incidents.csv")) as itFile:
        reader = csv.reader(itFile)
        header: bool = True
        for row in reader:
            if header == True:
                header = False
                continue
            cursor.execute("INSERT INTO Cyber_Incidents (id, incident_type, severity, status, date) VALUES (?, ?, ?, ?, ?)", (row[0], row[1], row[2], row[3], row[4]))

    conn.commit()
    conn.close()