# -*- coding: utf-8 -*-

class HexConvert:

    def __init__(self):
        pass

    '''
    string to bytes
    eg:
    '0123456789ABCDEF0123456789ABCDEF'
    b'0123456789ABCDEF0123456789ABCDEF'
    '''
    def stringTobytes(str):
        return bytes(str, encoding='utf8')

    '''
    bytes to string
    eg:
    b'0123456789ABCDEF0123456789ABCDEF'
    '0123456789ABCDEF0123456789ABCDEF'
    '''
    def bytesToString(bs):
        return bytes.decode(bs, encoding='utf8')

    '''
    hex string to bytes
    eg:
    '01 23 45 67 89 AB CD EF 01 23 45 67 89 AB CD EF'
    b'\x01#Eg\x89\xab\xcd\xef\x01#Eg\x89\xab\xcd\xef'
    '''
    def hexStringTobytes(str):
        str = str.replace(" ", "")
        return bytes.fromhex(str)
        # return a2b_hex(str)

    '''
    bytes to hex string 
    eg:
    b'\x01#Eg\x89\xab\xcd\xef\x01#Eg\x89\xab\xcd\xef'
    '01 23 45 67 89 AB CD EF 01 23 45 67 89 AB CD EF'
    '''
    def bytesToHexString(bs):
        # hex_str = ''
        # for item in bs:
        #     hex_str += str(hex(item))[2:].zfill(2).upper() + " "
        # return hex_str
        return ''.join(['%02X ' % b for b in bs])