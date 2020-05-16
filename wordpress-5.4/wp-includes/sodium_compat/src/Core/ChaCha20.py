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
if php_class_exists("ParagonIE_Sodium_Core_ChaCha20", False):
    sys.exit(-1)
# end if
#// 
#// Class ParagonIE_Sodium_Core_ChaCha20
#//
class ParagonIE_Sodium_Core_ChaCha20(ParagonIE_Sodium_Core_Util):
    #// 
    #// Bitwise left rotation
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $v
    #// @param int $n
    #// @return int
    #//
    @classmethod
    def rotate(self, v=None, n=None):
        
        v &= 4294967295
        n &= 31
        return php_int(4294967295 & v << n | v >> 32 - n)
    # end def rotate
    #// 
    #// The ChaCha20 quarter round function. Works on four 32-bit integers.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $a
    #// @param int $b
    #// @param int $c
    #// @param int $d
    #// @return array<int, int>
    #//
    def quarterround(self, a=None, b=None, c=None, d=None):
        
        #// # a = PLUS(a,b); d = ROTATE(XOR(d,a),16);
        #// @var int $a
        a = a + b & 4294967295
        d = self.rotate(d ^ a, 16)
        #// # c = PLUS(c,d); b = ROTATE(XOR(b,c),12);
        #// @var int $c
        c = c + d & 4294967295
        b = self.rotate(b ^ c, 12)
        #// # a = PLUS(a,b); d = ROTATE(XOR(d,a), 8);
        #// @var int $a
        a = a + b & 4294967295
        d = self.rotate(d ^ a, 8)
        #// # c = PLUS(c,d); b = ROTATE(XOR(b,c), 7);
        #// @var int $c
        c = c + d & 4294967295
        b = self.rotate(b ^ c, 7)
        return Array(php_int(a), php_int(b), php_int(c), php_int(d))
    # end def quarterround
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param ParagonIE_Sodium_Core_ChaCha20_Ctx $ctx
    #// @param string $message
    #// 
    #// @return string
    #// @throws TypeError
    #// @throws SodiumException
    #//
    @classmethod
    def encryptbytes(self, ctx=None, message=""):
        
        bytes = self.strlen(message)
        #// 
        #// j0 = ctx->input[0];
        #// j1 = ctx->input[1];
        #// j2 = ctx->input[2];
        #// j3 = ctx->input[3];
        #// j4 = ctx->input[4];
        #// j5 = ctx->input[5];
        #// j6 = ctx->input[6];
        #// j7 = ctx->input[7];
        #// j8 = ctx->input[8];
        #// j9 = ctx->input[9];
        #// j10 = ctx->input[10];
        #// j11 = ctx->input[11];
        #// j12 = ctx->input[12];
        #// j13 = ctx->input[13];
        #// j14 = ctx->input[14];
        #// j15 = ctx->input[15];
        #//
        j0 = php_int(ctx[0])
        j1 = php_int(ctx[1])
        j2 = php_int(ctx[2])
        j3 = php_int(ctx[3])
        j4 = php_int(ctx[4])
        j5 = php_int(ctx[5])
        j6 = php_int(ctx[6])
        j7 = php_int(ctx[7])
        j8 = php_int(ctx[8])
        j9 = php_int(ctx[9])
        j10 = php_int(ctx[10])
        j11 = php_int(ctx[11])
        j12 = php_int(ctx[12])
        j13 = php_int(ctx[13])
        j14 = php_int(ctx[14])
        j15 = php_int(ctx[15])
        c = ""
        while True:
            
            if bytes < 64:
                message += php_str_repeat(" ", 64 - bytes)
            # end if
            x0 = php_int(j0)
            x1 = php_int(j1)
            x2 = php_int(j2)
            x3 = php_int(j3)
            x4 = php_int(j4)
            x5 = php_int(j5)
            x6 = php_int(j6)
            x7 = php_int(j7)
            x8 = php_int(j8)
            x9 = php_int(j9)
            x10 = php_int(j10)
            x11 = php_int(j11)
            x12 = php_int(j12)
            x13 = php_int(j13)
            x14 = php_int(j14)
            x15 = php_int(j15)
            #// # for (i = 20; i > 0; i -= 2) {
            i = 20
            while i > 0:
                
                #// # QUARTERROUND( x0,  x4,  x8,  x12)
                x0, x4, x8, x12 = self.quarterround(x0, x4, x8, x12)
                #// # QUARTERROUND( x1,  x5,  x9,  x13)
                x1, x5, x9, x13 = self.quarterround(x1, x5, x9, x13)
                #// # QUARTERROUND( x2,  x6,  x10,  x14)
                x2, x6, x10, x14 = self.quarterround(x2, x6, x10, x14)
                #// # QUARTERROUND( x3,  x7,  x11,  x15)
                x3, x7, x11, x15 = self.quarterround(x3, x7, x11, x15)
                #// # QUARTERROUND( x0,  x5,  x10,  x15)
                x0, x5, x10, x15 = self.quarterround(x0, x5, x10, x15)
                #// # QUARTERROUND( x1,  x6,  x11,  x12)
                x1, x6, x11, x12 = self.quarterround(x1, x6, x11, x12)
                #// # QUARTERROUND( x2,  x7,  x8,  x13)
                x2, x7, x8, x13 = self.quarterround(x2, x7, x8, x13)
                #// # QUARTERROUND( x3,  x4,  x9,  x14)
                x3, x4, x9, x14 = self.quarterround(x3, x4, x9, x14)
                i -= 2
            # end while
            #// 
            #// x0 = PLUS(x0, j0);
            #// x1 = PLUS(x1, j1);
            #// x2 = PLUS(x2, j2);
            #// x3 = PLUS(x3, j3);
            #// x4 = PLUS(x4, j4);
            #// x5 = PLUS(x5, j5);
            #// x6 = PLUS(x6, j6);
            #// x7 = PLUS(x7, j7);
            #// x8 = PLUS(x8, j8);
            #// x9 = PLUS(x9, j9);
            #// x10 = PLUS(x10, j10);
            #// x11 = PLUS(x11, j11);
            #// x12 = PLUS(x12, j12);
            #// x13 = PLUS(x13, j13);
            #// x14 = PLUS(x14, j14);
            #// x15 = PLUS(x15, j15);
            #// 
            #// @var int $x0
            x0 = x0 & 4294967295 + j0
            #// @var int $x1
            x1 = x1 & 4294967295 + j1
            #// @var int $x2
            x2 = x2 & 4294967295 + j2
            #// @var int $x3
            x3 = x3 & 4294967295 + j3
            #// @var int $x4
            x4 = x4 & 4294967295 + j4
            #// @var int $x5
            x5 = x5 & 4294967295 + j5
            #// @var int $x6
            x6 = x6 & 4294967295 + j6
            #// @var int $x7
            x7 = x7 & 4294967295 + j7
            #// @var int $x8
            x8 = x8 & 4294967295 + j8
            #// @var int $x9
            x9 = x9 & 4294967295 + j9
            #// @var int $x10
            x10 = x10 & 4294967295 + j10
            #// @var int $x11
            x11 = x11 & 4294967295 + j11
            #// @var int $x12
            x12 = x12 & 4294967295 + j12
            #// @var int $x13
            x13 = x13 & 4294967295 + j13
            #// @var int $x14
            x14 = x14 & 4294967295 + j14
            #// @var int $x15
            x15 = x15 & 4294967295 + j15
            #// 
            #// x0 = XOR(x0, LOAD32_LE(m + 0));
            #// x1 = XOR(x1, LOAD32_LE(m + 4));
            #// x2 = XOR(x2, LOAD32_LE(m + 8));
            #// x3 = XOR(x3, LOAD32_LE(m + 12));
            #// x4 = XOR(x4, LOAD32_LE(m + 16));
            #// x5 = XOR(x5, LOAD32_LE(m + 20));
            #// x6 = XOR(x6, LOAD32_LE(m + 24));
            #// x7 = XOR(x7, LOAD32_LE(m + 28));
            #// x8 = XOR(x8, LOAD32_LE(m + 32));
            #// x9 = XOR(x9, LOAD32_LE(m + 36));
            #// x10 = XOR(x10, LOAD32_LE(m + 40));
            #// x11 = XOR(x11, LOAD32_LE(m + 44));
            #// x12 = XOR(x12, LOAD32_LE(m + 48));
            #// x13 = XOR(x13, LOAD32_LE(m + 52));
            #// x14 = XOR(x14, LOAD32_LE(m + 56));
            #// x15 = XOR(x15, LOAD32_LE(m + 60));
            #//
            x0 ^= self.load_4(self.substr(message, 0, 4))
            x1 ^= self.load_4(self.substr(message, 4, 4))
            x2 ^= self.load_4(self.substr(message, 8, 4))
            x3 ^= self.load_4(self.substr(message, 12, 4))
            x4 ^= self.load_4(self.substr(message, 16, 4))
            x5 ^= self.load_4(self.substr(message, 20, 4))
            x6 ^= self.load_4(self.substr(message, 24, 4))
            x7 ^= self.load_4(self.substr(message, 28, 4))
            x8 ^= self.load_4(self.substr(message, 32, 4))
            x9 ^= self.load_4(self.substr(message, 36, 4))
            x10 ^= self.load_4(self.substr(message, 40, 4))
            x11 ^= self.load_4(self.substr(message, 44, 4))
            x12 ^= self.load_4(self.substr(message, 48, 4))
            x13 ^= self.load_4(self.substr(message, 52, 4))
            x14 ^= self.load_4(self.substr(message, 56, 4))
            x15 ^= self.load_4(self.substr(message, 60, 4))
            #// 
            #// j12 = PLUSONE(j12);
            #// if (!j12) {
            #// j13 = PLUSONE(j13);
            #// }
            #//
            j12 += 1
            if j12 & 4026531840:
                raise php_new_class("SodiumException", lambda : SodiumException("Overflow"))
            # end if
            #// 
            #// STORE32_LE(c + 0, x0);
            #// STORE32_LE(c + 4, x1);
            #// STORE32_LE(c + 8, x2);
            #// STORE32_LE(c + 12, x3);
            #// STORE32_LE(c + 16, x4);
            #// STORE32_LE(c + 20, x5);
            #// STORE32_LE(c + 24, x6);
            #// STORE32_LE(c + 28, x7);
            #// STORE32_LE(c + 32, x8);
            #// STORE32_LE(c + 36, x9);
            #// STORE32_LE(c + 40, x10);
            #// STORE32_LE(c + 44, x11);
            #// STORE32_LE(c + 48, x12);
            #// STORE32_LE(c + 52, x13);
            #// STORE32_LE(c + 56, x14);
            #// STORE32_LE(c + 60, x15);
            #//
            block = self.store32_le(php_int(x0 & 4294967295)) + self.store32_le(php_int(x1 & 4294967295)) + self.store32_le(php_int(x2 & 4294967295)) + self.store32_le(php_int(x3 & 4294967295)) + self.store32_le(php_int(x4 & 4294967295)) + self.store32_le(php_int(x5 & 4294967295)) + self.store32_le(php_int(x6 & 4294967295)) + self.store32_le(php_int(x7 & 4294967295)) + self.store32_le(php_int(x8 & 4294967295)) + self.store32_le(php_int(x9 & 4294967295)) + self.store32_le(php_int(x10 & 4294967295)) + self.store32_le(php_int(x11 & 4294967295)) + self.store32_le(php_int(x12 & 4294967295)) + self.store32_le(php_int(x13 & 4294967295)) + self.store32_le(php_int(x14 & 4294967295)) + self.store32_le(php_int(x15 & 4294967295))
            #// Partial block
            if bytes < 64:
                c += self.substr(block, 0, bytes)
                break
            # end if
            #// Full block
            c += block
            bytes -= 64
            if bytes <= 0:
                break
            # end if
            message = self.substr(message, 64)
            
        # end while
        #// end for(;;) loop
        ctx[12] = j12
        ctx[13] = j13
        return c
    # end def encryptbytes
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $len
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def stream(self, len=64, nonce="", key=""):
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core_ChaCha20_Ctx", lambda : ParagonIE_Sodium_Core_ChaCha20_Ctx(key, nonce)), php_str_repeat(" ", len))
    # end def stream
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $len
    #// @param string $nonce
    #// @param string $key
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def ietfstream(self, len=None, nonce="", key=""):
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core_ChaCha20_IetfCtx", lambda : ParagonIE_Sodium_Core_ChaCha20_IetfCtx(key, nonce)), php_str_repeat(" ", len))
    # end def ietfstream
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $message
    #// @param string $nonce
    #// @param string $key
    #// @param string $ic
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def ietfstreamxoric(self, message=None, nonce="", key="", ic=""):
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core_ChaCha20_IetfCtx", lambda : ParagonIE_Sodium_Core_ChaCha20_IetfCtx(key, nonce, ic)), message)
    # end def ietfstreamxoric
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $message
    #// @param string $nonce
    #// @param string $key
    #// @param string $ic
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def streamxoric(self, message=None, nonce="", key="", ic=""):
        
        return self.encryptbytes(php_new_class("ParagonIE_Sodium_Core_ChaCha20_Ctx", lambda : ParagonIE_Sodium_Core_ChaCha20_Ctx(key, nonce, ic)), message)
    # end def streamxoric
# end class ParagonIE_Sodium_Core_ChaCha20
