from SharedMemory.nClient import nClient
from datetime import datetime
import sys
import math


def fp_to_bin(value, nb_bits):
    sign = 0
    if value < 0:
        sign = 1

    frac, whole = math.modf(round(abs(value), 5))
    frac = round(frac, 1)
    print("frac: " + str(frac))
    print("whole: " + str(whole))
    
    bin_whole = bin(math.trunc(whole))
    binary = 0b0 | sign
    mantissa = "" + str(bin_whole[2:]) + "."
    n = 0

    if frac == 0:
        mantissa = mantissa + "0"
    while frac != 0 and n != 5:
        frac = frac * 2
        frac, whole = math.modf(abs(frac))
        frac = round(frac, 1)
        mantissa = mantissa + str(math.trunc(whole))

        n = n + 1
 
    print("mantissa: " + str(mantissa)) 

    for i in range(0, len(mantissa)):
        if mantissa[0] == '0' and mantissa[i] == '1':
            break
        if mantissa[0] == '1' and mantissa[i] == '.':
            break

    if mantissa[0] == '0':
        exp = -(i-1) + 2**(math.trunc(nb_bits/2)-2)-1
        mantissa = str(mantissa[:1]) + str(mantissa[2:]) + '0' * exp
        binary = bin(binary) + mantissa
        binary = binary  + '0' * (nb_bits - len(binary[2:]))
    else:
        exp = (i-1) + 2**(math.trunc(nb_bits/2)-2)-1
        mantissa = str(mantissa[1:i]) + str(mantissa[i+1:])
        binary = bin(binary) + bin(exp)[2:] + mantissa
        binary = binary + '0' * (nb_bits - len(binary[2:]))

    print("exp: " + str(exp))
    print("ind: " + str(i))

    print("mantissa: " + str(mantissa))
    print("bin_whole: " + str(bin_whole))

    print("frac: " + str(frac))
    print("whole: " + str(whole))

    print("bin: " + binary)

    return binary

def bin_to_fp(value, nb_bits):
    mantissa = bin(0b00001111 & value)
    mantissa = "1." + "0" * (4 - len(mantissa[2:])) + mantissa[2:]
    sign = value >> 7
    print("sign: " + str(sign))
    exp = (0b0111 & value >> 4) - math.trunc(nb_bits/2 - 1)
    print("exp: " + str(exp))
    mantissa = str(mantissa[:1]) + str(mantissa[2:])
    print("mantissa: " + str((mantissa)))
    nv = 0
    for i in mantissa:
        nv = nv + int(i) * 2**exp
        exp = exp - 1
        
    if sign == 1:
        nv = nv * -1

    print("nv: " + str(nv))

    if value == 0:
        return 0
    return nv

def test(value):
    frac, whole = math.modf(round(abs(value), 5))
    b_whole = bin(math.trunc(whole))
    b_frac = bin(int(str(frac)[2:]))
    exp = (2**(3-1)-1) + 2**0
    binary = b_whole[2:] + '.' + b_frac[2:]

    print(bin(exp))

value =  1
nb_bits = 8

test(value)

# i = 2


# while i < 10:
#     print("-------------------")
#     print("I: " + str(i))
#     value = fp_to_bin(i, nb_bits)

#     print("-------------------")
#     # value = 0b00100110
#     # nb_bits = 8

#     nv = bin_to_fp(int(value, 2), nb_bits)
#     print("-------------------")

#     if nv != i:
#         exit(1)
#     i = i + 0.5