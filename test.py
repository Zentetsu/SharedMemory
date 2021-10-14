from SharedMemory.SharedMemory import SharedMemory
from datetime import datetime
import math
import sys


if __name__ == '__main__':
    c = SharedMemory(name="test", value=10, exist=True)
    # c = SharedMemory(name="test", value=10, exist=True)
    c.setValue(511)
    print(hex(c.getValue()))

    c.close()