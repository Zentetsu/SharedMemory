'''
File: Client.py
Created Date: Wednesday, July 3rd 2020, 8:16:24 pm
Author: Zentetsu

----

Last Modified: Wed Jul 01 2020
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
2020-07-01	Zen	Creating file and drafting class
'''


from multiprocessing import shared_memory


class Client:
    def __init__(self, name, value=None, path=None, size=10):
        if value is None and path is None or value is not None and path is not None:
            print("ERROR")
            exit(1)
            #TODO Adding try catch
        elif value is None:
            self.by_path = True
            self.value = self._InitValueByJSON(path)
        else:
            self.by_path = False
            self.value = value
            self.size = size

        self.name = name

        self._InitSharedMemory()

    def _InitValueByJSON(self, path):
        pass
        #TODO JSON reader

    def _InitSharedMemory(self):
        if self.by_path:
            pass
        elif self.value is dict or self.value is list:
            print("ERROR")
            exit(1)
            #TODO Adding try catch
        elif type(self.value) is type:
            if self.value is str:
                self.value = " " * self.size
            elif self.value is int:
                self.value = 0
            elif self.value is float:
                self.value = 0.0
            else:
                self.value = False
        elif type(self.value) is dict:
            print("ERROR")
            exit(1)
            #TODO Adding try catch
        elif type(self.value) is list and True in [type(x) is list for x in self.value]:
            print("ERROR")
            exit(1)
            #TODO Adding try catch

        self.sl = shared_memory.ShareableList(self.value, name=self.name)

    def close(self):
        try:
            self.sl.shm.close()
        except Exception:
            pass

    def unlink(self):
        try:
            self.sl.shm.unlink()
        except Exception:
            pass

    def stop(self):
        self.close()
        self.unlink()

    def __repr__(self):
        s = "Client: " + self.name + "\n" + "Value: " + self.value.__repr__()
    
        return s