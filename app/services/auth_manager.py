from models.users import User
from app.services.database_manager import DatabaseManager
import bcrypt


class Hasher:
    def HashPassword(self, plain: str) -> str:
        byteStr: bytes = plain.encode("utf-8")
        salt: bytes = bcrypt.gensalt()
        return bcrypt.hashpw(byteStr, salt).decode("utf-8")


    def CheckPassword(self, plain: str, hashed: str) -> bool:
        textBytes: bytes = plain.encode("utf-8")
        pWBytes: bytes = hashed.encode("utf-8")

        if bcrypt.checkpw(textBytes, pWBytes):
            return True
        
        return False


class AuthManager:
    """Handles user registration and login."""
    def __init__(self, db: DatabaseManager):
        self._db = db
    

    def RegisterUser(self, username: str, password: str, confPassword: str):
        hasher = Hasher()
        
        #Validate username and password
        userValid = self.__ValidateUserName(username)
        passValid = self.__ValidatePassWd(password, confPassword)
        errorMsg: str = ""
        if not userValid[0]: 
            errorMsg += userValid[1]
        if not passValid[0]:
            errorMsg += passValid[1]
        
        if errorMsg:
            return False, errorMsg #Registration did not happen

        password_hash = hasher.HashPassword(password)
        self._db.Exec("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        return True, User(username, password_hash)


    def LoginUser(self, username: str, password: str) -> bool:
        """
            Returns True if password is correct, False if incorrect
        """
        hasher = Hasher()
        row = self._db.FetchOne( "SELECT username, password_hash FROM users WHERE username = ?", (username,))
        if row is None:
            return False

        password_hash_db = row[1]
        if hasher.CheckPassword(password, password_hash_db):
            return True
        
        return False


    def __ValidateUserName(self, userName: str) -> tuple:
        """
            Validates username using various crtieria
            Returns: Tuple with bool and string containing error message for wrong username
        """
        criteria: dict[bool, str] = {len(userName) <= 20 and len(userName) >= 3: "Length should be between 3 and 21", userName.isalnum(): "Username can consist of alphanumeric characters only"}
        validated: bool = True
        errorMsg: str = ""
        for condition in criteria:
            if not condition:
                validated = False
                errorMsg += criteria[condition] + "\n"
                
        return (False, errorMsg) if not validated else (True, "")


    def __ValidatePassWd(self, passWd: str, confPWrd: str) -> tuple:
        """
            Validates passWd using various crtieria
            Returns: Tuple with bool and string containing error message for wrong password
        """
        criteria: dict[bool, str] = {len(passWd) <= 51 and len(passWd) >= 6 : "Length should be between 6 and 50", "_"  in passWd or "@" in passWd: "Must contain special characters", passWd == confPWrd: "Passwords do not match"}
        validated: bool = True
        errorMsg: str = ""
        for condition in criteria:
            if not condition:
                validated = False
                errorMsg += criteria[condition] + "\n"
                
        return (False, errorMsg) if not validated else (True, "")