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


def GetAllIncident():
    """Get all incidents as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


def TotalIncidents() -> int:
    conn = connect_database()
    query: str = "SELECT * FROM Cyber_Incidents"
    totalInc = pd.read_sql_query(query, conn)
    
    return len(totalInc)