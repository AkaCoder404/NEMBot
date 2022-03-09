#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import binascii
import hashlib
import json
import os

from Cryptodome.Cipher import AES

__all__ = ["encrypted_id", "encrypted_request"]

MODULUS = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
NONCE = b"0CoJUm6Qyw8W8jud"
PUBKEY = "010001"

# 歌曲加密算法 
def encrypted_id(id):
    magic = bytearray("3go8&$8*3*3h0k(2)2", "u8")
    song_id = bytearray(id, "u8")
    magic_len = len(magic)
    for i, sid in enumerate(song_id):
        song_id[i] = sid ^ magic[i % magic_len]
    m = hashlib.md5(song_id)
    result = m.digest()
    result = base64.b64encode(result).replace(b"/", b"_").replace(b"+", b"-")
    return result.decode("utf-8")

# 登录加密算法
def encrypted_request(text):
    data = json.dumps(text).encode("utf-8")
    secret = create_key(16)
    params = aes_encrypt(aes_encrypt(data, NONCE), secret)
    encseckey = rsa_encrypt(secret, PUBKEY, MODULUS)
    return {"params": params, "encSecKey": encseckey}

def aes_encrypt(text, key):
    pad = 16 - len(text) % 16
    text = text + bytearray([pad] * pad)
    encryptor = AES.new(key, 2, b"0102030405060708")
    ciphertext = encryptor.encrypt(text)
    return base64.b64encode(ciphertext)

def rsa_encrypt(text, pubkey, modulus):
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16), int(pubkey, 16), int(modulus, 16))
    return format(rs, "x").zfill(256)

def create_key(size):
    return binascii.hexlify(os.urandom(size))[:16]

def md5(string):
    return hashlib.md5(string.encode("utf-8")).hexdigest()
