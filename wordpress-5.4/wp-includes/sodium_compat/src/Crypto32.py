#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import cgi
    import os
    import os.path
    import copy
    import sys
    from goto import with_goto
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
if php_class_exists("ParagonIE_Sodium_Crypto32", False):
    sys.exit(-1)
# end if
#// 
#// Class ParagonIE_Sodium_Crypto
#// 
#// ATTENTION!
#// 
#// If you are using this library, you should be using
#// ParagonIE_Sodium_Compat in your code, not this class.
#//
class ParagonIE_Sodium_Crypto32():
    aead_chacha20poly1305_KEYBYTES = 32
    aead_chacha20poly1305_NSECBYTES = 0
    aead_chacha20poly1305_NPUBBYTES = 8
    aead_chacha20poly1305_ABYTES = 16
    aead_chacha20poly1305_IETF_KEYBYTES = 32
    aead_chacha20poly1305_IETF_NSECBYTES = 0
    aead_chacha20poly1305_IETF_NPUBBYTES = 12
    aead_chacha20poly1305_IETF_ABYTES = 16
    aead_xchacha20poly1305_IETF_KEYBYTES = 32
    aead_xchacha20poly1305_IETF_NSECBYTES = 0
    aead_xchacha20poly1305_IETF_NPUBBYTES = 24
    aead_xchacha20poly1305_IETF_ABYTES = 16
    box_curve25519xsalsa20poly1305_SEEDBYTES = 32
    box_curve25519xsalsa20poly1305_PUBLICKEYBYTES = 32
    box_curve25519xsalsa20poly1305_SECRETKEYBYTES = 32
    box_curve25519xsalsa20poly1305_BEFORENMBYTES = 32
    box_curve25519xsalsa20poly1305_NONCEBYTES = 24
    box_curve25519xsalsa20poly1305_MACBYTES = 16
    box_curve25519xsalsa20poly1305_BOXZEROBYTES = 16
    box_curve25519xsalsa20poly1305_ZEROBYTES = 32
    onetimeauth_poly1305_BYTES = 16
    onetimeauth_poly1305_KEYBYTES = 32
    secretbox_xsalsa20poly1305_KEYBYTES = 32
    secretbox_xsalsa20poly1305_NONCEBYTES = 24
    secretbox_xsalsa20poly1305_MACBYTES = 16
    secretbox_xsalsa20poly1305_BOXZEROBYTES = 16
    secretbox_xsalsa20poly1305_ZEROBYTES = 32
    secretbox_xchacha20poly1305_KEYBYTES = 32
    secretbox_xchacha20poly1305_NONCEBYTES = 24
    secretbox_xchacha20poly1305_MACBYTES = 16
    secretbox_xchacha20poly1305_BOXZEROBYTES = 16
    secretbox_xchacha20poly1305_ZEROBYTES = 32
    stream_salsa20_KEYBYTES = 32
    #// 
    #// AEAD Decryption with ChaCha20-Poly1305
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $message
    #// @param string $ad
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def aead_chacha20poly1305_decrypt(self, message="", ad="", nonce="", key=""):
        
        #// @var int $len - Length of message (ciphertext + MAC)
        len = ParagonIE_Sodium_Core32_Util.strlen(message)
        #// @var int  $clen - Length of ciphertext
        clen = len - self.aead_chacha20poly1305_ABYTES
        #// @var int $adlen - Length of associated data
        adlen = ParagonIE_Sodium_Core32_Util.strlen(ad)
        #// @var string $mac - Message authentication code
        mac = ParagonIE_Sodium_Core32_Util.substr(message, clen, self.aead_chacha20poly1305_ABYTES)
        #// @var string $ciphertext - The encrypted message (sans MAC)
        ciphertext = ParagonIE_Sodium_Core32_Util.substr(message, 0, clen)
        #// @var string The first block of the chacha20 keystream, used as a poly1305 key
        block0 = ParagonIE_Sodium_Core32_ChaCha20.stream(32, nonce, key)
        #// Recalculate the Poly1305 authentication tag (MAC):
        state = php_new_class("ParagonIE_Sodium_Core32_Poly1305_State", lambda : ParagonIE_Sodium_Core32_Poly1305_State(block0))
        try: 
            ParagonIE_Sodium_Compat.memzero(block0)
        except SodiumException as ex:
            block0 = None
        # end try
        state.update(ad)
        state.update(ParagonIE_Sodium_Core32_Util.store64_le(adlen))
        state.update(ciphertext)
        state.update(ParagonIE_Sodium_Core32_Util.store64_le(clen))
        computed_mac = state.finish()
        #// Compare the given MAC with the recalculated MAC:
        if (not ParagonIE_Sodium_Core32_Util.verify_16(computed_mac, mac)):
            raise php_new_class("SodiumException", lambda : SodiumException("Invalid MAC"))
        # end if
        #// Here, we know that the MAC is valid, so we decrypt and return the plaintext
        return ParagonIE_Sodium_Core32_ChaCha20.streamxoric(ciphertext, nonce, key, ParagonIE_Sodium_Core32_Util.store64_le(1))
    # end def aead_chacha20poly1305_decrypt
    #// 
    #// AEAD Encryption with ChaCha20-Poly1305
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $message
    #// @param string $ad
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def aead_chacha20poly1305_encrypt(self, message="", ad="", nonce="", key=""):
        
        #// @var int $len - Length of the plaintext message
        len = ParagonIE_Sodium_Core32_Util.strlen(message)
        #// @var int $adlen - Length of the associated data
        adlen = ParagonIE_Sodium_Core32_Util.strlen(ad)
        #// @var string The first block of the chacha20 keystream, used as a poly1305 key
        block0 = ParagonIE_Sodium_Core32_ChaCha20.stream(32, nonce, key)
        state = php_new_class("ParagonIE_Sodium_Core32_Poly1305_State", lambda : ParagonIE_Sodium_Core32_Poly1305_State(block0))
        try: 
            ParagonIE_Sodium_Compat.memzero(block0)
        except SodiumException as ex:
            block0 = None
        # end try
        #// @var string $ciphertext - Raw encrypted data
        ciphertext = ParagonIE_Sodium_Core32_ChaCha20.streamxoric(message, nonce, key, ParagonIE_Sodium_Core32_Util.store64_le(1))
        state.update(ad)
        state.update(ParagonIE_Sodium_Core32_Util.store64_le(adlen))
        state.update(ciphertext)
        state.update(ParagonIE_Sodium_Core32_Util.store64_le(len))
        return ciphertext + state.finish()
    # end def aead_chacha20poly1305_encrypt
    #// 
    #// AEAD Decryption with ChaCha20-Poly1305, IETF mode (96-bit nonce)
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $message
    #// @param string $ad
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def aead_chacha20poly1305_ietf_decrypt(self, message="", ad="", nonce="", key=""):
        
        #// @var int $adlen - Length of associated data
        adlen = ParagonIE_Sodium_Core32_Util.strlen(ad)
        #// @var int $len - Length of message (ciphertext + MAC)
        len = ParagonIE_Sodium_Core32_Util.strlen(message)
        #// @var int  $clen - Length of ciphertext
        clen = len - self.aead_chacha20poly1305_IETF_ABYTES
        #// @var string The first block of the chacha20 keystream, used as a poly1305 key
        block0 = ParagonIE_Sodium_Core32_ChaCha20.ietfstream(32, nonce, key)
        #// @var string $mac - Message authentication code
        mac = ParagonIE_Sodium_Core32_Util.substr(message, len - self.aead_chacha20poly1305_IETF_ABYTES, self.aead_chacha20poly1305_IETF_ABYTES)
        #// @var string $ciphertext - The encrypted message (sans MAC)
        ciphertext = ParagonIE_Sodium_Core32_Util.substr(message, 0, len - self.aead_chacha20poly1305_IETF_ABYTES)
        #// Recalculate the Poly1305 authentication tag (MAC):
        state = php_new_class("ParagonIE_Sodium_Core32_Poly1305_State", lambda : ParagonIE_Sodium_Core32_Poly1305_State(block0))
        try: 
            ParagonIE_Sodium_Compat.memzero(block0)
        except SodiumException as ex:
            block0 = None
        # end try
        state.update(ad)
        state.update(php_str_repeat(" ", 16 - adlen & 15))
        state.update(ciphertext)
        state.update(php_str_repeat(" ", 16 - clen & 15))
        state.update(ParagonIE_Sodium_Core32_Util.store64_le(adlen))
        state.update(ParagonIE_Sodium_Core32_Util.store64_le(clen))
        computed_mac = state.finish()
        #// Compare the given MAC with the recalculated MAC:
        if (not ParagonIE_Sodium_Core32_Util.verify_16(computed_mac, mac)):
            raise php_new_class("SodiumException", lambda : SodiumException("Invalid MAC"))
        # end if
        #// Here, we know that the MAC is valid, so we decrypt and return the plaintext
        return ParagonIE_Sodium_Core32_ChaCha20.ietfstreamxoric(ciphertext, nonce, key, ParagonIE_Sodium_Core32_Util.store64_le(1))
    # end def aead_chacha20poly1305_ietf_decrypt
    #// 
    #// AEAD Encryption with ChaCha20-Poly1305, IETF mode (96-bit nonce)
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $message
    #// @param string $ad
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def aead_chacha20poly1305_ietf_encrypt(self, message="", ad="", nonce="", key=""):
        
        #// @var int $len - Length of the plaintext message
        len = ParagonIE_Sodium_Core32_Util.strlen(message)
        #// @var int $adlen - Length of the associated data
        adlen = ParagonIE_Sodium_Core32_Util.strlen(ad)
        #// @var string The first block of the chacha20 keystream, used as a poly1305 key
        block0 = ParagonIE_Sodium_Core32_ChaCha20.ietfstream(32, nonce, key)
        state = php_new_class("ParagonIE_Sodium_Core32_Poly1305_State", lambda : ParagonIE_Sodium_Core32_Poly1305_State(block0))
        try: 
            ParagonIE_Sodium_Compat.memzero(block0)
        except SodiumException as ex:
            block0 = None
        # end try
        #// @var string $ciphertext - Raw encrypted data
        ciphertext = ParagonIE_Sodium_Core32_ChaCha20.ietfstreamxoric(message, nonce, key, ParagonIE_Sodium_Core32_Util.store64_le(1))
        state.update(ad)
        state.update(php_str_repeat(" ", 16 - adlen & 15))
        state.update(ciphertext)
        state.update(php_str_repeat(" ", 16 - len & 15))
        state.update(ParagonIE_Sodium_Core32_Util.store64_le(adlen))
        state.update(ParagonIE_Sodium_Core32_Util.store64_le(len))
        return ciphertext + state.finish()
    # end def aead_chacha20poly1305_ietf_encrypt
    #// 
    #// AEAD Decryption with ChaCha20-Poly1305, IETF mode (96-bit nonce)
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $message
    #// @param string $ad
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def aead_xchacha20poly1305_ietf_decrypt(self, message="", ad="", nonce="", key=""):
        
        subkey = ParagonIE_Sodium_Core32_HChaCha20.hchacha20(ParagonIE_Sodium_Core32_Util.substr(nonce, 0, 16), key)
        nonceLast = "    " + ParagonIE_Sodium_Core32_Util.substr(nonce, 16, 8)
        return self.aead_chacha20poly1305_ietf_decrypt(message, ad, nonceLast, subkey)
    # end def aead_xchacha20poly1305_ietf_decrypt
    #// 
    #// AEAD Encryption with ChaCha20-Poly1305, IETF mode (96-bit nonce)
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $message
    #// @param string $ad
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def aead_xchacha20poly1305_ietf_encrypt(self, message="", ad="", nonce="", key=""):
        
        subkey = ParagonIE_Sodium_Core32_HChaCha20.hchacha20(ParagonIE_Sodium_Core32_Util.substr(nonce, 0, 16), key)
        nonceLast = "    " + ParagonIE_Sodium_Core32_Util.substr(nonce, 16, 8)
        return self.aead_chacha20poly1305_ietf_encrypt(message, ad, nonceLast, subkey)
    # end def aead_xchacha20poly1305_ietf_encrypt
    #// 
    #// HMAC-SHA-512-256 (a.k.a. the leftmost 256 bits of HMAC-SHA-512)
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $message
    #// @param string $key
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def auth(self, message=None, key=None):
        
        return ParagonIE_Sodium_Core32_Util.substr(hash_hmac("sha512", message, key, True), 0, 32)
    # end def auth
    #// 
    #// HMAC-SHA-512-256 validation. Constant-time via hash_equals().
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $mac
    #// @param string $message
    #// @param string $key
    #// @return bool
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def auth_verify(self, mac=None, message=None, key=None):
        
        return ParagonIE_Sodium_Core32_Util.hashequals(mac, self.auth(message, key))
    # end def auth_verify
    #// 
    #// X25519 key exchange followed by XSalsa20Poly1305 symmetric encryption
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $plaintext
    #// @param string $nonce
    #// @param string $keypair
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def box(self, plaintext=None, nonce=None, keypair=None):
        
        return self.secretbox(plaintext, nonce, self.box_beforenm(self.box_secretkey(keypair), self.box_publickey(keypair)))
    # end def box
    #// 
    #// X25519-XSalsa20-Poly1305 with one ephemeral X25519 keypair.
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $message
    #// @param string $publicKey
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def box_seal(self, message=None, publicKey=None):
        
        #// @var string $ephemeralKeypair
        ephemeralKeypair = self.box_keypair()
        #// @var string $ephemeralSK
        ephemeralSK = self.box_secretkey(ephemeralKeypair)
        #// @var string $ephemeralPK
        ephemeralPK = self.box_publickey(ephemeralKeypair)
        #// @var string $nonce
        nonce = self.generichash(ephemeralPK + publicKey, "", 24)
        #// @var string $keypair - The combined keypair used in crypto_box()
        keypair = self.box_keypair_from_secretkey_and_publickey(ephemeralSK, publicKey)
        #// @var string $ciphertext Ciphertext + MAC from crypto_box
        ciphertext = self.box(message, nonce, keypair)
        try: 
            ParagonIE_Sodium_Compat.memzero(ephemeralKeypair)
            ParagonIE_Sodium_Compat.memzero(ephemeralSK)
            ParagonIE_Sodium_Compat.memzero(nonce)
        except SodiumException as ex:
            ephemeralKeypair = None
            ephemeralSK = None
            nonce = None
        # end try
        return ephemeralPK + ciphertext
    # end def box_seal
    #// 
    #// Opens a message encrypted via box_seal().
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $message
    #// @param string $keypair
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def box_seal_open(self, message=None, keypair=None):
        
        #// @var string $ephemeralPK
        ephemeralPK = ParagonIE_Sodium_Core32_Util.substr(message, 0, 32)
        #// @var string $ciphertext (ciphertext + MAC)
        ciphertext = ParagonIE_Sodium_Core32_Util.substr(message, 32)
        #// @var string $secretKey
        secretKey = self.box_secretkey(keypair)
        #// @var string $publicKey
        publicKey = self.box_publickey(keypair)
        #// @var string $nonce
        nonce = self.generichash(ephemeralPK + publicKey, "", 24)
        #// @var string $keypair
        keypair = self.box_keypair_from_secretkey_and_publickey(secretKey, ephemeralPK)
        #// @var string $m
        m = self.box_open(ciphertext, nonce, keypair)
        try: 
            ParagonIE_Sodium_Compat.memzero(secretKey)
            ParagonIE_Sodium_Compat.memzero(ephemeralPK)
            ParagonIE_Sodium_Compat.memzero(nonce)
        except SodiumException as ex:
            secretKey = None
            ephemeralPK = None
            nonce = None
        # end try
        return m
    # end def box_seal_open
    #// 
    #// Used by crypto_box() to get the crypto_secretbox() key.
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $sk
    #// @param string $pk
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def box_beforenm(self, sk=None, pk=None):
        
        return ParagonIE_Sodium_Core32_HSalsa20.hsalsa20(php_str_repeat(" ", 16), self.scalarmult(sk, pk))
    # end def box_beforenm
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @return string
    #// @throws Exception
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def box_keypair(self):
        
        sKey = random_bytes(32)
        pKey = self.scalarmult_base(sKey)
        return sKey + pKey
    # end def box_keypair
    #// 
    #// @param string $seed
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def box_seed_keypair(self, seed=None):
        
        sKey = ParagonIE_Sodium_Core32_Util.substr(hash("sha512", seed, True), 0, 32)
        pKey = self.scalarmult_base(sKey)
        return sKey + pKey
    # end def box_seed_keypair
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $sKey
    #// @param string $pKey
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def box_keypair_from_secretkey_and_publickey(self, sKey=None, pKey=None):
        
        return ParagonIE_Sodium_Core32_Util.substr(sKey, 0, 32) + ParagonIE_Sodium_Core32_Util.substr(pKey, 0, 32)
    # end def box_keypair_from_secretkey_and_publickey
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $keypair
    #// @return string
    #// @throws RangeException
    #// @throws TypeError
    #//
    @classmethod
    def box_secretkey(self, keypair=None):
        
        if ParagonIE_Sodium_Core32_Util.strlen(keypair) != 64:
            raise php_new_class("RangeException", lambda : RangeException("Must be ParagonIE_Sodium_Compat::CRYPTO_BOX_KEYPAIRBYTES bytes long."))
        # end if
        return ParagonIE_Sodium_Core32_Util.substr(keypair, 0, 32)
    # end def box_secretkey
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $keypair
    #// @return string
    #// @throws RangeException
    #// @throws TypeError
    #//
    @classmethod
    def box_publickey(self, keypair=None):
        
        if ParagonIE_Sodium_Core32_Util.strlen(keypair) != ParagonIE_Sodium_Compat.CRYPTO_BOX_KEYPAIRBYTES:
            raise php_new_class("RangeException", lambda : RangeException("Must be ParagonIE_Sodium_Compat::CRYPTO_BOX_KEYPAIRBYTES bytes long."))
        # end if
        return ParagonIE_Sodium_Core32_Util.substr(keypair, 32, 32)
    # end def box_publickey
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $sKey
    #// @return string
    #// @throws RangeException
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def box_publickey_from_secretkey(self, sKey=None):
        
        if ParagonIE_Sodium_Core32_Util.strlen(sKey) != ParagonIE_Sodium_Compat.CRYPTO_BOX_SECRETKEYBYTES:
            raise php_new_class("RangeException", lambda : RangeException("Must be ParagonIE_Sodium_Compat::CRYPTO_BOX_SECRETKEYBYTES bytes long."))
        # end if
        return self.scalarmult_base(sKey)
    # end def box_publickey_from_secretkey
    #// 
    #// Decrypt a message encrypted with box().
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $ciphertext
    #// @param string $nonce
    #// @param string $keypair
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def box_open(self, ciphertext=None, nonce=None, keypair=None):
        
        return self.secretbox_open(ciphertext, nonce, self.box_beforenm(self.box_secretkey(keypair), self.box_publickey(keypair)))
    # end def box_open
    #// 
    #// Calculate a BLAKE2b hash.
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $message
    #// @param string|null $key
    #// @param int $outlen
    #// @return string
    #// @throws RangeException
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def generichash(self, message=None, key="", outlen=32):
        
        #// This ensures that ParagonIE_Sodium_Core32_BLAKE2b::$iv is initialized
        ParagonIE_Sodium_Core32_BLAKE2b.pseudoconstructor()
        k = None
        if (not php_empty(lambda : key)):
            #// @var SplFixedArray $k
            k = ParagonIE_Sodium_Core32_BLAKE2b.stringtosplfixedarray(key)
            if k.count() > ParagonIE_Sodium_Core32_BLAKE2b.KEYBYTES:
                raise php_new_class("RangeException", lambda : RangeException("Invalid key size"))
            # end if
        # end if
        #// @var SplFixedArray $in
        in_ = ParagonIE_Sodium_Core32_BLAKE2b.stringtosplfixedarray(message)
        #// @var SplFixedArray $ctx
        ctx = ParagonIE_Sodium_Core32_BLAKE2b.init(k, outlen)
        ParagonIE_Sodium_Core32_BLAKE2b.update(ctx, in_, in_.count())
        #// @var SplFixedArray $out
        out = php_new_class("SplFixedArray", lambda : SplFixedArray(outlen))
        out = ParagonIE_Sodium_Core32_BLAKE2b.finish(ctx, out)
        #// @var array<int, int>
        outArray = out.toarray()
        return ParagonIE_Sodium_Core32_Util.intarraytostring(outArray)
    # end def generichash
    #// 
    #// Finalize a BLAKE2b hashing context, returning the hash.
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $ctx
    #// @param int $outlen
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def generichash_final(self, ctx=None, outlen=32):
        
        if (not php_is_string(ctx)):
            raise php_new_class("TypeError", lambda : TypeError("Context must be a string"))
        # end if
        out = php_new_class("SplFixedArray", lambda : SplFixedArray(outlen))
        #// @var SplFixedArray $context
        context = ParagonIE_Sodium_Core32_BLAKE2b.stringtocontext(ctx)
        #// @var SplFixedArray $out
        out = ParagonIE_Sodium_Core32_BLAKE2b.finish(context, out)
        #// @var array<int, int>
        outArray = out.toarray()
        return ParagonIE_Sodium_Core32_Util.intarraytostring(outArray)
    # end def generichash_final
    #// 
    #// Initialize a hashing context for BLAKE2b.
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $key
    #// @param int $outputLength
    #// @return string
    #// @throws RangeException
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def generichash_init(self, key="", outputLength=32):
        
        #// This ensures that ParagonIE_Sodium_Core32_BLAKE2b::$iv is initialized
        ParagonIE_Sodium_Core32_BLAKE2b.pseudoconstructor()
        k = None
        if (not php_empty(lambda : key)):
            k = ParagonIE_Sodium_Core32_BLAKE2b.stringtosplfixedarray(key)
            if k.count() > ParagonIE_Sodium_Core32_BLAKE2b.KEYBYTES:
                raise php_new_class("RangeException", lambda : RangeException("Invalid key size"))
            # end if
        # end if
        #// @var SplFixedArray $ctx
        ctx = ParagonIE_Sodium_Core32_BLAKE2b.init(k, outputLength)
        return ParagonIE_Sodium_Core32_BLAKE2b.contexttostring(ctx)
    # end def generichash_init
    #// 
    #// Initialize a hashing context for BLAKE2b.
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $key
    #// @param int $outputLength
    #// @param string $salt
    #// @param string $personal
    #// @return string
    #// @throws RangeException
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def generichash_init_salt_personal(self, key="", outputLength=32, salt="", personal=""):
        
        #// This ensures that ParagonIE_Sodium_Core32_BLAKE2b::$iv is initialized
        ParagonIE_Sodium_Core32_BLAKE2b.pseudoconstructor()
        k = None
        if (not php_empty(lambda : key)):
            k = ParagonIE_Sodium_Core32_BLAKE2b.stringtosplfixedarray(key)
            if k.count() > ParagonIE_Sodium_Core32_BLAKE2b.KEYBYTES:
                raise php_new_class("RangeException", lambda : RangeException("Invalid key size"))
            # end if
        # end if
        if (not php_empty(lambda : salt)):
            s = ParagonIE_Sodium_Core32_BLAKE2b.stringtosplfixedarray(salt)
        else:
            s = None
        # end if
        if (not php_empty(lambda : salt)):
            p = ParagonIE_Sodium_Core32_BLAKE2b.stringtosplfixedarray(personal)
        else:
            p = None
        # end if
        #// @var SplFixedArray $ctx
        ctx = ParagonIE_Sodium_Core32_BLAKE2b.init(k, outputLength, s, p)
        return ParagonIE_Sodium_Core32_BLAKE2b.contexttostring(ctx)
    # end def generichash_init_salt_personal
    #// 
    #// Update a hashing context for BLAKE2b with $message
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $ctx
    #// @param string $message
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def generichash_update(self, ctx=None, message=None):
        
        #// This ensures that ParagonIE_Sodium_Core32_BLAKE2b::$iv is initialized
        ParagonIE_Sodium_Core32_BLAKE2b.pseudoconstructor()
        #// @var SplFixedArray $context
        context = ParagonIE_Sodium_Core32_BLAKE2b.stringtocontext(ctx)
        #// @var SplFixedArray $in
        in_ = ParagonIE_Sodium_Core32_BLAKE2b.stringtosplfixedarray(message)
        ParagonIE_Sodium_Core32_BLAKE2b.update(context, in_, in_.count())
        return ParagonIE_Sodium_Core32_BLAKE2b.contexttostring(context)
    # end def generichash_update
    #// 
    #// Libsodium's crypto_kx().
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $my_sk
    #// @param string $their_pk
    #// @param string $client_pk
    #// @param string $server_pk
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def keyexchange(self, my_sk=None, their_pk=None, client_pk=None, server_pk=None):
        
        return self.generichash(self.scalarmult(my_sk, their_pk) + client_pk + server_pk)
    # end def keyexchange
    #// 
    #// ECDH over Curve25519
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $sKey
    #// @param string $pKey
    #// @return string
    #// 
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def scalarmult(self, sKey=None, pKey=None):
        
        q = ParagonIE_Sodium_Core32_X25519.crypto_scalarmult_curve25519_ref10(sKey, pKey)
        self.scalarmult_throw_if_zero(q)
        return q
    # end def scalarmult
    #// 
    #// ECDH over Curve25519, using the basepoint.
    #// Used to get a secret key from a public key.
    #// 
    #// @param string $secret
    #// @return string
    #// 
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def scalarmult_base(self, secret=None):
        
        q = ParagonIE_Sodium_Core32_X25519.crypto_scalarmult_curve25519_ref10_base(secret)
        self.scalarmult_throw_if_zero(q)
        return q
    # end def scalarmult_base
    #// 
    #// This throws an Error if a zero public key was passed to the function.
    #// 
    #// @param string $q
    #// @return void
    #// @throws SodiumException
    #// @throws TypeError
    #//
    def scalarmult_throw_if_zero(self, q=None):
        
        d = 0
        i = 0
        while i < self.box_curve25519xsalsa20poly1305_SECRETKEYBYTES:
            
            d |= ParagonIE_Sodium_Core32_Util.chrtoint(q[i])
            i += 1
        # end while
        #// branch-free variant of === 0
        if -1 & d - 1 >> 8:
            raise php_new_class("SodiumException", lambda : SodiumException("Zero public key is not allowed"))
        # end if
    # end def scalarmult_throw_if_zero
    #// 
    #// XSalsa20-Poly1305 authenticated symmetric-key encryption.
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $plaintext
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def secretbox(self, plaintext=None, nonce=None, key=None):
        
        #// @var string $subkey
        subkey = ParagonIE_Sodium_Core32_HSalsa20.hsalsa20(nonce, key)
        #// @var string $block0
        block0 = php_str_repeat(" ", 32)
        #// @var int $mlen - Length of the plaintext message
        mlen = ParagonIE_Sodium_Core32_Util.strlen(plaintext)
        mlen0 = mlen
        if mlen0 > 64 - self.secretbox_xsalsa20poly1305_ZEROBYTES:
            mlen0 = 64 - self.secretbox_xsalsa20poly1305_ZEROBYTES
        # end if
        block0 += ParagonIE_Sodium_Core32_Util.substr(plaintext, 0, mlen0)
        #// @var string $block0
        block0 = ParagonIE_Sodium_Core32_Salsa20.salsa20_xor(block0, ParagonIE_Sodium_Core32_Util.substr(nonce, 16, 8), subkey)
        #// @var string $c
        c = ParagonIE_Sodium_Core32_Util.substr(block0, self.secretbox_xsalsa20poly1305_ZEROBYTES)
        if mlen > mlen0:
            c += ParagonIE_Sodium_Core32_Salsa20.salsa20_xor_ic(ParagonIE_Sodium_Core32_Util.substr(plaintext, self.secretbox_xsalsa20poly1305_ZEROBYTES), ParagonIE_Sodium_Core32_Util.substr(nonce, 16, 8), 1, subkey)
        # end if
        state = php_new_class("ParagonIE_Sodium_Core32_Poly1305_State", lambda : ParagonIE_Sodium_Core32_Poly1305_State(ParagonIE_Sodium_Core32_Util.substr(block0, 0, self.onetimeauth_poly1305_KEYBYTES)))
        try: 
            ParagonIE_Sodium_Compat.memzero(block0)
            ParagonIE_Sodium_Compat.memzero(subkey)
        except SodiumException as ex:
            block0 = None
            subkey = None
        # end try
        state.update(c)
        #// @var string $c - MAC || ciphertext
        c = state.finish() + c
        state = None
        return c
    # end def secretbox
    #// 
    #// Decrypt a ciphertext generated via secretbox().
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $ciphertext
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def secretbox_open(self, ciphertext=None, nonce=None, key=None):
        
        #// @var string $mac
        mac = ParagonIE_Sodium_Core32_Util.substr(ciphertext, 0, self.secretbox_xsalsa20poly1305_MACBYTES)
        #// @var string $c
        c = ParagonIE_Sodium_Core32_Util.substr(ciphertext, self.secretbox_xsalsa20poly1305_MACBYTES)
        #// @var int $clen
        clen = ParagonIE_Sodium_Core32_Util.strlen(c)
        #// @var string $subkey
        subkey = ParagonIE_Sodium_Core32_HSalsa20.hsalsa20(nonce, key)
        #// @var string $block0
        block0 = ParagonIE_Sodium_Core32_Salsa20.salsa20(64, ParagonIE_Sodium_Core32_Util.substr(nonce, 16, 8), subkey)
        verified = ParagonIE_Sodium_Core32_Poly1305.onetimeauth_verify(mac, c, ParagonIE_Sodium_Core32_Util.substr(block0, 0, 32))
        if (not verified):
            try: 
                ParagonIE_Sodium_Compat.memzero(subkey)
            except SodiumException as ex:
                subkey = None
            # end try
            raise php_new_class("SodiumException", lambda : SodiumException("Invalid MAC"))
        # end if
        #// @var string $m - Decrypted message
        m = ParagonIE_Sodium_Core32_Util.xorstrings(ParagonIE_Sodium_Core32_Util.substr(block0, self.secretbox_xsalsa20poly1305_ZEROBYTES), ParagonIE_Sodium_Core32_Util.substr(c, 0, self.secretbox_xsalsa20poly1305_ZEROBYTES))
        if clen > self.secretbox_xsalsa20poly1305_ZEROBYTES:
            #// We had more than 1 block, so let's continue to decrypt the rest.
            m += ParagonIE_Sodium_Core32_Salsa20.salsa20_xor_ic(ParagonIE_Sodium_Core32_Util.substr(c, self.secretbox_xsalsa20poly1305_ZEROBYTES), ParagonIE_Sodium_Core32_Util.substr(nonce, 16, 8), 1, php_str(subkey))
        # end if
        return m
    # end def secretbox_open
    #// 
    #// XChaCha20-Poly1305 authenticated symmetric-key encryption.
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $plaintext
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def secretbox_xchacha20poly1305(self, plaintext=None, nonce=None, key=None):
        
        #// @var string $subkey
        subkey = ParagonIE_Sodium_Core32_HChaCha20.hchacha20(ParagonIE_Sodium_Core32_Util.substr(nonce, 0, 16), key)
        nonceLast = ParagonIE_Sodium_Core32_Util.substr(nonce, 16, 8)
        #// @var string $block0
        block0 = php_str_repeat(" ", 32)
        #// @var int $mlen - Length of the plaintext message
        mlen = ParagonIE_Sodium_Core32_Util.strlen(plaintext)
        mlen0 = mlen
        if mlen0 > 64 - self.secretbox_xchacha20poly1305_ZEROBYTES:
            mlen0 = 64 - self.secretbox_xchacha20poly1305_ZEROBYTES
        # end if
        block0 += ParagonIE_Sodium_Core32_Util.substr(plaintext, 0, mlen0)
        #// @var string $block0
        block0 = ParagonIE_Sodium_Core32_ChaCha20.streamxoric(block0, nonceLast, subkey)
        #// @var string $c
        c = ParagonIE_Sodium_Core32_Util.substr(block0, self.secretbox_xchacha20poly1305_ZEROBYTES)
        if mlen > mlen0:
            c += ParagonIE_Sodium_Core32_ChaCha20.streamxoric(ParagonIE_Sodium_Core32_Util.substr(plaintext, self.secretbox_xchacha20poly1305_ZEROBYTES), nonceLast, subkey, ParagonIE_Sodium_Core32_Util.store64_le(1))
        # end if
        state = php_new_class("ParagonIE_Sodium_Core32_Poly1305_State", lambda : ParagonIE_Sodium_Core32_Poly1305_State(ParagonIE_Sodium_Core32_Util.substr(block0, 0, self.onetimeauth_poly1305_KEYBYTES)))
        try: 
            ParagonIE_Sodium_Compat.memzero(block0)
            ParagonIE_Sodium_Compat.memzero(subkey)
        except SodiumException as ex:
            block0 = None
            subkey = None
        # end try
        state.update(c)
        #// @var string $c - MAC || ciphertext
        c = state.finish() + c
        state = None
        return c
    # end def secretbox_xchacha20poly1305
    #// 
    #// Decrypt a ciphertext generated via secretbox_xchacha20poly1305().
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $ciphertext
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def secretbox_xchacha20poly1305_open(self, ciphertext=None, nonce=None, key=None):
        
        #// @var string $mac
        mac = ParagonIE_Sodium_Core32_Util.substr(ciphertext, 0, self.secretbox_xchacha20poly1305_MACBYTES)
        #// @var string $c
        c = ParagonIE_Sodium_Core32_Util.substr(ciphertext, self.secretbox_xchacha20poly1305_MACBYTES)
        #// @var int $clen
        clen = ParagonIE_Sodium_Core32_Util.strlen(c)
        #// @var string $subkey
        subkey = ParagonIE_Sodium_Core32_HChaCha20.hchacha20(nonce, key)
        #// @var string $block0
        block0 = ParagonIE_Sodium_Core32_ChaCha20.stream(64, ParagonIE_Sodium_Core32_Util.substr(nonce, 16, 8), subkey)
        verified = ParagonIE_Sodium_Core32_Poly1305.onetimeauth_verify(mac, c, ParagonIE_Sodium_Core32_Util.substr(block0, 0, 32))
        if (not verified):
            try: 
                ParagonIE_Sodium_Compat.memzero(subkey)
            except SodiumException as ex:
                subkey = None
            # end try
            raise php_new_class("SodiumException", lambda : SodiumException("Invalid MAC"))
        # end if
        #// @var string $m - Decrypted message
        m = ParagonIE_Sodium_Core32_Util.xorstrings(ParagonIE_Sodium_Core32_Util.substr(block0, self.secretbox_xchacha20poly1305_ZEROBYTES), ParagonIE_Sodium_Core32_Util.substr(c, 0, self.secretbox_xchacha20poly1305_ZEROBYTES))
        if clen > self.secretbox_xchacha20poly1305_ZEROBYTES:
            #// We had more than 1 block, so let's continue to decrypt the rest.
            m += ParagonIE_Sodium_Core32_ChaCha20.streamxoric(ParagonIE_Sodium_Core32_Util.substr(c, self.secretbox_xchacha20poly1305_ZEROBYTES), ParagonIE_Sodium_Core32_Util.substr(nonce, 16, 8), php_str(subkey), ParagonIE_Sodium_Core32_Util.store64_le(1))
        # end if
        return m
    # end def secretbox_xchacha20poly1305_open
    #// 
    #// @param string $key
    #// @return array<int, string> Returns a state and a header.
    #// @throws Exception
    #// @throws SodiumException
    #//
    @classmethod
    def secretstream_xchacha20poly1305_init_push(self, key=None):
        
        #// # randombytes_buf(out, crypto_secretstream_xchacha20poly1305_HEADERBYTES);
        out = random_bytes(24)
        #// # crypto_core_hchacha20(state->k, out, k, NULL);
        subkey = ParagonIE_Sodium_Core32_HChaCha20.hchacha20(out, key)
        state = php_new_class("ParagonIE_Sodium_Core32_SecretStream_State", lambda : ParagonIE_Sodium_Core32_SecretStream_State(subkey, ParagonIE_Sodium_Core32_Util.substr(out, 16, 8) + php_str_repeat(" ", 4)))
        #// # _crypto_secretstream_xchacha20poly1305_counter_reset(state);
        state.counterreset()
        #// # memcpy(STATE_INONCE(state), out + crypto_core_hchacha20_INPUTBYTES,
        #// #        crypto_secretstream_xchacha20poly1305_INONCEBYTES);
        #// # memset(state->_pad, 0, sizeof state->_pad);
        return Array(state.tostring(), out)
    # end def secretstream_xchacha20poly1305_init_push
    #// 
    #// @param string $key
    #// @param string $header
    #// @return string Returns a state.
    #// @throws Exception
    #//
    @classmethod
    def secretstream_xchacha20poly1305_init_pull(self, key=None, header=None):
        
        #// # crypto_core_hchacha20(state->k, in, k, NULL);
        subkey = ParagonIE_Sodium_Core32_HChaCha20.hchacha20(ParagonIE_Sodium_Core32_Util.substr(header, 0, 16), key)
        state = php_new_class("ParagonIE_Sodium_Core32_SecretStream_State", lambda : ParagonIE_Sodium_Core32_SecretStream_State(subkey, ParagonIE_Sodium_Core32_Util.substr(header, 16)))
        state.counterreset()
        #// # memcpy(STATE_INONCE(state), in + crypto_core_hchacha20_INPUTBYTES,
        #// #     crypto_secretstream_xchacha20poly1305_INONCEBYTES);
        #// # memset(state->_pad, 0, sizeof state->_pad);
        #// # return 0;
        return state.tostring()
    # end def secretstream_xchacha20poly1305_init_pull
    #// 
    #// @param string $state
    #// @param string $msg
    #// @param string $aad
    #// @param int $tag
    #// @return string
    #// @throws SodiumException
    #//
    @classmethod
    def secretstream_xchacha20poly1305_push(self, state=None, msg=None, aad="", tag=0):
        
        st = ParagonIE_Sodium_Core32_SecretStream_State.fromstring(state)
        #// # crypto_onetimeauth_poly1305_state poly1305_state;
        #// # unsigned char                     block[64U];
        #// # unsigned char                     slen[8U];
        #// # unsigned char                    *c;
        #// # unsigned char                    *mac;
        msglen = ParagonIE_Sodium_Core32_Util.strlen(msg)
        aadlen = ParagonIE_Sodium_Core32_Util.strlen(aad)
        if msglen + 63 >> 6 > 4294967294:
            raise php_new_class("SodiumException", lambda : SodiumException("message cannot be larger than SODIUM_CRYPTO_SECRETSTREAM_XCHACHA20POLY1305_MESSAGEBYTES_MAX bytes"))
        # end if
        #// # if (outlen_p != NULL) {
        #// #     *outlen_p = 0U;
        #// # }
        #// # if (mlen > crypto_secretstream_xchacha20poly1305_MESSAGEBYTES_MAX) {
        #// #     sodium_misuse();
        #// # }
        #// # crypto_stream_chacha20_ietf(block, sizeof block, state->nonce, state->k);
        #// # crypto_onetimeauth_poly1305_init(&poly1305_state, block);
        #// # sodium_memzero(block, sizeof block);
        auth = php_new_class("ParagonIE_Sodium_Core32_Poly1305_State", lambda : ParagonIE_Sodium_Core32_Poly1305_State(ParagonIE_Sodium_Core32_ChaCha20.ietfstream(32, st.getcombinednonce(), st.getkey())))
        #// # crypto_onetimeauth_poly1305_update(&poly1305_state, ad, adlen);
        auth.update(aad)
        #// # crypto_onetimeauth_poly1305_update(&poly1305_state, _pad0,
        #// #     (0x10 - adlen) & 0xf);
        auth.update(php_str_repeat(" ", 16 - aadlen & 15))
        #// # memset(block, 0, sizeof block);
        #// # block[0] = tag;
        #// # crypto_stream_chacha20_ietf_xor_ic(block, block, sizeof block,
        #// #                                    state->nonce, 1U, state->k);
        block = ParagonIE_Sodium_Core32_ChaCha20.ietfstreamxoric(ParagonIE_Sodium_Core32_Util.inttochr(tag) + php_str_repeat(" ", 63), st.getcombinednonce(), st.getkey(), ParagonIE_Sodium_Core32_Util.store64_le(1))
        #// # crypto_onetimeauth_poly1305_update(&poly1305_state, block, sizeof block);
        auth.update(block)
        #// # out[0] = block[0];
        out = block[0]
        #// # c = out + (sizeof tag);
        #// # crypto_stream_chacha20_ietf_xor_ic(c, m, mlen, state->nonce, 2U, state->k);
        cipher = ParagonIE_Sodium_Core32_ChaCha20.ietfstreamxoric(msg, st.getcombinednonce(), st.getkey(), ParagonIE_Sodium_Core32_Util.store64_le(2))
        #// # crypto_onetimeauth_poly1305_update(&poly1305_state, c, mlen);
        auth.update(cipher)
        out += cipher
        cipher = None
        #// # crypto_onetimeauth_poly1305_update
        #// # (&poly1305_state, _pad0, (0x10 - (sizeof block) + mlen) & 0xf);
        auth.update(php_str_repeat(" ", 16 - 64 + msglen & 15))
        #// # STORE64_LE(slen, (uint64_t) adlen);
        slen = ParagonIE_Sodium_Core32_Util.store64_le(aadlen)
        #// # crypto_onetimeauth_poly1305_update(&poly1305_state, slen, sizeof slen);
        auth.update(slen)
        #// # STORE64_LE(slen, (sizeof block) + mlen);
        slen = ParagonIE_Sodium_Core32_Util.store64_le(64 + msglen)
        #// # crypto_onetimeauth_poly1305_update(&poly1305_state, slen, sizeof slen);
        auth.update(slen)
        #// # mac = c + mlen;
        #// # crypto_onetimeauth_poly1305_final(&poly1305_state, mac);
        mac = auth.finish()
        out += mac
        auth = None
        #// # XOR_BUF(STATE_INONCE(state), mac,
        #// #     crypto_secretstream_xchacha20poly1305_INONCEBYTES);
        st.xornonce(mac)
        #// # sodium_increment(STATE_COUNTER(state),
        #// #     crypto_secretstream_xchacha20poly1305_COUNTERBYTES);
        st.incrementcounter()
        #// Overwrite by reference:
        state = st.tostring()
        #// @var bool $rekey
        rekey = tag & ParagonIE_Sodium_Compat.CRYPTO_SECRETSTREAM_XCHACHA20POLY1305_TAG_REKEY != 0
        #// # if ((tag & crypto_secretstream_xchacha20poly1305_TAG_REKEY) != 0 ||
        #// #     sodium_is_zero(STATE_COUNTER(state),
        #// #         crypto_secretstream_xchacha20poly1305_COUNTERBYTES)) {
        #// #     crypto_secretstream_xchacha20poly1305_rekey(state);
        #// # }
        if rekey or st.needsrekey():
            #// DO REKEY
            self.secretstream_xchacha20poly1305_rekey(state)
        # end if
        #// # if (outlen_p != NULL) {
        #// #     *outlen_p = crypto_secretstream_xchacha20poly1305_ABYTES + mlen;
        #// # }
        return out
    # end def secretstream_xchacha20poly1305_push
    #// 
    #// @param string $state
    #// @param string $cipher
    #// @param string $aad
    #// @return bool|array{0: string, 1: int}
    #// @throws SodiumException
    #//
    @classmethod
    def secretstream_xchacha20poly1305_pull(self, state=None, cipher=None, aad=""):
        
        st = ParagonIE_Sodium_Core32_SecretStream_State.fromstring(state)
        cipherlen = ParagonIE_Sodium_Core32_Util.strlen(cipher)
        #// #     mlen = inlen - crypto_secretstream_xchacha20poly1305_ABYTES;
        msglen = cipherlen - ParagonIE_Sodium_Compat.CRYPTO_SECRETSTREAM_XCHACHA20POLY1305_ABYTES
        aadlen = ParagonIE_Sodium_Core32_Util.strlen(aad)
        #// #     if (mlen > crypto_secretstream_xchacha20poly1305_MESSAGEBYTES_MAX) {
        #// #         sodium_misuse();
        #// #     }
        if msglen + 63 >> 6 > 4294967294:
            raise php_new_class("SodiumException", lambda : SodiumException("message cannot be larger than SODIUM_CRYPTO_SECRETSTREAM_XCHACHA20POLY1305_MESSAGEBYTES_MAX bytes"))
        # end if
        #// #     crypto_stream_chacha20_ietf(block, sizeof block, state->nonce, state->k);
        #// #     crypto_onetimeauth_poly1305_init(&poly1305_state, block);
        #// #     sodium_memzero(block, sizeof block);
        auth = php_new_class("ParagonIE_Sodium_Core32_Poly1305_State", lambda : ParagonIE_Sodium_Core32_Poly1305_State(ParagonIE_Sodium_Core32_ChaCha20.ietfstream(32, st.getcombinednonce(), st.getkey())))
        #// #     crypto_onetimeauth_poly1305_update(&poly1305_state, ad, adlen);
        auth.update(aad)
        #// #     crypto_onetimeauth_poly1305_update(&poly1305_state, _pad0,
        #// #         (0x10 - adlen) & 0xf);
        auth.update(php_str_repeat(" ", 16 - aadlen & 15))
        #// #     memset(block, 0, sizeof block);
        #// #     block[0] = in[0];
        #// #     crypto_stream_chacha20_ietf_xor_ic(block, block, sizeof block,
        #// #                                        state->nonce, 1U, state->k);
        block = ParagonIE_Sodium_Core32_ChaCha20.ietfstreamxoric(cipher[0] + php_str_repeat(" ", 63), st.getcombinednonce(), st.getkey(), ParagonIE_Sodium_Core32_Util.store64_le(1))
        #// #     tag = block[0];
        #// #     block[0] = in[0];
        #// #     crypto_onetimeauth_poly1305_update(&poly1305_state, block, sizeof block);
        tag = ParagonIE_Sodium_Core32_Util.chrtoint(block[0])
        block[0] = cipher[0]
        auth.update(block)
        #// #     c = in + (sizeof tag);
        #// #     crypto_onetimeauth_poly1305_update(&poly1305_state, c, mlen);
        auth.update(ParagonIE_Sodium_Core32_Util.substr(cipher, 1, msglen))
        #// #     crypto_onetimeauth_poly1305_update
        #// #     (&poly1305_state, _pad0, (0x10 - (sizeof block) + mlen) & 0xf);
        auth.update(php_str_repeat(" ", 16 - 64 + msglen & 15))
        #// #     STORE64_LE(slen, (uint64_t) adlen);
        #// #     crypto_onetimeauth_poly1305_update(&poly1305_state, slen, sizeof slen);
        slen = ParagonIE_Sodium_Core32_Util.store64_le(aadlen)
        auth.update(slen)
        #// #     STORE64_LE(slen, (sizeof block) + mlen);
        #// #     crypto_onetimeauth_poly1305_update(&poly1305_state, slen, sizeof slen);
        slen = ParagonIE_Sodium_Core32_Util.store64_le(64 + msglen)
        auth.update(slen)
        #// #     crypto_onetimeauth_poly1305_final(&poly1305_state, mac);
        #// #     sodium_memzero(&poly1305_state, sizeof poly1305_state);
        mac = auth.finish()
        #// #     stored_mac = c + mlen;
        #// #     if (sodium_memcmp(mac, stored_mac, sizeof mac) != 0) {
        #// #     sodium_memzero(mac, sizeof mac);
        #// #         return -1;
        #// #     }
        stored = ParagonIE_Sodium_Core32_Util.substr(cipher, msglen + 1, 16)
        if (not ParagonIE_Sodium_Core32_Util.hashequals(mac, stored)):
            return False
        # end if
        #// #     crypto_stream_chacha20_ietf_xor_ic(m, c, mlen, state->nonce, 2U, state->k);
        out = ParagonIE_Sodium_Core32_ChaCha20.ietfstreamxoric(ParagonIE_Sodium_Core32_Util.substr(cipher, 1, msglen), st.getcombinednonce(), st.getkey(), ParagonIE_Sodium_Core32_Util.store64_le(2))
        #// #     XOR_BUF(STATE_INONCE(state), mac,
        #// #         crypto_secretstream_xchacha20poly1305_INONCEBYTES);
        st.xornonce(mac)
        #// #     sodium_increment(STATE_COUNTER(state),
        #// #         crypto_secretstream_xchacha20poly1305_COUNTERBYTES);
        st.incrementcounter()
        #// #     if ((tag & crypto_secretstream_xchacha20poly1305_TAG_REKEY) != 0 ||
        #// #         sodium_is_zero(STATE_COUNTER(state),
        #// #             crypto_secretstream_xchacha20poly1305_COUNTERBYTES)) {
        #// #         crypto_secretstream_xchacha20poly1305_rekey(state);
        #// #     }
        #// Overwrite by reference:
        state = st.tostring()
        #// @var bool $rekey
        rekey = tag & ParagonIE_Sodium_Compat.CRYPTO_SECRETSTREAM_XCHACHA20POLY1305_TAG_REKEY != 0
        if rekey or st.needsrekey():
            #// DO REKEY
            self.secretstream_xchacha20poly1305_rekey(state)
        # end if
        return Array(out, tag)
    # end def secretstream_xchacha20poly1305_pull
    #// 
    #// @param string $state
    #// @return void
    #// @throws SodiumException
    #//
    @classmethod
    def secretstream_xchacha20poly1305_rekey(self, state=None):
        
        st = ParagonIE_Sodium_Core32_SecretStream_State.fromstring(state)
        #// # unsigned char new_key_and_inonce[crypto_stream_chacha20_ietf_KEYBYTES +
        #// # crypto_secretstream_xchacha20poly1305_INONCEBYTES];
        #// # size_t        i;
        #// # for (i = 0U; i < crypto_stream_chacha20_ietf_KEYBYTES; i++) {
        #// #     new_key_and_inonce[i] = state->k[i];
        #// # }
        new_key_and_inonce = st.getkey()
        #// # for (i = 0U; i < crypto_secretstream_xchacha20poly1305_INONCEBYTES; i++) {
        #// #     new_key_and_inonce[crypto_stream_chacha20_ietf_KEYBYTES + i] =
        #// #         STATE_INONCE(state)[i];
        #// # }
        new_key_and_inonce += ParagonIE_Sodium_Core32_Util.substr(st.getnonce(), 0, 8)
        #// # crypto_stream_chacha20_ietf_xor(new_key_and_inonce, new_key_and_inonce,
        #// #                                 sizeof new_key_and_inonce,
        #// #                                 state->nonce, state->k);
        st.rekey(ParagonIE_Sodium_Core32_ChaCha20.ietfstreamxoric(new_key_and_inonce, st.getcombinednonce(), st.getkey(), ParagonIE_Sodium_Core32_Util.store64_le(0)))
        #// # for (i = 0U; i < crypto_stream_chacha20_ietf_KEYBYTES; i++) {
        #// #     state->k[i] = new_key_and_inonce[i];
        #// # }
        #// # for (i = 0U; i < crypto_secretstream_xchacha20poly1305_INONCEBYTES; i++) {
        #// #     STATE_INONCE(state)[i] =
        #// #          new_key_and_inonce[crypto_stream_chacha20_ietf_KEYBYTES + i];
        #// # }
        #// # _crypto_secretstream_xchacha20poly1305_counter_reset(state);
        st.counterreset()
        state = st.tostring()
    # end def secretstream_xchacha20poly1305_rekey
    #// 
    #// Detached Ed25519 signature.
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $message
    #// @param string $sk
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def sign_detached(self, message=None, sk=None):
        
        return ParagonIE_Sodium_Core32_Ed25519.sign_detached(message, sk)
    # end def sign_detached
    #// 
    #// Attached Ed25519 signature. (Returns a signed message.)
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $message
    #// @param string $sk
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def sign(self, message=None, sk=None):
        
        return ParagonIE_Sodium_Core32_Ed25519.sign(message, sk)
    # end def sign
    #// 
    #// Opens a signed message. If valid, returns the message.
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $signedMessage
    #// @param string $pk
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def sign_open(self, signedMessage=None, pk=None):
        
        return ParagonIE_Sodium_Core32_Ed25519.sign_open(signedMessage, pk)
    # end def sign_open
    #// 
    #// Verify a detached signature of a given message and public key.
    #// 
    #// @internal Do not use this directly. Use ParagonIE_Sodium_Compat.
    #// 
    #// @param string $signature
    #// @param string $message
    #// @param string $pk
    #// @return bool
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def sign_verify_detached(self, signature=None, message=None, pk=None):
        
        return ParagonIE_Sodium_Core32_Ed25519.verify_detached(signature, message, pk)
    # end def sign_verify_detached
# end class ParagonIE_Sodium_Crypto32
