class Incident:
    def __init__(self, id: int, incType: str, severity: str, status: str, createdDate: str) -> None:
        self.__id = id
        self.__inc = incType
        self.__sev = severity
        self.__status = status
        self.__crDate = createdDate
    
    
    def __str__(self):
        return f"ID: {self.__id}, Incident Type: {self.__inc}, Severity: {self.__sev}, Status: {self.__status}, Created Date: {self.__crDate}"
    
        
    #Get Functions
    def GetID(self) -> int:
        return self.__id
    def GetIncident(self) -> str:
        return self.__inc
    def GetSev(self) -> str:
        return self.__sev
    def GetStatus(self) -> str:
        return self.__status
    def GetCrDate(self) -> str:
        return self.__crDate
    def GetAll(self):
        return (self.__id, self.__inc, self.__sev, self.__status, self.__crDate)