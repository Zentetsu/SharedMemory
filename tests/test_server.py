'''
File: test_server.py
Created Date: Wednesday, July 3rd 2020, 8:17:04 pm
Author: Zentetsu

----

Last Modified: Thu Oct 15 2020
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
2020-10-12	Zen	Updating test
2020-07-23	Zen	Adding test for availability
2020-07-18	Zen	Adding some tests
2020-07-03	Zen	Updating test file
2020-07-01	Zen	Creating file
'''

# from context import Client, Server
from SharedMemory.Client import Client
from SharedMemory.Server import Server
import contextlib

def test_connection():
    print("Create Server instance without Client:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            s = Server("test1")
            s.stop()
        assert True
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_connection2():
    print("Create Server instance with Client(after):", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test2", "azerty")
            s = Server("test2")
            assert s.getAvailability()[0] and s.getAvailability()[1]
            c.stop()
            s.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_connection3():
    print("Create Server instance with Client(before):", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            s = Server("test3")
            c = Client("test3", "azerty")
            s.connect()
            assert s.getAvailability()[0] and s.getAvailability()[1]
            c.stop()
            s.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_value():
    print("Server check value \"azerty\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test3", "azerty")
            s = Server("test3")
            assert s.getValue() == "azerty"
            c.stop()
            s.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_editValue():
    print("Server edit value \"azerty\" to \"ytreza\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test3", "azerty")
            s = Server("test3")
            s.updateValue("ytreza")
            assert c.getValue() == "ytreza"
            assert c[0]== "ytreza"
            c.stop()
            s.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_clientStopped():
    print("Server test access value when Client stopped:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test4", "azerty")
            s = Server("test4")
            c.stop()
            s.updateValue("toto")
            assert s.getValue() == "azerty"
            assert s[0] == "azerty"
            s.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_serverStopped():
    print("Client test access value when Server stopped:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test5", "azerty")
            s = Server("test5")
            s.stop()
            c.updateValue("toto")
            assert c.getValue() == "toto"
            assert c[0] == "toto"
            s.connect()
            c.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_multiStop():
    print("Server test mutli stop:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test6", "azerty")
            s = Server("test6")
            s.stop()
            s.stop()
            c.stop()
        assert True
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_availability():
    print("Check availability for Client and Server:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test7", "azerty")
            s = Server("test7")
            assert c.getAvailability() == (True, True)
            assert s.getAvailability() == (True, True)
            s.stop()
            c.stop()
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