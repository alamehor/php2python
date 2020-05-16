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
#// getID3() by James Heinrich <info@getid3.org>
#// available at https://github.com/JamesHeinrich/getID3
#// or https://www.getid3.org
#// or http://getid3.sourceforge.net
#// see readme.txt for more details
#// 
#// 
#// module.tag.id3v1.php
#// module for analyzing ID3v1 tags
#// dependencies: NONE
#// 
#//
class getid3_id3v1(getid3_handler):
    #// 
    #// @return bool
    #//
    def analyze(self):
        
        info = self.getid3.info
        if (not getid3_lib.intvaluesupported(info["filesize"])):
            self.warning("Unable to check for ID3v1 because file is larger than " + round(PHP_INT_MAX / 1073741824) + "GB")
            return False
        # end if
        self.fseek(-256, SEEK_END)
        preid3v1 = self.fread(128)
        id3v1tag = self.fread(128)
        if php_substr(id3v1tag, 0, 3) == "TAG":
            info["avdataend"] = info["filesize"] - 128
            ParsedID3v1["title"] = self.cutfield(php_substr(id3v1tag, 3, 30))
            ParsedID3v1["artist"] = self.cutfield(php_substr(id3v1tag, 33, 30))
            ParsedID3v1["album"] = self.cutfield(php_substr(id3v1tag, 63, 30))
            ParsedID3v1["year"] = self.cutfield(php_substr(id3v1tag, 93, 4))
            ParsedID3v1["comment"] = php_substr(id3v1tag, 97, 30)
            #// can't remove nulls yet, track detection depends on them
            ParsedID3v1["genreid"] = php_ord(php_substr(id3v1tag, 127, 1))
            #// If second-last byte of comment field is null and last byte of comment field is non-null
            #// then this is ID3v1.1 and the comment field is 28 bytes long and the 30th byte is the track number
            if id3v1tag[125] == " " and id3v1tag[126] != " ":
                ParsedID3v1["track_number"] = php_ord(php_substr(ParsedID3v1["comment"], 29, 1))
                ParsedID3v1["comment"] = php_substr(ParsedID3v1["comment"], 0, 28)
            # end if
            ParsedID3v1["comment"] = self.cutfield(ParsedID3v1["comment"])
            ParsedID3v1["genre"] = self.lookupgenrename(ParsedID3v1["genreid"])
            if (not php_empty(lambda : ParsedID3v1["genre"])):
                ParsedID3v1["genreid"] = None
            # end if
            if (php_isset(lambda : ParsedID3v1["genre"])) and php_empty(lambda : ParsedID3v1["genre"]) or ParsedID3v1["genre"] == "Unknown":
                ParsedID3v1["genre"] = None
            # end if
            for key,value in ParsedID3v1:
                ParsedID3v1["comments"][key][0] = value
            # end for
            #// ID3v1 encoding detection hack START
            #// ID3v1 is defined as always using ISO-8859-1 encoding, but it is not uncommon to find files tagged with ID3v1 using Windows-1251 or other character sets
            #// Since ID3v1 has no concept of character sets there is no certain way to know we have the correct non-ISO-8859-1 character set, but we can guess
            ID3v1encoding = "ISO-8859-1"
            for tag_key,valuearray in ParsedID3v1["comments"]:
                for key,value in valuearray:
                    if php_preg_match("#^[\\x00-\\x40\\xA8\\xB8\\x80-\\xFF]+$#", value):
                        for id3v1_bad_encoding in Array("Windows-1251", "KOI8-R"):
                            if php_function_exists("mb_convert_encoding") and php_no_error(lambda: mb_convert_encoding(value, id3v1_bad_encoding, id3v1_bad_encoding)) == value:
                                ID3v1encoding = id3v1_bad_encoding
                                break
                            elif php_function_exists("iconv") and php_no_error(lambda: iconv(id3v1_bad_encoding, id3v1_bad_encoding, value)) == value:
                                ID3v1encoding = id3v1_bad_encoding
                                break
                            # end if
                        # end for
                    # end if
                # end for
            # end for
            #// ID3v1 encoding detection hack END
            #// ID3v1 data is supposed to be padded with NULL characters, but some taggers pad with spaces
            GoodFormatID3v1tag = self.generateid3v1tag(ParsedID3v1["title"], ParsedID3v1["artist"], ParsedID3v1["album"], ParsedID3v1["year"], self.lookupgenreid(ParsedID3v1["genre"]) if (php_isset(lambda : ParsedID3v1["genre"])) else False, ParsedID3v1["comment"], ParsedID3v1["track_number"] if (not php_empty(lambda : ParsedID3v1["track_number"])) else "")
            ParsedID3v1["padding_valid"] = True
            if id3v1tag != GoodFormatID3v1tag:
                ParsedID3v1["padding_valid"] = False
                self.warning("Some ID3v1 fields do not use NULL characters for padding")
            # end if
            ParsedID3v1["tag_offset_end"] = info["filesize"]
            ParsedID3v1["tag_offset_start"] = ParsedID3v1["tag_offset_end"] - 128
            info["id3v1"] = ParsedID3v1
            info["id3v1"]["encoding"] = ID3v1encoding
        # end if
        if php_substr(preid3v1, 0, 3) == "TAG":
            #// The way iTunes handles tags is, well, brain-damaged.
            #// It completely ignores v1 if ID3v2 is present.
            #// This goes as far as adding a new v1 tag *even if there already is one
            #// A suspected double-ID3v1 tag has been detected, but it could be that
            #// the "TAG" identifier is a legitimate part of an APE or Lyrics3 tag
            if php_substr(preid3v1, 96, 8) == "APETAGEX":
                pass
            elif php_substr(preid3v1, 119, 6) == "LYRICS":
                pass
            else:
                #// APE and Lyrics3 footers not found - assume double ID3v1
                self.warning("Duplicate ID3v1 tag detected - this has been known to happen with iTunes")
                info["avdataend"] -= 128
            # end if
        # end if
        return True
    # end def analyze
    #// 
    #// @param string $str
    #// 
    #// @return string
    #//
    @classmethod
    def cutfield(self, str=None):
        
        return php_trim(php_substr(str, 0, strcspn(str, " ")))
    # end def cutfield
    #// 
    #// @param bool $allowSCMPXextended
    #// 
    #// @return string[]
    #//
    @classmethod
    def arrayofgenres(self, allowSCMPXextended=False):
        
        GenreLookup = Array({0: "Blues", 1: "Classic Rock", 2: "Country", 3: "Dance", 4: "Disco", 5: "Funk", 6: "Grunge", 7: "Hip-Hop", 8: "Jazz", 9: "Metal", 10: "New Age", 11: "Oldies", 12: "Other", 13: "Pop", 14: "R&B", 15: "Rap", 16: "Reggae", 17: "Rock", 18: "Techno", 19: "Industrial", 20: "Alternative", 21: "Ska", 22: "Death Metal", 23: "Pranks", 24: "Soundtrack", 25: "Euro-Techno", 26: "Ambient", 27: "Trip-Hop", 28: "Vocal", 29: "Jazz+Funk", 30: "Fusion", 31: "Trance", 32: "Classical", 33: "Instrumental", 34: "Acid", 35: "House", 36: "Game", 37: "Sound Clip", 38: "Gospel", 39: "Noise", 40: "Alt. Rock", 41: "Bass", 42: "Soul", 43: "Punk", 44: "Space", 45: "Meditative", 46: "Instrumental Pop", 47: "Instrumental Rock", 48: "Ethnic", 49: "Gothic", 50: "Darkwave", 51: "Techno-Industrial", 52: "Electronic", 53: "Pop-Folk", 54: "Eurodance", 55: "Dream", 56: "Southern Rock", 57: "Comedy", 58: "Cult", 59: "Gangsta Rap", 60: "Top 40", 61: "Christian Rap", 62: "Pop/Funk", 63: "Jungle", 64: "Native American", 65: "Cabaret", 66: "New Wave", 67: "Psychedelic", 68: "Rave", 69: "Showtunes", 70: "Trailer", 71: "Lo-Fi", 72: "Tribal", 73: "Acid Punk", 74: "Acid Jazz", 75: "Polka", 76: "Retro", 77: "Musical", 78: "Rock & Roll", 79: "Hard Rock", 80: "Folk", 81: "Folk/Rock", 82: "National Folk", 83: "Swing", 84: "Fast-Fusion", 85: "Bebob", 86: "Latin", 87: "Revival", 88: "Celtic", 89: "Bluegrass", 90: "Avantgarde", 91: "Gothic Rock", 92: "Progressive Rock", 93: "Psychedelic Rock", 94: "Symphonic Rock", 95: "Slow Rock", 96: "Big Band", 97: "Chorus", 98: "Easy Listening", 99: "Acoustic", 100: "Humour", 101: "Speech", 102: "Chanson", 103: "Opera", 104: "Chamber Music", 105: "Sonata", 106: "Symphony", 107: "Booty Bass", 108: "Primus", 109: "Porn Groove", 110: "Satire", 111: "Slow Jam", 112: "Club", 113: "Tango", 114: "Samba", 115: "Folklore", 116: "Ballad", 117: "Power Ballad", 118: "Rhythmic Soul", 119: "Freestyle", 120: "Duet", 121: "Punk Rock", 122: "Drum Solo", 123: "A Cappella", 124: "Euro-House", 125: "Dance Hall", 126: "Goa", 127: "Drum & Bass", 128: "Club-House", 129: "Hardcore", 130: "Terror", 131: "Indie", 132: "BritPop", 133: "Negerpunk", 134: "Polsk Punk", 135: "Beat", 136: "Christian Gangsta Rap", 137: "Heavy Metal", 138: "Black Metal", 139: "Crossover", 140: "Contemporary Christian", 141: "Christian Rock", 142: "Merengue", 143: "Salsa", 144: "Thrash Metal", 145: "Anime", 146: "JPop", 147: "Synthpop", 255: "Unknown", "CR": "Cover", "RX": "Remix"})
        GenreLookupSCMPX = Array()
        if allowSCMPXextended and php_empty(lambda : GenreLookupSCMPX):
            GenreLookupSCMPX = GenreLookup
            #// http://www.geocities.co.jp/SiliconValley-Oakland/3664/alittle.html#GenreExtended
            #// Extended ID3v1 genres invented by SCMPX
            #// Note that 255 "Japanese Anime" conflicts with standard "Unknown"
            GenreLookupSCMPX[240] = "Sacred"
            GenreLookupSCMPX[241] = "Northern Europe"
            GenreLookupSCMPX[242] = "Irish & Scottish"
            GenreLookupSCMPX[243] = "Scotland"
            GenreLookupSCMPX[244] = "Ethnic Europe"
            GenreLookupSCMPX[245] = "Enka"
            GenreLookupSCMPX[246] = "Children's Song"
            GenreLookupSCMPX[247] = "Japanese Sky"
            GenreLookupSCMPX[248] = "Japanese Heavy Rock"
            GenreLookupSCMPX[249] = "Japanese Doom Rock"
            GenreLookupSCMPX[250] = "Japanese J-POP"
            GenreLookupSCMPX[251] = "Japanese Seiyu"
            GenreLookupSCMPX[252] = "Japanese Ambient Techno"
            GenreLookupSCMPX[253] = "Japanese Moemoe"
            GenreLookupSCMPX[254] = "Japanese Tokusatsu"
            pass
        # end if
        return GenreLookupSCMPX if allowSCMPXextended else GenreLookup
    # end def arrayofgenres
    #// 
    #// @param string $genreid
    #// @param bool   $allowSCMPXextended
    #// 
    #// @return string|false
    #//
    @classmethod
    def lookupgenrename(self, genreid=None, allowSCMPXextended=True):
        
        for case in Switch(genreid):
            if case("RX"):
                pass
            # end if
            if case("CR"):
                break
            # end if
            if case():
                if (not php_is_numeric(genreid)):
                    return False
                # end if
                genreid = php_intval(genreid)
                break
            # end if
        # end for
        GenreLookup = self.arrayofgenres(allowSCMPXextended)
        return GenreLookup[genreid] if (php_isset(lambda : GenreLookup[genreid])) else False
    # end def lookupgenrename
    #// 
    #// @param string $genre
    #// @param bool   $allowSCMPXextended
    #// 
    #// @return string|false
    #//
    @classmethod
    def lookupgenreid(self, genre=None, allowSCMPXextended=False):
        
        GenreLookup = self.arrayofgenres(allowSCMPXextended)
        LowerCaseNoSpaceSearchTerm = php_strtolower(php_str_replace(" ", "", genre))
        for key,value in GenreLookup:
            if php_strtolower(php_str_replace(" ", "", value)) == LowerCaseNoSpaceSearchTerm:
                return key
            # end if
        # end for
        return False
    # end def lookupgenreid
    #// 
    #// @param string $OriginalGenre
    #// 
    #// @return string|false
    #//
    @classmethod
    def standardiseid3v1genrename(self, OriginalGenre=None):
        
        GenreID = self.lookupgenreid(OriginalGenre)
        if GenreID != False:
            return self.lookupgenrename(GenreID)
        # end if
        return OriginalGenre
    # end def standardiseid3v1genrename
    #// 
    #// @param string     $title
    #// @param string     $artist
    #// @param string     $album
    #// @param string     $year
    #// @param int        $genreid
    #// @param string     $comment
    #// @param int|string $track
    #// 
    #// @return string
    #//
    @classmethod
    def generateid3v1tag(self, title=None, artist=None, album=None, year=None, genreid=None, comment=None, track=""):
        
        ID3v1Tag = "TAG"
        ID3v1Tag += php_str_pad(php_trim(php_substr(title, 0, 30)), 30, " ", STR_PAD_RIGHT)
        ID3v1Tag += php_str_pad(php_trim(php_substr(artist, 0, 30)), 30, " ", STR_PAD_RIGHT)
        ID3v1Tag += php_str_pad(php_trim(php_substr(album, 0, 30)), 30, " ", STR_PAD_RIGHT)
        ID3v1Tag += php_str_pad(php_trim(php_substr(year, 0, 4)), 4, " ", STR_PAD_LEFT)
        if (not php_empty(lambda : track)) and track > 0 and track <= 255:
            ID3v1Tag += php_str_pad(php_trim(php_substr(comment, 0, 28)), 28, " ", STR_PAD_RIGHT)
            ID3v1Tag += " "
            if gettype(track) == "string":
                track = php_int(track)
            # end if
            ID3v1Tag += chr(track)
        else:
            ID3v1Tag += php_str_pad(php_trim(php_substr(comment, 0, 30)), 30, " ", STR_PAD_RIGHT)
        # end if
        if genreid < 0 or genreid > 147:
            genreid = 255
            pass
        # end if
        for case in Switch(gettype(genreid)):
            if case("string"):
                pass
            # end if
            if case("integer"):
                ID3v1Tag += chr(php_intval(genreid))
                break
            # end if
            if case():
                ID3v1Tag += chr(255)
                break
            # end if
        # end for
        return ID3v1Tag
    # end def generateid3v1tag
# end class getid3_id3v1
