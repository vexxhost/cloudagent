# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 VEXXHOST, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
SimpleDH
"""

import base64
import binascii
import hashlib
import os

from Crypto.Cipher import AES


class SimpleDH(object):
    """
    This class wraps all the functionality needed to implement
    basic Diffie-Hellman-Merkle key exchange in Python. It features
    intelligent defaults for the prime and base numbers needed for the
    calculation, while allowing you to supply your own. It requires that
    the openssl binary be installed on the system on which this is run,
    as it uses that to handle the encryption and decryption. If openssl
    is not available, a RuntimeError will be raised.
    """
    def __init__(self):
        self._prime = 162259276829213363391578010288127
        self._base = 5
        self._public = None
        self._shared = None
        self.generate_private()

    def generate_private(self):
        self._private = int(binascii.hexlify(os.urandom(10)), 16)
        return self._private

    def get_public(self):
        self._public = self.mod_exp(self._base, self._private, self._prime)
        return self._public

    def compute_shared(self, other):
        self._shared = self.mod_exp(other, self._private, self._prime)
        return self._shared

    @staticmethod
    def mod_exp(num, exp, mod):
        """Efficient implementation of (num ** exp) % mod"""
        result = 1
        while exp > 0:
            if (exp & 1) == 1:
                result = (result * num) % mod
            exp = exp >> 1
            num = (num * num) % mod
        return result

    def decrypt(self, text):
        # Get the key and IV from the generated password
        key, iv = self._bytes_to_key(self._shared)

        # Decode the data from base64 to binary
        data = base64.b64decode(text)

        # Decrypt the data using key and IV
        unpad = lambda s : s[0:-ord(s[-1])]
        decrypt = AES.new(key, AES.MODE_CBC, iv)
        return unpad(decrypt.decrypt(data))

    def _bytes_to_key(self, password, salt=0, key_len=16, iv_len=16):
        dtot =  hashlib.md5(str(password + salt)).digest()
        d = [ dtot ]
        while len(dtot)<(iv_len+key_len):
            d.append( hashlib.md5(d[-1] + str(password + salt)).digest() )
            dtot += d[-1]
        return dtot[:key_len], dtot[key_len:key_len+iv_len]
