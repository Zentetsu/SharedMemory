'''
File: test_client.py
Created Date: Wednesday, July 3rd 2020, 8:16:57 pm
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
2020-10-11	Zen	Updating test
2020-09-17	Zen	Adding test for overloaded methods
2020-07-18	Zen	Adding new tests
2020-07-03	Zen	Adding new tests
2020-07-02	Zen	Adding test with json file
2020-07-01	Zen	Creating file
'''

# from context import Client
from SharedMemory.Client import Client
import contextlib

def test_str():
    print("Create Client instance containing a \"string\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test1", "azerty")
            assert type(c.getValue()) is str
            assert type(c[0]) is str
            c.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_int():
    print("Create Client instance containing an \"int\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test2", 1)
            assert type(c.getValue()) is int
            assert type(c[0]) is int
            assert c.getValue() == 1
            assert c[0] == 1
            c.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_float():
    print("Create Client instance containing a \"float\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test3", 1.2)
            assert type(c.getValue()) is float
            assert type(c[0]) is float
            assert c.getValue() == 1.2
            assert c[0] == 1.2
            c.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_bool():
    print("Create Client instance containing a \"boolean\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test4", True)
            assert type(c.getValue()) is bool
            assert type(c[0]) is bool
            assert c.getValue()
            assert c[0]
            c.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_dict1():
    print("Create Client instance containing a \"dict\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test5", {'a': 1})
            assert type(c.getValue()) is dict
            assert c.getType() is dict
            assert c.getValue()['a'] == 1
            assert c['a'] == 1
            c.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_list1():
    print("Create Client instance containing a \"list\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test6", [0, 1])
            assert type(c.getValue()) is list
            assert c.getType() is list
            assert c.getValue()[0] == 0
            assert c.getValue()[1] == 1
            assert c[0] == 0
            assert c[1] == 1
            c.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_list2():
    print("Create Client instance containing a \"[int, bool, str]\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test7", [int, bool, str])
            assert type(c.getValue()) is list
            assert c.getType() is list
            assert type(c.getValue()[0]) is int
            assert type(c.getValue()[1]) is bool
            assert type(c.getValue()[2]) is str
            assert type(c[0]) is int
            assert type(c[1]) is bool
            assert type(c[2]) is str
            c.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_list3():
    print("Create Client instance containing a \"[int, 10.2, str]\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test8", [int, 10.2, str])
            assert type(c.getValue()) is list
            assert c.getType() is list
            assert type(c.getValue()[0]) is int
            assert type(c.getValue()[1]) is float
            assert type(c.getValue()[2]) is str
            assert type(c[0]) is int
            assert type(c[1]) is float
            assert type(c[2]) is str
            c.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_file():
    print("Create Client instance from JSON file:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test9", path="./tests/test.json")
            assert type(c.getValue()) is dict
            c.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_newValue():
    print("Update Client value:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test10", 1)
            c.updateValue(12)
            assert c.getValue() == 12
            assert c[0] == 12
            c.stop()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_stop():
    print("Stop Client:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test11", 1)
            c.stop()
        assert True
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_call():
    print("Stop Client 2:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test12", 1)
            c.stop()
            c.stop()
        assert True
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_call2():
    print("Stop Client 3:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test13", 1)
            c.start()
            c.stop()
        assert True
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_valueAccess():
    print("Deleting value from overloaded method:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = Client("test13", {'0':0, '1':1, '2':2, '3':3})
            c.start()
            del c['0']
            c.stop()
        assert True
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False


print("-"*10)
test_str()
test_int()
test_float()
test_bool()
test_dict1()
test_list1()
test_list2()
test_list3()
test_file()
test_newValue()
test_stop()
test_call()
test_call2()
test_valueAccess()
print("-"*10)