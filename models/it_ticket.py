class ITTicket:
    def __init__(self, tid: int, sub: str, prio: str, status: str, createdDate: str) -> None:
        self.__tid = tid
        self.__sub = sub
        self.__prio = prio
        self.__status = status
        self.__crDate = createdDate
    
    
    def __str__(self):
        return f"ID: {self.__tid}, Subject: {self.__sub}, Priority: {self.__prio}, Status: {self.__status}, Created Date: {self.__crDate}"
    
        
    #Get Functions
    def GetID(self) -> int:
        return self.__tid
    def GetSub(self):
        return self.__sub
    def GetPrio(self):
        return self.__prio
    def GetStatus(self):
        return self.__status
    def GetCrDate(self):
        return self.__crDate
    def GetAll(self):
        return (self.__tid, self.__sub, self.__prio, self.__status, self.__crDate)