'''
File: SMErrorType.py
Created Date: Thursday, July 4th 2020, 9:36:57 pm
Author: Zentetsu

----

Last Modified: Tue Oct 19 2021
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
2021-10-19	Zen	Adding error
2020-07-13	Zen	Adding comments
2020-07-03	Zen	Adding new exception
2020-07-02	Zen	Creating file
'''


class SMTypeError(Exception):
    """CLass focused on catching types that aren't accepted

    Args:
        Exception (Exception):
    """
    def __init__(self, type, message=" is not accepted."):
        """Class constructor

        Args:
            type (type): type that has not been accepted
            message (str, optional): message. Defaults to " is not accepted.".
        """
        self.type = type
        self.message = str(self.type) + message
        super().__init__(self.message)

class SMSizeError(Exception):
    """Class focused on catching over resizing when data are updated

    Args:
        Exception (Exception):
    """
    def __init__(self, message="size of new value exceeds the previous one."):
        """CLass constructor

        Args:
            message (str, optional): message. Defaults to "size of new value exceeds the previous one.".
        """
        self.message = message
        super().__init__(self.message)

class SMMultiInputError(Exception):
    """class focused on catching the fact that value adn path are initialized or not

    Args:
        Exception (Exception):
    """
    def __init__(self, message="value xor path must be None."):
        self.message = message
        super().__init__(self.message)

class SMNotDefined(Exception):
    """Class focused on catching an attempt to access an unintialized shared memory

    Args:
        Exception (Exception):
    """
    def __init__(self, name, message=None):
        """Class constructor

        Args:
            name (str): shared memory name
            message (str, optional): message. Defaults to None.
        """
        if message is None:
            self.message = "shared memory called '" + name + "' is not defined."
        else:
            self.message = message

        super().__init__(self.message)

class SMAlreadyExist(Exception):
    """Class focused on catching an attempt to create an intialized shared memory

    Args:
        Exception (Exception):
    """
    def __init__(self, name, message=None):
        """Class constructor

        Args:
            name (str): shared memory name
            message (str, optional): message. Defaults to None.
        """
        if message is None:
            self.message = "shared memory called '" + name + "' already exist."
        else:
            self.message = message

        super().__init__(self.message)

class SMEncoding(Exception):
    """Class focused on catching an attempt to create an intialized shared memory

    Args:
        Exception (Exception):
    """
    def __init__(self, name, message=None):
        """Class constructor

        Args:
            name (str): shared memory name
            message (str, optional): message. Defaults to None.
        """
        if message is None:
            self.message = "Error in '" + name + "' trame value."
        else:
            self.message = message

        super().__init__(self.message)