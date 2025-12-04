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


def GetAllIncidents(filter: str):
    """
        Get all incidents as DataFrame.
        Takes filter: str as parameter and filters incidents
    """
    conn = connect_database()
    df = pd.read_sql_query(
        f"SELECT * FROM cyber_incidents ORDER BY id DESC WHERE {filter}",
        conn
    )
    conn.close()
    return df


def TotalIncidents(filter: str) -> int:
    conn = connect_database()
    query: str = f"SELECT * FROM Cyber_Incidents WHERE {filter}"
    totalInc = pd.read_sql_query(query, conn)
    
    return len(totalInc)