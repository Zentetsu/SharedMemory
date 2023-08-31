# SharedMemory

Python shared memory library based an posix-ipc.

### Features
* Shared type:
    * Basic type (int, float, bool, str)
    * list, tuple, dict and nparray
* Management of the availability of shared memory space
* Overloaded methods for list and dict
* Semaphore

### Future improvement
* Timeout for Semaphore
* Adding more tests

### Example
Example of execution in two instances of ipython.

#### Client side
```python
In [1]: from SharedMemory import SharedMemory

In [2]: # Creating client instance with a shared space named 'shared_space' with a size of 10
   ...: C = SharedMemory(name="shared_space", value="Hello", client=True)

In [4]: C.getAvailability()
Out[4]: True

In [5]: C.getValue()
Out[5]: 'Hello'

In [6]: # Waiting for Server to update shared data

In [7]: C.getValue()
Out[7]: 'World'

In [8]: C.setValue('HW')
Out[8]: True

In [9]: C.getValue()
Out[9]: 'HW'

In [10]: # Closing the client side
    ...: C.close()

In [11]: C.getAvailability()
Out[11]: False
```
#### Server side
```python
In [1]: from SharedMemory import SharedMemory

In [2]: # Creating server instance access to the shared named 'shared_space'
   ...: S = SharedMemory(name="shared_space", client=False)

In [4]: S.getAvailability()
Out[4]: True

In [5]: S.getValue()
Out[5]: 'Hello'

In [6]: S.setValue("World")
Out[6]: True

In [7]: S.getValue()
Out[7]: 'Hello'

In [8]: # Waiting for Client to update shared data

In [9]: S.getValue()
Out[9]: 'HW'

In [10]: # Waiting Client to close the shared space

In [11]: S.getAvailability()
Out[11]: False


In [12]: # Closing the server side
    ...: S.close()
INFO: Client already stopped.
```



### More
[![PyPI version](https://badge.fury.io/py/SharedMemory.svg)](https://badge.fury.io/py/SharedMemory)
![Python package](https://github.com/Zentetsu/SharedMemory/workflows/Python%20package/badge.svg?branch=master)
![Upload Python Package](https://github.com/Zentetsu/SharedMemory/workflows/Upload%20Python%20Package/badge.svg)
[![Python](https://shields.io/badge/python-3.7_|_3.8_|_3.9_|_3.10-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
