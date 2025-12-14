class User:
    def __init__(self, userName: str, passwdHash: str):
        self.__userName = userName
        self.__passwdHash = passwdHash
    
    
    def GetUserName(self):
        return self.__userName
    def GetPassHash(self):
        return self.__passwdHash
    
    
    def VerifyPasswd(self, plainText: str, hasher):
        return hasher.checkPasswd(plainText, self.__passwdHash)
    
    
    def __str__(self):
        return f"Username: {self.__userName}"