"""
File: SharedMemory.py
Created Date: Thursday, October 7th 2021, 8:37:52 pm
Author: Zentetsu

----

Last Modified: Thu Nov 07 2024
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
2023-03-06	Zen	Correcting mutex behavior + Fixing mutex bug
2023-07-14	Zen	Adding support for numpy array and complex number
2023-07-14	Zen	Fixing int conversion
2023-08-13	Zen	Correcting numpy support + int conversion
2023-08-31	Zen	Correcting setitem method
2023-09-01	Zen	Correcting memory allocation
2023-09-08	Zen	Correcting memory and nummpy support + empty list support
2023-10-18	Zen	Correcting close method
2024-11-03	Zen	Updating docstring + type + silent mode
2024-11-07	Zen	Optimizing code for memory allocation
"""  # noqa

from re import S
from .SMError import SMMultiInputError, SMTypeError, SMSizeError, SMManagerName, SMAlreadyExist, SMEncoding, SMNameLength
import posix_ipc
import logging
import struct
import numpy
import json
import mmap
import sys
import os

_SHM_NAME_PREFIX = "/psm_"
_SEM_NAME_PREFIX = "/sem_"

_MAX_LEN = 14

_MODE = 0o666
_FLAG = posix_ipc.O_CREX | os.O_RDWR

_BEGIN = b"\xaa"
_END = b"\xbb"
_CLOSED = b"\xab"

_INT = b"\x00"
_FLOAT = b"\x01"
_BOOL = b"\x02"
_COMPLEX = b"\x03"
_STR = b"\x04"
_LIST = b"\x05"
_DICT = b"\x06"
_TUPLE = b"\x07"
_NPARRAY = b"\x08"

_MAN_NAME = "man"


class SharedMemory:
    """Shared Memory class."""

    MAN = False

    def __init__(self, name: str, value: any = None, path: str = None, size: int = None, client: bool = False, log: str = None, silent: bool = False) -> None:
        """Class constructor.

        Args:
            name (str): desired name for the sharing space
            value ([type], optional): value to share with the other Server. Defaults to None.
            path (str, optional): path to load JSON file and sharing data inside. Defaults to None.
            size (int, optional): size in bytes of the shared space. Defaults to None.
            client (bool, optional): will creat a client or server instance
            log (str, optional): write log into a file. Defaults to None.
            silent (bool, optional): silent mode. Defaults to False.

        Raises:
            SMMultiInputError: raise an error when value and path are both at None or initialized

        """
        self.__log = log
        self.__size = None
        self.__silent = silent

        if self.__log is not None:
            logging.basicConfig(filename=self.__log, format="%(asctime)s - " + _SHM_NAME_PREFIX[1:] + name + " - %(levelname)s - %(message)s")

            f = open(os.devnull, "w")
            sys.stdout = f

        if name == _MAN_NAME and sys.platform == "darwin" and not SharedMemory.MAN:
            if self.__log is not None:
                self.__writeLog(1, "shared memory called '" + _MAN_NAME + "' is defined as the shared memory manager.")
            elif not self.__silent:
                print("ERROR: shared memory called '" + _MAN_NAME + "' is defined as the shared memory manager.")

            raise SMManagerName(_MAN_NAME)
        if client and (value is None and path is None or value is not None and path is not None):
            if self.__log is not None:
                self.__writeLog(1, "Conflict between value and json path intialization.")
            elif not self.__silent:
                print("ERROR: Conflict between value and json path intialization.")

            raise SMMultiInputError
        elif client and value is None and path is not None:
            self.__value = self.__initValueByJSON(path)
        elif not client and (value is not None or path is not None):
            if self.__log is not None:
                self.__writeLog(1, "Conflict between value and json path intialization.")
            elif not self.__silent:
                print("ERROR: Conflict between value and json path intialization.")

            raise SMMultiInputError
        else:
            self.__value = value
            self.__size = size

        self.__name_memory = _SHM_NAME_PREFIX + name
        self.__name_semaphore = _SEM_NAME_PREFIX + name
        self.__type = type(self.__value)
        self.__client = client

        if len(self.__name_memory) > _MAX_LEN:
            raise SMNameLength(_MAN_NAME, len(self.__name_memory) - len(_SHM_NAME_PREFIX))

        self.__initSharedMemory()

        if not SharedMemory.MAN:
            SharedMemory.__addToManager(name)

    def restart(self) -> None:
        """Restart the shared memory space."""
        if not self.__client:
            if self.__log is not None:
                self.__writeLog(3, "Only client can restart Shared Memory space.")
            elif not self.__silent:
                print("WARNING: Only client can restart Shared Memory space.")

            return

        if self.getAvailability():
            if self.__log is not None:
                self.__writeLog(0, "Client already running.")
            elif not self.__silent:
                print("INFO: Client already running.")

            return

        self.__initSharedMemory()

    def close(self) -> None:
        """Close the shared memory space."""
        if not self.getAvailability():
            if self.__log is not None:
                self.__writeLog(0, "Client already stopped.")
            elif not self.__silent:
                print("INFO: Client already stopped.")

            if not SharedMemory.MAN:
                SharedMemory.__removeFromManager(self.__name_memory[5:])

            return

        self.__semaphore.acquire()

        if self.__mapfile is not None:
            self.__mapfile.seek(0)

            self.__mapfile.write(_BEGIN + _CLOSED + _END)

            self.__mapfile.close()
            self.__mapfile = None

        if self.__memory is not None:
            try:
                posix_ipc.unlink_shared_memory(self.__name_memory)

                self.__semaphore.release()
                self.__semaphore.unlink()
            except:
                if self.__log is not None:
                    self.__writeLog(0, "SharedMemory already closed.")
                elif not self.__silent:
                    print("INFO: SharedMemory already closed.")

            self.__memory = None
            self.__semaphore = None

        if not SharedMemory.MAN:
            SharedMemory.__removeFromManager(self.__name_memory[5:])

    def setValue(self, value: any, mutex: bool = False) -> bool:
        """Set the shared memory value.

        Args:
            value (any): data to add to the shared memory
            mutex (bool, optional): use mutex or not. Defaults to False.

        Returns:
            bool: return if value has been updated

        """
        if not self.getAvailability() or self.__semaphore is None:
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            elif not self.__silent:
                print("ERROR: Shared Memory space doesn't exist.")

            return None
        elif not mutex:
            self.__semaphore.acquire()

        if not self.__checkValue(type(value)):
            raise SMTypeError()

        _data = self.__encoding(value)

        if sys.getsizeof(_data) > self.__size:
            if self.__log is not None:
                self.__writeLog(1, "Data size is too big for the shared memory space.")
            elif not self.__silent:
                print("ERROR: Data size is too big for the shared memory space.")

            if not mutex:
                self.__semaphore.release()

            return False

        self.__mapfile.seek(0)
        self.__mapfile.write(_data)

        if not mutex:
            self.__semaphore.release()

        return True

    def getValue(self, mutex: bool = False) -> any:
        """Return the shared memory value.

        Args:
            mutex (bool, optional): use mutex or not. Defaults to False.

        Returns:
            any: return data from the shared space

        """
        if not self.getAvailability() or self.__semaphore is None:
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            elif not self.__silent:
                print("ERROR: Shared Memory space doesn't exist.")

            return None
        elif not mutex:
            self.__semaphore.acquire()

        try:
            self.__mapfile.seek(0)
            _packed = self.__mapfile.read()
            _shift = int.from_bytes(_packed[2:10], "big") + 11 if _packed[1].to_bytes(1, byteorder="big") in [_NPARRAY, _LIST, _TUPLE, _DICT] else _packed[2] + 4
            _encoded_data = _packed[0:_shift]
        except:
            return None

        if (b := _encoded_data[0].to_bytes(1, byteorder="big") != _BEGIN) or _encoded_data[-1].to_bytes(1, byteorder="big") != _END:
            if not mutex:
                self.__semaphore.release()

            raise SMEncoding("BEGIN" if b else "END")

        if _encoded_data[1].to_bytes(1, byteorder="big") == _CLOSED:
            if not mutex:
                self.__semaphore.release()

            raise SMEncoding("CLOSED")

        _decoded_data = self.__decoding(_encoded_data[1:-1])

        if not mutex:
            self.__semaphore.release()

        return _decoded_data

    def getType(self) -> type:
        """Return data type of shared momory.

        Returns:
            type: data type

        """
        return self.__type

    def getAvailability(self) -> bool:
        """Return the availability of Shared Memory.

        Returns:
            bool: Shared Memory availability status

        """
        if self.__memory is None and self.__mapfile is None and not self.__client:
            try:
                self.__initSharedMemory()
            except:
                return False

        try:
            self.__mapfile.seek(0)
            _encoded_data = self.__mapfile.read()

            return _encoded_data[:3] != _BEGIN + _CLOSED + _END
        except:
            return False

    def exportToJSON(self, path: str) -> None:
        """Export dict to JSON file.

        Args:
            path (str): file path

        """
        if self.__type is not dict:
            if self.__log is not None:
                self.__writeLog(1, "Data type must be dict.")
            elif not self.__silent:
                print("ERROR: Data type must be dict.")

            raise TypeError("Data type must be dict.")

        _file = open(path, "w+")
        json.dump(self.getValue(), _file)
        _file.close()

    def __initSharedMemory(self) -> None:
        """Initialize the shared space."""
        if self.__size is None:
            self.__size = sys.getsizeof(self.__encoding(self.__value))

        _page_size = mmap.ALLOCATIONGRANULARITY
        self.__size = ((self.__size + _page_size - 1) // _page_size) * _page_size

        self.__memory = None
        self.__semaphore = None
        self.__mapfile = None

        if self.__client:
            try:
                try:
                    posix_ipc.unlink_shared_memory(self.__name_memory)
                except posix_ipc.ExistentialError:
                    pass

                self.__memory = posix_ipc.SharedMemory(self.__name_memory, flags=_FLAG, mode=_MODE, size=self.__size)
                self.__semaphore = posix_ipc.Semaphore(self.__name_semaphore, _FLAG, _MODE, initial_value=1)

                # os.ftruncate(self.__memory.fd, self.__size)
            except posix_ipc.ExistentialError:
                if self.__value is not None:
                    self.__memory = posix_ipc.SharedMemory(self.__name_memory)

                    try:
                        self.__semaphore = posix_ipc.Semaphore(self.__name_semaphore)
                    except posix_ipc.ExistentialError:
                        self.__semaphore = posix_ipc.Semaphore(self.__name_semaphore, _FLAG, _MODE, initial_value=1)
                else:
                    self.close()
                    raise SMAlreadyExist(self.__name_memory)
        else:
            try:
                self.__memory = posix_ipc.SharedMemory(self.__name_memory)
                self.__semaphore = posix_ipc.Semaphore(self.__name_semaphore)
                self.__size = self.__memory.size
            except posix_ipc.ExistentialError:
                if self.__log is not None:
                    self.__writeLog(3, "Memory space not yet created.")
                elif not self.__silent:
                    print("WARNING: Memory space not yet created.")

                return

        self.__mapfile = mmap.mmap(self.__memory.fd, self.__size)

        if self.__client:
            self.setValue(self.__value)
        else:
            self.__value = self.getValue()
            self.__type = type(self.__value)

    def __checkValue(self, value: type) -> bool:
        """Check value type.

        Args:
            value (type): value to test

        Raises:
            SMTypeError: raise an error when the value is a dict or a list

        Returns:
            type: return the initialized value

        """
        if value != self.__type:
            raise SMTypeError(value)

        return True

    def __encoding(self, value: any) -> list:
        """Encode value.

        Args:
            value (any): data to encode

        """
        _data = _BEGIN

        if type(value) == int:
            _data += _INT + b"\x08" + value.to_bytes(8, "big", signed=True)

        elif type(value) == float:
            _encoded_float = struct.pack(">d", value)

            _data += _FLOAT + len(_encoded_float).to_bytes(1, byteorder="big") + _encoded_float

        if type(value) == complex:
            _encoded_cplx = self.__encoding(value.real)[1:-1] + self.__encoding(value.imag)[1:-1]

            _data += _COMPLEX + len(_encoded_cplx).to_bytes(1, byteorder="big") + _encoded_cplx

        elif type(value) == bool:
            _data += _BOOL + b"\x01" + int(value).to_bytes(1, byteorder="big")

        elif type(value) == str:
            _str_encoded = value.encode("utf-8")

            _data += _STR + len(_str_encoded).to_bytes(1, byteorder="big") + _str_encoded

        elif type(value) == list or type(value) == tuple:
            _lt_encoded = b""

            for e in value:
                _lt_encoded += self.__encoding(e)

            _data += (_LIST if type(value) == list else _TUPLE) + len(_lt_encoded).to_bytes(8, byteorder="big") + _lt_encoded

        elif type(value) == dict:
            if list(value.keys())[0] == "_LIST":
                return self.__encoding([0] * value[list(value.keys())[0]])
            elif list(value.keys())[0] == "_NPARRAY":
                return self.__encoding(numpy.zeros(value[list(value.keys())[0]][0], dtype=value[list(value.keys())[0]][1]))
            else:
                _dict_encoded = b""

                for k in value:
                    _dict_encoded += self.__encoding(k)
                    _dict_encoded += self.__encoding(value[k])

                _data += _DICT + len(_dict_encoded).to_bytes(8, byteorder="big") + _dict_encoded

        elif type(value) == numpy.ndarray:
            _encoded_shape = self.__encoding(value.shape)
            _encoded_dtype = self.__encoding(value.dtype.name)
            _encoded_np = len(_encoded_shape).to_bytes(8, byteorder="big") + len(_encoded_dtype).to_bytes(1, byteorder="big") + value.tobytes() + _encoded_shape + _encoded_dtype

            _data += _NPARRAY + len(_encoded_np).to_bytes(8, byteorder="big") + _encoded_np

        _data += _END

        return _data

    def __decoding(self, value: bytes) -> any:
        """MDecode value.

        Args:
            value (any): data to decode

        """
        if value[0].to_bytes(1, "big") == _INT:
            _d_data = int.from_bytes(value[2 : value[1] + 2], "big", signed=True)

        elif value[0].to_bytes(1, "big") == _FLOAT:
            _d_data = struct.unpack(">d", value[2 : value[1] + 2])[0]

        elif value[0].to_bytes(1, "big") == _COMPLEX:
            _d_data = complex(self.__decoding(value[2 : value[3] + 4]), self.__decoding(value[value[3] + 4 : value[3] + 4 + value[value[3] + 6]]))

        elif value[0].to_bytes(1, "big") == _BOOL:
            _d_data = bool(value[2])

        elif value[0].to_bytes(1, "big") == _STR:
            _d_data = value[2 : value[1] + 2].decode("utf-8")

        elif value[0].to_bytes(1, "big") == _LIST or value[0].to_bytes(1, "big") == _TUPLE:
            c_type = value[0]
            _d_data = []

            if len(value) != 2:
                value = value[9:]

                while len(value) != 0:
                    _shift = int.from_bytes(value[2:10], "big") + 10 if value[1].to_bytes(1, "big") in [_NPARRAY, _LIST, _TUPLE, _DICT] else value[2] + 3
                    new_data = value[1:_shift]
                    value = value[_shift + 1 :]
                    _d_data.append(self.__decoding(new_data))

            if c_type.to_bytes(1, "big") == _TUPLE:
                _d_data = tuple(_d_data)

        elif value[0].to_bytes(1, "big") == _DICT:
            _d_data = {}

            value = value[9:]

            while len(value) != 0:
                new_key = self.__decoding(value[1 : value[2] + 3])
                value = value[value[2] + 4 :]
                _shift = int.from_bytes(value[2:10], "big") + 10 if value[1].to_bytes(1, "big") in [_NPARRAY, _LIST, _TUPLE, _DICT] else value[2] + 3
                new_data = self.__decoding(value[1:_shift])
                _d_data[new_key] = new_data
                value = value[_shift + 1 :]

        elif value[0].to_bytes(1, "big") == _NPARRAY:
            _size_data = int.from_bytes(value[1:9], "big")
            _size_shape = int.from_bytes(value[9:17], "big")
            _data = value[18 : -_size_shape - value[17]]
            _shape = value[9 + _size_data - _size_shape - value[17] : -value[17]]
            _type = value[9 + _size_data - value[17] :]

            _d_data = numpy.frombuffer(_data, dtype=self.__decoding(_type[1:-1])).reshape(self.__decoding(_shape[1:-1]))

        return _d_data

    def __initValueByJSON(self, path: str) -> dict:
        """Extract value from a JSON file.

        Args:
            path (str): path to the JSON file

        Returns:
            dict: return  data from JSON file

        """
        _json_file = open(path)
        _value = json.load(_json_file)
        _json_file.close()

        return _value

    def __writeLog(self, log_id: int, message: str) -> None:
        """Write information into a log file.

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

    def __getitem__(self, key: any) -> any:
        """Get item value from the shared data.

        Args:
            key (any): key

        """
        if not self.getAvailability() or self.__semaphore is None:
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            elif not self.__silent:
                print("ERROR: Shared Memory space doesn't exist.")

            return None
        else:
            self.__semaphore.acquire()

        self.__value = self.getValue(mutex=True)

        self.__semaphore.release()

        if self.__type == dict:
            if type(key) is int:
                key = str(key)

            return self.__value[key]
        elif self.__type == list:
            return self.__value[key]
        else:
            return self.__value

    def __setitem__(self, key: any, value: any) -> None:
        """Update data of the shared space.

        Args:
            key (str): key
            value (any): new key value

        """
        if not self.getAvailability() or self.__semaphore is None:
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            elif not self.__silent:
                print("ERROR: Shared Memory space doesn't exist.")

            return None
        else:
            self.__semaphore.acquire()

        self.__value = self.getValue(mutex=True)

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

        self.setValue(self.__value, mutex=True)

        self.__semaphore.release()

    def __len__(self) -> int:
        """Return the size of the shared data.

        Returns:
            int: size of the shared data

        Raises:
            TypeError: raise an error when this method is called and tha data shared type is not a dict

        """
        if not self.getAvailability() or self.__semaphore is None:
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            elif not self.__silent:
                print("ERROR: Shared Memory space doesn't exist.")

            return None
        else:
            self.__semaphore.acquire()

        self.__value = self.getValue(mutex=True)

        self.__semaphore.release()

        return self.__value.__len__()

    def __contains__(self, key: any) -> bool:
        """Check if an element is into the shared data.

        Args:
            key (any): Element to find

        Returns:
            bool: boolean to determine if the element is or not into the shared data

        Raises:
            TypeError: raise an error when this method is called and tha data shared type is not a dict

        """
        if not self.getAvailability() or self.__semaphore is None:
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            elif not self.__silent:
                print("ERROR: Shared Memory space doesn't exist.")

            return None
        else:
            self.__semaphore.acquire()

        self.__value = self.getValue(mutex=True)

        self.__semaphore.release()

        return self.__value.__contains__(key)

    def __delitem__(self, key: any) -> None:
        """Remove an element from the shared data.

        Args:
            key (any): Element to remove

        Raises:
            TypeError: raise an error when this method is called and tha data shared type is not a dict

        """
        if not self.getAvailability() or self.__semaphore is None:
            if self.__log is not None:
                self.__writeLog(1, "Shared Memory space doesn't exist.")
            elif not self.__silent:
                print("ERROR: Shared Memory space doesn't exist.")

            return
        else:
            self.__semaphore.acquire()

        self.__value = self.getValue(mutex=True)

        self.__value.__delitem__(key)

        self.setValue(self.__value, mutex=True)

        self.__semaphore.release()

    def __repr__(self) -> str:
        """Print value of the Client Class instance.

        Returns:
            str: printable value of Client Class instance

        """
        _s = "Client: " + str(self.__name_memory) + "\n" + "\tAvailable: " + self.getAvailability().__repr__() + "\n" + "\tValue: " + self.getValue().__repr__()

        return _s

    @staticmethod
    def getSharedMemorySpace() -> list:
        """Get list of all shared memory space."""
        return SharedMemory.__getSharedMemoryList()

    @staticmethod
    def cleanSharedMemorySpace() -> None:
        """Clean all shared memory space."""
        l = SharedMemory.__getSharedMemoryList()

        for name in l:
            if name == _MAN_NAME:
                continue
            SharedMemory.__killShareMemorySpace(name)

            if sys.platform == "darwin":
                SharedMemory.__removeFromManager(name)

    @staticmethod
    def killManager() -> None:
        """Kill all shared memory with the manager."""
        SharedMemory.cleanSharedMemorySpace()
        SharedMemory.__killShareMemorySpace(_MAN_NAME)

    @staticmethod
    def __killShareMemorySpace(name: str) -> None:
        """Kill a specific shared memory space."""
        try:
            __name_memory = _SHM_NAME_PREFIX + name
            __semaphore = posix_ipc.Semaphore(_SEM_NAME_PREFIX + name)

            posix_ipc.unlink_shared_memory(__name_memory)

            __semaphore.release()
            __semaphore.unlink()
        except:
            pass

    @staticmethod
    def __getSharedMemoryList() -> list:
        """Get list of all shared memory space."""
        if sys.platform == "darwin":
            SharedMemory.MAN = True
            man = SharedMemory(_MAN_NAME, client=False)

            if not man.getAvailability():
                man.close()
                man = SharedMemory(_MAN_NAME, value=["man"], size=1024 * 10, client=True)

            l = man.getValue()
            SharedMemory.MAN = False

            return l

        return next(os.walk("/dev/shm/"), (None, None, []))[2]

    @staticmethod
    def __addToManager(name: str) -> None:
        """Add a shared memory space to the manager."""
        SharedMemory.MAN = True
        man = SharedMemory(_MAN_NAME, client=False)

        if not man.getAvailability():
            man.close()
            man = SharedMemory(_MAN_NAME, value=["man"], size=1024 * 10, client=True)

        l = man.getValue()
        l.append(name)
        man.setValue(l)

        SharedMemory.MAN = False

    @staticmethod
    def __removeFromManager(name: str) -> None:
        """Remove a shared memory space from the manager."""
        SharedMemory.MAN = True
        man = SharedMemory(_MAN_NAME, client=False)

        l = man.getValue()
        if name in l:
            l.remove(name)

        man.setValue(l)
        SharedMemory.MAN = False
