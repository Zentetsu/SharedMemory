from functools import partial
import mmap
import os
import errno
import struct
import secrets
import types
 
import posix_ipc
# import _posixshmem
 
_O_CREX = os.O_CREAT | os.O_EXCL
 
# FreeBSD (and perhaps other BSDs) limit names to 14 characters.
_SHM_SAFE_NAME_LENGTH = 14
 
# Shared memory block name prefix
_SHM_NAME_PREFIX = '/psm_'
 

_flags = _O_CREX | os.O_RDWR
 

_name = "test"
_fd = -1
_mmap = None
_buf = None
_flags = _O_CREX | os.O_RDWR
_mode = 0o600
_prepend_leading_slash = True
 
name = _SHM_NAME_PREFIX + _name if _prepend_leading_slash else _name
memory = None
stats = None
size = 100
print(name)
 
print("START")
try:
    posix_ipc.unlink_shared_memory(name)
except:
    print("NO CLEAN")
 
memory = posix_ipc.SharedMemory(name, _flags, _mode)
os.ftruncate(memory.fd, size)
stats = os.fstat(memory.fd)
size = stats.st_size
 
print(size)
 
try: 
    mapfile = mmap.mmap(memory.fd, size)
except Exception:
    print(" MMAP Error")
 
mapfile.close()
 
try:
    posix_ipc.unlink_shared_memory(name)
except:
    print("NO CLEAN")
 
print("END")