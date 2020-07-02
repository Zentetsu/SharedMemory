'''
File: SMErrorType.py
Created Date: Thursday, July 4th 2020, 9:36:57 pm
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
2020-07-02	Zen	Creating file
'''


class SMErrorType(Exception):
    def __init__(self, type, message=" is not accepted."):
        self.type = type
        self.message = str(self.type) + message
        super().__init__(self.message)

class MultiInput(Exception):
    def __init__(self, message="value or path must be None."):
        self.message = message
        super().__init__(self.message)