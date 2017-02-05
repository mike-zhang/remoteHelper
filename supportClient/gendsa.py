#! /usr/bin/env python
#-*- coding:utf-8 -*-

from Crypto.PublicKey import DSA
from Crypto.Hash import HMAC
from struct import pack
from Crypto.Util import asn1
from twisted.conch.ssh import keys
import os,argparse

versionInfo = "gendsa 1.0.0"

def show(key, keytype):
    seq = asn1.DerSequence()
    seq[:] = [ 0, key.p, key.q, key.g, key.y, key.x ]
    private_key = "-----BEGIN DSA PRIVATE KEY-----\n%s-----END DSA PRIVATE KEY-----" % seq.encode().encode("base64")
    public_key = keys.Key(key).public().toString("openssh") # add key to authorized_keys
    keyInf = ""
    if keytype == 0 :
        keyInf += private_key
        keyInf += '\n'
        keyInf +=  public_key
    elif keytype == 1:
        keyInf += public_key
    elif keytype == 2:
        keyInf += private_key        
    print keyInf
    
def savePrivateKey(filename,private_key):
    with open(filename,'wb') as fout:
        fout.write(private_key)
    os.system("chmod 600 id_dsa3") # ssh -i id_dsa3 test@127.0.0.1

class PRNG(object):
    def __init__(self, seed):
        self.index = 0
        self.seed = seed
        self.buffer = b""
        
    def __call__(self, n):
        while len(self.buffer) < n:
            self.buffer += HMAC.new(self.seed +
                                    pack("<I", self.index)).digest()
            self.index += 1
        result, self.buffer = self.buffer[:n], self.buffer[n:]
        #print('result : %s',result)
        return result

def main():
    parser = argparse.ArgumentParser(description='Generate DSA keys')

    parser.add_argument('-V', dest='version', action='version', version=versionInfo, 
                        help='Print version information')

    parser.add_argument('-b', dest='nbits', action='store',metavar='nbits', required=True,type=int,
                        choices=(512, 1024),help='Number of bits in DSA key (maximum of 1024)')

    parser.add_argument('-s', dest='salt', action='store',required=True, type=str, 
                        help='Use salt when initializing PRNG (thwart offline attacks)')

    parser.add_argument('-p', dest='password', action='store',required=True, type=str, 
                        help='Passphrase to derive DSA key from')
    
    parser.add_argument('-t', dest='keytype', action='store', metavar='keytype',type=int,
                        choices=(0, 1, 2), help='Get DSA key , 0 : all, 1 : publickey,2 : privatekey')

    args = parser.parse_args()
    #print(args)# Output the collected arguments        
    nbits = args.nbits
    passwd = args.password
    salt = args.salt
    keytype = (args.keytype) or 0    
    seed = HMAC.new(passwd+salt).digest()
    key = DSA.generate(nbits, randfunc=PRNG(seed))
    show(key, keytype)
    
if __name__ == "__main__":
    # example : gendsa.py -b 1024 -s aa -p 22 -t 0
    main()
