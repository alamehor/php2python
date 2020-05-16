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
if php_class_exists("ParagonIE_Sodium_Core32_Poly1305_State", False):
    sys.exit(-1)
# end if
#// 
#// Class ParagonIE_Sodium_Core32_Poly1305_State
#//
class ParagonIE_Sodium_Core32_Poly1305_State(ParagonIE_Sodium_Core32_Util):
    buffer = Array()
    final = False
    h = Array()
    leftover = 0
    r = Array()
    pad = Array()
    #// 
    #// ParagonIE_Sodium_Core32_Poly1305_State constructor.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $key
    #// @throws InvalidArgumentException
    #// @throws SodiumException
    #// @throws TypeError
    #//
    def __init__(self, key=""):
        
        if self.strlen(key) < 32:
            raise php_new_class("InvalidArgumentException", lambda : InvalidArgumentException("Poly1305 requires a 32-byte key"))
        # end if
        #// r &= 0xffffffc0ffffffc0ffffffc0fffffff
        self.r = Array(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key, 0, 4)).setunsignedint(True).mask(67108863), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key, 3, 4)).setunsignedint(True).shiftright(2).mask(67108611), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key, 6, 4)).setunsignedint(True).shiftright(4).mask(67092735), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key, 9, 4)).setunsignedint(True).shiftright(6).mask(66076671), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key, 12, 4)).setunsignedint(True).shiftright(8).mask(1048575))
        #// h = 0
        self.h = Array(php_new_class("ParagonIE_Sodium_Core32_Int32", lambda : ParagonIE_Sodium_Core32_Int32(Array(0, 0), True)), php_new_class("ParagonIE_Sodium_Core32_Int32", lambda : ParagonIE_Sodium_Core32_Int32(Array(0, 0), True)), php_new_class("ParagonIE_Sodium_Core32_Int32", lambda : ParagonIE_Sodium_Core32_Int32(Array(0, 0), True)), php_new_class("ParagonIE_Sodium_Core32_Int32", lambda : ParagonIE_Sodium_Core32_Int32(Array(0, 0), True)), php_new_class("ParagonIE_Sodium_Core32_Int32", lambda : ParagonIE_Sodium_Core32_Int32(Array(0, 0), True)))
        #// save pad for later
        self.pad = Array(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key, 16, 4)).setunsignedint(True).toint64(), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key, 20, 4)).setunsignedint(True).toint64(), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key, 24, 4)).setunsignedint(True).toint64(), ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(key, 28, 4)).setunsignedint(True).toint64())
        self.leftover = 0
        self.final = False
    # end def __init__
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $message
    #// @return self
    #// @throws SodiumException
    #// @throws TypeError
    #//
    def update(self, message=""):
        
        bytes = self.strlen(message)
        #// handle leftover
        if self.leftover:
            #// @var int $want
            want = ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE - self.leftover
            if want > bytes:
                want = bytes
            # end if
            i = 0
            while i < want:
                
                mi = self.chrtoint(message[i])
                self.buffer[self.leftover + i] = mi
                i += 1
            # end while
            #// We snip off the leftmost bytes.
            message = self.substr(message, want)
            bytes = self.strlen(message)
            self.leftover += want
            if self.leftover < ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE:
                #// We still don't have enough to run $this->blocks()
                return self
            # end if
            self.blocks(self.intarraytostring(self.buffer), ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE)
            self.leftover = 0
        # end if
        #// process full blocks
        if bytes >= ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE:
            #// @var int $want
            want = bytes & (1 << (ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE - 1).bit_length()) - 1 - ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE - 1
            if want >= ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE:
                #// @var string $block
                block = self.substr(message, 0, want)
                if self.strlen(block) >= ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE:
                    self.blocks(block, want)
                    message = self.substr(message, want)
                    bytes = self.strlen(message)
                # end if
            # end if
        # end if
        #// store leftover
        if bytes:
            i = 0
            while i < bytes:
                
                mi = self.chrtoint(message[i])
                self.buffer[self.leftover + i] = mi
                i += 1
            # end while
            self.leftover = php_int(self.leftover) + bytes
        # end if
        return self
    # end def update
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $message
    #// @param int $bytes
    #// @return self
    #// @throws SodiumException
    #// @throws TypeError
    #//
    def blocks(self, message=None, bytes=None):
        
        if self.strlen(message) < 16:
            message = php_str_pad(message, 16, " ", STR_PAD_RIGHT)
        # end if
        hibit = ParagonIE_Sodium_Core32_Int32.fromint(php_int(0 if self.final else 1 << 24))
        #// 1 << 128
        hibit.setunsignedint(True)
        zero = php_new_class("ParagonIE_Sodium_Core32_Int64", lambda : ParagonIE_Sodium_Core32_Int64(Array(0, 0, 0, 0), True))
        #// 
        #// @var ParagonIE_Sodium_Core32_Int64 $d0
        #// @var ParagonIE_Sodium_Core32_Int64 $d1
        #// @var ParagonIE_Sodium_Core32_Int64 $d2
        #// @var ParagonIE_Sodium_Core32_Int64 $d3
        #// @var ParagonIE_Sodium_Core32_Int64 $d4
        #// @var ParagonIE_Sodium_Core32_Int64 $r0
        #// @var ParagonIE_Sodium_Core32_Int64 $r1
        #// @var ParagonIE_Sodium_Core32_Int64 $r2
        #// @var ParagonIE_Sodium_Core32_Int64 $r3
        #// @var ParagonIE_Sodium_Core32_Int64 $r4
        #// 
        #// @var ParagonIE_Sodium_Core32_Int32 $h0
        #// @var ParagonIE_Sodium_Core32_Int32 $h1
        #// @var ParagonIE_Sodium_Core32_Int32 $h2
        #// @var ParagonIE_Sodium_Core32_Int32 $h3
        #// @var ParagonIE_Sodium_Core32_Int32 $h4
        #//
        r0 = self.r[0].toint64()
        r1 = self.r[1].toint64()
        r2 = self.r[2].toint64()
        r3 = self.r[3].toint64()
        r4 = self.r[4].toint64()
        s1 = r1.toint64().mulint(5, 3)
        s2 = r2.toint64().mulint(5, 3)
        s3 = r3.toint64().mulint(5, 3)
        s4 = r4.toint64().mulint(5, 3)
        h0 = self.h[0]
        h1 = self.h[1]
        h2 = self.h[2]
        h3 = self.h[3]
        h4 = self.h[4]
        while True:
            
            if not (bytes >= ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE):
                break
            # end if
            #// h += m[i]
            h0 = h0.addint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 0, 4)).mask(67108863)).toint64()
            h1 = h1.addint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 3, 4)).shiftright(2).mask(67108863)).toint64()
            h2 = h2.addint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 6, 4)).shiftright(4).mask(67108863)).toint64()
            h3 = h3.addint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 9, 4)).shiftright(6).mask(67108863)).toint64()
            h4 = h4.addint32(ParagonIE_Sodium_Core32_Int32.fromreversestring(self.substr(message, 12, 4)).shiftright(8).orint32(hibit)).toint64()
            #// h *= r
            d0 = zero.addint64(h0.mulint64(r0, 25)).addint64(s4.mulint64(h1, 26)).addint64(s3.mulint64(h2, 26)).addint64(s2.mulint64(h3, 26)).addint64(s1.mulint64(h4, 26))
            d1 = zero.addint64(h0.mulint64(r1, 25)).addint64(h1.mulint64(r0, 25)).addint64(s4.mulint64(h2, 26)).addint64(s3.mulint64(h3, 26)).addint64(s2.mulint64(h4, 26))
            d2 = zero.addint64(h0.mulint64(r2, 25)).addint64(h1.mulint64(r1, 25)).addint64(h2.mulint64(r0, 25)).addint64(s4.mulint64(h3, 26)).addint64(s3.mulint64(h4, 26))
            d3 = zero.addint64(h0.mulint64(r3, 25)).addint64(h1.mulint64(r2, 25)).addint64(h2.mulint64(r1, 25)).addint64(h3.mulint64(r0, 25)).addint64(s4.mulint64(h4, 26))
            d4 = zero.addint64(h0.mulint64(r4, 25)).addint64(h1.mulint64(r3, 25)).addint64(h2.mulint64(r2, 25)).addint64(h3.mulint64(r1, 25)).addint64(h4.mulint64(r0, 25))
            #// (partial) h %= p
            c = d0.shiftright(26)
            h0 = d0.toint32().mask(67108863)
            d1 = d1.addint64(c)
            c = d1.shiftright(26)
            h1 = d1.toint32().mask(67108863)
            d2 = d2.addint64(c)
            c = d2.shiftright(26)
            h2 = d2.toint32().mask(67108863)
            d3 = d3.addint64(c)
            c = d3.shiftright(26)
            h3 = d3.toint32().mask(67108863)
            d4 = d4.addint64(c)
            c = d4.shiftright(26)
            h4 = d4.toint32().mask(67108863)
            h0 = h0.addint32(c.toint32().mulint(5, 3))
            c = h0.shiftright(26)
            h0 = h0.mask(67108863)
            h1 = h1.addint32(c)
            #// Chop off the left 32 bytes.
            message = self.substr(message, ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE)
            bytes -= ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE
        # end while
        #// @var array<int, ParagonIE_Sodium_Core32_Int32> $h
        self.h = Array(h0, h1, h2, h3, h4)
        return self
    # end def blocks
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @return string
    #// @throws SodiumException
    #// @throws TypeError
    #//
    def finish(self):
        
        #// process the remaining block
        if self.leftover:
            i = self.leftover
            self.buffer[i] = 1
            i += 1
            while i < ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE:
                
                self.buffer[i] = 0
                i += 1
            # end while
            self.final = True
            self.blocks(self.substr(self.intarraytostring(self.buffer), 0, ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE), b = ParagonIE_Sodium_Core32_Poly1305.BLOCK_SIZE)
        # end if
        #// 
        #// @var ParagonIE_Sodium_Core32_Int32 $f
        #// @var ParagonIE_Sodium_Core32_Int32 $g0
        #// @var ParagonIE_Sodium_Core32_Int32 $g1
        #// @var ParagonIE_Sodium_Core32_Int32 $g2
        #// @var ParagonIE_Sodium_Core32_Int32 $g3
        #// @var ParagonIE_Sodium_Core32_Int32 $g4
        #// @var ParagonIE_Sodium_Core32_Int32 $h0
        #// @var ParagonIE_Sodium_Core32_Int32 $h1
        #// @var ParagonIE_Sodium_Core32_Int32 $h2
        #// @var ParagonIE_Sodium_Core32_Int32 $h3
        #// @var ParagonIE_Sodium_Core32_Int32 $h4
        #//
        h0 = self.h[0]
        h1 = self.h[1]
        h2 = self.h[2]
        h3 = self.h[3]
        h4 = self.h[4]
        c = h1.shiftright(26)
        #// # $c = $h1 >> 26;
        h1 = h1.mask(67108863)
        #// # $h1 &= 0x3ffffff;
        h2 = h2.addint32(c)
        #// # $h2 += $c;
        c = h2.shiftright(26)
        #// # $c = $h2 >> 26;
        h2 = h2.mask(67108863)
        #// # $h2 &= 0x3ffffff;
        h3 = h3.addint32(c)
        #// # $h3 += $c;
        c = h3.shiftright(26)
        #// # $c = $h3 >> 26;
        h3 = h3.mask(67108863)
        #// # $h3 &= 0x3ffffff;
        h4 = h4.addint32(c)
        #// # $h4 += $c;
        c = h4.shiftright(26)
        #// # $c = $h4 >> 26;
        h4 = h4.mask(67108863)
        #// # $h4 &= 0x3ffffff;
        h0 = h0.addint32(c.mulint(5, 3))
        #// # $h0 += self::mul($c, 5);
        c = h0.shiftright(26)
        #// # $c = $h0 >> 26;
        h0 = h0.mask(67108863)
        #// # $h0 &= 0x3ffffff;
        h1 = h1.addint32(c)
        #// # $h1 += $c;
        #// compute h + -p
        g0 = h0.addint(5)
        c = g0.shiftright(26)
        g0 = g0.mask(67108863)
        g1 = h1.addint32(c)
        c = g1.shiftright(26)
        g1 = g1.mask(67108863)
        g2 = h2.addint32(c)
        c = g2.shiftright(26)
        g2 = g2.mask(67108863)
        g3 = h3.addint32(c)
        c = g3.shiftright(26)
        g3 = g3.mask(67108863)
        g4 = h4.addint32(c).subint(1 << 26)
        #// # $mask = ($g4 >> 31) - 1;
        #// select h if h < p, or h + -p if h >= p
        mask = php_int(g4.toint() >> 31 + 1)
        g0 = g0.mask(mask)
        g1 = g1.mask(mask)
        g2 = g2.mask(mask)
        g3 = g3.mask(mask)
        g4 = g4.mask(mask)
        #// @var int $mask
        mask = (1 << (mask).bit_length()) - 1 - mask & 4294967295
        h0 = h0.mask(mask).orint32(g0)
        h1 = h1.mask(mask).orint32(g1)
        h2 = h2.mask(mask).orint32(g2)
        h3 = h3.mask(mask).orint32(g3)
        h4 = h4.mask(mask).orint32(g4)
        #// h = h % (2^128)
        h0 = h0.orint32(h1.shiftleft(26))
        h1 = h1.shiftright(6).orint32(h2.shiftleft(20))
        h2 = h2.shiftright(12).orint32(h3.shiftleft(14))
        h3 = h3.shiftright(18).orint32(h4.shiftleft(8))
        #// mac = (h + pad) % (2^128)
        f = h0.toint64().addint64(self.pad[0])
        h0 = f.toint32()
        f = h1.toint64().addint64(self.pad[1]).addint(h0.overflow)
        h1 = f.toint32()
        f = h2.toint64().addint64(self.pad[2]).addint(h1.overflow)
        h2 = f.toint32()
        f = h3.toint64().addint64(self.pad[3]).addint(h2.overflow)
        h3 = f.toint32()
        return h0.toreversestring() + h1.toreversestring() + h2.toreversestring() + h3.toreversestring()
    # end def finish
    i += 1
# end class ParagonIE_Sodium_Core32_Poly1305_State
