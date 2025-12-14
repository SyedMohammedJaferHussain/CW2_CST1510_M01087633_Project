from app.services.auth_manager import AuthManager
from app.services.database_manager import DatabaseManager
from pathlib import Path
from models.users import User
import pickle


def LoginUser(username: str, password: str):
    dbMgr = DatabaseManager(str(Path("DATA") / "intelligence_platform.db"))
    authMgr = AuthManager(dbMgr)
    loginResult = authMgr.LoginUser(username, password)
    if loginResult == True:
        return True
    return False


def RegisterUser(username: str, password: str, confPass: str):
    users: list[User] = GetUsers()
    dbMgr = DatabaseManager(str(Path("DATA") / "intelligence_platform.db"))
    authMgr = AuthManager(dbMgr)
    registerResult: tuple = authMgr.RegisterUser(username, password, confPass)
    if registerResult[0] == True:
        users.append(registerResult[1])
        WriteUsers(users)
        return None
    else:
        return registerResult[1]


def WriteUsers(users: list[User]):
    """
        Args:
            tickets (list[User]): Contains all tickets in users.bin
    """    
    with open(Path("DATA") / "users.bin", "wb") as usersObjs:
        pickle.dump(users, usersObjs)
        

def Commit():
    """
        Explanation:
            Commits all changes made to tickets after logging out
            Iterates through every ticket and adds ticket to IT_Tickets in intelligence_platform.db
    """
    users: list[User] = GetUsers()
    dbMgr = DatabaseManager(str(Path("DATA") / "intelligence_platform.db"))
    dbMgr.Exec("DELETE FROM Users")
    for user in users:
        dbMgr.Exec("INSERT INTO IT_Tickets (username, password_hash) VALUES (?, ?)", (user.GetUserName(), user.__passwdHash) )
    
    dbMgr.Close()


def TransferFromDB():
    """
        Gets all rows from Users and creates a list of User
        Returns: users (_list[User]_): List containing all tickets in database
    """
    dbMgr = DatabaseManager(str(Path("DATA") / "intelligence_platform.db"))
    df = dbMgr.FetchAll("SELECT * FROM Users")
    users: list[User] = []
    userName: list[str] = df["username"].tolist()
    passHash: list[str] = df["password_hash"].tolist()
    for i in range(len(df)):
        user: User = User(userName[i], passHash[i])
        users.append(user)
    
    return users


def GetUsers() -> list[User]:
    """
        Explanation:
            Uses pickle module to read(Deserialise) tickets.bin containing tickets
        Returns: 
            tickets (list[ITTicket]): Contains all tickets
    """
    with open(Path("DATA") / "users.bin", "rb") as usersObjs:
        users = pickle.load(usersObjs) 
    return users