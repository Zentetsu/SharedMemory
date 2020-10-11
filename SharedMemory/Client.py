'''
File: Client.py
Created Date: Wednesday, July 3rd 2020, 8:16:24 pm
Author: Zentetsu

----

Last Modified: Sun Oct 11 2020
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
import json
import time
import sys


class Client:
    """Client class focused on sharing data with a Server
    """
    def __init__(self, name:str, value=None, path:str=None, size:int=10, timeout:int=1):
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
        if value is None and path is None or value is not None and path is not None:
            raise SMMultiInputError
        elif value is None:
            self.value = self._initValueByJSON(path)
        else:
            self.value = value
            self.size = size

        self.timeout = timeout
        self.type = type(self.value)
        self.name = name
        self.state = "Stopped"
        self.availability = False
        self.server_availability = False
        self.server_availability_ls = False

        self._initSharedMemory()

    def _initValueByJSON(self, path:str)->dict:
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

    def _checkValue(self, value):
        """Method to check if value isn't a dict or list and to initialize

        Args:
            value ([type]): value to test

        Raises:
            SMTypeError: raise an error when the value is a dict or a list

        Returns:
            [type]: return the initialized value
        """
        if value is str:
            value = " " * self.size
        elif value is int:
            value = 0
        elif value is float:
            value = 0.0
        elif value is bool:
            value = False
        elif value is dict or value is list:
            raise SMTypeError(value)

        return value

    def _initSharedMemory(self):
        """Method to initialize the shared space
        """
        if type(self.value) is list and type in [type(e) for e in self.value]:
            for i in range(0, len(self.value)):
                self.value[i] = self._checkValue(self.value[i])

        self.size = sys.getsizeof(self.value)

        print(self.value)

        self.start()

    def _checkServerAvailability(self):
        """Method to get the Server's availability
        """
        try:
            self.server_availability = json.loads(self.sl_tmx[0])[2]
            self.server_availability_ls = self.server_availability
        except:
            self.server_availability = False

    # @PendingDeprecationWarning
    def getValue(self):
        """Method to return the shared value

        Returns:
            [type]: return data from the shared space
        """
        self._checkServerAvailability()

        if not self.server_availability:# and self.server_availability_ls:
            print("INFO: Server unavailable, restarting shared memory space.")
            self.server_availability_ls = False
            self.restart()

        print(self.value)
        self.value = json.loads(self.sl[0])

        return self.value

    # @PendingDeprecationWarning
    def updateValue(self, n_value):
        """Method to update data fo the shared space

        Args:
            n_value ([type]): new version of data

        Raises:
            SMTypeError: raise en error when the new value is not correspoding to the initial type
            SMSizeError: raise an error when the size of the new value exced the previous one
        """
        self._checkServerAvailability()

        if not self.server_availability:# and self.server_availability_ls:
            print("INFO: Server unavailable, restarting shared memory space.")
            self.server_availability_ls = False
            self.restart()

        start = time.time()

        while json.loads(self.sl_tmx[0])[0]:
            if (time.time() - start) > self.timeout:
                print("WARNING: timeout MUTEX.")
                return

        self.sl_tmx[0] = json.dumps([True, self.availability, self.server_availability])
        self.value = json.loads(self.sl[0])

        if type(n_value) is not self.type:
            raise SMTypeError(type(n_value))

        if sys.getsizeof(n_value) > self.size:
            raise SMSizeError

        self.value = n_value
        self.sl[0] = json.dumps(self.value)
        self.sl_tmx[0] = json.dumps([False, self.availability, self.server_availability])

    def __getitem__(self, key):
        """Method to get item value from the shared data

        Args:
            key ([type]): key
        """
        self._checkServerAvailability()

        if not self.server_availability:# and self.server_availability_ls:
            print("INFO: Server unavailable, restarting shared memory space.")
            self.server_availability_ls = False
            self.restart()

        self.value = json.loads(self.sl[0])

        if self.type == dict:
            if type(key) is int:
                key = str(key)
            return self.value[key]
        elif self.type == list:
            return self.value[key]
        else:
            return self.value

    def __setitem__(self, key, value):
        """Method to update data of the shared space

        Args:
            key (str): key
            value ([type]): new key value

        Raises:
            TypeError: raise an error when this method is called and tha data shared type is not a dict
        """
        if self.type == list:
            raise TypeError("Data shared type is list not dict.")

        self._checkServerAvailability()

        if not self.server_availability:# and self.server_availability_ls:
            print("INFO: Server unavailable, restarting shared memory space.")
            self.server_availability_ls = False
            self.restart()

        start = time.time()

        while json.loads(self.sl_tmx[0])[0]:
            if (time.time() - start) > self.timeout:
                print("WARNING: timeout MUTEX.")
                return

        self.sl_tmx[0] = json.dumps([True, self.availability, self.server_availability])
        self.value = json.loads(self.sl[0])

        if type(key) is int:
            key = str(key)

        if self.type == dict:
            if type(key) is int:
                key = str(key)
            self.value[key] = value
        elif self.type == list:
            self.value[key] = value
        else:
            self.value = value

        if sys.getsizeof(self.value) > self.size:
            raise SMSizeError

        self.sl[0] = json.dumps(self.value)
        self.sl_tmx[0] = json.dumps([False, self.availability, self.server_availability])

    def __len__(self):
        """Method that returns the size of the shared data

        Returns:
            int: size of the shared data
        """
        self._checkServerAvailability()

        if not self.server_availability:# and self.server_availability_ls:
            print("INFO: Server unavailable, restarting shared memory space.")
            self.server_availability_ls = False
            self.restart()

        self.value = json.loads(self.sl[0])

        return self.value.__len__()

    def __contains__(self, key):
        """Method to check if an element is into the shared data

        Args:
            key ([type]): Element to find

        Returns:
            bool: boolean to determine if the element is or not into the shared data
        """
        self._checkServerAvailability()

        if not self.server_availability:# and self.server_availability_ls:
            print("INFO: Server unavailable, restarting shared memory space.")
            self.server_availability_ls = False
            self.restart()

        self.value = json.loads(self.sl[0])

        return self.value.__contains__(key)

    def __delitem__(self, key):
        """Method to remove an element from the shared data

        Args:
            key ([type]): Element to remove
        """
        self._checkServerAvailability()

        if not self.server_availability:# and self.server_availability_ls:
            print("INFO: Server unavailable, restarting shared memory space.")
            self.server_availability_ls = False
            self.restart()

        start = time.time()

        while json.loads(self.sl_tmx[0])[0]:
            if (time.time() - start) > self.timeout:
                print("WARNING: timeout MUTEX.")
                return

        self.sl_tmx[0] = json.dumps([True, self.availability, self.server_availability])
        self.value = json.loads(self.sl[0])

        self.value.__delitem__(key)

        self.sl[0] = json.dumps(self.value)
        self.sl_tmx[0] = json.dumps([False, self.availability, self.server_availability])

    def getStatus(self) -> str:
        """Method that return shared memory state

        Returns:
            str: shared memory state
        """
        return self.state

    def getAvailability(self) -> [bool, bool]:
        """Method that return the availability of Client and Server

        Returns:
            [bool, bool]: Client and Server availability status
        """
        self._checkServerAvailability()

        return self.availability, self.server_availability

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
        if self.state == "Started":
            print("INFO: Client already started.")
            return

        self.state = "Started"
        self.availability = True

        try:
            self.sl = shared_memory.ShareableList([json.dumps(self.value)], name=self.name,)
            self.sl_tmx = shared_memory.ShareableList([json.dumps([False, self.availability, self.server_availability])], name=self.name + "_tmx")
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
        if self.state == "Stopped":
            print("INFO: Client already stopped.")
            return

        self.state = "Stopped"
        self.availability = False
        self.sl_tmx[0] = json.dumps([False, self.availability, self.server_availability])

        self.close()
        self.unlink()

    def __repr__(self):
        """Redefined method to print value of the Client Class instance

        Returns:
            str: printable value of Client Class instance
        """
        self._checkServerAvailability()

        s = "Client: " + self.name + "\n"\
            + "\tStatus: " + self.state + "\n"\
            + "\tAvailable: " + self.availability.__repr__() + "\n"\
            + "\tServer Available: " + self.server_availability.__repr__() + "\n"\
            + "\tValue: " + self.value.__repr__()

        return s