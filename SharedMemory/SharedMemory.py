'''
File: SharedMemory.py
Created Date: Thursday, October 7th 2021, 8:37:52 pm
Author: Zentetsu

----

Last Modified: Sun Oct 24 2021
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
2021-10-17  Zen Encoding data and adding basic methods + export and import JSON file
2021-10-19	Zen	Adding comment and logging
2021-10-20	Zen	Adjusting some behavior
2021-10-21	Zen	Adjusting close and restart methods
'''

from abc import ABC, abstractmethod
from .SMError import SMMultiInputError, SMTypeError, SMSizeError, SMNotDefined, SMAlreadyExist, SMEncoding
import posix_ipc
import logging
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
_CLOSED = 0xAB

_INT = 0x0
_FLOAT = 0x1
_BOOL = 0x2
_COMPLEX = 0x3
_STR = 0x4
_LIST = 0x5
_DICT = 0x6
_TUPLE = 0x7
_NPARRAY = 0x8

class SharedMemory:
    """Shared Memory class
    """
    def __init__(self, name:str, value=None, path:str=None, size:int=8, exist:bool=False, log:str=None):
        """Class constructor

        Args:
            name (str): desired name for the sharing space
            value ([type], optional): value to share with the other Server. Defaults to None.
            path (str, optional): path to load JSON file and sharing data inside. Defaults to None.
            size (int, optional): size of the shared space or str value. Defaults to 10.
            exist (bool, optional): will authorize to access to an existing shared memory space
            timeout (int, optional): mutex timeout. Defaults to 1.

        Raises:
            SMMultiInputError: raise an error when value and path are both at None or initialized
        """
        self.__log = log

        if value is None and path is None and not exist or value is not None and path is not None:
            if self.__log is not None:
                self.__writeLog(1, "Conflict between value and json path intialization.")

            raise SMMultiInputError
        elif value is None and path is not None:
            self.__value = self.__initValueByJSON(path)
        else:
            self.__value = value
            self.__size = size

        self.__name = _SHM_NAME_PREFIX + name
        self.__type = type(self.__value)
        self.__exist = exist

        self.__initSharedMemory()

    def restart(self):
        """Method to restart the shared memory space
        """
        if not self.__client:
            if self.__log is not None:
                self.__writeLog(3, "Only client can restart Shared Memory space.")
            else:
                print("WARNING: Only client can restart Shared Memory space.")

            return

        if self.getAvailability():
            if self.__log is not None:
                self.__writeLog(0, "Client already running.")
            else:
                print("INFO: Client already running.")

            return

        self.__initSharedMemory()

    def close(self):
        """Method to close the shared space
        """
        if not self.getAvailability():
            if self.__log is not None:
                self.__writeLog(0, "Client already stopped.")
            else:
                print("INFO: Client already stopped.")

            return

        if self.__mapfile is not None:
            self.__mapfile.seek(0)

            self.__mapfile.write_byte(_BEGIN)
            self.__mapfile.write_byte(_CLOSED)
            self.__mapfile.write_byte(_END)

            self.__mapfile.close()
            self.__mapfile = None

        if self.__memory is not None:
            try:
                posix_ipc.unlink_shared_memory(self.__name)
            except:
                if self.__log:
                    self.__writeLog(0, "SharedMemory already closed.")

            self.__memory = None

    def setValue(self, value) -> bool:
        """Method to set the shared value

        Args:
            value ([type]): data to add to the shared memory

        Returns:
            bool: return if value has been updated
        """
        if not self.getAvailability():
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            else:
                print("ERROR: Shared Memory space doesn't exist.")

            return False

        if not self.__checkValue(type(value)):
            raise SMTypeError()

        __data = self.__encoding(value)

        self.__mapfile.seek(0)

        for d in __data:
            self.__mapfile.write_byte(d)

        return True

    def getValue(self):
        """Method to return the shared value

        Returns:
            [type]: return data from the shared space
        """
        if not self.getAvailability():
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            else:
                print("ERROR: Shared Memory space doesn't exist.")

            return None

        encoded_data = []
        self.__mapfile.seek(0)

        encoded_data.append(self.__mapfile.read_byte())
        if encoded_data[0] != _BEGIN:
            raise SMEncoding("BEGIN")

        encoded_data.append(self.__mapfile.read_byte())

        if encoded_data[1] == _CLOSED:
            raise SMEncoding("CLOSED")

        encoded_data.append(self.__mapfile.read_byte())

        for _ in range(0, encoded_data[2]):
            encoded_data.append(self.__mapfile.read_byte())

        encoded_data.append(self.__mapfile.read_byte())
        if encoded_data[len(encoded_data)-1] != _END:
            raise SMEncoding("END")

        decoded_data = self.__decoding(encoded_data[1:len(encoded_data)-1])

        self.__value == decoded_data

        return decoded_data

    def getType(self):
        """Method that returns data type

        Returns:
            [type]: data type
        """
        return self.__type

    def getAvailability(self) -> bool:
        """Method that return the availability of Shared Memory

        Returns:
            bool: Shared Memory availability status
        """
        if self.__memory is None and self.__mapfile is None and not self.__client:
            try:
                self.__initSharedMemory()
            except:
                return False

        try:
            encoded_data = []
            self.__mapfile.seek(0)

            encoded_data.append(self.__mapfile.read_byte())
            encoded_data.append(self.__mapfile.read_byte())
            encoded_data.append(self.__mapfile.read_byte())

            return encoded_data != [_BEGIN, _CLOSED, _END]
        except:
            return False

    def exportToJSON(self, path:str):
        """Method to export dict to JSON file

        Args:
            path (str): file path
        """
        if self.__type is not dict:
            if self.__log is not None:
                self.__writeLog(1, "Data type must be dict.")

            raise TypeError("Data type must be dict.")

        file = open(path, 'w+')
        json.dump(self.getValue(), file)
        file.close()

    def __initSharedMemory(self):
        """Method to initialize the shared space
        """
        self.__size = sys.getsizeof(self.__value)
        self.__memory = None
        self.__mapfile = None

        if not self.__exist:
            try:
                self.__memory = posix_ipc.SharedMemory(self.__name, _FLAG, _MODE)
                os.ftruncate(self.__memory.fd, self.__size)
            except posix_ipc.ExistentialError:
                if self.__value is not None:
                    self.__memory = posix_ipc.SharedMemory(self.__name)
                else:
                    self.close()
                    raise SMAlreadyExist(self.__name)

            self.__client = True
        else:
            try:
                self.__memory = posix_ipc.SharedMemory(self.__name)
            except posix_ipc.ExistentialError:
                self.close()
                raise SMNotDefined(self.__name)

            self.__client = False

        self.__mapfile = mmap.mmap(self.__memory.fd, self.__size)

        if not self.__exist:
            self.setValue(self.__value)
        else:
            self.__value = self.getValue()
            self.__type = type(self.__value)

    def __checkValue(self, value:type):
        """Method to check value type

        Args:
            value ([type]): value to test

        Raises:
            SMTypeError: raise an error when the value is a dict or a list

        Returns:
            [type]: return the initialized value
        """
        if value != self.__type:
            raise SMTypeError(value)

        return True

    def __encoding(self, value):
        """Method to encode value

        Args:
            value ([type]): data to encode
        """
        data = [_BEGIN]

        if type(value) == int or type(value) == float:
            if type(value) == float:
                value = int("0b" + self.__convertFloat2Bin(value), 2)
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

        elif type(value) == bool:
            data.append(_BOOL)
            data.append(1)
            data.append(0xFF & value)

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

    def __decoding(self, value):
        """Method to decode value

        Args:
            value ([type]): data to decode
        """
        d_data = 0

        if value[0] == _INT or value[0] == _FLOAT:
            d_data = (value[2] << 56) + \
                     (value[3] << 48) + \
                     (value[4] << 40) + \
                     (value[5] << 32) + \
                     (value[6] << 24) + \
                     (value[7] << 16) + \
                     (value[8] << 8) + \
                     (value[9] << 0)

            if value[0] == _FLOAT:
                d_data = self.__convertBin2Float(bin(d_data))

        elif value[0] == _BOOL:

            d_data = bool(value[2])

        elif value[0] == _STR:
            d_data = (value[2] << 64) + \
                     (value[3] << 56) + \
                     (value[4] << 48) + \
                     (value[5] << 40) + \
                     (value[6] << 32) + \
                     (value[7] << 24) + \
                     (value[8] << 16) + \
                     (value[9] << 8) + \
                     (value[10] << 0)
            d_data = bytearray.fromhex(hex(d_data)[2:]).decode()

        elif value[0] == _LIST or value[0] == _TUPLE:
            value = value[2:]
            d_data = []
            c_type = value[0]

            while len(value) != 0:
                new_data = value[:2+value[1]]
                value = value[2+value[1]:]
                d_data.append(self.__decoding(new_data))

            if c_type == _TUPLE:
                d_data = tuple(d_data)

        elif value[0] == _DICT:
            value = value[2:]
            d_data = {}

            while len(value) != 0:
                new_key = value[:2+value[1]]
                value = value[2+value[1]:]
                new_data = value[:2+value[1]]
                value = value[2+value[1]:]
                d_data[self.__decoding(new_key)] = self.__decoding(new_data)

        return d_data

    def __convertBin2Float(self, value:int) -> float:
        """Method to convert value to float

        Args:
            value (int): data to convert

        Returns:
            float: data converted
        """
        h = int(value, 2).to_bytes(8, byteorder="big")

        return struct.unpack('>d', h)[0]

    def __convertFloat2Bin(self, value:float) -> int:
        """Method to convert value to bin

        Args:
            value (float): data to convert

        Returns:
            int: data converted
        """
        [d] = struct.unpack(">Q", struct.pack(">d", value))

        return f'{d:064b}'

    def __initValueByJSON(self, path:str) -> dict:
        """Method to extract value from a JSON file

        Args:
            path (str): path to the JSON file

        Returns:
            dict: return  data from JSON file
        """
        json_file = open(path)
        value = json.load(json_file)
        json_file.close()

        return value

    def __writeLog(self, log_id:int, message:str):
        """Write information into a log file

        Args:
            log_id (int): log id
            message (str): message to write into the log file
        """
        if log_id == 0:
            logging.info(message)
        elif log_id == 1:
            logging.error(message)
        elif log_id == 2:
            logging.debug(message)
        elif log_id == 3:
            logging.warning(message)

    def __getitem__(self, key):
        """Method to get item value from the shared data

        Args:
            key ([type]): key

        Raises:
            TypeError: raise an error when this method is called and tha data shared type is not a dict
        """
        if not self.getAvailability():
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            else:
                print("ERROR: Shared Memory space doesn't exist.")

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
        """Method to update data of the shared space

        Args:
            key (str): key
            value ([type]): new key value

        Raises:
            TypeError: raise an error when this method is called and tha data shared type is not a dict
        """
        if not self.getAvailability():
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            else:
                print("ERROR: Shared Memory space doesn't exist.")

            return None

        if self.__type == list:
            if self.__log is not None:
                self.__writeLog(1, "Data shared type is list not dict.")

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

    def __len__(self) -> int:
        """Method that returns the size of the shared data

        Returns:
            int: size of the shared data

        Raises:
            TypeError: raise an error when this method is called and tha data shared type is not a dict
        """
        if not self.getAvailability():
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            else:
                print("ERROR: Shared Memory space doesn't exist.")

            return None

        self.__value = self.getValue()

        return self.__value.__len__()

    def __contains__(self, key) -> bool:
        """Method to check if an element is into the shared data

        Args:
            key ([type]): Element to find

        Returns:
            bool: boolean to determine if the element is or not into the shared data

        Raises:
            TypeError: raise an error when this method is called and tha data shared type is not a dict
        """
        if not self.getAvailability():
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            else:
                print("ERROR: Shared Memory space doesn't exist.")

            return None

        self.__value = self.getValue()

        return self.__value.__contains__(key)

    def __delitem__(self, key):
        """Method to remove an element from the shared data

        Args:
            key ([type]): Element to remove

        Raises:
            TypeError: raise an error when this method is called and tha data shared type is not a dict
        """
        if not self.getAvailability():
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            else:
                print("ERROR: Shared Memory space doesn't exist.")

            return None

        self.__value = self.getValue()

        self.__value.__delitem__(key)

        self.setValue(self.__value)

    def __repr__(self):
        """Redefined method to print value of the Client Class instance

        Returns:
            str: printable value of Client Class instance
        """
        s = "Client: " + str(self.__name) + "\n"\
            + "\tAvailable: " + self.getAvailability().__repr__() + "\n"\
            + "\tValue: " + self.__value.__repr__()

        return s

    @staticmethod
    def getSharedMemorySpace():
        if os.name == "Windows" or os.name == "Darwin":
            print("Not yet implemented.")

            return

        return next(os.walk("/dev/shm/"), (None, None, []))[2]