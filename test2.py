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

def test(value, nb_bits):
    print("--get sign")
    sign = '0'
    if value < 0:
        sign = '1'
    print(sign)
    frac, whole = math.modf(round(abs(value), 5))
    print("--get whole bin")
    b_whole = bin(math.trunc(whole))[2:]
    print(b_whole)
    
    print("--get frac bin")
    b_frac = frac
    if b_frac == 0:
        b_frac = '0'
    else:
        nb = 0
        while b_frac != 0 and nb < 10:
            f = frac*2
            print(frac, f)
            frac, whole = math.modf(round(f), 5)
            nb = nb + 1    
    print(b_frac)

    print("--get append bin part")
    append_bin_part = b_whole + '.' + b_frac
    print(append_bin_part)

    print("--get normalize")
    norm = 0
    if append_bin_part[0] == '1':
        norm = len(b_whole) - 1
        normalize = b_whole[0] + '.' + b_whole[1:] + b_frac
        print(normalize)
        # normalize = 

        pass
    print(normalize)

    print("--get mantissa")
    mantissa = normalize[2:]
    print(mantissa)

    print("--get exponent")
    exp = bin(norm + math.trunc(2**((nb_bits/2-1)-1)-1))[2:]
    print(exp)
    
    print("--get result")
    result = '0b' + sign + '0' * math.trunc((nb_bits/2-1) - len(exp)) + exp + mantissa + '0' * math.trunc(nb_bits/2 -  len(mantissa))
    print(result)

    return result

def tset(value, nb_bits):
    binary = value[2:]
    print("--get separate")
    sign = binary[0]

    print("--get mantissa")
    mantissa = "1." + binary[math.trunc(nb_bits/2-1)+1:]
    print(mantissa)

    print("--get exponent")
    exp = binary[1:math.trunc(nb_bits/2-1)+1]
    exp = int(exp, 2) - math.trunc(2**((nb_bits/2-1)-1)-1)
    print(exp)

    print("--get denormalize")
    denormalize = mantissa
    if exp > 0:
        denormalize = mantissa[0] + mantissa[2:]
        denormalize = denormalize[0:1+exp] + '.' + denormalize[1+exp:]
        pass
    print(denormalize)

    print("--get convert")
    convert = 0
    for d in denormalize:
        if d != '.':
            convert = convert + int(d) * 2**exp
            exp = exp - 1
    print(convert)

    print("--get sign")
    if sign == 1:
        sign = -1
    else:
        sign = 1
    print(sign)

    print("--get result")
    result = sign * convert
    print(result)

    return result

value =  1.5
nb_bits = 8

# for value in range(1, 20):
res1 = test(value, nb_bits)
print("----------------")
res2 = tset(res1, nb_bits)

    # if res2 != value:
        # exit(1)
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