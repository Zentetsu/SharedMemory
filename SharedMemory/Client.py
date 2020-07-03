'''
File: Client.py
Created Date: Wednesday, July 3rd 2020, 8:16:24 pm
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
2020-07-03	Zen	Data simplification
2020-07-02	Zen	Adding exception and json reader
2020-07-01	Zen	Creating file and drafting class
'''


from .SMError import SMErrorType, SMSizeError, MultiInput
from multiprocessing import shared_memory
import json
import sys


class Client:
    def __init__(self, name, value=None, path=None, size=10):
        if value is None and path is None or value is not None and path is not None:
            raise MultiInput
        elif value is None:
            self.value = self._initValueByJSON(path)
        else:
            self.value = value
            self.size = size


        self.type = type(self.value)
        self.name = name

        self._initSharedMemory()

    def _initValueByJSON(self, path):
        json_file = open(path)        
        value = json.load(json_file)
        json_file.close()

        return value

    def _checkValue(self, value):
        if value is str:
            value = " " * self.size
        elif value is int:
            value = 0
        elif value is float:
            value = 0.0
        elif value is bool:
            value = False
        elif value is dict or value is list:
            raise SMErrorType(value)

        return value

    def _initSharedMemory(self):
        if type(self.value) is list and type in [type(e) for e in self.value]:
            for i in range(0, len(self.value)):
                self.value[i] = self._checkValue(self.value[i])

        self.size = sys.getsizeof(self.value)

        self.sl = shared_memory.ShareableList([json.dumps(self.value)], name=self.name)

    def getValue(self):
        return self.value

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
        s = "Client: " + self.name + "\n" + "Value: " + self.value.__repr__()
    
        return s