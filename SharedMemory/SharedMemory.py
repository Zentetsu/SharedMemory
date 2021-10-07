from abc import ABC, abstractmethod
 
class SharedMemory(ABC):
    @abstractmethod
    def __init__(self):
        pass
    
    def exportToJSON(self):
        pass
    
    def getValue(self):
        pass
    
    def getType(self):
        pass
    
    def updateValue(self):
        pass
    
    def getStatus(self):
        pass
    
    def getAvailability(self):
        pass
    
    def close(self):
        pass
    
    def unlink(self):
        pass
    
    def start(self):
        pass
    
    def restart(self):
        pass
    
    def stop(self):
        pass
    
    def __initValueByJSON(self):
        pass
    
    def __checkServerAvailability(self):
        pass
    
    def __writeLog(self):
        pass
    
    def __getitem__(self):
        pass
    
    def __setitem__(self):
        pass
    
    def __len__(self):
        pass
    
    def __contains__(self):
        pass
    
    def __delitem__(self):
        pass

    def __repr__(self):
        pass  