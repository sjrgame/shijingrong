# !/usr/bin/python
# -*- coding:utf-8-*-
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


# 自己实现了一个aes类，用于aes的加密和解密
class ly_aes():
    # key为aes秘钥,mode为加密模式
    def __init__(self,key, mode):
        self.key = key
        self.mode = mode
    # text的为要加密的文本或者二进制流,count为加密数据的长度
    def encrypt(self, text, count):
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        length = 16
        if count < length:
            add = (length-count)
            #\0 backspace
            text = text + ('\0' * (add-1))
            text = text + chr(add)
        elif count > length:
            add = (length-(count % length))
            # print add
            text = text + ('\0' * (add - 1))
            text = text + chr(add)
        self.cipherText = cryptor.encrypt(text)
        # return b2a_base64(self.cipherText)
        # 将内存中的数据已base64字符串打印出来
        return b2a_hex(self.cipherText)
        # return self.cipherText
        # 将内存中的数据已16进制字符串打印出来

    # cipherText类型为16进制字符串如:"fa0345da",一般为32个字节长度
    def decrypt(self,cipherText):
        cryptor = AES.new(self.key,self.mode,b'0000000000000000')
        plainText = cryptor.decrypt(a2b_hex(cipherText))
        # 将秘钥转换为二进制流
        # 返回值为二进制流，因为有很多不可打印字符
        # plainText = cryptor.decrypt(a2b_base64(cipherText))
        return plainText


def  main():
    key = '1234567890123456'
    # 秘钥的长度必须为16
    cryptor = ly_aes(key, AES.MODE_ECB)
    # 这里选用的是ECB模式
    msg = 'abcdefghijklmnop'
    ms = 'fb4663cecea43421d620347ff2ac393a'
    # ms = '+0Zjzs6kNCHWIDR/8qw5Og=='
    msg1 = 'abcdefghijklmnopqrstuvwxyz123456'
    mw = 'fcad715bd73b5cb0488f840f3bad7889d0e709d0ffd38c6dfec55ccb9f475b01d65707103a771ee7c1cb5e021e44a557'
    # mw = '/K1xW9c7XLBIj4QPO614idDnCdD/04xt/sVcy59HWwHWVwcQOnce58HLXgIeRKVX'
    # 加密字符串
    cipher = cryptor.encrypt(msg, len(msg))
    # 返回值是内存中的16进制字符串
    print(cipher)
    plainText = cryptor.decrypt(cipher)
    #解密函数,秘钥在aes初始化的时候设置好了,aes是对称加密的,加密的秘钥和解密的秘钥是一样的
    print(plainText)


if __name__=="__main__":
    main()
