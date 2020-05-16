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
if php_class_exists("ParagonIE_Sodium_Core_Util", False):
    sys.exit(-1)
# end if
#// 
#// Class ParagonIE_Sodium_Core_Util
#//
class ParagonIE_Sodium_Core_Util():
    #// 
    #// @param int $integer
    #// @param int $size (16, 32, 64)
    #// @return int
    #//
    @classmethod
    def abs(self, integer=None, size=0):
        
        #// @var int $realSize
        realSize = PHP_INT_SIZE << 3 - 1
        if size:
            size -= 1
        else:
            #// @var int $size
            size = realSize
        # end if
        negative = -integer >> size & 1
        return php_int(integer ^ negative + negative >> realSize & 1)
    # end def abs
    #// 
    #// Convert a binary string into a hexadecimal string without cache-timing
    #// leaks
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $binaryString (raw binary)
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def bin2hex(self, binaryString=None):
        
        #// Type checks:
        if (not php_is_string(binaryString)):
            raise php_new_class("TypeError", lambda : TypeError("Argument 1 must be a string, " + gettype(binaryString) + " given."))
        # end if
        hex = ""
        len = self.strlen(binaryString)
        i = 0
        while i < len:
            
            #// @var array<int, int> $chunk
            chunk = unpack("C", binaryString[i])
            #// @var int $c
            c = chunk[1] & 15
            #// @var int $b
            b = chunk[1] >> 4
            hex += pack("CC", 87 + b + b - 10 >> 8 & (1 << (38).bit_length()) - 1 - 38, 87 + c + c - 10 >> 8 & (1 << (38).bit_length()) - 1 - 38)
            i += 1
        # end while
        return hex
    # end def bin2hex
    #// 
    #// Convert a binary string into a hexadecimal string without cache-timing
    #// leaks, returning uppercase letters (as per RFC 4648)
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $bin_string (raw binary)
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def bin2hexupper(self, bin_string=None):
        
        hex = ""
        len = self.strlen(bin_string)
        i = 0
        while i < len:
            
            #// @var array<int, int> $chunk
            chunk = unpack("C", bin_string[i])
            #// 
            #// Lower 16 bits
            #// 
            #// @var int $c
            #//
            c = chunk[1] & 15
            #// 
            #// Upper 16 bits
            #// @var int $b
            #//
            b = chunk[1] >> 4
            #// 
            #// Use pack() and binary operators to turn the two integers
            #// into hexadecimal characters. We don't use chr() here, because
            #// it uses a lookup table internally and we want to avoid
            #// cache-timing side-channels.
            #//
            hex += pack("CC", 55 + b + b - 10 >> 8 & (1 << (6).bit_length()) - 1 - 6, 55 + c + c - 10 >> 8 & (1 << (6).bit_length()) - 1 - 6)
            i += 1
        # end while
        return hex
    # end def bin2hexupper
    #// 
    #// Cache-timing-safe variant of ord()
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $chr
    #// @return int
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def chrtoint(self, chr=None):
        
        #// Type checks:
        if (not php_is_string(chr)):
            raise php_new_class("TypeError", lambda : TypeError("Argument 1 must be a string, " + gettype(chr) + " given."))
        # end if
        if self.strlen(chr) != 1:
            raise php_new_class("SodiumException", lambda : SodiumException("chrToInt() expects a string that is exactly 1 character long"))
        # end if
        #// @var array<int, int> $chunk
        chunk = unpack("C", chr)
        return php_int(chunk[1])
    # end def chrtoint
    #// 
    #// Compares two strings.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $left
    #// @param string $right
    #// @param int $len
    #// @return int
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def compare(self, left=None, right=None, len=None):
        
        leftLen = self.strlen(left)
        rightLen = self.strlen(right)
        if len == None:
            len = php_max(leftLen, rightLen)
            left = php_str_pad(left, len, " ", STR_PAD_RIGHT)
            right = php_str_pad(right, len, " ", STR_PAD_RIGHT)
        # end if
        gt = 0
        eq = 1
        i = len
        while True:
            
            if not (i != 0):
                break
            # end if
            i -= 1
            gt |= self.chrtoint(right[i]) - self.chrtoint(left[i]) >> 8 & eq
            eq &= self.chrtoint(right[i]) ^ self.chrtoint(left[i]) - 1 >> 8
        # end while
        return gt + gt + eq - 1
    # end def compare
    #// 
    #// If a variable does not match a given type, throw a TypeError.
    #// 
    #// @param mixed $mixedVar
    #// @param string $type
    #// @param int $argumentIndex
    #// @throws TypeError
    #// @throws SodiumException
    #// @return void
    #//
    @classmethod
    def declarescalartype(self, mixedVar=None, type="void", argumentIndex=0):
        
        if php_func_num_args() == 0:
            #// Tautology, by default
            return
        # end if
        if php_func_num_args() == 1:
            raise php_new_class("TypeError", lambda : TypeError("Declared void, but passed a variable"))
        # end if
        realType = php_strtolower(gettype(mixedVar))
        type = php_strtolower(type)
        for case in Switch(type):
            if case("null"):
                if mixedVar != None:
                    raise php_new_class("TypeError", lambda : TypeError("Argument " + argumentIndex + " must be null, " + realType + " given."))
                # end if
                break
            # end if
            if case("integer"):
                pass
            # end if
            if case("int"):
                allow = Array("int", "integer")
                if (not php_in_array(type, allow)):
                    raise php_new_class("TypeError", lambda : TypeError("Argument " + argumentIndex + " must be an integer, " + realType + " given."))
                # end if
                mixedVar = php_int(mixedVar)
                break
            # end if
            if case("boolean"):
                pass
            # end if
            if case("bool"):
                allow = Array("bool", "boolean")
                if (not php_in_array(type, allow)):
                    raise php_new_class("TypeError", lambda : TypeError("Argument " + argumentIndex + " must be a boolean, " + realType + " given."))
                # end if
                mixedVar = php_bool(mixedVar)
                break
            # end if
            if case("string"):
                if (not php_is_string(mixedVar)):
                    raise php_new_class("TypeError", lambda : TypeError("Argument " + argumentIndex + " must be a string, " + realType + " given."))
                # end if
                mixedVar = php_str(mixedVar)
                break
            # end if
            if case("decimal"):
                pass
            # end if
            if case("double"):
                pass
            # end if
            if case("float"):
                allow = Array("decimal", "double", "float")
                if (not php_in_array(type, allow)):
                    raise php_new_class("TypeError", lambda : TypeError("Argument " + argumentIndex + " must be a float, " + realType + " given."))
                # end if
                mixedVar = php_float(mixedVar)
                break
            # end if
            if case("object"):
                if (not php_is_object(mixedVar)):
                    raise php_new_class("TypeError", lambda : TypeError("Argument " + argumentIndex + " must be an object, " + realType + " given."))
                # end if
                break
            # end if
            if case("array"):
                if (not php_is_array(mixedVar)):
                    if php_is_object(mixedVar):
                        if type(mixedVar).__name__ == "ArrayAccess":
                            return
                        # end if
                    # end if
                    raise php_new_class("TypeError", lambda : TypeError("Argument " + argumentIndex + " must be an array, " + realType + " given."))
                # end if
                break
            # end if
            if case():
                raise php_new_class("SodiumException", lambda : SodiumException("Unknown type (" + realType + ") does not match expect type (" + type + ")"))
            # end if
        # end for
    # end def declarescalartype
    #// 
    #// Evaluate whether or not two strings are equal (in constant-time)
    #// 
    #// @param string $left
    #// @param string $right
    #// @return bool
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def hashequals(self, left=None, right=None):
        
        #// Type checks:
        if (not php_is_string(left)):
            raise php_new_class("TypeError", lambda : TypeError("Argument 1 must be a string, " + gettype(left) + " given."))
        # end if
        if (not php_is_string(right)):
            raise php_new_class("TypeError", lambda : TypeError("Argument 2 must be a string, " + gettype(right) + " given."))
        # end if
        if php_is_callable("hash_equals"):
            return hash_equals(left, right)
        # end if
        d = 0
        #// @var int $len
        len = self.strlen(left)
        if len != self.strlen(right):
            return False
        # end if
        i = 0
        while i < len:
            
            d |= self.chrtoint(left[i]) ^ self.chrtoint(right[i])
            i += 1
        # end while
        if d != 0:
            return False
        # end if
        return left == right
    # end def hashequals
    #// 
    #// Convert a hexadecimal string into a binary string without cache-timing
    #// leaks
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $hexString
    #// @param bool $strictPadding
    #// @return string (raw binary)
    #// @throws RangeException
    #// @throws TypeError
    #//
    @classmethod
    def hex2bin(self, hexString=None, strictPadding=False):
        
        #// Type checks:
        if (not php_is_string(hexString)):
            raise php_new_class("TypeError", lambda : TypeError("Argument 1 must be a string, " + gettype(hexString) + " given."))
        # end if
        #// @var int $hex_pos
        hex_pos = 0
        #// @var string $bin
        bin = ""
        #// @var int $c_acc
        c_acc = 0
        #// @var int $hex_len
        hex_len = self.strlen(hexString)
        #// @var int $state
        state = 0
        if hex_len & 1 != 0:
            if strictPadding:
                raise php_new_class("RangeException", lambda : RangeException("Expected an even number of hexadecimal characters"))
            else:
                hexString = "0" + hexString
                hex_len += 1
            # end if
        # end if
        chunk = unpack("C*", hexString)
        while True:
            
            if not (hex_pos < hex_len):
                break
            # end if
            hex_pos += 1
            #// @var int $c
            c = chunk[hex_pos]
            #// @var int $c_num
            c_num = c ^ 48
            #// @var int $c_num0
            c_num0 = c_num - 10 >> 8
            #// @var int $c_alpha
            c_alpha = c & (1 << (32).bit_length()) - 1 - 32 - 55
            #// @var int $c_alpha0
            c_alpha0 = c_alpha - 10 ^ c_alpha - 16 >> 8
            if c_num0 | c_alpha0 == 0:
                raise php_new_class("RangeException", lambda : RangeException("hex2bin() only expects hexadecimal characters"))
            # end if
            #// @var int $c_val
            c_val = c_num0 & c_num | c_alpha & c_alpha0
            if state == 0:
                c_acc = c_val * 16
            else:
                bin += pack("C", c_acc | c_val)
            # end if
            state ^= 1
        # end while
        return bin
    # end def hex2bin
    #// 
    #// Turn an array of integers into a string
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param array<int, int> $ints
    #// @return string
    #//
    @classmethod
    def intarraytostring(self, ints=None):
        
        #// @var array<int, int> $args
        args = ints
        for i,v in args:
            args[i] = php_int(v & 255)
        # end for
        array_unshift(args, php_str_repeat("C", php_count(ints)))
        return php_str(call_user_func_array("pack", args))
    # end def intarraytostring
    #// 
    #// Cache-timing-safe variant of ord()
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $int
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def inttochr(self, int=None):
        
        return pack("C", int)
    # end def inttochr
    #// 
    #// Load a 3 character substring into an integer
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $string
    #// @return int
    #// @throws RangeException
    #// @throws TypeError
    #//
    @classmethod
    def load_3(self, string=None):
        
        #// Type checks:
        if (not php_is_string(string)):
            raise php_new_class("TypeError", lambda : TypeError("Argument 1 must be a string, " + gettype(string) + " given."))
        # end if
        #// Input validation:
        if self.strlen(string) < 3:
            raise php_new_class("RangeException", lambda : RangeException("String must be 3 bytes or more; " + self.strlen(string) + " given."))
        # end if
        #// @var array<int, int> $unpacked
        unpacked = unpack("V", string + " ")
        return php_int(unpacked[1] & 16777215)
    # end def load_3
    #// 
    #// Load a 4 character substring into an integer
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $string
    #// @return int
    #// @throws RangeException
    #// @throws TypeError
    #//
    @classmethod
    def load_4(self, string=None):
        
        #// Type checks:
        if (not php_is_string(string)):
            raise php_new_class("TypeError", lambda : TypeError("Argument 1 must be a string, " + gettype(string) + " given."))
        # end if
        #// Input validation:
        if self.strlen(string) < 4:
            raise php_new_class("RangeException", lambda : RangeException("String must be 4 bytes or more; " + self.strlen(string) + " given."))
        # end if
        #// @var array<int, int> $unpacked
        unpacked = unpack("V", string)
        return php_int(unpacked[1] & 4294967295)
    # end def load_4
    #// 
    #// Load a 8 character substring into an integer
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $string
    #// @return int
    #// @throws RangeException
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def load64_le(self, string=None):
        
        #// Type checks:
        if (not php_is_string(string)):
            raise php_new_class("TypeError", lambda : TypeError("Argument 1 must be a string, " + gettype(string) + " given."))
        # end if
        #// Input validation:
        if self.strlen(string) < 4:
            raise php_new_class("RangeException", lambda : RangeException("String must be 4 bytes or more; " + self.strlen(string) + " given."))
        # end if
        if PHP_VERSION_ID >= 50603 and PHP_INT_SIZE == 8:
            #// @var array<int, int> $unpacked
            unpacked = unpack("P", string)
            return php_int(unpacked[1])
        # end if
        #// @var int $result
        result = self.chrtoint(string[0]) & 255
        result |= self.chrtoint(string[1]) & 255 << 8
        result |= self.chrtoint(string[2]) & 255 << 16
        result |= self.chrtoint(string[3]) & 255 << 24
        result |= self.chrtoint(string[4]) & 255 << 32
        result |= self.chrtoint(string[5]) & 255 << 40
        result |= self.chrtoint(string[6]) & 255 << 48
        result |= self.chrtoint(string[7]) & 255 << 56
        return php_int(result)
    # end def load64_le
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $left
    #// @param string $right
    #// @return int
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def memcmp(self, left=None, right=None):
        
        if self.hashequals(left, right):
            return 0
        # end if
        return -1
    # end def memcmp
    #// 
    #// Multiply two integers in constant-time
    #// 
    #// Micro-architecture timing side-channels caused by how your CPU
    #// implements multiplication are best prevented by never using the
    #// multiplication operators and ensuring that our code always takes
    #// the same number of operations to complete, regardless of the values
    #// of $a and $b.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $a
    #// @param int $b
    #// @param int $size Limits the number of operations (useful for small,
    #// constant operands)
    #// @return int
    #//
    @classmethod
    def mul(self, a=None, b=None, size=0):
        
        if ParagonIE_Sodium_Compat.fastMult:
            return php_int(a * b)
        # end if
        mul.defaultSize = None
        #// @var int $defaultSize
        if (not mul.defaultSize):
            #// @var int $defaultSize
            mul.defaultSize = PHP_INT_SIZE << 3 - 1
        # end if
        if size < 1:
            #// @var int $size
            size = mul.defaultSize
        # end if
        #// @var int $size
        c = 0
        #// 
        #// Mask is either -1 or 0.
        #// 
        #// -1 in binary looks like 0x1111 ... 1111
        #// 0 in binary looks like 0x0000 ... 0000
        #// 
        #// @var int
        #//
        mask = -b >> php_int(mul.defaultSize) & 1
        #// 
        #// Ensure $b is a positive integer, without creating
        #// a branching side-channel
        #// 
        #// @var int $b
        #//
        b = b & (1 << (mask).bit_length()) - 1 - mask | mask & -b
        #// 
        #// Unless $size is provided:
        #// 
        #// This loop always runs 32 times when PHP_INT_SIZE is 4.
        #// This loop always runs 64 times when PHP_INT_SIZE is 8.
        #//
        i = size
        while i >= 0:
            
            c += php_int(a & -b & 1)
            a <<= 1
            b >>= 1
            i -= 1
        # end while
        #// 
        #// If $b was negative, we then apply the same value to $c here.
        #// It doesn't matter much if $a was negative; the $c += above would
        #// have produced a negative integer to begin with. But a negative $b
        #// makes $b >>= 1 never return 0, so we would end up with incorrect
        #// results.
        #// 
        #// The end result is what we'd expect from integer multiplication.
        #//
        return php_int(c & (1 << (mask).bit_length()) - 1 - mask | mask & -c)
    # end def mul
    #// 
    #// Convert any arbitrary numbers into two 32-bit integers that represent
    #// a 64-bit integer.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int|float $num
    #// @return array<int, int>
    #//
    @classmethod
    def numericto64bitinteger(self, num=None):
        
        high = 0
        #// @var int $low
        low = num & 4294967295
        if +abs(num) >= 1:
            if num > 0:
                #// @var int $high
                high = php_min(+floor(num / 4294967296), 4294967295)
            else:
                #// @var int $high
                high = (1 << ((1 << (+ceil(num - +(1 << ((1 << (num).bit_length()) - 1 - num).bit_length()) - 1 - (1 << (num).bit_length()) - 1 - num / 4294967296)).bit_length()) - 1 - +ceil(num - +(1 << ((1 << (num).bit_length()) - 1 - num).bit_length()) - 1 - (1 << (num).bit_length()) - 1 - num / 4294967296)).bit_length()) - 1 - (1 << (+ceil(num - +(1 << ((1 << (num).bit_length()) - 1 - num).bit_length()) - 1 - (1 << (num).bit_length()) - 1 - num / 4294967296)).bit_length()) - 1 - +ceil(num - +(1 << ((1 << (num).bit_length()) - 1 - num).bit_length()) - 1 - (1 << (num).bit_length()) - 1 - num / 4294967296)
            # end if
        # end if
        return Array(php_int(high), php_int(low))
    # end def numericto64bitinteger
    #// 
    #// Store a 24-bit integer into a string, treating it as big-endian.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $int
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def store_3(self, int=None):
        
        #// Type checks:
        if (not php_is_int(int)):
            if php_is_numeric(int):
                int = php_int(int)
            else:
                raise php_new_class("TypeError", lambda : TypeError("Argument 1 must be an integer, " + gettype(int) + " given."))
            # end if
        # end if
        #// @var string $packed
        packed = pack("N", int)
        return self.substr(packed, 1, 3)
    # end def store_3
    #// 
    #// Store a 32-bit integer into a string, treating it as little-endian.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $int
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def store32_le(self, int=None):
        
        #// Type checks:
        if (not php_is_int(int)):
            if php_is_numeric(int):
                int = php_int(int)
            else:
                raise php_new_class("TypeError", lambda : TypeError("Argument 1 must be an integer, " + gettype(int) + " given."))
            # end if
        # end if
        #// @var string $packed
        packed = pack("V", int)
        return packed
    # end def store32_le
    #// 
    #// Store a 32-bit integer into a string, treating it as big-endian.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $int
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def store_4(self, int=None):
        
        #// Type checks:
        if (not php_is_int(int)):
            if php_is_numeric(int):
                int = php_int(int)
            else:
                raise php_new_class("TypeError", lambda : TypeError("Argument 1 must be an integer, " + gettype(int) + " given."))
            # end if
        # end if
        #// @var string $packed
        packed = pack("N", int)
        return packed
    # end def store_4
    #// 
    #// Stores a 64-bit integer as an string, treating it as little-endian.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param int $int
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def store64_le(self, int=None):
        
        #// Type checks:
        if (not php_is_int(int)):
            if php_is_numeric(int):
                int = php_int(int)
            else:
                raise php_new_class("TypeError", lambda : TypeError("Argument 1 must be an integer, " + gettype(int) + " given."))
            # end if
        # end if
        if PHP_INT_SIZE == 8:
            if PHP_VERSION_ID >= 50603:
                #// @var string $packed
                packed = pack("P", int)
                return packed
            # end if
            return self.inttochr(int & 255) + self.inttochr(int >> 8 & 255) + self.inttochr(int >> 16 & 255) + self.inttochr(int >> 24 & 255) + self.inttochr(int >> 32 & 255) + self.inttochr(int >> 40 & 255) + self.inttochr(int >> 48 & 255) + self.inttochr(int >> 56 & 255)
        # end if
        if int > PHP_INT_MAX:
            hiB, int = self.numericto64bitinteger(int)
        else:
            hiB = 0
        # end if
        return self.inttochr(int & 255) + self.inttochr(int >> 8 & 255) + self.inttochr(int >> 16 & 255) + self.inttochr(int >> 24 & 255) + self.inttochr(hiB & 255) + self.inttochr(hiB >> 8 & 255) + self.inttochr(hiB >> 16 & 255) + self.inttochr(hiB >> 24 & 255)
    # end def store64_le
    #// 
    #// Safe string length
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @ref mbstring.func_overload
    #// 
    #// @param string $str
    #// @return int
    #// @throws TypeError
    #//
    @classmethod
    def strlen(self, str=None):
        
        #// Type checks:
        if (not php_is_string(str)):
            raise php_new_class("TypeError", lambda : TypeError("String expected"))
        # end if
        return php_int(php_mb_strlen(str, "8bit") if self.ismbstringoverride() else php_strlen(str))
    # end def strlen
    #// 
    #// Turn a string into an array of integers
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $string
    #// @return array<int, int>
    #// @throws TypeError
    #//
    @classmethod
    def stringtointarray(self, string=None):
        
        if (not php_is_string(string)):
            raise php_new_class("TypeError", lambda : TypeError("String expected"))
        # end if
        #// 
        #// @var array<int, int>
        #//
        values = php_array_values(unpack("C*", string))
        return values
    # end def stringtointarray
    #// 
    #// Safe substring
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @ref mbstring.func_overload
    #// 
    #// @param string $str
    #// @param int $start
    #// @param int $length
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def substr(self, str=None, start=0, length=None):
        
        #// Type checks:
        if (not php_is_string(str)):
            raise php_new_class("TypeError", lambda : TypeError("String expected"))
        # end if
        if length == 0:
            return ""
        # end if
        if self.ismbstringoverride():
            if PHP_VERSION_ID < 50400 and length == None:
                length = self.strlen(str)
            # end if
            sub = php_str(php_mb_substr(str, start, length, "8bit"))
        elif length == None:
            sub = php_str(php_substr(str, start))
        else:
            sub = php_str(php_substr(str, start, length))
        # end if
        if sub != "":
            return sub
        # end if
        return ""
    # end def substr
    #// 
    #// Compare a 16-character byte string in constant time.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $a
    #// @param string $b
    #// @return bool
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def verify_16(self, a=None, b=None):
        
        #// Type checks:
        if (not php_is_string(a)):
            raise php_new_class("TypeError", lambda : TypeError("String expected"))
        # end if
        if (not php_is_string(b)):
            raise php_new_class("TypeError", lambda : TypeError("String expected"))
        # end if
        return self.hashequals(self.substr(a, 0, 16), self.substr(b, 0, 16))
    # end def verify_16
    #// 
    #// Compare a 32-character byte string in constant time.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $a
    #// @param string $b
    #// @return bool
    #// @throws SodiumException
    #// @throws TypeError
    #//
    @classmethod
    def verify_32(self, a=None, b=None):
        
        #// Type checks:
        if (not php_is_string(a)):
            raise php_new_class("TypeError", lambda : TypeError("String expected"))
        # end if
        if (not php_is_string(b)):
            raise php_new_class("TypeError", lambda : TypeError("String expected"))
        # end if
        return self.hashequals(self.substr(a, 0, 32), self.substr(b, 0, 32))
    # end def verify_32
    #// 
    #// Calculate $a ^ $b for two strings.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @param string $a
    #// @param string $b
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def xorstrings(self, a=None, b=None):
        
        #// Type checks:
        if (not php_is_string(a)):
            raise php_new_class("TypeError", lambda : TypeError("Argument 1 must be a string"))
        # end if
        if (not php_is_string(b)):
            raise php_new_class("TypeError", lambda : TypeError("Argument 2 must be a string"))
        # end if
        return php_str(a ^ b)
    # end def xorstrings
    #// 
    #// Returns whether or not mbstring.func_overload is in effect.
    #// 
    #// @internal You should not use this directly from another application
    #// 
    #// @return bool
    #//
    def ismbstringoverride(self):
        
        ismbstringoverride.mbstring = None
        if ismbstringoverride.mbstring == None:
            ismbstringoverride.mbstring = php_extension_loaded("mbstring") and php_int(php_ini_get("mbstring.func_overload")) & MB_OVERLOAD_STRING
        # end if
        #// @var bool $mbstring
        return ismbstringoverride.mbstring
    # end def ismbstringoverride
# end class ParagonIE_Sodium_Core_Util
