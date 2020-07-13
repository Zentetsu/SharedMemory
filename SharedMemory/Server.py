'''
File: Server.py
Created Date: Wednesday, July 3rd 2020, 8:16:32 pm
Author: Zentetsu

----

Last Modified: Mon Jul 13 2020
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

        try:
            self.sl = shared_memory.ShareableList(name=self.name)
            self.sl_tmx = shared_memory.ShareableList(name=self.name + "_tmx")
        except FileNotFoundError:
            raise SMNotDefined(self.name)

        self.timeout = timeout
        self.size = sys.getsizeof(json.loads(self.sl[0]))
        self.type = type(json.loads(self.sl[0]))
        self.state = "Disconnected"

    def getValue(self):
        """Method to return the shared value

        Returns:
            [type]: return data from the shared space
        """
        return json.loads(self.sl[0])

    def updateValue(self, n_value):
        """Method to update data fo the shared space

        Args:
            n_value ([type]): new version of data

        Raises:
            SMTypeError: raise en error when the new value is not correspoding to the initial type
            SMSizeError: raise an error when the size of the new value exced the previous one
        """
        start = time.time()

        while json.loads(self.sl_tmx[0]):
            if (time.time() - start) > self.timeout:
                print("WARNING: timeout MUTEX.")
                return

        self.sl_tmx[0] = json.dumps(True)

        if type(n_value) is not self.type:
            raise SMTypeError

        if sys.getsizeof(n_value) > self.size:
            raise SMSizeError

        self.sl[0] = json.dumps(n_value)
        self.sl_tmx[0] = json.dumps(False)

    def getStatus(self) -> str:
        """Method that return shared memory state

        Returns:
            str: shared memory state
        """
        return self.state

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

    def connect(self):
        """Method that connect Server to the Client shared memory
        """
        self.state = "Connected"

        try:
            self.sl = shared_memory.ShareableList(name=self.name)
            self.sl_tmx = shared_memory.ShareableList(name=self.name + "_tmx")
        except Exception:
            pass

    def reconnect(self):
        """Method to reconnect to the shared memory
        """
        self.stop()
        self.connection()

    def stop(self):
        """Method that calls stop and unlink method
        """
        self.state = "Disconnected"

        self.close()
        self.unlink()

    def __repr__(self):
        """Redefined method to print value of the Server Class instance

        Returns:
            str: printable value of Server Class instance
        """
        s = "Server: " + self.name + "\n" + "Status: " + self.state + "\n" + "Value: " + json.loads(self.sl[0]).__repr__()

        return s