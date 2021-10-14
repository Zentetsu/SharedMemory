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
2021-10-13  Zen Preparing new Shared Memory version
'''

from .SMError import SMMultiInputError, SMTypeError, SMSizeError, SMNotDefined
import posix_ipc
import struct
import json
import mmap
import sys
import os

_SHM_NAME_PREFIX = '/psm_'
_MODE = 0o600
_FLAG = posix_ipc.O_CREX

_BEGIN = 0xAA
_END = 0xBB

_INT = 0x0
_FLOAT = 0x1
_COMPLEX = 0x2
_STR = 0x3
_LIST = 0x4
_DICT = 0x5
_NPARRAY = 0x6

class SharedMemory:
    def __init__(self, name:str, value=None, size:int=8, exist=False):
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

    # def __checkValue(self, value):
    #     if value is str:
    #         value = " " * self.__size
    #     elif value is int:
    #         value = 0
    #     elif value is float:
    #         value = 0.0
    #     elif value is bool:
    #         value = False
    #     elif value is dict or value is list:
    #         raise SMTypeError(value)

    #     return
        # self.__semaphore.release()

    # def __del__(self):
    #     self.close()

    def exportToJSON(self):
        pass

    def setValue(self, value):
        if not self.__checkValue(type(value)):
            print("TODO")
            return 0

        __data = self.__prepareData(value)

        self.__mapfile.seek(0)

        for d in __data:
            self.__mapfile.write_byte(d)

    def getValue(self):
        encoded_data = []
        self.__mapfile.seek(0)

        encoded_data.append(self.__mapfile.read_byte())
        if encoded_data[0] != _BEGIN:
            print("B TODO")
            return 0

        encoded_data.append(self.__mapfile.read_byte())
        encoded_data.append(self.__mapfile.read_byte())

        for _ in range(0, encoded_data[2]):
            encoded_data.append(self.__mapfile.read_byte())

        encoded_data.append(self.__mapfile.read_byte())
        if encoded_data[len(encoded_data)-1] != _END:
            print("E TODO")
            return 0

        decoded_data = self.__decoding(encoded_data[1:len(encoded_data)-1])

        return 0

    def __checkValue(self, v_type: type):
        if v_type != self.__type:
            return False

        return True

    def __prepareData(self, value):
        data = [_BEGIN]
        if type(value) == int:
            data.insert(1, _INT)

            h = 0xFF & value
            data.insert(2, h)
            while h != 0:
                print(h)
                h = 0xFF & (h >> 8)
                data.insert(2, h)

            data.insert(2, len(data)-2)

        data.insert(len(data), _END)

        print([hex(i) for i in data])

        return data

    def __decoding(self, e_data):

        print([hex(i) for i in e_data])

        if e_data[0] == _INT:
            d_data = e_data[2:e_data[1]+2]

            print([hex(i) for i in d_data])
            value = d_data[0]
            for i in range(1, len(d_data)):
                value = value << 8 | d_data[i]

            print(value)

        return value

    # def __checkSize(self, value):
    #     if self.__type == int:
    #         pass

    #     return True

    def __repr__(self):
        s = "Client: " + str(self.__name) + "\n"\
            + "\tStatus: " + str(self.__state) + "\n"\
            + "\tAvailable: " + self.__availability.__repr__() + "\n"\
            + "\tValue: " + self.__value.__repr__()

        return s

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