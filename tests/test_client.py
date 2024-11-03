"""
File: test_client.py
Created Date: Wednesday, July 3rd 2020, 8:16:57 pm
Author: Zentetsu

----

Last Modified: Sun Nov 03 2024
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
2024-11-03	Zen	Updating docstring + unittest
"""  # noqa

# import sys

# sys.path.insert(0, "../")

from SharedMemory.SharedMemory import SharedMemory
import numpy as np
import unittest


class TestSharedMemoryClient(unittest.TestCase):
    """Test the SharedMemory class in client mode."""

    def test_str(self) -> None:
        """Test client creation containing a string."""
        try:
            c = SharedMemory("test1", "azerty", size=1024, client=True, silent=True)
            self.assertTrue(type(c.getValue()) is str)
            self.assertTrue(type(c[0]) is str)
            c.close()
            self.assertTrue("test1" not in SharedMemory.getSharedMemorySpace())
        except:
            self.assertTrue(False)

    def test_int(self) -> None:
        """Test client creation containing an integer."""
        try:
            c = SharedMemory("test2", -125, size=1024, client=True, silent=True)
            res1 = type(c.getValue()) is int
            res2 = type(c[0]) is int
            res3 = c.getValue() == -125
            res4 = c[0] == -125
            c.close()
            self.assertTrue("test2" not in SharedMemory.getSharedMemorySpace())
            self.assertTrue(res1 and res2 and res3 and res4)
        except:
            self.assertTrue(False)

    def test_float(self) -> None:
        """Test client creation containing a float."""
        try:
            c = SharedMemory("test3", -1.2, size=1024, client=True, silent=True)
            res1 = type(c.getValue()) is float
            res2 = type(c[0]) is float
            res3 = c.getValue() == -1.2
            res4 = c[0] == -1.2
            c.close()
            self.assertTrue("test3" not in SharedMemory.getSharedMemorySpace())
            self.assertTrue(res1 and res2 and res3 and res4)
        except:
            self.assertTrue(False)

    def test_bool(self) -> None:
        """Test client creation containing a boolean."""
        try:
            c = SharedMemory("test4", True, size=1024, client=True, silent=True)
            res1 = type(c.getValue()) is bool
            res2 = type(c[0]) is bool
            res3 = c.getValue()
            res4 = c[0]
            c.close()
            self.assertTrue("test4" not in SharedMemory.getSharedMemorySpace())
            self.assertTrue(res1 and res2 and res3 and res4)
        except:
            self.assertTrue(False)

    def test_dict(self) -> None:
        """Test client creation containing a dictionary."""
        try:
            c = SharedMemory("test5", {"a": 1}, size=1024, client=True, silent=True)
            res1 = type(c.getValue()) is dict
            res2 = c.getType() is dict
            res3 = c.getValue()["a"] == 1
            res4 = c["a"] == 1
            c.close()
            self.assertTrue("test5" not in SharedMemory.getSharedMemorySpace())
            self.assertTrue(res1 and res2 and res3 and res4)
        except:
            self.assertTrue(False)

    def test_list(self) -> None:
        """Test client creation containing a list."""
        try:
            c = SharedMemory("test6", [0, 1], size=1024, client=True, silent=True)
            res1 = type(c.getValue()) is list
            res2 = c.getType() is list
            res3 = c.getValue()[0] == 0
            res4 = c.getValue()[1] == 1
            res5 = c[0] == 0
            res6 = c[1] == 1
            c.close()
            self.assertTrue("test6" not in SharedMemory.getSharedMemorySpace())
            self.assertTrue(res1 and res2 and res3 and res4 and res5 and res6)
        except:
            self.assertTrue(False)

    def test_numpy(self) -> None:
        """Test client creation containing a numpy array."""
        try:
            c = SharedMemory("test7", np.array([10, 20]), size=1024, client=True, silent=True)
            res1 = type(c.getValue()) is np.ndarray
            res2 = c.getType() is np.ndarray
            res3 = c.getValue()[0] == 10
            res4 = c.getValue()[1] == 20
            c.close()
            self.assertTrue("test7" not in SharedMemory.getSharedMemorySpace())
            self.assertTrue(res1 and res2 and res3 and res4)
        except:
            self.assertTrue(False)

    def test_file(self) -> None:
        """Test client creation from a JSON file."""
        try:
            c = SharedMemory(name="test8", path="tests/test.json", size=1024, client=True, silent=True)
            res = type(c.getValue()) is dict
            c.close()
            self.assertTrue("test8" not in SharedMemory.getSharedMemorySpace() and res)
        except:
            self.assertTrue(False)

    def test_newValue(self) -> None:
        """Test updating the value of the client."""
        try:
            c = SharedMemory("test9", 1, size=1024, client=True, silent=True)
            c.setValue(12)
            res1 = c.getValue() == 12
            res2 = c[0] == 12
            c.close()
            self.assertTrue("test9" not in SharedMemory.getSharedMemorySpace() and res1 and res2)
        except:
            self.assertTrue(False)

    def test_stop(self) -> None:
        """Test stopping the client."""
        try:
            c = SharedMemory("test10", 1, size=1024, client=True, silent=True)
            c.close()
            self.assertTrue("test10" not in SharedMemory.getSharedMemorySpace())
        except:
            self.assertTrue(False)

    def test_call(self) -> None:
        """Test client correctly stopped."""
        try:
            c = SharedMemory("test11", 1, size=1024, client=True, silent=True)
            c.close()
            c.close()
            self.assertTrue("test11" not in SharedMemory.getSharedMemorySpace())
        except:
            self.assertTrue(False)

    def test_call2(self) -> None:
        """Test client correctly stop after restart."""
        try:
            c = SharedMemory("test12", 1, size=1024, client=True, silent=True)
            c.restart()
            c.close()
            self.assertTrue("test12" not in SharedMemory.getSharedMemorySpace())
        except:
            self.assertTrue(False)

    def test_valueAccess(self) -> None:
        """Test __delitem__ method."""
        try:
            c = SharedMemory("test13", {"0": 0, "1": 1, "2": 2, "3": 3}, size=1024, client=True, silent=True)
            c.restart()
            del c["0"]
            c.close()
            self.assertTrue("test13" not in SharedMemory.getSharedMemorySpace())
        except:
            self.assertTrue(False)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSharedMemoryClient)
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
