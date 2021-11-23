'''
File: test_server.py
Created Date: Wednesday, July 3rd 2020, 8:17:04 pm
Author: Zentetsu

----

Last Modified: Wed Nov 24 2021
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
2021-10-19	Zen	Adaptation to the new version
2020-12-10	Zen	Updating test for log file
2020-10-12	Zen	Updating test
2020-07-23	Zen	Adding test for availability
2020-07-18	Zen	Adding some tests
2020-07-03	Zen	Updating test file
2020-07-01	Zen	Creating file
'''

# import sys
# sys.path.insert(0, "../")

from SharedMemory.SharedMemory import SharedMemory
import contextlib

def test_connection():
    print("Create Server instance without Client:", end=" ")
    try:
        # with contextlib.redirect_stdout(None):
        s = SharedMemory("test1", log="./test_server.log", exist=True)
        s.close()
        print("FAILED")
    except:
        assert True
        print("SUCCESSED")

def test_connection2():
    print("Create Server instance with Client(after):", end=" ")
    try:
        # with contextlib.redirect_stdout(None):
        c = SharedMemory("test27", "azerty", log="./test_server.log")
        s = SharedMemory("test27", log="./test_server.log", exist=True)
        res = c.getAvailability() and s.getAvailability()
        c.close()
        s.close()
        assert res
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_connection3():
    print("Create Server instance with Client(before):", end=" ")
    try:
        # with contextlib.redirect_stdout(None):
        s = SharedMemory("test31", log="./test_server.log", exist=True)
        c = SharedMemory("test31", "azerty", log="./test_server.log")
        res = s.getAvailability() and c.getAvailability()
        c.close()
        s.close()
        assert res
        print("FAILED")
    except:
        print("SUCCESSED")
        assert True

def test_value():
    print("Server check value \"azerty\":", end=" ")
    try:
        # with contextlib.redirect_stdout(None):
        c = SharedMemory("test41", "azerty", log="./test_server.log")
        s = SharedMemory("test41", log="./test_server.log", exist=True)
        res = s.getValue() == "azerty"
        c.close()
        s.close()
        assert res
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_editValue():
    print("Server edit value \"azerty\" to \"ytreza\":", end=" ")
    try:
        # with contextlib.redirect_stdout(None):
        c = SharedMemory("test51", "azerty", log="./test_server.log")
        s = SharedMemory("test51", log="./test_server.log", exist=True)
        s.setValue("ytreza")
        res1 = c.getValue() == "ytreza"
        res2 = c[0]== "ytreza"
        c.close()
        s.close()
        assert res1
        assert res2
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_clientStopped():
    print("Server test access value when Client stopped:", end=" ")
    try:
        # with contextlib.redirect_stdout(None):
        c = SharedMemory("test62", "azerty", log="./test_server.log")
        s = SharedMemory("test62", log="./test_server.log", exist=True)
        c.close()
        s.setValue("toto")
        res1 = s.getValue() == None
        s.close()
        assert res1
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_serverStopped():
    print("Client test access value when Server stopped:", end=" ")
    try:
        # with contextlib.redirect_stdout(None):
        c = SharedMemory("test8", "azerty", log="./test_server.log")
        s = SharedMemory("test8", log="./test_server.log", exist=True)
        s.close()
        c.setValue("toto")
        assert c.getValue() == None
        assert c[0] == None
        c.restart()
        c.setValue("toto")
        assert c.getValue() == "toto"
        assert c[0] == "toto"
        s.restart()
        assert s.getValue() == "toto"
        assert s[0] == "toto"
        c.close()
        s.close()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_multiStop():
    print("Server test mutli stop:", end=" ")
    try:
        # with contextlib.redirect_stdout(None):
        c = SharedMemory("test9", "azerty", log="./test_server.log")
        s = SharedMemory("test9", log="./test_server.log", exist=True)
        s.close()
        s.close()
        c.close()
        assert True
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_availability():
    print("Check availability for Client and Server:", end=" ")
    try:
        # with contextlib.redirect_stdout(None):
        c = SharedMemory("test10", "azerty", log="./test_server.log")
        s = SharedMemory("test10", log="./test_server.log", exist=True)
        res1 = c.getAvailability() == True
        res2 =  s.getAvailability() == True
        s.close()
        c.close()
        assert res1
        assert res2
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

print("-"*10)
test_connection()
test_connection2()
test_connection3()
test_value()
test_editValue()
test_clientStopped()
test_serverStopped()
test_multiStop()
test_availability()
print("-"*10)