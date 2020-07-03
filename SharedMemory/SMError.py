'''
File: SMErrorType.py
Created Date: Thursday, July 4th 2020, 9:36:57 pm
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
2020-07-03	Zen	Adding new exception
2020-07-02	Zen	Creating file
'''


class SMErrorType(Exception):
    def __init__(self, type, message=" is not accepted."):
        self.type = type
        self.message = str(self.type) + message
        super().__init__(self.message)

class SMSizeError(Exception):
    def __init__(self, message="size of new value exceeds the previous one."):
        self.type = type
        self.message = str(self.type) + message
        super().__init__(self.message)

class MultiInput(Exception):
    def __init__(self, message="value xor path must be None."):
        self.message = message
        super().__init__(self.message)

class SMNotDefined(Exception):
    def __init__(self, name, message=None):
        if message is None:
            self.message = "shared memory called '" + name + "' is not defined."
        else: 
            self.message = message

        super().__init__(self.message)