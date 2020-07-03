'''
File: test_client.py
Created Date: Wednesday, July 3rd 2020, 8:16:57 pm
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
2020-07-03	Zen	Adding new tests
2020-07-02	Zen	Adding test with json file
2020-07-01	Zen	Creating file
'''


from SharedMemory.Client import Client

def test_str():
    c = Client("test", "azerty")
    assert type(c.getValue()) is str
    c.stop()

def test_int():
    c = Client("test", 1)
    assert type(c.getValue()) is int
    assert c.getValue() == 1
    c.stop()

def test_float():
    c = Client("test", 1.2)
    assert type(c.getValue()) is float
    assert c.getValue() == 1.2
    c.stop()

def test_bool():
    c = Client("test", True)
    assert type(c.getValue()) is bool
    assert c.getValue()
    c.stop()

def test_dict1():
    c = Client("test", {'a': 1})
    assert type(c.getValue()) is dict
    assert c.getValue()['a'] == 1
    c.stop()

def test_list1():
    c = Client("test", [0, 1])
    assert type(c.getValue()) is list
    assert c.getValue()[0] == 0
    assert c.getValue()[1] == 1
    c.stop()

# def test_1():
#     # c = Client("test", (0, 1))
#     # assert type(c.getValue()) is int
#     # c.stop()
#     pass

def test_list2():
    c = Client("test", [int, bool, str])
    assert type(c.getValue()) is list
    assert type(c.getValue()[0]) is int
    assert type(c.getValue()[0]) is bool
    assert type(c.getValue()[0]) is str
    c.stop()

def test_list3():
    c = Client("test", [int, 10.2, str])
    assert type(c.getValue()) is list
    assert type(c.getValue()[0]) is int
    assert type(c.getValue()[0]) is float
    assert type(c.getValue()[0]) is str
    c.stop()

def test_file():
    c = Client("test", path="./tests/test.json")
    assert type(c.getValue()) is dict
    c.stop()
