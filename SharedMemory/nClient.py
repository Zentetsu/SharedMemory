from SMError import SMMultiInputError, SMTypeError, SMSizeError, SMNotDefined
from SharedMemory import SharedMemory
import posix_ipc
import json
import mmap
import sys
import os
 
_SHM_NAME_PREFIX = '/psm_'
_MODE = 0o600
_FLAG = posix_ipc.O_CREX
 
class nClient(SharedMemory):
    def __init__(self, name:str, value=None, size:int=10, exist=False):
        if value is None:
            raise SMMultiInputError
 
        self.__name = _SHM_NAME_PREFIX + name
        self.__value = value
        self.__size = size
        self.__exist = exist
        self.__type = type(value)
 
        self.__state = "Stopped"
        self.__availability = False
 
        self.__initSharedMemory()

    def close(self):
        self.__mapfile.close()
        posix_ipc.unlink_shared_memory(self.__name)
    
    def __initSharedMemory(self):
        if type(self.__value) is list and type in [type(e) for e in self.__value]:
            for i in range(0, len(self.__value)):
                self.__value[i] = self.__checkValue(self.__value[i])
 
        self.__size = sys.getsizeof(self.__value)
        self.__memory = None
        self.__mapfile = None
 
        try:
            self.__memory = posix_ipc.SharedMemory(self.__name, _FLAG, _MODE)
            os.ftruncate(self.__memory.fd, self.__size)
            # self.__semaphore = posix_ipc.Semaphore(self.__name, posix_ipc.O_CREX)
        except posix_ipc.ExistentialError:
            if not self.__exist:
                print("TODO")
                exit(1)

            self.__memory = posix_ipc.SharedMemory(self.__name)

        self.__mapfile = mmap.mmap(self.__memory.fd, self.__size)
        # self.__semaphore.release()      
 
    def __checkValue(self, value):
        if value is str:
            value = " " * self.__size
        elif value is int:
            value = 0
        elif value is float:
            value = 0.0
        elif value is bool:
            value = False
        elif value is dict or value is list:
            raise SMTypeError(value)
 
        return value

    def __repr__(self):
        s = "Client: " + str(self.__name) + "\n"\
            + "\tStatus: " + str(self.__state) + "\n"\
            + "\tAvailable: " + self.__availability.__repr__() + "\n"\
            + "\tValue: " + self.__value.__repr__()

        return s