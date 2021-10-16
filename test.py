from SharedMemory.SharedMemory import SharedMemory
from datetime import datetime
import math
import sys
import binascii


if __name__ == '__main__':
    data = {"A": [1, {"B": (10, 1.1)}]}
    c = SharedMemory(name="test", value=data, exist=True)
    # c = SharedMemory(name="test", value=10, exist=True)

    # c.setValue(data)
    print(c.getValue())

    c.close()
    c.restart()
    print(c["A"])
    c["A"] = 10
    print(c.getValue())
    print(c)