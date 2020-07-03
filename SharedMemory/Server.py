'''
File: Server.py
Created Date: Wednesday, July 3rd 2020, 8:16:32 pm
Author: Zentetsu

----

Last Modified: Fri Jul 03 2020
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
2020-07-03	Zen	Server implementation
2020-07-01	Zen	Creating file
'''

from .SMError import SMErrorType, SMSizeError, SMNotDefined
from multiprocessing import shared_memory
import json
import sys


class Server:
    def __init__(self, name):
        self.name = name

        try:
            self.sl = shared_memory.ShareableList(name=self.name)
        except FileNotFoundError:
            raise SMNotDefined(self.name)

        self.value = self.sl
        self.size = sys.getsizeof(json.loads(self.value[0]))

    def getValue(self):
        return json.loads(self.value[0])

    def updateValue(self, n_value):
        if type(n_value) is not self.type:
            raise SMErrorType

        if sys.getsizeof(n_value) > self.size:
            raise SMSizeError

        self.value = n_value

    def close(self):
        try:
            self.sl.shm.close()
        except FileNotFoundError:
            pass
        
    def unlink(self):
        try:
            self.sl.shm.unlink()
        except FileNotFoundError:
            pass

    def stop(self):
        self.close()
        self.unlink()

    def __repr__(self):
        s = "Server: " + self.name + "\n" + "Value: " + json.loads(self.value[0]).__repr__()
    
        return s