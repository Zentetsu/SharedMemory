'''
File: test_client.py
Created Date: Wednesday, July 3rd 2020, 8:16:57 pm
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
2020-10-11	Zen	Updating test
2020-09-17	Zen	Adding test for overloaded methods
2020-07-18	Zen	Adding new tests
2020-07-03	Zen	Adding new tests
2020-07-02	Zen	Adding test with json file
2020-07-01	Zen	Creating file
2023-09-08	Zen	Adding numpy test
2023-10-18	Zen	Updating test: checking manager
'''

# import sys
# sys.path.insert(0, "../")

from SharedMemory.SharedMemory import SharedMemory
import contextlib
import numpy as np

def test_str():
    print("Create Client instance containing a \"string\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test1", "azerty", size=1024, client=True)
            assert type(c.getValue()) is str
            assert type(c[0]) is str
            c.close()
            assert "test1" not in SharedMemory.getSharedMemorySpace()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_int():
    print("Create Client instance containing an \"int\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test2", -125, size=1024, client=True)
            res1 = type(c.getValue()) is int
            res2 = type(c[0]) is int
            res3 = c.getValue() == -125
            res4 = c[0] == -125
            c.close()
            assert "test2" not in SharedMemory.getSharedMemorySpace()
            assert res1 and res2 and res3 and res4
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_float():
    print("Create Client instance containing a \"float\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test3", -1.2, size=1024, client=True)
            res1 = type(c.getValue()) is float
            res2 = type(c[0]) is float
            res3 = c.getValue() == -1.2
            res4 = c[0] == -1.2
            c.close()
            assert "test3" not in SharedMemory.getSharedMemorySpace()
            assert res1 and res2 and res3 and res4
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_bool():
    print("Create Client instance containing a \"boolean\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test4", True, size=1024, client=True)
            res1 = type(c.getValue()) is bool
            res2 = type(c[0]) is bool
            res3 = c.getValue()
            res4 = c[0]
            c.close()
            assert "test4" not in SharedMemory.getSharedMemorySpace()
            assert res1 and res2 and res3 and res4
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_dict():
    print("Create Client instance containing a \"dict\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test5", {'a': 1}, size=1024, client=True)
            res1 = type(c.getValue()) is dict
            res2 = c.getType() is dict
            res3 = c.getValue()['a'] == 1
            res4 = c['a'] == 1
            c.close()
            assert "test5" not in SharedMemory.getSharedMemorySpace()
            assert res1 and res2 and res3 and res4
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_list():
    print("Create Client instance containing a \"list\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test6", [0, 1], size=1024, client=True)
            res1 = type(c.getValue()) is list
            res2 = c.getType() is list
            res3 = c.getValue()[0] == 0
            res4 = c.getValue()[1] == 1
            res5 = c[0] == 0
            res6 = c[1] == 1
            c.close()
            assert "test6" not in SharedMemory.getSharedMemorySpace()
            assert res1 and res2 and res3 and res4 and res5 and res6
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_numpy():
    print("Create Client instance containing a \"numpy\":", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test7", np.array([10, 20]), size=1024, client=True)
            res1 = type(c.getValue()) is np.ndarray
            res2 = c.getType() is np.ndarray
            res3 = c.getValue()[0] == 10
            res4 = c.getValue()[1] == 20
            c.close()
            assert "test7" not in SharedMemory.getSharedMemorySpace()
            assert res1 and res2 and res3 and res4
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_file():
    print("Create Client instance from JSON file:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory(name="test8", path="tests/test.json", size=1024, client=True)
            res = type(c.getValue()) is dict
            c.close()
            assert "test8" not in SharedMemory.getSharedMemorySpace() and res
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_newValue():
    print("Update Client value:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test9", 1, size=1024, client=True)
            c.setValue(12)
            res1 = c.getValue() == 12
            res2 = c[0] == 12
            c.close()
            assert "test9" not in SharedMemory.getSharedMemorySpace() and res1 and res2
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_stop():
    print("Stop Client:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test10", 1, size=1024, client=True)
            c.close()
            assert "test10" not in SharedMemory.getSharedMemorySpace()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_call():
    print("Stop Client 2:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test11", 1, size=1024, client=True)
            c.close()
            c.close()
            assert "test11" not in SharedMemory.getSharedMemorySpace()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_call2():
    print("Stop Client 3:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test12", 1, size=1024, client=True)
            c.restart()
            c.close()
            assert "test12" not in SharedMemory.getSharedMemorySpace()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_valueAccess():
    print("Deleting value from overloaded method:", end=" ")
    try:
        with contextlib.redirect_stdout(None):
            c = SharedMemory("test13", {'0':0, '1':1, '2':2, '3':3}, size=1024, client=True)
            c.restart()
            del c['0']
            c.close()
            assert "test13" not in SharedMemory.getSharedMemorySpace()
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False


print("-"*10)
test_str()
test_int()
test_float()
test_bool()
test_dict()
test_list()
test_numpy()
test_file()
test_newValue()
test_stop()
test_call()
test_call2()
test_valueAccess()
print("-"*10)