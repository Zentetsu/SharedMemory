from SharedMemory.nClient import nClient
from datetime import datetime
import sys
import math
 
_INT = 0x5
_FLOAT = 0x1
_COMPLEX = 0x2
_STR = 0x3
_LIST = 0x4
_DICT = 0x5
_NPARRAY = 0x6
 
def conv_hex(value):
    n_value = 0x0
    if type(value) is int:
        n_value = _INT << 64 | int(hex(value), 16)
 
    if type(value) is float:
        # n_value = float.hex(value)
        pass
 
    if type(value) is str:
        n_value = _STR << 64 | int((value.encode('utf-8')).hex(), 16)
 
    return n_value
 
def create_data_hex(value):
 
    return conv_hex(value)
 
def conv_value(value):
    t = value >> 64
    val = 0
 
    if t == _INT:
        val = int(hex(0x0FFFFFFFFFFFFFFF & value), 16)
 
    if t == _STR:
        val = (bytes.fromhex(hex(0x0FFFFFFFFFFFFFFF & value)[2:])).decode("ASCII")
 
    return val
 
def get_data(value):
 
    return conv_value(value)

_M_32 = 0b11111111111111111111111111111111

def conv_bin_swf(value, nb_bits):
    sign = 0
    if value < 0:
        sign = 1

    frac, whole = math.modf(round(abs(value), math.trunc(nb_bits/2)))
    bin_whole = int(bin(math.trunc(whole)), 2)
    bin_frac = int(bin(int(str(round(frac, math.trunc(nb_bits/2)))[2:])), 2)
    bin_value = sign << (nb_bits - 1) | bin_whole << math.trunc(nb_bits / 2) | bin_frac

    return bin_value

def conv_float_swf(value, nb_bits):
    dec = math.trunc((32 - nb_bits/2))
    print(dec)
    bin_frac = float("0." + str(_M_32 >> dec & value))
    print(bin_frac)
    bin_whole = _M_32 >> (dec + 1) & value >> math.trunc(nb_bits/2)
    print(bin_whole)
    sign = value >> (nb_bits - 1)
    
    if sign == 1:
        sign = -1
    else:
        sign = 1

    nv = sign * (bin_whole + bin_frac)

    return nv

if __name__ == '__main__':
    # c = nClient(name="test", value=10, exist=True)
    # c = nClient(name="test", value=10, exist=True)
    # c.close()
 
    # print("TEST SIZE")
    # print("int: " + str(sys.getsizeof(1000000000)))
    # print("float: " + str(sys.getsizeof(5.5)))
    # print("str: " + str(len("TESTS_OF_SIZES".encode('utf-8'))))
    # print("bool: " + str(sys.getsizeof(True)))
    # # print("complex: " + str(sys.getsizeof(complex)))
    list = [5, "dfsddgf"]
    print("\nTEST TIME")
    for e in list:
        a = datetime.now()
        value = create_data_hex(e)
        b = datetime.now()
        c = b-a
        # print(str(hex(value)) + " -> " + str(get_data(value)) + ": " + str(c.microseconds))

    nb = 4

    print(bin(nb))

    nb = -4.5
    nb_bits = 8
    n = 0
   
    sign = 0
    if nb < 0:
        sign = 1
    frac, whole = math.modf(abs(nb))
    print("SIGN: " + str(sign))
    print("WHOLE: " + str(whole))
    print("FRAC: " + str(frac))
    binval = int(bin(math.trunc(whole)), 2)
    print("BIN: " + bin(binval)[2:])
    exp = len(bin(binval)[2:])-1
    
    while frac != 0 and n != 4:
        frac, whole = math.modf(frac * 2)
        binval = binval << 1 | abs(math.trunc(whole))
        n = n + 1
    
    print("NORM: " + bin(binval))

    exp = math.trunc(exp + (nb_bits/2 - 1))
    print("EXP: " + bin(exp))

    nv_value = sign << 7 | exp << 4 | binval
    print(bin(nv_value))

    print("---------------------------------------")
   
    sign = 0
    if nb < 0:
        sign = 1
    frac, whole = math.modf(abs(nb))
    val_str = ""
    print("SIGN: " + str(sign))
    print("WHOLE: " + str(whole))
    print("FRAC: " + str(frac))
    bin_whole = int(bin(math.trunc(whole)), 2)
    print("BIN: " + bin(bin_whole))
    val_str = val_str + bin(bin_whole)[2:] + '.'
    
    while frac != 0 and n != 4:
        frac, whole = math.modf(frac * 2)
        binval = binval << 1 | abs(math.trunc(whole))
        n = n + 1

    print(val_str)
   
    print("---------------------------------------")
    
    value = -0.01
    nb_bits = 16
    binary = conv_bin_swf(value, nb_bits)
    print("BIN:" + bin(binary))
    print("FLOAT: " + str(conv_float_swf(binary, nb_bits)))