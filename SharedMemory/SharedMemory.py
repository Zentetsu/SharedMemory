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
2021-10-17  Zen Encoding data and adding basic methods
'''

from ctypes import c_byte
from datetime import date
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
_TUPLE = 0x6
_NPARRAY = 0x7

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

    def restart(self):
        self.__initSharedMemory()

    def close(self):
        if self.__mapfile is not None:
            self.__mapfile.close()
            self.__mapfile = None

        if self.__memory is not None:
            posix_ipc.unlink_shared_memory(self.__name)
            self.__memory = None

        self.__availability = False
        self.__state = "Stopped"

    def exportToJSON(self):
        pass

    def setValue(self, value):
        if not self.__availability:
            print("TODO: not available")
            return None

        if not self.__checkValue(type(value)):
            print("TODO")
            return 0

        __data = self.__encoding(value)

        self.__mapfile.seek(0)

        for d in __data:
            self.__mapfile.write_byte(d)

    def getValue(self):
        if not self.__availability:
            print("TODO: not available")
            return None

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

        self.__value == decoded_data

        return decoded_data

    def getType(self):
        return self.__type

    def getStatus(self):
        return self.__state

    def getAvailability(self):
        return self.__availability

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
        self.__availability = True
        self.__state = "Running"

        self.setValue(self.__value)

    def __checkValue(self, v_type: type):
        if v_type != self.__type:
            return False

        return True

    def __encoding(self, value):
        data = [_BEGIN]

        if type(value) == int or type(value) == float:
            if type(value) == float:
                value = int("0b" + self.__convertFlaot2Bin(value), 2)
                data.append(_FLOAT)
            else:
                data.append(_INT)

            data.append(8)
            data.append((0xFF00000000000000 & value) >> 56)
            data.append((0xFF000000000000 & value) >> 48)
            data.append((0xFF0000000000 & value) >> 40)
            data.append((0xFF00000000 & value) >> 32)
            data.append((0xFF000000 & value) >> 24)
            data.append((0xFF0000 & value) >> 16)
            data.append((0xFF00 & value) >> 8)
            data.append((0xFF & value) >> 0)

        elif type(value) == str:
            data.append(_STR)
            data.append(9)

            str_encoded = int(value.encode('utf-8').hex(), 16)
            data.append((0xFF0000000000000000 & str_encoded) >> 64)
            data.append((0xFF00000000000000 & str_encoded) >> 56)
            data.append((0xFF000000000000 & str_encoded) >> 48)
            data.append((0xFF0000000000 & str_encoded) >> 40)
            data.append((0xFF00000000 & str_encoded) >> 32)
            data.append((0xFF000000 & str_encoded) >> 24)
            data.append((0xFF0000 & str_encoded) >> 16)
            data.append((0xFF00 & str_encoded) >> 8)
            data.append((0xFF & str_encoded) >> 0)

        elif type(value) == list or type(value) == tuple:
            if type(value) == list:
                data.append(_LIST)
            else:
                data.append(_TUPLE)

            data.append(0)

            for i in value:
                data.extend(self.__encoding(i)[1:-1])

            data[2] = len(data) - 3

        elif type(value) == dict:
            data.append(_DICT)
            data.append(0)

            for k in value:
                data.extend(self.__encoding(k)[1:-1])
                data.extend(self.__encoding(value[k])[1:-1])

            data[2] = len(data) - 3

        data.append(_END)

        return data

    def __decoding(self, e_data):
        d_data = 0

        if e_data[0] == _INT or e_data[0] == _FLOAT:
            d_data = (e_data[2] << 56) + \
                     (e_data[3] << 48) + \
                     (e_data[4] << 40) + \
                     (e_data[5] << 32) + \
                     (e_data[6] << 24) + \
                     (e_data[7] << 16) + \
                     (e_data[8] << 8) + \
                     (e_data[9] << 0)

            if e_data[0] == _FLOAT:
                d_data = self.__convertBin2Flaot(bin(d_data))

        elif e_data[0] == _STR:
            d_data = (e_data[2] << 64) + \
                     (e_data[3] << 56) + \
                     (e_data[4] << 48) + \
                     (e_data[5] << 40) + \
                     (e_data[6] << 32) + \
                     (e_data[7] << 24) + \
                     (e_data[8] << 16) + \
                     (e_data[9] << 8) + \
                     (e_data[10] << 0)
            d_data = bytearray.fromhex(hex(d_data)[2:]).decode()

        elif e_data[0] == _LIST or e_data[0] == _TUPLE:
            e_data = e_data[2:]
            d_data = []
            c_type = e_data[0]

            while len(e_data) != 0:
                new_data = e_data[:2+e_data[1]]
                e_data = e_data[2+e_data[1]:]
                d_data.append(self.__decoding(new_data))

            if c_type == _TUPLE:
                d_data = tuple(d_data)

        elif e_data[0] == _DICT:
            e_data = e_data[2:]
            d_data = {}

            while len(e_data) != 0:
                new_key = e_data[:2+e_data[1]]
                e_data = e_data[2+e_data[1]:]
                new_data = e_data[:2+e_data[1]]
                e_data = e_data[2+e_data[1]:]
                d_data[self.__decoding(new_key)] = self.__decoding(new_data)

        return d_data

    def __convertBin2Flaot(self, b):
        h = int(b, 2).to_bytes(8, byteorder="big")
        return struct.unpack('>d', h)[0]

    def __convertFlaot2Bin(self, f):
        [d] = struct.unpack(">Q", struct.pack(">d", f))
        return f'{d:064b}'

    def __getitem__(self, key):
        if not self.__availability:
            print("TODO: not available")
            return None

        self.__value = self.getValue()

        if self.__type == dict:
            if type(key) is int:
                key = str(key)
            return self.__value[key]
        elif self.__type == list:
            return self.__value[key]
        else:
            return self.__value

    def __setitem__(self, key, value):
        if not self.__availability:
            print("TODO: not available")
            return None

        if self.__type == list:
            if self.__log is not None:
                print("TODO: log")
                # self.__writeLog(1, "Data shared type is list not dict.")
            else:
                print("INFO: Data shared type is list not dict.")
            raise TypeError("Data shared type is list not dict.")

        self.__value = self.getValue()

        if type(key) is int:
            key = str(key)

        if self.__type == dict:
            if type(key) is int:
                key = str(key)
            self.__value[key] = value
        elif self.__type == list:
            self.__value[key] = value
        else:
            self.__value = value

        if sys.getsizeof(self.__value) > self.__size:
            raise SMSizeError

        self.setValue(self.__value)

    def __len__(self):
        if not self.__availability:
            print("TODO: not available")
            return None

        self.__value = self.getValue()

        return self.__value.__len__()

    def __contains__(self, key):
        if not self.__availability:
            print("TODO: not available")
            return None

        self.__value = self.getValue()

        return self.__value.__contains__(key)

    def __delitem__(self, key):
        if not self.__availability:
            print("TODO: not available")
            return None

        self.__value = self.getValue()

        self.__value.__delitem__(key)

        self.setValue(self.__value)

    def __repr__(self):
        s = "Client: " + str(self.__name) + "\n"\
            + "\tStatus: " + str(self.__state) + "\n"\
            + "\tAvailable: " + self.__availability.__repr__() + "\n"\
            + "\tValue: " + self.__value.__repr__()

        return s

    def __initValueByJSON(self):
        pass

    def __writeLog(self):
        pass