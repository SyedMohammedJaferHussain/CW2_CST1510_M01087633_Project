def CreateUsersTable(conn):
    """Create users table."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)
    conn.commit()
    

def CreateCyberIncidentsTable(conn):
    """
    Create the cyber_incidents table.
    """
    
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            incident_type TEXT,
            severity TEXT,
            status TEXT,
            description TEXT,
            reported_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    print("SUCCCESS")


def CreateDatasetsMetadataTable(conn):
    """
    Create the datasets_metadata table.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_name TEXT NOT NULL,
            category: TEXT,
            source: TEXT,
            last_updated: TEXT,
            record_count INTEGER,
            file_size_mb REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def CreateITTicketsTable(conn):
    """
    Create the it_tickets table.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id: INTEGER PRIMARY KEY AUTOINCREMENT
            ticket_id: TEXT UNIQUE NOT NULL
            priority: TEXT 
            status: TEXT 
            category: TEX
            subject: TEXT NOT NULL
            description: TEXT
            created_date: TEXT
            resolved_date: TEXT
            assigned_to: TEXT
            created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()



def create_all_tables(conn):
    """Create all tables."""
    CreateUsersTable(conn)
    CreateCyberIncidentsTable(conn)
    CreateDatasetsMetadataTable(conn)
    CreateITTicketsTable(conn)