'''
File: test_server.py
Created Date: Wednesday, July 3rd 2020, 8:17:04 pm
Author: Zentetsu

----

Last Modified: Sat Jul 18 2020
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
2020-07-18	Zen	Adding some tests
2020-07-03	Zen	Updating test file
2020-07-01	Zen	Creating file
'''

# from context import Client, Server
from SharedMemory.Server import Server

def test_connection():
    c = Client("test1", "azerty")
    try:
        s = Server("test1")
        assert True
    except:
        assert False

    print(c)
    print(s)
    c.stop()
    s.stop()

def test_value():
    c = Client("test2", "azerty")
    s = Server("test2")
    print(c)
    print(s)
    assert s.getValue() == "azerty"
    c.stop()
    s.stop()

def test_edit_value():
    c = Client("test3", "azerty")
    s = Server("test3")
    print(c)
    print(s)
    s.updateValue("toto")
    assert c.getValue() == "toto"
    print(c)
    print(s)
    c.stop()
    s.stop()

def test_client_stopped():
    c = Client("test4", "azerty")
    s = Server("test4")
    print(c)
    print(s)
    c.stop()
    s.updateValue("toto")
    assert s.getValue() == "azerty"
    print(c)
    print(s)
    s.stop()

def test_server_stopped():
    c = Client("test5", "azerty")
    s = Server("test5")
    print(c)
    print(s)
    s.stop()
    c.updateValue("toto")
    assert c.getValue() == "toto"
    print(s)
    print(c)
    s.connect()
    print(c)
    print(s)
    c.stop()

print("-"*10)
test_connection()
print("-"*10)
test_value()
print("-"*10)
test_edit_value()
print("-"*10)
test_client_stopped()
print("-"*10)
test_server_stopped()
print("-"*10)