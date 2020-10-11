'''
File: Server.py
Created Date: Wednesday, July 3rd 2020, 8:16:32 pm
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
2020-10-11	Zen	Server now able to run without Client
2020-10-11	Zen	Updating overloaded methods for simple type
2020-09-17	Zen	Adding overloaded methods
2020-07-23	Zen	Fix availability when checking availability
2020-07-18	Zen	Adding method to get access to data availability information
2020-07-18	Zen	Adding method to check data availability
2020-07-13	Zen	Adding getStatus, connect and reconnect methods
2020-07-13	Zen	Adding comments
2020-07-03	Zen	Correction of data acquisition
2020-07-03	Zen	Server implementation
2020-07-01	Zen	Creating file
'''

from .SMError import SMTypeError, SMSizeError, SMNotDefined
from multiprocessing import shared_memory
import json
import time
import sys


class Server:
    """Client class focused on receiving data from Client
    """
    def __init__(self, name, timeout=10):
        """Class constructor

        Args:
            name (str): name of the existing shared memory
            timeout (int, optional): mutex timeout. Defaults to 10.

        Raises:
            SMNotDefined: raise an error when the shared memory with this name isn't defined
        """
        self.name = name
        self.timeout = timeout

        self.connect()

        # try:
        #     self.sl = shared_memory.ShareableList(name=self.name)
        #     self.sl_tmx = shared_memory.ShareableList(name=self.name + "_tmx")
        # except FileNotFoundError:
        #     raise SMNotDefined(self.name)

        # self.availability = True
        # self.sl_tmx[0] = json.dumps([json.loads(self.sl_tmx[0])[0], json.loads(self.sl_tmx[0])[1], self.availability])
        # self.client_availability = json.loads(self.sl_tmx[0])[1]
        # self.size = sys.getsizeof(json.loads(self.sl[0]))
        # self.type = type(json.loads(self.sl[0]))
        # self.value = json.loads(self.sl[0])
        # self.state = "Connected"

    def _checkClientAvailability(self):
        """Method to get the Client's availability
        """
        try:
            self.client_availability = json.loads(self.sl_tmx[0])[1]
        except:
            self.client_availability = False
            self.state = "Disconnected"

    # @PendingDeprecationWarning
    def getValue(self):
        """Method to return the shared value

        Returns:
            [type]: return data from the shared space
        """
        self._checkClientAvailability()

        if not self.client_availability:
            print("WARNING: Unable to get data due to the Client's unavailability.")
        else:
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
        self._checkClientAvailability()

        if not self.client_availability:
            print("WARNING: Unable to update data due to the Client's unavailability.")
            return

        start = time.time()

        while json.loads(self.sl_tmx[0])[0]:
            if (time.time() - start) > self.timeout:
                print("WARNING: timeout MUTEX.")
                return

        self.sl_tmx[0] = json.dumps([True, self.client_availability, self.availability])
        self.value = json.loads(self.sl[0])

        if type(n_value) is not self.type:
            raise SMTypeError

        if sys.getsizeof(n_value) > self.size:
            raise SMSizeError

        self.value = n_value
        self.sl[0] = json.dumps(self.value)
        self.sl_tmx[0] = json.dumps([False, self.client_availability, self.availability])

    def __getitem__(self, key):
        """Method to get item value from the shared data

        Args:
            key ([type]): key
        """
        self._checkClientAvailability()

        if not self.client_availability:
            print("WARNING: Unable to get data due to the Client's unavailability.")
        else:
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

        self._checkClientAvailability()

        if not self.client_availability:
            print("WARNING: Unable to update data due to the Client's unavailability.")
            return

        start = time.time()

        while json.loads(self.sl_tmx[0])[0]:
            if (time.time() - start) > self.timeout:
                print("WARNING: timeout MUTEX.")
                return

        self.sl_tmx[0] = json.dumps([True, self.client_availability, self.availability])
        self.value = json.loads(self.sl[0])

        if self.type == dict:
            if type(key) is int:
                key = str(key)
            self.value[key] = value
        elif self.type == list:
            self.value[key] = value
        else:
            self.value = value

        self.sl[0] = json.dumps(self.value)
        self.sl_tmx[0] = json.dumps([False, self.client_availability, self.availability])

    def __len__(self):
        """Method that returns the size of the shared data

        Returns:
            int: size of the shared data
        """
        if self.type == list:
            raise TypeError("Data shared type is list not dict.")

        self._checkClientAvailability()

        self.value = json.loads(self.sl[0])

        return self.value.__len__()

    def __contains__(self):
        """Method to check if an element is into the shared data

        Returns:
            bool: boolean to determine if the element is or not into the shared data
        """
        if self.type == list:
            raise TypeError("Data shared type is list not dict.")

        self._checkClientAvailability()

        self.value = json.loads(self.sl[0])

        return self.value.__contains__()

    def __delitem__(self, key):
        """Method to remove an element from the shared data

        Args:
            key ([type]): Element to remove
        """
        if self.type == list:
            raise TypeError("Data shared type is list not dict.")

        self._checkClientAvailability()

        if not self.client_availability:
            print("WARNING: Unable to update data due to the Client's unavailability.")
            return

        start = time.time()

        while json.loads(self.sl_tmx[0])[0]:
            if (time.time() - start) > self.timeout:
                print("WARNING: timeout MUTEX.")
                return

        self.sl_tmx[0] = json.dumps([True, self.client_availability, self.availability])
        self.value = json.loads(self.sl[0])

        self.value.__delitem__(key)

        self.sl[0] = json.dumps(self.value)
        self.sl_tmx[0] = json.dumps([False, self.client_availability, self.availability])

    def getStatus(self) -> str:
        """Method that return shared memory state

        Returns:
            str: shared memory state
        """
        return self.state

    def getAvailability(self) -> [bool, bool]:
        """Method that return the availability of Server and Client

        Returns:
            [bool, bool]: Server and Client availability status
        """
        self._checkClientAvailability()

        return self.availability, self.client_availability

    def close(self):
        """Method to close the shared space
        """
        try:
            self.sl.shm.close()
            self.sl_tmx.shm.close()
        except FileNotFoundError:
            pass
        except Exception:
            print("WARNING: Client doesn't exist.")

    def unlink(self):
        """Method to remove the shared space from the memory
        """
        try:
            self.sl.shm.unlink()
            self.sl_tmx.shm.unlink()
        except FileNotFoundError:
            pass
        except Exception:
            print("WARNING: Client doesn't exist.")

    # def connect(self):
    #     """Method that connect Server to the Client shared memory
    #     """
    #     try:
    #         self.state = "Connected"
    #         self.availability = True

    #         self.sl = shared_memory.ShareableList(name=self.name)
    #         self.sl_tmx = shared_memory.ShareableList(name=self.name + "_tmx")

    #         self.value = json.loads(self.sl[0])
    #         self.sl_tmx[0] = json.dumps([json.loads(self.sl_tmx[0])[0], json.loads(self.sl_tmx[0])[1], self.availability])
    #     except Exception:
    #         self.state = "Disconnected"

    def connect(self):
        """Method that connect Server to the Client shared memory
        """
        try:
            self.sl = shared_memory.ShareableList(name=self.name)
            self.sl_tmx = shared_memory.ShareableList(name=self.name + "_tmx")

            self.availability = True
            self.sl_tmx[0] = json.dumps([json.loads(self.sl_tmx[0])[0], json.loads(self.sl_tmx[0])[1], self.availability])
            self.client_availability = json.loads(self.sl_tmx[0])[1]
            self.size = sys.getsizeof(json.loads(self.sl[0]))
            self.type = type(json.loads(self.sl[0]))
            self.value = json.loads(self.sl[0])
            self.state = "Connected"
        except Exception:
            self.sl = None
            self.sl_tmx = None

            self.availability = True
            self.client_availability = False
            self.size = 0
            self.type = None
            self.value = None
            self.state = "Disconnected"
            print("WARNING: Client not available.")

    def reconnect(self):
        """Method to reconnect to the shared memory
        """
        self.stop()
        self.connect()

    def stop(self):
        """Method that calls stop and unlink method
        """
        if self.state == "Disconnected":
            print("INFO: Client already disconnected.")
            return

        self.state = "Disconnected"
        self.availability = False
        self.sl_tmx[0] = json.dumps([json.loads(self.sl_tmx[0])[0], json.loads(self.sl_tmx[0])[1], self.availability])

        self.close()
        self.unlink()

    def __repr__(self):
        """Redefined method to print value of the Server Class instance

        Returns:
            str: printable value of Server Class instance
        """
        self._checkClientAvailability()

        s = "Server: " + self.name + "\n"\
            + "\tStatus: " + self.state + "\n"\
            + "\tAvailable: " + self.availability.__repr__() + "\n"\
            + "\tClient available: " + self.client_availability.__repr__() + "\n"\
            + "\tValue: " + self.value.__repr__()

        return s