'''
File: Client.py
Created Date: Wednesday, July 3rd 2020, 8:16:24 pm
Author: Zentetsu

----

Last Modified: Thu Jul 02 2020
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
2020-07-02	Zen	Adding exception and json reader
2020-07-01	Zen	Creating file and drafting class
'''


from .SMErrorType import SMErrorType, MultiInput
from multiprocessing import shared_memory
import json


class Client:
    def __init__(self, name, value=None, path=None, size=10):
        if value is None and path is None or value is not None and path is not None:
            raise MultiInput
        elif value is None:
            self.value = self._initValueByJSON(path)
        else:
            self.value = value
            self.size = size

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
        elif type(value) is str:
            value = value
        elif value is int or type(value) is int:
            value = 0
        elif value is float or type(value) is float:
            value = 0.0
        elif value is bool or type(value) is bool:
            value = False
        elif value is dict or type(value) is dict:
            value = json.dumps(value)
        else:
            raise SMErrorType(list)

        return value     

    def _initSharedMemory(self):
        if self.value is dict or self.value is list:
            raise SMErrorType(self.value)
        elif type(self.value) is type:
            self.value = self._checkValue(self.value)
        elif type(self.value) is list:
            if True in [type(x) is list for x in self.value]:
                raise SMErrorType(list)
            else:
                for i in range(0, len(self.value)):
                    self.value[i] = self._checkValue(self.value[i])

        self.sl = shared_memory.ShareableList(self.value, name=self.name)

    def close(self):
        self.sl.shm.close()

    def unlink(self):
        self.sl.shm.unlink()

    def stop(self):
        self.close()
        self.unlink()

    def __repr__(self):
        s = "Client: " + self.name + "\n" + "Value: " + self.value.__repr__()
    
        return s