class Dataset:
    def __init__(self, id: int, name: str, ctgry: str, sizeMB :float, source: str, lastUpd: str) -> None:
        self.__id: int = id
        self.__name: str = name
        self.__ctgry: str = ctgry
        self.__fileSize: float = sizeMB
        self.__source: str = source
        self.__lastUpd: str = lastUpd
    
    def CalcSizeB(self):
        return self.__fileSize * 1048576 #1MB = 1048576B (2^20)

    def __str__(self):
        return f"ID: {self.__id}, Name: {self.__name}, Category: {self.__ctgry}, File Size(MB): {self.__fileSize}, File Size (B): {self.CalcSizeB()}, Source: {self.__source}, Last Updated: {self.__lastUpd}"

    #Get Functions
    def GetID(self) -> int:
        return self.__id
    def GetName(self) -> str:
        return self.__name
    def GetCtgry(self) -> str:
        return self.__ctgry
    def GetFileSize(self) -> float:
        return self.__fileSize
    def GetSource(self) -> str:
        return self.__source
    def GetLastUpd(self) -> str:
        return self.__lastUpd
    def GetAll(self):
        return (self.__id, self.__name, self.__ctgry, self.__fileSize, self.__source, self.__lastUpd)