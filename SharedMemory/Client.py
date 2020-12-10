'''
File: Client.py
Created Date: Wednesday, July 3rd 2020, 8:16:24 pm
Author: Zentetsu

----

Last Modified: Thu Dec 10 2020
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
2020-12-10	Zen	Adding log file
2020-10-15	Zen	Updating private status of varaibles and methods
2020-10-14	Zen	Adding export method
2020-10-11	Zen	Updating overloaded methods for simple type
2020-09-17	Zen	Adding overloaded methods
2020-07-23	Zen	Fix availability when checking availability
2020-07-18	Zen	Adding method to get access to data availability information
2020-07-18	Zen	fix state behavior and and adding method to check data availability
2020-07-13	Zen	Adding getStatus, start and restart methods
2020-07-09	Zen	Adding some comments
2020-07-03	Zen	Correction of data acquisition
2020-07-03	Zen	Data simplification
2020-07-02	Zen	Adding exception and json reader
2020-07-01	Zen	Creating file and drafting class
'''


from .SMError import SMTypeError, SMSizeError, SMMultiInputError
from multiprocessing import shared_memory
import logging
import json
import time
import sys


class Client:
    """Client class focused on sharing data with a Server
    """
    def __init__(self, name:str, value=None, path:str=None, size:int=10, timeout:int=1, log:str=None):
        """Class constructor

        Args:
            name (str): desired name for the sharing space
            value ([type], optional): value to share with the other Server. Defaults to None.
            path (str, optional): path to load JSON file and sharing data inside. Defaults to None.
            size (int, optional): size of the shared space or str value. Defaults to 10.
            timeout (int, optional): mutex timeout. Defaults to 1.

        Raises:
            SMMultiInputError: raise an error when value and path are both at None or initialized
        """
        self.__log = log

        if self.__log is not None:
            logging.basicConfig(filename=self.__log, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s', level=logging.DEBUG)
            self.__writeLog(0, "Starting SharedMemory Client...")


        if value is None and path is None or value is not None and path is not None:
            raise SMMultiInputError
        elif value is None:
            self.__value = self.__initValueByJSON(path)
        else:
            self.__value = value
            self.__size = size

        self.__timeout = timeout
        self.__type = type(self.__value)
        self.__name = name
        self.__state = "Stopped"
        self.__availability = False
        self.__server_availability = False
        self.__server_availability_ls = False

        self.__initSharedMemory()

    def __initValueByJSON(self, path:str)->dict:
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

    def exportToJSON(self, path:str):
        """Method to export dict to JSON file

        Args:
            path (str): file path
        """
        if self.__type is not dict:
            if self.__log is not None:
                self.__writeLog(1, "Data type must be dict")
            else:
                print("INFO: Data type must be dict")
            raise TypeError("Data type must be dict")

        file = open(path, 'w+')
        json.dump(self.getValue(), file)
        file.close()

    def __checkValue(self, value):
        """Method to check if value isn't a dict or list and to initialize

        Args:
            value ([type]): value to test

        Raises:
            SMTypeError: raise an error when the value is a dict or a list

        Returns:
            [type]: return the initialized value
        """
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

    def __initSharedMemory(self):
        """Method to initialize the shared space
        """
        if type(self.__value) is list and type in [type(e) for e in self.__value]:
            for i in range(0, len(self.__value)):
                self.__value[i] = self.__checkValue(self.__value[i])

        self.__size = sys.getsizeof(self.__value)

        self.start()

    def __checkServerAvailability(self):
        """Method to get the Server's availability
        """
        try:
            self.__server_availability = json.loads(self.sl_tmx[0])[2]
            self.__server_availability_ls = self.__server_availability
        except:
            self.__server_availability = False

    # @PendingDeprecationWarning
    def getValue(self):
        """Method to return the shared value

        Returns:
            [type]: return data from the shared space
        """
        self.__checkServerAvailability()

        if not self.__server_availability:# and self.__server_availability_ls:
            if self.__log is not None:
                self.__writeLog(0, "Server unavailable, restarting shared memory space.")
            else:
                print("INFO: Server unavailable, restarting shared memory space.")
            self.__server_availability_ls = False
            self.restart()

        self.__value = json.loads(self.sl[0])

        return self.__value

    def getType(self):
        """Method that returns data type

        Returns:
            [type]: data type
        """
        return self.__type

    # @PendingDeprecationWarning
    def updateValue(self, n_value):
        """Method to update data fo the shared space

        Args:
            n_value ([type]): new version of data

        Raises:
            SMTypeError: raise en error when the new value is not correspoding to the initial type
            SMSizeError: raise an error when the size of the new value exced the previous one
        """
        self.__checkServerAvailability()

        if not self.__server_availability:# and self.__server_availability_ls:
            if self.__log is not None:
                self.__writeLog(0, "Server unavailable, restarting shared memory space.")
            else:
                print("INFO: Server unavailable, restarting shared memory space.")
            self.__server_availability_ls = False
            self.restart()

        start = time.time()

        while json.loads(self.sl_tmx[0])[0]:
            if (time.time() - start) > self.__timeout:
                if self.__log is not None:
                    self.__writeLog(3, "timeout MUTEX.")
                else:
                    print("WARNING: timeout MUTEX.")
                return

        self.sl_tmx[0] = json.dumps([True, self.__availability, self.__server_availability])
        self.__value = json.loads(self.sl[0])

        if type(n_value) is not self.__type:
            raise SMTypeError(type(n_value))

        if sys.getsizeof(n_value) > self.__size:
            raise SMSizeError

        self.__value = n_value
        self.sl[0] = json.dumps(self.__value)
        self.sl_tmx[0] = json.dumps([False, self.__availability, self.__server_availability])

    def __getitem__(self, key):
        """Method to get item value from the shared data

        Args:
            key ([type]): key
        """
        self.__checkServerAvailability()

        if not self.__server_availability:# and self.__server_availability_ls:
            if self.__log is not None:
                self.__writeLog(0, "Server unavailable, restarting shared memory space.")
            else:
                print("INFO: Server unavailable, restarting shared memory space.")
            self.__server_availability_ls = False
            self.restart()

        self.__value = json.loads(self.sl[0])

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
        if self.__type == list:
            if self.__log is not None:
                self.__writeLog(1, "Data shared type is list not dict.")
            else:
                print("INFO: Data shared type is list not dict.")
            raise TypeError("Data shared type is list not dict.")

        self.__checkServerAvailability()

        if not self.__server_availability:# and self.__server_availability_ls:
            if self.__log is not None:
                self.__writeLog(0, "Server unavailable, restarting shared memory space.")
            else:
                print("INFO: Server unavailable, restarting shared memory space.")
            self.__server_availability_ls = False
            self.restart()

        start = time.time()

        while json.loads(self.sl_tmx[0])[0]:
            if (time.time() - start) > self.__timeout:
                if self.__log is not None:
                    self.__writeLog(3, "timeout MUTEX.")
                else:
                    print("WARNING: timeout MUTEX.")
                return

        self.sl_tmx[0] = json.dumps([True, self.__availability, self.__server_availability])
        self.__value = json.loads(self.sl[0])

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

        self.sl[0] = json.dumps(self.__value)
        self.sl_tmx[0] = json.dumps([False, self.__availability, self.__server_availability])

    def __len__(self):
        """Method that returns the size of the shared data

        Returns:
            int: size of the shared data
        """
        self.__checkServerAvailability()

        if not self.__server_availability:# and self.__server_availability_ls:
            if self.__log is not None:
                self.__writeLog(0, "Server unavailable, restarting shared memory space.")
            else:
                print("INFO: Server unavailable, restarting shared memory space.")
            self.__server_availability_ls = False
            self.restart()

        self.__value = json.loads(self.sl[0])

        return self.__value.__len__()

    def __contains__(self, key):
        """Method to check if an element is into the shared data

        Args:
            key ([type]): Element to find

        Returns:
            bool: boolean to determine if the element is or not into the shared data
        """
        self.__checkServerAvailability()

        if not self.__server_availability:# and self.__server_availability_ls:
            if self.__log is not None:
                self.__writeLog(0, "Server unavailable, restarting shared memory space.")
            else:
                print("INFO: Server unavailable, restarting shared memory space.")
            self.__server_availability_ls = False
            self.restart()

        self.__value = json.loads(self.sl[0])

        return self.__value.__contains__(key)

    def __delitem__(self, key):
        """Method to remove an element from the shared data

        Args:
            key ([type]): Element to remove
        """
        self.__checkServerAvailability()

        if not self.__server_availability:# and self.__server_availability_ls:
            if self.__log is not None:
                self.__writeLog(0, "Server unavailable, restarting shared memory space.")
            else:
                print("INFO: Server unavailable, restarting shared memory space.")
            self.__server_availability_ls = False
            self.restart()

        start = time.time()

        while json.loads(self.sl_tmx[0])[0]:
            if (time.time() - start) > self.__timeout:
                if self.__log is not None:
                    self.__writeLog(3, "timeout MUTEX.")
                else:
                    print("WARNING: timeout MUTEX.")
                return

        self.sl_tmx[0] = json.dumps([True, self.__availability, self.__server_availability])
        self.__value = json.loads(self.sl[0])

        self.__value.__delitem__(key)

        self.sl[0] = json.dumps(self.__value)
        self.sl_tmx[0] = json.dumps([False, self.__availability, self.__server_availability])

    def getStatus(self) -> str:
        """Method that return shared memory state

        Returns:
            str: shared memory state
        """
        return self.__state

    def getAvailability(self) -> [bool, bool]:
        """Method that return the availability of Client and Server

        Returns:
            [bool, bool]: Client and Server availability status
        """
        self.__checkServerAvailability()

        return self.__availability, self.__server_availability

    def close(self):
        """Method to close the shared space
        """
        try:
            self.sl.shm.close()
            self.sl_tmx.shm.close()
        except FileNotFoundError:
            pass

    def unlink(self):
        """Method to remove the shared space from the memory
        """
        try:
            self.sl.shm.unlink()
            self.sl_tmx.shm.unlink()
        except FileNotFoundError:
            pass

    def start(self):
        """Method that create shared memory space
        """
        if self.__state == "Started":
            if self.__log is not None:
                self.__writeLog(0, "Client already started.")
            else:
                print("INFO: Client already started.")
            return

        self.__state = "Started"
        self.__availability = True

        try:
            self.sl = shared_memory.ShareableList([json.dumps(self.__value)], name=self.__name,)
            self.sl_tmx = shared_memory.ShareableList([json.dumps([False, self.__availability, self.__server_availability])], name=self.__name + "_tmx")
        except Exception:
            pass

    def restart(self):
        """Method to restart the shared memory space
        """
        self.stop()
        self.start()

    def stop(self):
        """Method that calls stop and unlink method
        """
        if self.__state == "Stopped":
            if self.__log is not None:
                self.__writeLog(0, "Client already stopped.")
            else:
                print("INFO: Client already stopped.")
            return

        self.__state = "Stopped"
        self.__availability = False
        self.sl_tmx[0] = json.dumps([False, self.__availability, self.__server_availability])

        self.close()
        self.unlink()

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

    def __repr__(self):
        """Redefined method to print value of the Client Class instance

        Returns:
            str: printable value of Client Class instance
        """
        self.__checkServerAvailability()

        s = "Client: " + self.__name + "\n"\
            + "\tStatus: " + self.__state + "\n"\
            + "\tAvailable: " + self.__availability.__repr__() + "\n"\
            + "\tServer Available: " + self.__server_availability.__repr__() + "\n"\
            + "\tValue: " + self.__value.__repr__()

        return s