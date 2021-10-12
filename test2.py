from SharedMemory.nClient import nClient
from datetime import datetime
import sys
import math
import struct
import ctypes

from test import _NPARRAY

def float_to_bin(value, nb_bits, prec):
    if value == 0:
        return '0b' + '0' * nb_bits

    # print("--get sign")
    sign = '0'
    if value < 0:
        sign = '1'
    frac, whole = math.modf(round(abs(value), prec))

    # print("--get whole bin")
    b_whole = bin(math.trunc(whole))[2:]

    # print("--get frac bin")
    b_frac = frac
    if b_frac == 0:
        b_frac = '0'
    else:
        nb = 0
        b_frac = ''
        while b_frac != 0 and nb < nb_bits:
            frac, whole = math.modf(frac*2)
            nb = nb + 1
            frac = round(frac, 5)
            n_w = math.trunc(whole)
            b_frac = b_frac + str(n_w)

    # print("--get append bin part")
    append_bin_part = b_whole + '.' + b_frac

    # print("--get normalize")
    norm = 0
    if append_bin_part[0] == '1':
        norm = len(b_whole) - 1
        normalize = b_whole[0] + '.' + b_whole[1:] + b_frac
    elif append_bin_part[0] == '0':
        norm = append_bin_part.find('1')
        normalize = append_bin_part[:norm+1] + '.' + append_bin_part[norm+1:]
        normalize = normalize[:1] + normalize[1+1:]
        norm = -1 * (norm - 1)

    # print("--get mantissa")
    point = normalize.find('.')
    mantissa = normalize[point+1:]

    # print("--get exponent")
    exp = bin(norm + math.trunc(2**((nb_bits/2-1)-1)-1))[2:]

    # print("--get result")
    result = '0b' + sign + '0' * math.trunc((nb_bits/2-1) - len(exp)) + exp + mantissa + '0' * math.trunc(nb_bits/2 -  len(mantissa))
    result = result[:nb_bits+2]

    return result

def bin_to_float(value, nb_bits, prec):
    if int(value, 2) == 0:
        return 0

    # print("--get separate")
    binary = value[2:]

    # print("--get mantissa")
    mantissa = "1." + binary[math.trunc(nb_bits/2-1)+1:]

    # print("--get exponent")
    exp = binary[1:math.trunc(nb_bits/2-1)+1]
    exp = int(exp, 2) - math.trunc(2**((nb_bits/2-1)-1)-1)

    # print("--get denormalize")
    denormalize = mantissa
    if exp > 0:
        denormalize = mantissa[0] + mantissa[2:]
        denormalize = denormalize[0:1+exp] + '.' + denormalize[1+exp:]

    # print("--get convert")
    convert = 0
    for d in denormalize:
        if d != '.':
            convert = convert + int(d) * 2**exp
            exp = exp - 1

    # print("--get sign")
    if binary[0] == '1':
        sign = -1
    else:
        sign = 1

    # print("--get result")
    result = sign * round(convert, prec)

    return result

value =  0.1
nb_bits = 64
prec = 5

def bin2float(b):
    h = int(b, 2).to_bytes(8, byteorder="big")
    return struct.unpack('>d', h)[0]


def float2bin(f):
    [d] = struct.unpack(">Q", struct.pack(">d", f))
    return f'{d:064b}'

for value in range(-10000000, 10000000):
    v = value
    print(v)
    res1 = float2bin(v)
    # print(res1)
    # print("----------------")
    res2 = bin2float(res1)
    # print(res2)

    if res2 != v:
        print("err")
        exit(1)
