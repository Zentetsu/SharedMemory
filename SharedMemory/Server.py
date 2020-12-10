'''
File: Server.py
Created Date: Wednesday, July 3rd 2020, 8:16:32 pm
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
import logging
import json
import time
import sys


class Server:
    """Client class focused on receiving data from Client
    """
    def __init__(self, name:str, timeout:int=10, log:str=None):
        """Class constructor

        Args:
            name (str): name of the existing shared memory
            timeout (int, optional): mutex timeout. Defaults to 10.

        Raises:
            SMNotDefined: raise an error when the shared memory with this name isn't defined
        """
        self.__name = name
        self.__timeout = timeout
        self.__log = log

        if self.__log is not None:
            logging.basicConfig(filename=self.__log, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s', level=logging.DEBUG)
            self.__writeLog(0, "Starting SharedMemory Server...")

        self.connect()

    def __checkClientAvailability(self):
        """Method to get the Client's availability
        """
        try:
            self.__client_availability = json.loads(self.__sl_tmx[0])[1]
        except:
            self.__client_availability = False
            self.__state = "Disconnected"

    # @PendingDeprecationWarning
    def getValue(self):
        """Method to return the shared value

        Returns:
            [type]: return data from the shared space
        """
        self.__checkClientAvailability()

        if not self.__client_availability:
            if self.__log is not None:
                self.__writeLog(3, "Unable to get data due to the Client's unavailability.")
            else:
                print("WARNING: Unable to get data due to the Client's unavailability.")
        else:
            self.__value = json.loads(self.__sl[0])

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
        self.__checkClientAvailability()

        if not self.__client_availability:
            if self.__log is not None:
                self.__writeLog(3, "Unable to update data due to the Client's unavailability.")
            else:
                print("WARNING: Unable to get data due to the Client's unavailability.")
            return

        start = time.time()

        while json.loads(self.__sl_tmx[0])[0]:
            if (time.time() - start) > self.__timeout:
                if self.__log is not None:
                    self.__writeLog(3, "timeout MUTEX.")
                else:
                    print("WARNING: timeout MUTEX.")
                return

        self.__sl_tmx[0] = json.dumps([True, self.__client_availability, self.__availability])
        self.__value = json.loads(self.__sl[0])

        if type(n_value) is not self.__type:
            raise SMTypeError

        if sys.getsizeof(n_value) > self.__size:
            raise SMSizeError

        self.__value = n_value
        self.__sl[0] = json.dumps(self.__value)
        self.__sl_tmx[0] = json.dumps([False, self.__client_availability, self.__availability])

    def __getitem__(self, key):
        """Method to get item value from the shared data

        Args:
            key ([type]): key
        """
        self.__checkClientAvailability()

        if not self.__client_availability:
            if self.__log is not None:
                self.__writeLog(3, "Unable to get data due to the Client's unavailability.")
            else:
                print("WARNING: Unable to get data due to the Client's unavailability.")
        else:
            self.__value = json.loads(self.__sl[0])

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
            raise TypeError("Data shared type is list not dict.")

        self.__checkClientAvailability()

        if not self.__client_availability:
            if self.__log is not None:
                self.__writeLog(3, "Unable to update data due to the Client's unavailability.")
            else:
                print("WARNING: Unable to get data due to the Client's unavailability.")
            return

        start = time.time()

        while json.loads(self.__sl_tmx[0])[0]:
            if (time.time() - start) > self.__timeout:
                if self.__log is not None:
                    self.__writeLog(3, "timeout MUTEX.")
                else:
                    print("WARNING: timeout MUTEX.")
                return

        self.__sl_tmx[0] = json.dumps([True, self.__client_availability, self.__availability])
        self.__value = json.loads(self.__sl[0])

        if self.__type == dict:
            if type(key) is int:
                key = str(key)
            self.__value[key] = value
        elif self.__type == list:
            self.__value[key] = value
        else:
            self.__value = value

        self.__sl[0] = json.dumps(self.__value)
        self.__sl_tmx[0] = json.dumps([False, self.__client_availability, self.__availability])

    def __len__(self):
        """Method that returns the size of the shared data

        Returns:
            int: size of the shared data
        """
        if self.__type == list:
            if self.__log is not None:
                self.__writeLog(1, "Data shared type is list not dict.")
            else:
                print("ERROR: Data shared type is list not dict.")
            raise TypeError("Data shared type is list not dict.")

        self.__checkClientAvailability()

        self.__value = json.loads(self.__sl[0])

        return self.__value.__len__()

    def __contains__(self):
        """Method to check if an element is into the shared data

        Returns:
            bool: boolean to determine if the element is or not into the shared data
        """
        if self.__type == list:
            if self.__log is not None:
                self.__writeLog(1, "Data shared type is list not dict.")
            else:
                print("ERROR: Data shared type is list not dict.")
            raise TypeError("Data shared type is list not dict.")

        self.__checkClientAvailability()

        self.__value = json.loads(self.__sl[0])

        return self.__value.__contains__()

    def __delitem__(self, key):
        """Method to remove an element from the shared data

        Args:
            key ([type]): Element to remove
        """
        if self.__type == list:
            if self.__log is not None:
                self.__writeLog(1, "Data shared type is list not dict.")
            else:
                print("ERROR: Data shared type is list not dict.")
            raise TypeError("Data shared type is list not dict.")

        self.__checkClientAvailability()

        if not self.__client_availability:
            if self.__log is not None:
                self.__writeLog(3, "Unable to update data due to the Client's unavailability.")
            else:
                print("WARNING: Unable to get data due to the Client's unavailability.")
            return

        start = time.time()

        while json.loads(self.__sl_tmx[0])[0]:
            if (time.time() - start) > self.__timeout:
                if self.__log is not None:
                    self.__writeLog(3, "timeout MUTEX.")
                else:
                    print("WARNING: timeout MUTEX.")
                return

        self.__sl_tmx[0] = json.dumps([True, self.__client_availability, self.__availability])
        self.__value = json.loads(self.__sl[0])

        self.__value.__delitem__(key)

        self.__sl[0] = json.dumps(self.__value)
        self.__sl_tmx[0] = json.dumps([False, self.__client_availability, self.__availability])

    def getStatus(self) -> str:
        """Method that return shared memory state

        Returns:
            str: shared memory state
        """
        return self.__state

    def getAvailability(self) -> [bool, bool]:
        """Method that return the availability of Server and Client

        Returns:
            [bool, bool]: Server and Client availability status
        """
        self.__checkClientAvailability()

        return self.__availability, self.__client_availability

    def close(self):
        """Method to close the shared space
        """
        try:
            self.__sl.shm.close()
            self.__sl_tmx.shm.close()
        except FileNotFoundError:
            pass
        except Exception:
            if self.__log is not None:
                self.__writeLog(3, "Client doesn't exist.")
            else:
                print("WARNING: Client doesn't exist.")

    def unlink(self):
        """Method to remove the shared space from the memory
        """
        try:
            self.__sl.shm.unlink()
            self.__sl_tmx.shm.unlink()
        except FileNotFoundError:
            pass
        except Exception:
            if self.__log is not None:
                self.__writeLog(3, "Client doesn't exist.")
            else:
                print("WARNING: Client doesn't exist.")

    def connect(self):
        """Method that connect Server to the Client shared memory
        """
        try:
            self.__sl = shared_memory.ShareableList(name=self.__name)
            self.__sl_tmx = shared_memory.ShareableList(name=self.__name + "_tmx")

            self.__availability = True
            self.__sl_tmx[0] = json.dumps([json.loads(self.__sl_tmx[0])[0], json.loads(self.__sl_tmx[0])[1], self.__availability])
            self.__client_availability = json.loads(self.__sl_tmx[0])[1]
            self.__size = sys.getsizeof(json.loads(self.__sl[0]))
            self.__type = type(json.loads(self.__sl[0]))
            self.__value = json.loads(self.__sl[0])
            self.__state = "Connected"
        except Exception:
            self.__sl = None
            self.__sl_tmx = None

            self.__availability = True
            self.__client_availability = False
            self.__size = 0
            self.__type = None
            self.__value = None
            self.__state = "Disconnected"
            if self.__log is not None:
                self.__writeLog(3, "Client not available.")
            else:
                print("WARNING: Client not available.")

    def reconnect(self):
        """Method to reconnect to the shared memory
        """
        self.stop()
        self.connect()

    def stop(self):
        """Method that calls stop and unlink method
        """
        if self.__state == "Disconnected":
            if self.__log is not None:
                self.__writeLog(0, "Client already disconnected.")
            else:
                print("INFO: Client already disconnected.")
            return

        self.__state = "Disconnected"
        self.__availability = False
        self.__sl_tmx[0] = json.dumps([json.loads(self.__sl_tmx[0])[0], json.loads(self.__sl_tmx[0])[1], self.__availability])

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
        """Redefined method to print value of the Server Class instance

        Returns:
            str: printable value of Server Class instance
        """
        self.__checkClientAvailability()

        s = "Server: " + self.__name + "\n"\
            + "\tStatus: " + self.__state + "\n"\
            + "\tAvailable: " + self.__availability.__repr__() + "\n"\
            + "\tClient available: " + self.__client_availability.__repr__() + "\n"\
            + "\tValue: " + self.__value.__repr__()

        return s