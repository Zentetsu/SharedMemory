'''
File: test_server.py
Created Date: Wednesday, July 3rd 2020, 8:17:04 pm
Author: Zentetsu

----

Last Modified: Wed Oct 18 2023
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
2023-10-18	Zen	Updating test: checking manager
'''

# import sys
# sys.path.insert(0, "../")

from SharedMemory.SharedMemory import SharedMemory
import contextlib

def test_connection():
    print("Create Server instance without Client:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            s = SharedMemory("test1", log="./test_server.log", client=False)
            s.getValue()
            s.close()
            assert "test1" not in SharedMemory.getSharedMemorySpace()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_connection2():
    print("Create Server instance with Client(after):", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test2", "azerty", log="./test_server.log", client=True)
            s = SharedMemory("test2", log="./test_server.log", client=False)
            res = c.getAvailability() and s.getAvailability()
            c.close()
            s.close()
            assert "test2" not in SharedMemory.getSharedMemorySpace() and res
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_value():
    print("Server check value \"azerty\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test3", "azerty", log="./test_server.log", client=True)
            s = SharedMemory("test3", log="./test_server.log", client=False)
            res = s.getValue() == "azerty"
            c.close()
            s.close()
            assert "test3" not in SharedMemory.getSharedMemorySpace() and res
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_editValue():
    print("Server edit value \"azerty\" to \"ytreza\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test4", "azerty", log="./test_server.log", client=True)
            s = SharedMemory("test4", log="./test_server.log", client=False)
            s.setValue("ytreza")
            res1 = c.getValue() == "ytreza"
            res2 = c[0] == "ytreza"
            c.close()
            s.close()
            assert "test4" not in SharedMemory.getSharedMemorySpace() and res1 and res2
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_clientStopped():
    print("Server test access value when Client stopped:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test5", "azerty", log="./test_server.log", client=True)
            s = SharedMemory("test5", log="./test_server.log", client=False)
            c.close()
            s.setValue("toto")
            res1 = s.getValue() == None
            s.close()
            assert "test5" not in SharedMemory.getSharedMemorySpace() and res1
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_serverStopped():
    print("Client test access value when Server stopped:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test6", "azerty", log="./test_server.log", client=True)
            s = SharedMemory("test6", log="./test_server.log", client=False)
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
            assert "test6" not in SharedMemory.getSharedMemorySpace()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_multiStop():
    print("Server test mutli stop:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test7", "azerty", log="./test_server.log", client=True)
            s = SharedMemory("test7", log="./test_server.log", client=False)
            s.close()
            s.close()
            c.close()
            assert "test7" not in SharedMemory.getSharedMemorySpace()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_availability():
    print("Check availability for Client and Server:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test8", "azerty", log="./test_server.log", client=True)
            s = SharedMemory("test8", log="./test_server.log", client=False)
            res1 = c.getAvailability() == True
            res2 =  s.getAvailability() == True
            s.close()
            c.close()
            assert "test8" not in SharedMemory.getSharedMemorySpace() and res1 and res2
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_serverFirst():
    print("Create Server first:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            s = SharedMemory("test9", log="./test_server.log", client=False)
            c = SharedMemory("test9", "azerty", log="./test_server.log", client=True)
            res1 = c.getAvailability() == True
            res2 =  s.getAvailability() == True
            assert res1
            assert res2
            assert s.getValue() == c.getValue()
            s.close()
            c.close()
            assert "test9" not in SharedMemory.getSharedMemorySpace()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False


print("-"*10)
test_connection()
test_connection2()
test_value()
test_editValue()
test_clientStopped()
test_serverStopped()
test_multiStop()
test_availability()
test_serverFirst()
print("-"*10)