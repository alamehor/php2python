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
#// 
#// Class ParagonIE_Sodium_Core32_SecretStream_State
#//
class ParagonIE_Sodium_Core32_SecretStream_State():
    key = Array()
    counter = Array()
    nonce = Array()
    _pad = Array()
    #// 
    #// ParagonIE_Sodium_Core32_SecretStream_State constructor.
    #// @param string $key
    #// @param string|null $nonce
    #//
    def __init__(self, key=None, nonce=None):
        
        self.key = key
        self.counter = 1
        if is_null(nonce):
            nonce = php_str_repeat(" ", 12)
        # end if
        self.nonce = php_str_pad(nonce, 12, " ", STR_PAD_RIGHT)
        self._pad = php_str_repeat(" ", 4)
    # end def __init__
    #// 
    #// @return self
    #//
    def counterreset(self):
        
        self.counter = 1
        self._pad = php_str_repeat(" ", 4)
        return self
    # end def counterreset
    #// 
    #// @return string
    #//
    def getkey(self):
        
        return self.key
    # end def getkey
    #// 
    #// @return string
    #//
    def getcounter(self):
        
        return ParagonIE_Sodium_Core32_Util.store32_le(self.counter)
    # end def getcounter
    #// 
    #// @return string
    #//
    def getnonce(self):
        
        if (not php_is_string(self.nonce)):
            self.nonce = php_str_repeat(" ", 12)
        # end if
        if ParagonIE_Sodium_Core32_Util.strlen(self.nonce) != 12:
            self.nonce = php_str_pad(self.nonce, 12, " ", STR_PAD_RIGHT)
        # end if
        return self.nonce
    # end def getnonce
    #// 
    #// @return string
    #//
    def getcombinednonce(self):
        
        return self.getcounter() + ParagonIE_Sodium_Core32_Util.substr(self.getnonce(), 0, 8)
    # end def getcombinednonce
    #// 
    #// @return self
    #//
    def incrementcounter(self):
        
        self.counter += 1
        return self
    # end def incrementcounter
    #// 
    #// @return bool
    #//
    def needsrekey(self):
        
        return self.counter & 65535 == 0
    # end def needsrekey
    #// 
    #// @param string $newKeyAndNonce
    #// @return self
    #//
    def rekey(self, newKeyAndNonce=None):
        
        self.key = ParagonIE_Sodium_Core32_Util.substr(newKeyAndNonce, 0, 32)
        self.nonce = php_str_pad(ParagonIE_Sodium_Core32_Util.substr(newKeyAndNonce, 32), 12, " ", STR_PAD_RIGHT)
        return self
    # end def rekey
    #// 
    #// @param string $str
    #// @return self
    #//
    def xornonce(self, str=None):
        
        self.nonce = ParagonIE_Sodium_Core32_Util.xorstrings(self.getnonce(), php_str_pad(ParagonIE_Sodium_Core32_Util.substr(str, 0, 8), 12, " ", STR_PAD_RIGHT))
        return self
    # end def xornonce
    #// 
    #// @param string $string
    #// @return self
    #//
    @classmethod
    def fromstring(self, string=None):
        
        state = php_new_class("ParagonIE_Sodium_Core32_SecretStream_State", lambda : ParagonIE_Sodium_Core32_SecretStream_State(ParagonIE_Sodium_Core32_Util.substr(string, 0, 32)))
        state.counter = ParagonIE_Sodium_Core32_Util.load_4(ParagonIE_Sodium_Core32_Util.substr(string, 32, 4))
        state.nonce = ParagonIE_Sodium_Core32_Util.substr(string, 36, 12)
        state._pad = ParagonIE_Sodium_Core32_Util.substr(string, 48, 8)
        return state
    # end def fromstring
    #// 
    #// @return string
    #//
    def tostring(self):
        
        return self.key + self.getcounter() + self.nonce + self._pad
    # end def tostring
# end class ParagonIE_Sodium_Core32_SecretStream_State
