'''
File: SharedMemory.py
Created Date: Thursday, October 7th 2021, 8:37:52 pm
Author: Zentetsu

----

Last Modified: Wed Oct 13 2021
Modified By: Zentetsu

----

Project: SharedMemory
Copyright (c) 2020 Zentetsu

----

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

----

HISTORY:
2021-10-13	Zen Preparing new Shared Memory version
'''

from .SMError import SMMultiInputError, SMTypeError, SMSizeError, SMNotDefined
import posix_ipc
import json
import mmap
import sys
import os

_SHM_NAME_PREFIX = '/psm_'
_MODE = 0o600
_FLAG = posix_ipc.O_CREX

_BEGIN = 0xF0
_END = 0x0F

_INT = 0x0
_FLOAT = 0x1
_COMPLEX = 0x2
_STR = 0x3
_LIST = 0x4
_DICT = 0x5
_NPARRAY = 0x6

class SharedMemory:
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
        if self.__mapfile is not None:
            self.__mapfile.close()
            self.__mapfile = None

        if self.__memory is not None:
            posix_ipc.unlink_shared_memory(self.__name)
            self.__memory = None

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

        return
        # self.__semaphore.release()

    def __repr__(self):
        s = "Client: " + str(self.__name) + "\n"\
            + "\tStatus: " + str(self.__state) + "\n"\
            + "\tAvailable: " + self.__availability.__repr__() + "\n"\
            + "\tValue: " + self.__value.__repr__()

        return s

    # def __del__(self):
    #     self.close()

    def exportToJSON(self):
        pass

    def setValue(self, value):
        self.__mapfile.seek(0)
        self.__mapfile.write_byte(0xF0)

        if type(value) is int:
            self.__mapfile.write_byte(0x02)
            self.__mapfile.write_byte(_INT)
            self.__mapfile.write_byte(value)

        self.__mapfile.write_byte(0x0F)

    def getValue(self):
        self.__mapfile.seek(0)
        __begin = self.__mapfile.read_byte()

        if __begin != _BEGIN:
            return 0

        __size = self.__mapfile.read_byte()

        data = __begin << 8 | __size
        __current_data = __begin
        for _ in range(0, __size):
            __current_data = self.__mapfile.read_byte()
            data = data << 8 | __current_data

        __end = self.__mapfile.read_byte()
        if __end != _END:
            return 0

        data = data << 8 | __end

        return data

    def getType(self):
        pass

    def updateValue(self):
        pass

    def getStatus(self):
        pass

    def getAvailability(self):
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