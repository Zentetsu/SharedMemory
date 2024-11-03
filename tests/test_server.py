"""
File: test_server.py
Created Date: Wednesday, July 3rd 2020, 8:17:04 pm
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
2020-10-12	Zen	Updating test
2020-07-23	Zen	Adding test for availability
2020-07-18	Zen	Adding some tests
2020-07-03	Zen	Updating test file
2020-07-01	Zen	Creating file
2023-10-18	Zen	Updating test: checking manager
2024-11-03	Zen	Updating docstring + unittest
"""  # noqa

# import sys

# sys.path.insert(0, "../")

from SharedMemory.SharedMemory import SharedMemory
import unittest


class TestSharedMemoryServer(unittest.TestCase):
    """Test the SharedMemory class in server mode."""

    def test_connection(self) -> None:
        """Test server connection without client."""
        try:
            s = SharedMemory("test1", client=False, silent=True)
            s.getValue()
            s.close()
            self.assertTrue("test1" not in SharedMemory.getSharedMemorySpace())
        except:
            self.assertTrue(False)

    def test_connection2(self) -> None:
        """Test server connection with client."""
        try:
            c = SharedMemory("test2", "azerty", client=True, silent=True)
            s = SharedMemory("test2", client=False, silent=True)
            res = c.getAvailability() and s.getAvailability()
            c.close()
            s.close()
            self.assertTrue("test2" not in SharedMemory.getSharedMemorySpace() and res)
        except:
            self.assertTrue(False)

    def test_value(self) -> None:
        """Test server value."""
        try:
            c = SharedMemory("test3", "azerty", client=True, silent=True)
            s = SharedMemory("test3", client=False, silent=True)
            res = s.getValue() == "azerty"
            c.close()
            s.close()
            self.assertTrue("test3" not in SharedMemory.getSharedMemorySpace() and res)
        except:
            self.assertTrue(False)

    def test_editValue(self) -> None:
        """Test server edit value."""
        try:
            c = SharedMemory("test4", "azerty", client=True, silent=True)
            s = SharedMemory("test4", client=False, silent=True)
            s.setValue("ytreza")
            res1 = c.getValue() == "ytreza"
            res2 = c[0] == "ytreza"
            c.close()
            s.close()
            self.assertTrue("test4" not in SharedMemory.getSharedMemorySpace() and res1 and res2)
        except:
            self.assertTrue(False)

    def test_clientStopped(self) -> None:
        """Test server access value when client stopped."""
        try:
            c = SharedMemory("test5", "azerty", client=True, silent=True)
            s = SharedMemory("test5", client=False, silent=True)
            c.close()
            s.setValue("toto")
            res1 = s.getValue() == None
            s.close()
            self.assertTrue("test5" not in SharedMemory.getSharedMemorySpace() and res1)
        except:
            self.assertTrue(False)

    def test_serverStopped(self) -> None:
        """Test client access value when server stopped."""
        try:
            c = SharedMemory("test6", "azerty", client=True, silent=True)
            s = SharedMemory("test6", client=False, silent=True)
            s.close()
            c.setValue("toto")
            self.assertTrue(c.getValue() == None)
            self.assertTrue(c[0] == None)
            c.restart()
            c.setValue("toto")
            self.assertTrue(c.getValue() == "toto")
            self.assertTrue(c[0] == "toto")
            s.restart()
            self.assertTrue(s.getValue() == "toto")
            self.assertTrue(s[0] == "toto")
            c.close()
            s.close()
            self.assertTrue("test6" not in SharedMemory.getSharedMemorySpace())
        except:
            self.assertTrue(False)

    def test_multiStop(self) -> None:
        """Test when the server is stopped multiple times."""
        try:
            c = SharedMemory("test7", "azerty", client=True, silent=True)
            s = SharedMemory("test7", client=False, silent=True)
            s.close()
            s.close()
            c.close()
            self.assertTrue("test7" not in SharedMemory.getSharedMemorySpace())
        except:
            self.assertTrue(False)

    def test_availability(self) -> None:
        """Check the availability of the server and the client."""
        try:
            c = SharedMemory("test8", "azerty", client=True, silent=True)
            s = SharedMemory("test8", client=False, silent=True)
            res1 = c.getAvailability() == True
            res2 = s.getAvailability() == True
            s.close()
            c.close()
            self.assertTrue("test8" not in SharedMemory.getSharedMemorySpace() and res1 and res2)
        except:
            self.assertTrue(False)

    def test_serverFirst(self) -> None:
        """Test when the server is created first."""
        try:
            s = SharedMemory("test9", client=False, silent=True)
            c = SharedMemory("test9", "azerty", client=True, silent=True)
            res1 = c.getAvailability() == True
            res2 = s.getAvailability() == True
            self.assertTrue(res1)
            self.assertTrue(res2)
            self.assertTrue(s.getValue() == c.getValue())
            s.close()
            c.close()
            self.assertTrue("test9" not in SharedMemory.getSharedMemorySpace())
        except:
            self.assertTrue(False)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSharedMemoryServer)
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
