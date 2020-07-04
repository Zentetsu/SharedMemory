'''
File: test_server.py
Created Date: Wednesday, July 3rd 2020, 8:17:04 pm
Author: Zentetsu

----

Last Modified: Sat Jul 04 2020
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
2020-07-03	Zen	Updating test file
2020-07-01	Zen	Creating file
'''


from SharedMemory.Server import Server

while 1:
    try:
        s = Server("test")
        print(s)
        s.stop()
    except:
        break

# s = Server("test")
# print(s)
# s.stop()