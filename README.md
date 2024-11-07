# SharedMemory

Python shared memory library based an posix-ipc.

### Features
* Shared type:
  * Basic type: `int`, `float`, `bool`, `str`, `complex`
  * Python defined type: `list`, `tuple` and `dict`
  * Other: `nparray`
* Can define shared data through a `JSON`
  * Define directly the value inside the json (excpet `tuple`)
  * Define value structure `list`and `nparray` example [HERE](https://github.com/Zentetsu/SharedMemory/wiki/JSON)
* Possibility to manage shared memory space
* Can use `__getitem__`and `__setitem__` on:
  * `list`and `dict`
* Space Memory configurable
* Semaphore

### Installation
```console
> pip install SharedMemory
```

### Documentation
Documentation and example are provided [HERE](https://github.com/Zentetsu/SharedMemory/wiki)

### More
[![PyPI version](https://badge.fury.io/py/SharedMemory.svg)](https://badge.fury.io/py/SharedMemory)
![Python package](https://github.com/Zentetsu/SharedMemory/workflows/Python%20package/badge.svg?branch=master)
![Upload Python Package](https://github.com/Zentetsu/SharedMemory/workflows/Upload%20Python%20Package/badge.svg)
[![Python](https://shields.io/badge/3.8_|_3.9_|_3.10_|_3.11-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
