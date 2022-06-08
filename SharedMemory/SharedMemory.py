'''
File: SharedMemory.py
Created Date: Thursday, October 7th 2021, 8:37:52 pm
Author: Zentetsu

----

Last Modified: Thu Dec 16 2021
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
2021-11-24	Zen	SharedMemory init size fixed
2021-11-25	Zen	Changing Server behavior
2021-11-26	Zen	Fix int and dict encoding
2021-11-27	Zen	Fix getValue behavior
2021-11-27	Zen	Adding semaphore
'''

from abc import ABC, abstractmethod
from .SMError import SMMultiInputError, SMTypeError, SMSizeError, SMNotDefined, SMAlreadyExist, SMEncoding
import posix_ipc
import logging
import struct
import time
import json
import mmap
import sys
import os

_SHM_NAME_PREFIX = '/psm_'
_SEM_NAME_PREFIX = '/sem_'

_MODE = 0o600
_FLAG = posix_ipc.O_CREX | os.O_RDWR

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
    def __init__(self, name:str, value=None, path:str=None, size:int=8, client:bool=False, log:str=None, sleep:float=0):
        """Class constructor

        Args:
            name (str): desired name for the sharing space
            value ([type], optional): value to share with the other Server. Defaults to None.
            path (str, optional): path to load JSON file and sharing data inside. Defaults to None.
            size (int, optional): size of the shared space or str value. Defaults to 10.
            client (bool, optional): will creat a client or server instance
            timeout (int, optional): mutex timeout. Defaults to 1.

        Raises:
            SMMultiInputError: raise an error when value and path are both at None or initialized
        """
        self.__log = log

        if self.__log is not None:
            f = open(os.devnull, 'w')
            sys.stdout = f

        if client and (value is None and path is None or value is not None and path is not None):
            if self.__log is not None:
                self.__writeLog(1, "Conflict between value and json path intialization.")

            raise SMMultiInputError
        elif client and value is None and path is not None:
            self.__value = self.__initValueByJSON(path)
        elif not client and (value is not None or path is not None):
            if self.__log is not None:
                self.__writeLog(1, "Conflict between value and json path intialization.")

            raise SMMultiInputError
        else:
            self.__value = value
            self.__size = size

        self.__name_memory = _SHM_NAME_PREFIX + name
        self.__name_semaphore = _SEM_NAME_PREFIX + name
        self.__type = type(self.__value)
        self.__client = client
        self.__sleep = sleep

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
                posix_ipc.unlink_shared_memory(self.__name_memory)

                self.__semaphore.release()
                self.__semaphore.unlink()
            except:
                if self.__log:
                    self.__writeLog(0, "SharedMemory already closed.")

            self.__memory = None
            self.__semaphore = None

    def setValue(self, value) -> bool:
        """Method to set the shared value

        Args:
            value ([type]): data to add to the shared memory

        Returns:
            bool: return if value has been updated
        """
        self.__semaphore.acquire(self.__sleep)

        if not self.getAvailability():
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            else:
                print("ERROR: Shared Memory space doesn't exist.")

            return False

        if not self.__checkValue(type(value)):
            raise SMTypeError()

        _data = self.__encoding(value)

        _packed = struct.pack('<%dI' % len(_data), *_data)

        self.__mapfile.seek(0)
        self.__mapfile.write(_packed)

        self.__semaphore.release()

        time.sleep(self.__sleep)

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

        try:
            self.__mapfile.seek(0)
            _packed = self.__mapfile.read()
            _encoded_data = list(struct.unpack('<%dI' % (len(_packed) // 4), _packed))
            _res = len(_encoded_data) - 1 - _encoded_data[::-1].index(_END)
            _encoded_data = _encoded_data[:_res+1]
        except:
            return None

        time.sleep(self.__sleep)

        if _encoded_data[0] != _BEGIN:
            raise SMEncoding("BEGIN")

        if _encoded_data[1] == _CLOSED:
            raise SMEncoding("CLOSED")
        elif _encoded_data[1] == _DICT:
            nb_element = [self.__decoding(_encoded_data[2:_encoded_data[3]+4])][0]
            _encoded_data = _encoded_data[:nb_element+5+_encoded_data[3]]
        else:
            nb_element = _encoded_data[2]
            _encoded_data = _encoded_data[:nb_element+4]

        if _encoded_data[len(_encoded_data)-1] != _END:
            raise SMEncoding("END")

        _decoded_data = self.__decoding(_encoded_data[1:len(_encoded_data)-1])

        self.__value == _decoded_data

        return _decoded_data

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
            _encoded_data = []
            self.__mapfile.seek(0)

            _encoded_data.append(self.__mapfile.read_byte())
            _encoded_data.append(self.__mapfile.read_byte())
            _encoded_data.append(self.__mapfile.read_byte())

            return _encoded_data != [_BEGIN, _CLOSED, _END]
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

        _file = open(path, 'w+')
        json.dump(self.getValue(), _file)
        _file.close()

    def __initSharedMemory(self):
        """Method to initialize the shared space
        """
        self.__size = sys.getsizeof(self.__encoding(self.__value))
        self.__memory = None
        self.__semaphore = None
        self.__mapfile = None

        if self.__client:
            try:
                self.__memory = posix_ipc.SharedMemory(self.__name_memory, _FLAG, _MODE)
                self.__semaphore = posix_ipc.Semaphore(self.__name_semaphore, _FLAG, _MODE)
                os.ftruncate(self.__memory.fd, self.__size)
            except posix_ipc.ExistentialError:
                if self.__value is not None:
                    self.__memory = posix_ipc.SharedMemory(self.__name_memory)
                    self.__semaphore = posix_ipc.Semaphore(self.__name_semaphore)
                else:
                    self.close()
                    raise SMAlreadyExist(self.__name_memory)

            self.__semaphore.release()
        else:
            try:
                self.__memory = posix_ipc.SharedMemory(self.__name_memory)
                self.__semaphore = posix_ipc.Semaphore(self.__name_semaphore)
                self.__size = self.__memory.size
            except posix_ipc.ExistentialError:
                if self.__log is not None:
                    self.__writeLog(3, "Memory space not yet created.")
                else:
                    print("WARNING: Memory space not yet created.")

                return

        self.__mapfile = mmap.mmap(self.__memory.fd, self.__size)

        if self.__client:
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
        _data = [_BEGIN]

        if type(value) == int:
            value = int("0b" + self.__convertIF2Bin(value, int), 2)
            _data.append(_INT)

            # nb = -(-value.bit_length() // 8)
            # if value == 0:
            #     nb = 1
            # dec = 0xFF << (8 * (nb-1))

            # _data.append(nb)

            # for i in range(nb-1, -1, -1):
            #     _data.append((dec & value) >> i*8)
            #     dec = dec >> 8

            _data.append(8)
            _data.append((0xFF00000000000000 & value) >> 56)
            _data.append((0xFF000000000000 & value) >> 48)
            _data.append((0xFF0000000000 & value) >> 40)
            _data.append((0xFF00000000 & value) >> 32)
            _data.append((0xFF000000 & value) >> 24)
            _data.append((0xFF0000 & value) >> 16)
            _data.append((0xFF00 & value) >> 8)
            _data.append((0xFF & value) >> 0)

        if type(value) == float:
            value = int("0b" + self.__convertIF2Bin(value, float), 2)
            _data.append(_FLOAT)

            _data.append(8)
            _data.append((0xFF00000000000000 & value) >> 56)
            _data.append((0xFF000000000000 & value) >> 48)
            _data.append((0xFF0000000000 & value) >> 40)
            _data.append((0xFF00000000 & value) >> 32)
            _data.append((0xFF000000 & value) >> 24)
            _data.append((0xFF0000 & value) >> 16)
            _data.append((0xFF00 & value) >> 8)
            _data.append((0xFF & value) >> 0)

        elif type(value) == bool:
            _data.append(_BOOL)
            _data.append(1)
            _data.append(0xFF & value)

        elif type(value) == str:
            _data.append(_STR)
            _data.append(9)

            str_encoded = int(value.encode('utf-8').hex(), 16)

            _data.append((0xFF0000000000000000 & str_encoded) >> 64)
            _data.append((0xFF00000000000000 & str_encoded) >> 56)
            _data.append((0xFF000000000000 & str_encoded) >> 48)
            _data.append((0xFF0000000000 & str_encoded) >> 40)
            _data.append((0xFF00000000 & str_encoded) >> 32)
            _data.append((0xFF000000 & str_encoded) >> 24)
            _data.append((0xFF0000 & str_encoded) >> 16)
            _data.append((0xFF00 & str_encoded) >> 8)
            _data.append((0xFF & str_encoded) >> 0)

        elif type(value) == list or type(value) == tuple:
            if type(value) == list:
                _data.append(_LIST)
            else:
                _data.append(_TUPLE)

            _data.append(0)

            for i in value:
                _data.extend(self.__encoding(i)[1:-1])

            _data[2] = len(_data) - 3

        elif type(value) == dict:
            _data.append(_DICT)

            for k in value:
                _data.extend(self.__encoding(k)[1:-1])
                _data.extend(self.__encoding(value[k])[1:-1])

            _data[2:2] = self.__encoding(len(_data) - 2)[1:-1]

        _data.append(_END)

        return _data

    def __decoding(self, value):
        """Method to decode value

        Args:
            value ([type]): data to decode
        """
        if value[0] == _INT:
        #     for i in range(0, value[1]):
        #         _d_data = _d_data + (value[i+2] << 8 * (value[1]-i-1))

            _d_data = (value[2] << 56) + \
                     (value[3] << 48) + \
                     (value[4] << 40) + \
                     (value[5] << 32) + \
                     (value[6] << 24) + \
                     (value[7] << 16) + \
                     (value[8] << 8) + \
                     (value[9] << 0)

            _d_data = self.__convertBin2IF(bin(_d_data), int)

        if value[0] == _FLOAT:
            _d_data = (value[2] << 56) + \
                     (value[3] << 48) + \
                     (value[4] << 40) + \
                     (value[5] << 32) + \
                     (value[6] << 24) + \
                     (value[7] << 16) + \
                     (value[8] << 8) + \
                     (value[9] << 0)

            _d_data = self.__convertBin2IF(bin(_d_data), float)

        elif value[0] == _BOOL:

            _d_data = bool(value[2])

        elif value[0] == _STR:
            _d_data = (value[2] << 64) + \
                     (value[3] << 56) + \
                     (value[4] << 48) + \
                     (value[5] << 40) + \
                     (value[6] << 32) + \
                     (value[7] << 24) + \
                     (value[8] << 16) + \
                     (value[9] << 8) + \
                     (value[10] << 0)
            _d_data = bytearray.fromhex(hex(_d_data)[2:]).decode()

        elif value[0] == _LIST or value[0] == _TUPLE:
            value = value[2:]
            _d_data = []
            c_type = value[0]

            while len(value) != 0:
                new_data = value[:2+value[1]]
                value = value[2+value[1]:]
                _d_data.append(self.__decoding(new_data))

            if c_type == _TUPLE:
                _d_data = tuple(_d_data)

        elif value[0] == _DICT:
            nb_value = value[1:value[2]+3]
            nb_value = self.__decoding(nb_value)
            value = value[value[2]+3:value[2]+3+nb_value]
            _d_data = {}

            while len(value) != 0:
                new_key = value[:value[1]+2]
                value = value[value[1]+2:]

                if value[0] == 6:
                    nb_value = self.__decoding(value[1:value[2]+3])
                    new_data = value[:nb_value+value[2]+3]
                    value = value[nb_value+value[2]+3:]
                else:
                    new_data = value[:2+value[1]]
                    value = value[2+value[1]:]

                _d_data[self.__decoding(new_key)] = self.__decoding(new_data)

        return _d_data

    def __convertBin2IF(self, value:int, type:type) -> float:
        """Method to convert value to int or float

        Args:
            value (int): data to convert

        Returns:
            data converted
        """
        if type is int:
            return struct.unpack('>i', int(value, 2).to_bytes(4, byteorder="big"))[0]

        return struct.unpack('>d', int(value, 2).to_bytes(8, byteorder="big"))[0]

    def __convertIF2Bin(self, value, type: type) -> int:
        """Method to convert value to bin

        Args:
            value: data to convert

        Returns:
            int: data converted
        """
        if type is int:
            [d] = struct.unpack(">L", struct.pack(">i", value))
        else:
            [d] = struct.unpack(">Q", struct.pack(">d", value))

        return f'{d:064b}'

    def __initValueByJSON(self, path:str) -> dict:
        """Method to extract value from a JSON file

        Args:
            path (str): path to the JSON file

        Returns:
            dict: return  data from JSON file
        """
        _json_file = open(path)
        _value = json.load(_json_file)
        _json_file.close()

        return _value

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
        _s = "Client: " + str(self.__name_memory) + "\n"\
            + "\tAvailable: " + self.getAvailability().__repr__() + "\n"\
            + "\tValue: " + self.__value.__repr__()

        return _s

    @staticmethod
    def getSharedMemorySpace():
        if os.name == "Windows" or os.name == "Darwin":
            print("Not yet implemented.")

            return

        return next(os.walk("/dev/shm/"), (None, None, []))[2]