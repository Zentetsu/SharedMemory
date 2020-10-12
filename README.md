# SharedMemory

Encapsulation of the python shared_memory library.

### Features
* Shared type:
    * Basic type (int, float, bool, str)
    * list and dict
* Mutex
* Timeout for Mutex
* Management of the availability of shared memory space
* Overloaded methods for list and dict

### Future improvement
* Adding more tests

### Example
Example of execution in two instances of ipython.

#### Client side
```python
In [1]: from SharedMemory import Client

In [2]: # Creating client instance with a shared space named 'shared_space' with a size of 10
   ...: C = Client(name="shared_space", value="Hello", size=10, timeout=1)

In [3]: C.getStatus()
Out[3]: 'Started'

In [4]: C.getAvailability() # First boolean: Client Availability, Second boolean: Server Availability
Out[4]: (True, True)

In [5]: C.getValue()
Out[5]: 'Hello'

In [6]: # Waiting for Server to update shared data

In [7]: C.getValue()
Out[7]: 'World'

In [8]: C.updateValue('HW')

In [9]: C.getValue()
Out[9]: 'HW'

In [10]: # Closing the client side
    ...: C.stop()
```
#### Server side
```python
In [1]: from SharedMemory import Server

In [2]: # Creating server instance access to the shared named 'shared_space'
   ...: S = Server(name="shared_space", timeout=1)

In [3]: S.getStatus()
Out[3]: 'Connected'

In [4]: S.getAvailability() # First boolean: Server Availability, Second boolean: Client Availability
Out[4]: (True, True)

In [5]: S.getValue()
Out[5]: 'Hello'

In [6]: S.updateValue("World")

In [7]: S.getValue()
Out[7]: 'Hello'

In [8]: # Waiting for Client to update shared data

In [9]: S.getValue()
Out[9]: 'HW'

In [10]: # Closing the server side
    ...: S.stop()
```



### More
[![PyPI version](https://badge.fury.io/py/SharedMemory.svg)](https://badge.fury.io/py/SharedMemory)
![Python package](https://github.com/Zentetsu/SharedMemory/workflows/Python%20package/badge.svg?branch=master)
![Upload Python Package](https://github.com/Zentetsu/SharedMemory/workflows/Upload%20Python%20Package/badge.svg)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
