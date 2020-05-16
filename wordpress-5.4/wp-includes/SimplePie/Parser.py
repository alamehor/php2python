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
#// SimplePie
#// 
#// A PHP-Based RSS and Atom Feed Framework.
#// Takes the hard work out of managing a complete RSS/Atom solution.
#// 
#// Copyright (c) 2004-2012, Ryan Parman, Geoffrey Sneddon, Ryan McCue, and contributors
#// All rights reserved.
#// 
#// Redistribution and use in source and binary forms, with or without modification, are
#// permitted provided that the following conditions are met:
#// 
#// Redistributions of source code must retain the above copyright notice, this list of
#// conditions and the following disclaimer.
#// 
#// Redistributions in binary form must reproduce the above copyright notice, this list
#// of conditions and the following disclaimer in the documentation and/or other materials
#// provided with the distribution.
#// 
#// Neither the name of the SimplePie Team nor the names of its contributors may be used
#// to endorse or promote products derived from this software without specific prior
#// written permission.
#// 
#// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
#// OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
#// AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS
#// AND CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#// OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#// POSSIBILITY OF SUCH DAMAGE.
#// 
#// @package SimplePie
#// @version 1.3.1
#// @copyright 2004-2012 Ryan Parman, Geoffrey Sneddon, Ryan McCue
#// @author Ryan Parman
#// @author Geoffrey Sneddon
#// @author Ryan McCue
#// @link http://simplepie.org/ SimplePie
#// @license http://www.opensource.org/licenses/bsd-license.php BSD License
#// 
#// 
#// Parses XML into something sane
#// 
#// 
#// This class can be overloaded with {@see SimplePie::set_parser_class()}
#// 
#// @package SimplePie
#// @subpackage Parsing
#//
class SimplePie_Parser():
    error_code = Array()
    error_string = Array()
    current_line = Array()
    current_column = Array()
    current_byte = Array()
    separator = " "
    namespace = Array("")
    element = Array("")
    xml_base = Array("")
    xml_base_explicit = Array(False)
    xml_lang = Array("")
    data = Array()
    datas = Array(Array())
    current_xhtml_construct = -1
    encoding = Array()
    registry = Array()
    def set_registry(self, registry=None):
        
        self.registry = registry
    # end def set_registry
    def parse(self, data=None, encoding=None):
        
        #// Use UTF-8 if we get passed US-ASCII, as every US-ASCII character is a UTF-8 character
        if php_strtoupper(encoding) == "US-ASCII":
            self.encoding = "UTF-8"
        else:
            self.encoding = encoding
        # end if
        #// Strip BOM:
        #// UTF-32 Big Endian BOM
        if php_substr(data, 0, 4) == "  þÿ":
            data = php_substr(data, 4)
            #// UTF-32 Little Endian BOM
        elif php_substr(data, 0, 4) == "ÿþ  ":
            data = php_substr(data, 4)
            #// UTF-16 Big Endian BOM
        elif php_substr(data, 0, 2) == "þÿ":
            data = php_substr(data, 2)
            #// UTF-16 Little Endian BOM
        elif php_substr(data, 0, 2) == "ÿþ":
            data = php_substr(data, 2)
            #// UTF-8 BOM
        elif php_substr(data, 0, 3) == "ï»¿":
            data = php_substr(data, 3)
        # end if
        pos = php_strpos(data, "?>")
        if php_substr(data, 0, 5) == "<?xml" and strspn(php_substr(data, 5, 1), "   \n\r ") and pos != False:
            declaration = self.registry.create("XML_Declaration_Parser", Array(php_substr(data, 5, pos - 5)))
            if declaration.parse():
                data = php_substr(data, pos + 2)
                data = "<?xml version=\"" + declaration.version + "\" encoding=\"" + encoding + "\" standalone=\"" + "yes" if declaration.standalone else "no" + "\"?>" + data
            else:
                self.error_string = "SimplePie bug! Please report this!"
                return False
            # end if
        # end if
        return_ = True
        parse.xml_is_sane = None
        if parse.xml_is_sane == None:
            parser_check = xml_parser_create()
            xml_parse_into_struct(parser_check, "<foo>&amp;</foo>", values)
            xml_parser_free(parser_check)
            parse.xml_is_sane = (php_isset(lambda : values[0]["value"]))
        # end if
        #// Create the parser
        if parse.xml_is_sane:
            xml = xml_parser_create_ns(self.encoding, self.separator)
            xml_parser_set_option(xml, XML_OPTION_SKIP_WHITE, 1)
            xml_parser_set_option(xml, XML_OPTION_CASE_FOLDING, 0)
            xml_set_object(xml, self)
            xml_set_character_data_handler(xml, "cdata")
            xml_set_element_handler(xml, "tag_open", "tag_close")
            #// Parse!
            if (not xml_parse(xml, data, True)):
                self.error_code = xml_get_error_code(xml)
                self.error_string = xml_error_string(self.error_code)
                return_ = False
            # end if
            self.current_line = xml_get_current_line_number(xml)
            self.current_column = xml_get_current_column_number(xml)
            self.current_byte = xml_get_current_byte_index(xml)
            xml_parser_free(xml)
            return return_
        else:
            libxml_clear_errors()
            xml = php_new_class("XMLReader", lambda : XMLReader())
            xml.xml(data)
            while True:
                
                if not (php_no_error(lambda: xml.read())):
                    break
                # end if
                for case in Switch(xml.nodeType):
                    if case(constant("XMLReader::END_ELEMENT")):
                        if xml.namespaceURI != "":
                            tagName = xml.namespaceURI + self.separator + xml.localName
                        else:
                            tagName = xml.localName
                        # end if
                        self.tag_close(None, tagName)
                        break
                    # end if
                    if case(constant("XMLReader::ELEMENT")):
                        empty = xml.isEmptyElement
                        if xml.namespaceURI != "":
                            tagName = xml.namespaceURI + self.separator + xml.localName
                        else:
                            tagName = xml.localName
                        # end if
                        attributes = Array()
                        while True:
                            
                            if not (xml.movetonextattribute()):
                                break
                            # end if
                            if xml.namespaceURI != "":
                                attrName = xml.namespaceURI + self.separator + xml.localName
                            else:
                                attrName = xml.localName
                            # end if
                            attributes[attrName] = xml.value
                        # end while
                        self.tag_open(None, tagName, attributes)
                        if empty:
                            self.tag_close(None, tagName)
                        # end if
                        break
                    # end if
                    if case(constant("XMLReader::TEXT")):
                        pass
                    # end if
                    if case(constant("XMLReader::CDATA")):
                        self.cdata(None, xml.value)
                        break
                    # end if
                # end for
            # end while
            error = libxml_get_last_error()
            if error:
                self.error_code = error.code
                self.error_string = error.message
                self.current_line = error.line
                self.current_column = error.column
                return False
            else:
                return True
            # end if
        # end if
    # end def parse
    def get_error_code(self):
        
        return self.error_code
    # end def get_error_code
    def get_error_string(self):
        
        return self.error_string
    # end def get_error_string
    def get_current_line(self):
        
        return self.current_line
    # end def get_current_line
    def get_current_column(self):
        
        return self.current_column
    # end def get_current_column
    def get_current_byte(self):
        
        return self.current_byte
    # end def get_current_byte
    def get_data(self):
        
        return self.data
    # end def get_data
    def tag_open(self, parser=None, tag=None, attributes=None):
        
        self.namespace[-1], self.element[-1] = self.split_ns(tag)
        attribs = Array()
        for name,value in attributes:
            attrib_namespace, attribute = self.split_ns(name)
            attribs[attrib_namespace][attribute] = value
        # end for
        if (php_isset(lambda : attribs[SIMPLEPIE_NAMESPACE_XML]["base"])):
            base = self.registry.call("Misc", "absolutize_url", Array(attribs[SIMPLEPIE_NAMESPACE_XML]["base"], php_end(self.xml_base)))
            if base != False:
                self.xml_base[-1] = base
                self.xml_base_explicit[-1] = True
            # end if
        else:
            self.xml_base[-1] = php_end(self.xml_base)
            self.xml_base_explicit[-1] = php_end(self.xml_base_explicit)
        # end if
        if (php_isset(lambda : attribs[SIMPLEPIE_NAMESPACE_XML]["lang"])):
            self.xml_lang[-1] = attribs[SIMPLEPIE_NAMESPACE_XML]["lang"]
        else:
            self.xml_lang[-1] = php_end(self.xml_lang)
        # end if
        if self.current_xhtml_construct >= 0:
            self.current_xhtml_construct += 1
            if php_end(self.namespace) == SIMPLEPIE_NAMESPACE_XHTML:
                self.data["data"] += "<" + php_end(self.element)
                if (php_isset(lambda : attribs[""])):
                    for name,value in attribs[""]:
                        self.data["data"] += " " + name + "=\"" + htmlspecialchars(value, ENT_COMPAT, self.encoding) + "\""
                    # end for
                # end if
                self.data["data"] += ">"
            # end if
        else:
            self.datas[-1] = self.data
            self.data = self.data["child"][php_end(self.namespace)][php_end(self.element)][-1]
            self.data = Array({"data": "", "attribs": attribs, "xml_base": php_end(self.xml_base), "xml_base_explicit": php_end(self.xml_base_explicit), "xml_lang": php_end(self.xml_lang)})
            if php_end(self.namespace) == SIMPLEPIE_NAMESPACE_ATOM_03 and php_in_array(php_end(self.element), Array("title", "tagline", "copyright", "info", "summary", "content")) and (php_isset(lambda : attribs[""]["mode"])) and attribs[""]["mode"] == "xml" or php_end(self.namespace) == SIMPLEPIE_NAMESPACE_ATOM_10 and php_in_array(php_end(self.element), Array("rights", "subtitle", "summary", "info", "title", "content")) and (php_isset(lambda : attribs[""]["type"])) and attribs[""]["type"] == "xhtml" or php_end(self.namespace) == SIMPLEPIE_NAMESPACE_RSS_20 and php_in_array(php_end(self.element), Array("title")) or php_end(self.namespace) == SIMPLEPIE_NAMESPACE_RSS_090 and php_in_array(php_end(self.element), Array("title")) or php_end(self.namespace) == SIMPLEPIE_NAMESPACE_RSS_10 and php_in_array(php_end(self.element), Array("title")):
                self.current_xhtml_construct = 0
            # end if
        # end if
    # end def tag_open
    def cdata(self, parser=None, cdata=None):
        
        if self.current_xhtml_construct >= 0:
            self.data["data"] += htmlspecialchars(cdata, ENT_QUOTES, self.encoding)
        else:
            self.data["data"] += cdata
        # end if
    # end def cdata
    def tag_close(self, parser=None, tag=None):
        
        if self.current_xhtml_construct >= 0:
            self.current_xhtml_construct -= 1
            if php_end(self.namespace) == SIMPLEPIE_NAMESPACE_XHTML and (not php_in_array(php_end(self.element), Array("area", "base", "basefont", "br", "col", "frame", "hr", "img", "input", "isindex", "link", "meta", "param"))):
                self.data["data"] += "</" + php_end(self.element) + ">"
            # end if
        # end if
        if self.current_xhtml_construct == -1:
            self.data = self.datas[php_count(self.datas) - 1]
            php_array_pop(self.datas)
        # end if
        php_array_pop(self.element)
        php_array_pop(self.namespace)
        php_array_pop(self.xml_base)
        php_array_pop(self.xml_base_explicit)
        php_array_pop(self.xml_lang)
    # end def tag_close
    def split_ns(self, string=None):
        
        split_ns.cache = Array()
        if (not (php_isset(lambda : split_ns.cache[string]))):
            pos = php_strpos(string, self.separator)
            if pos:
                split_ns.separator_length = None
                if (not split_ns.separator_length):
                    split_ns.separator_length = php_strlen(self.separator)
                # end if
                namespace = php_substr(string, 0, pos)
                local_name = php_substr(string, pos + split_ns.separator_length)
                if php_strtolower(namespace) == SIMPLEPIE_NAMESPACE_ITUNES:
                    namespace = SIMPLEPIE_NAMESPACE_ITUNES
                # end if
                #// Normalize the Media RSS namespaces
                if namespace == SIMPLEPIE_NAMESPACE_MEDIARSS_WRONG or namespace == SIMPLEPIE_NAMESPACE_MEDIARSS_WRONG2 or namespace == SIMPLEPIE_NAMESPACE_MEDIARSS_WRONG3 or namespace == SIMPLEPIE_NAMESPACE_MEDIARSS_WRONG4 or namespace == SIMPLEPIE_NAMESPACE_MEDIARSS_WRONG5:
                    namespace = SIMPLEPIE_NAMESPACE_MEDIARSS
                # end if
                split_ns.cache[string] = Array(namespace, local_name)
            else:
                split_ns.cache[string] = Array("", string)
            # end if
        # end if
        return split_ns.cache[string]
    # end def split_ns
# end class SimplePie_Parser
