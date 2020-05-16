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
#// module.audio.mp3.php
#// module for analyzing MP3 files
#// dependencies: NONE
#// 
#// 
#// number of frames to scan to determine if MPEG-audio sequence is valid
#// Lower this number to 5-20 for faster scanning
#// Increase this number to 50+ for most accurate detection of valid VBR/CBR
#// mpeg-audio streams
php_define("GETID3_MP3_VALID_CHECK_FRAMES", 35)
class getid3_mp3(getid3_handler):
    allow_bruteforce = False
    #// 
    #// @return bool
    #//
    def analyze(self):
        
        info = self.getid3.info
        initialOffset = info["avdataoffset"]
        if (not self.getonlympegaudioinfo(info["avdataoffset"])):
            if self.allow_bruteforce:
                self.error("Rescanning file in BruteForce mode")
                self.getonlympegaudioinfobruteforce()
            # end if
        # end if
        if (php_isset(lambda : info["mpeg"]["audio"]["bitrate_mode"])):
            info["audio"]["bitrate_mode"] = php_strtolower(info["mpeg"]["audio"]["bitrate_mode"])
        # end if
        if (php_isset(lambda : info["id3v2"]["headerlength"])) and info["avdataoffset"] > info["id3v2"]["headerlength"] or (not (php_isset(lambda : info["id3v2"]))) and info["avdataoffset"] > 0 and info["avdataoffset"] != initialOffset:
            synchoffsetwarning = "Unknown data before synch "
            if (php_isset(lambda : info["id3v2"]["headerlength"])):
                synchoffsetwarning += "(ID3v2 header ends at " + info["id3v2"]["headerlength"] + ", then " + info["avdataoffset"] - info["id3v2"]["headerlength"] + " bytes garbage, "
            elif initialOffset > 0:
                synchoffsetwarning += "(should be at " + initialOffset + ", "
            else:
                synchoffsetwarning += "(should be at beginning of file, "
            # end if
            synchoffsetwarning += "synch detected at " + info["avdataoffset"] + ")"
            if (php_isset(lambda : info["audio"]["bitrate_mode"])) and info["audio"]["bitrate_mode"] == "cbr":
                if (not php_empty(lambda : info["id3v2"]["headerlength"])) and info["avdataoffset"] - info["id3v2"]["headerlength"] == info["mpeg"]["audio"]["framelength"]:
                    synchoffsetwarning += ". This is a known problem with some versions of LAME (3.90-3.92) DLL in CBR mode."
                    info["audio"]["codec"] = "LAME"
                    CurrentDataLAMEversionString = "LAME3."
                elif php_empty(lambda : info["id3v2"]["headerlength"]) and info["avdataoffset"] == info["mpeg"]["audio"]["framelength"]:
                    synchoffsetwarning += ". This is a known problem with some versions of LAME (3.90 - 3.92) DLL in CBR mode."
                    info["audio"]["codec"] = "LAME"
                    CurrentDataLAMEversionString = "LAME3."
                # end if
            # end if
            self.warning(synchoffsetwarning)
        # end if
        if (php_isset(lambda : info["mpeg"]["audio"]["LAME"])):
            info["audio"]["codec"] = "LAME"
            if (not php_empty(lambda : info["mpeg"]["audio"]["LAME"]["long_version"])):
                info["audio"]["encoder"] = php_rtrim(info["mpeg"]["audio"]["LAME"]["long_version"], " ")
            elif (not php_empty(lambda : info["mpeg"]["audio"]["LAME"]["short_version"])):
                info["audio"]["encoder"] = php_rtrim(info["mpeg"]["audio"]["LAME"]["short_version"], " ")
            # end if
        # end if
        CurrentDataLAMEversionString = CurrentDataLAMEversionString if (not php_empty(lambda : CurrentDataLAMEversionString)) else info["audio"]["encoder"] if (php_isset(lambda : info["audio"]["encoder"])) else ""
        if (not php_empty(lambda : CurrentDataLAMEversionString)) and php_substr(CurrentDataLAMEversionString, 0, 6) == "LAME3." and (not php_preg_match("[0-9\\)]", php_substr(CurrentDataLAMEversionString, -1))):
            #// a version number of LAME that does not end with a number like "LAME3.92"
            #// or with a closing parenthesis like "LAME3.88 (alpha)"
            #// or a version of LAME with the LAMEtag-not-filled-in-DLL-mode bug (3.90-3.92)
            #// not sure what the actual last frame length will be, but will be less than or equal to 1441
            PossiblyLongerLAMEversion_FrameLength = 1441
            #// Not sure what version of LAME this is - look in padding of last frame for longer version string
            PossibleLAMEversionStringOffset = info["avdataend"] - PossiblyLongerLAMEversion_FrameLength
            self.fseek(PossibleLAMEversionStringOffset)
            PossiblyLongerLAMEversion_Data = self.fread(PossiblyLongerLAMEversion_FrameLength)
            for case in Switch(php_substr(CurrentDataLAMEversionString, -1)):
                if case("a"):
                    pass
                # end if
                if case("b"):
                    #// "LAME3.94a" will have a longer version string of "LAME3.94 (alpha)" for example
                    #// need to trim off "a" to match longer string
                    CurrentDataLAMEversionString = php_substr(CurrentDataLAMEversionString, 0, -1)
                    break
                # end if
            # end for
            PossiblyLongerLAMEversion_String = php_strstr(PossiblyLongerLAMEversion_Data, CurrentDataLAMEversionString)
            if PossiblyLongerLAMEversion_String != False:
                if php_substr(PossiblyLongerLAMEversion_String, 0, php_strlen(CurrentDataLAMEversionString)) == CurrentDataLAMEversionString:
                    PossiblyLongerLAMEversion_NewString = php_substr(PossiblyLongerLAMEversion_String, 0, strspn(PossiblyLongerLAMEversion_String, "LAME0123456789., (abcdefghijklmnopqrstuvwxyzJFSOND)"))
                    #// "LAME3.90.3"  "LAME3.87 (beta 1, Sep 27 2000)" "LAME3.88 (beta)"
                    if php_empty(lambda : info["audio"]["encoder"]) or php_strlen(PossiblyLongerLAMEversion_NewString) > php_strlen(info["audio"]["encoder"]):
                        info["audio"]["encoder"] = PossiblyLongerLAMEversion_NewString
                    # end if
                # end if
            # end if
        # end if
        if (not php_empty(lambda : info["audio"]["encoder"])):
            info["audio"]["encoder"] = php_rtrim(info["audio"]["encoder"], "  ")
        # end if
        for case in Switch(info["mpeg"]["audio"]["layer"] if (php_isset(lambda : info["mpeg"]["audio"]["layer"])) else ""):
            if case(1):
                pass
            # end if
            if case(2):
                info["audio"]["dataformat"] = "mp" + info["mpeg"]["audio"]["layer"]
                break
            # end if
        # end for
        if (php_isset(lambda : info["fileformat"])) and info["fileformat"] == "mp3":
            for case in Switch(info["audio"]["dataformat"]):
                if case("mp1"):
                    pass
                # end if
                if case("mp2"):
                    pass
                # end if
                if case("mp3"):
                    info["fileformat"] = info["audio"]["dataformat"]
                    break
                # end if
                if case():
                    self.warning("Expecting [audio][dataformat] to be mp1/mp2/mp3 when fileformat == mp3, [audio][dataformat] actually \"" + info["audio"]["dataformat"] + "\"")
                    break
                # end if
            # end for
        # end if
        if php_empty(lambda : info["fileformat"]):
            info["fileformat"] = None
            info["audio"]["bitrate_mode"] = None
            info["avdataoffset"] = None
            info["avdataend"] = None
            return False
        # end if
        info["mime_type"] = "audio/mpeg"
        info["audio"]["lossless"] = False
        #// Calculate playtime
        if (not (php_isset(lambda : info["playtime_seconds"]))) and (php_isset(lambda : info["audio"]["bitrate"])) and info["audio"]["bitrate"] > 0:
            #// https://github.com/JamesHeinrich/getID3/issues/161
            #// VBR header frame contains ~0.026s of silent audio data, but is not actually part of the original encoding and should be ignored
            xingVBRheaderFrameLength = info["mpeg"]["audio"]["framelength"] if (php_isset(lambda : info["mpeg"]["audio"]["VBR_frames"])) and (php_isset(lambda : info["mpeg"]["audio"]["framelength"])) else 0
            info["playtime_seconds"] = info["avdataend"] - info["avdataoffset"] - xingVBRheaderFrameLength * 8 / info["audio"]["bitrate"]
        # end if
        info["audio"]["encoder_options"] = self.guessencoderoptions()
        return True
    # end def analyze
    #// 
    #// @return string
    #//
    def guessencoderoptions(self):
        
        #// shortcuts
        info = self.getid3.info
        thisfile_mpeg_audio = Array()
        thisfile_mpeg_audio_lame = Array()
        if (not php_empty(lambda : info["mpeg"]["audio"])):
            thisfile_mpeg_audio = info["mpeg"]["audio"]
            if (not php_empty(lambda : thisfile_mpeg_audio["LAME"])):
                thisfile_mpeg_audio_lame = thisfile_mpeg_audio["LAME"]
            # end if
        # end if
        encoder_options = ""
        NamedPresetBitrates = Array(16, 24, 40, 56, 112, 128, 160, 192, 256)
        if (php_isset(lambda : thisfile_mpeg_audio["VBR_method"])) and thisfile_mpeg_audio["VBR_method"] == "Fraunhofer" and (not php_empty(lambda : thisfile_mpeg_audio["VBR_quality"])):
            encoder_options = "VBR q" + thisfile_mpeg_audio["VBR_quality"]
        elif (not php_empty(lambda : thisfile_mpeg_audio_lame["preset_used"])) and (php_isset(lambda : thisfile_mpeg_audio_lame["preset_used_id"])) and (not php_in_array(thisfile_mpeg_audio_lame["preset_used_id"], NamedPresetBitrates)):
            encoder_options = thisfile_mpeg_audio_lame["preset_used"]
        elif (not php_empty(lambda : thisfile_mpeg_audio_lame["vbr_quality"])):
            KnownEncoderValues = Array()
            if php_empty(lambda : KnownEncoderValues):
                #// $KnownEncoderValues[abrbitrate_minbitrate][vbr_quality][raw_vbr_method][raw_noise_shaping][raw_stereo_mode][ath_type][lowpass_frequency] = 'preset name';
                KnownEncoderValues[255][58][1][1][3][2][20500] = "--alt-preset insane"
                #// 3.90,   3.90.1, 3.92
                KnownEncoderValues[255][58][1][1][3][2][20600] = "--alt-preset insane"
                #// 3.90.2, 3.90.3, 3.91
                KnownEncoderValues[255][57][1][1][3][4][20500] = "--alt-preset insane"
                #// 3.94,   3.95
                KnownEncoderValues["**"][78][3][2][3][2][19500] = "--alt-preset extreme"
                #// 3.90,   3.90.1, 3.92
                KnownEncoderValues["**"][78][3][2][3][2][19600] = "--alt-preset extreme"
                #// 3.90.2, 3.91
                KnownEncoderValues["**"][78][3][1][3][2][19600] = "--alt-preset extreme"
                #// 3.90.3
                KnownEncoderValues["**"][78][4][2][3][2][19500] = "--alt-preset fast extreme"
                #// 3.90,   3.90.1, 3.92
                KnownEncoderValues["**"][78][4][2][3][2][19600] = "--alt-preset fast extreme"
                #// 3.90.2, 3.90.3, 3.91
                KnownEncoderValues["**"][78][3][2][3][4][19000] = "--alt-preset standard"
                #// 3.90,   3.90.1, 3.90.2, 3.91, 3.92
                KnownEncoderValues["**"][78][3][1][3][4][19000] = "--alt-preset standard"
                #// 3.90.3
                KnownEncoderValues["**"][78][4][2][3][4][19000] = "--alt-preset fast standard"
                #// 3.90,   3.90.1, 3.90.2, 3.91, 3.92
                KnownEncoderValues["**"][78][4][1][3][4][19000] = "--alt-preset fast standard"
                #// 3.90.3
                KnownEncoderValues["**"][88][4][1][3][3][19500] = "--r3mix"
                #// 3.90,   3.90.1, 3.92
                KnownEncoderValues["**"][88][4][1][3][3][19600] = "--r3mix"
                #// 3.90.2, 3.90.3, 3.91
                KnownEncoderValues["**"][67][4][1][3][4][18000] = "--r3mix"
                #// 3.94,   3.95
                KnownEncoderValues["**"][68][3][2][3][4][18000] = "--alt-preset medium"
                #// 3.90.3
                KnownEncoderValues["**"][68][4][2][3][4][18000] = "--alt-preset fast medium"
                #// 3.90.3
                KnownEncoderValues[255][99][1][1][1][2][0] = "--preset studio"
                #// 3.90,   3.90.1, 3.90.2, 3.91, 3.92
                KnownEncoderValues[255][58][2][1][3][2][20600] = "--preset studio"
                #// 3.90.3, 3.93.1
                KnownEncoderValues[255][58][2][1][3][2][20500] = "--preset studio"
                #// 3.93
                KnownEncoderValues[255][57][2][1][3][4][20500] = "--preset studio"
                #// 3.94,   3.95
                KnownEncoderValues[192][88][1][1][1][2][0] = "--preset cd"
                #// 3.90,   3.90.1, 3.90.2,   3.91, 3.92
                KnownEncoderValues[192][58][2][2][3][2][19600] = "--preset cd"
                #// 3.90.3, 3.93.1
                KnownEncoderValues[192][58][2][2][3][2][19500] = "--preset cd"
                #// 3.93
                KnownEncoderValues[192][57][2][1][3][4][19500] = "--preset cd"
                #// 3.94,   3.95
                KnownEncoderValues[160][78][1][1][3][2][18000] = "--preset hifi"
                #// 3.90,   3.90.1, 3.90.2,   3.91, 3.92
                KnownEncoderValues[160][58][2][2][3][2][18000] = "--preset hifi"
                #// 3.90.3, 3.93,   3.93.1
                KnownEncoderValues[160][57][2][1][3][4][18000] = "--preset hifi"
                #// 3.94,   3.95
                KnownEncoderValues[128][67][1][1][3][2][18000] = "--preset tape"
                #// 3.90,   3.90.1, 3.90.2,   3.91, 3.92
                KnownEncoderValues[128][67][1][1][3][2][15000] = "--preset radio"
                #// 3.90,   3.90.1, 3.90.2,   3.91, 3.92
                KnownEncoderValues[112][67][1][1][3][2][15000] = "--preset fm"
                #// 3.90,   3.90.1, 3.90.2,   3.91, 3.92
                KnownEncoderValues[112][58][2][2][3][2][16000] = "--preset tape/radio/fm"
                #// 3.90.3, 3.93,   3.93.1
                KnownEncoderValues[112][57][2][1][3][4][16000] = "--preset tape/radio/fm"
                #// 3.94,   3.95
                KnownEncoderValues[56][58][2][2][0][2][10000] = "--preset voice"
                #// 3.90.3, 3.93,   3.93.1
                KnownEncoderValues[56][57][2][1][0][4][15000] = "--preset voice"
                #// 3.94,   3.95
                KnownEncoderValues[56][57][2][1][0][4][16000] = "--preset voice"
                #// 3.94a14
                KnownEncoderValues[40][65][1][1][0][2][7500] = "--preset mw-us"
                #// 3.90,   3.90.1, 3.92
                KnownEncoderValues[40][65][1][1][0][2][7600] = "--preset mw-us"
                #// 3.90.2, 3.91
                KnownEncoderValues[40][58][2][2][0][2][7000] = "--preset mw-us"
                #// 3.90.3, 3.93,   3.93.1
                KnownEncoderValues[40][57][2][1][0][4][10500] = "--preset mw-us"
                #// 3.94,   3.95
                KnownEncoderValues[40][57][2][1][0][4][11200] = "--preset mw-us"
                #// 3.94a14
                KnownEncoderValues[40][57][2][1][0][4][8800] = "--preset mw-us"
                #// 3.94a15
                KnownEncoderValues[24][58][2][2][0][2][4000] = "--preset phon+/lw/mw-eu/sw"
                #// 3.90.3, 3.93.1
                KnownEncoderValues[24][58][2][2][0][2][3900] = "--preset phon+/lw/mw-eu/sw"
                #// 3.93
                KnownEncoderValues[24][57][2][1][0][4][5900] = "--preset phon+/lw/mw-eu/sw"
                #// 3.94,   3.95
                KnownEncoderValues[24][57][2][1][0][4][6200] = "--preset phon+/lw/mw-eu/sw"
                #// 3.94a14
                KnownEncoderValues[24][57][2][1][0][4][3200] = "--preset phon+/lw/mw-eu/sw"
                #// 3.94a15
                KnownEncoderValues[16][58][2][2][0][2][3800] = "--preset phone"
                #// 3.90.3, 3.93.1
                KnownEncoderValues[16][58][2][2][0][2][3700] = "--preset phone"
                #// 3.93
                KnownEncoderValues[16][57][2][1][0][4][5600] = "--preset phone"
                pass
            # end if
            if (php_isset(lambda : KnownEncoderValues[thisfile_mpeg_audio_lame["raw"]["abrbitrate_minbitrate"]][thisfile_mpeg_audio_lame["vbr_quality"]][thisfile_mpeg_audio_lame["raw"]["vbr_method"]][thisfile_mpeg_audio_lame["raw"]["noise_shaping"]][thisfile_mpeg_audio_lame["raw"]["stereo_mode"]][thisfile_mpeg_audio_lame["ath_type"]][thisfile_mpeg_audio_lame["lowpass_frequency"]])):
                encoder_options = KnownEncoderValues[thisfile_mpeg_audio_lame["raw"]["abrbitrate_minbitrate"]][thisfile_mpeg_audio_lame["vbr_quality"]][thisfile_mpeg_audio_lame["raw"]["vbr_method"]][thisfile_mpeg_audio_lame["raw"]["noise_shaping"]][thisfile_mpeg_audio_lame["raw"]["stereo_mode"]][thisfile_mpeg_audio_lame["ath_type"]][thisfile_mpeg_audio_lame["lowpass_frequency"]]
            elif (php_isset(lambda : KnownEncoderValues["**"][thisfile_mpeg_audio_lame["vbr_quality"]][thisfile_mpeg_audio_lame["raw"]["vbr_method"]][thisfile_mpeg_audio_lame["raw"]["noise_shaping"]][thisfile_mpeg_audio_lame["raw"]["stereo_mode"]][thisfile_mpeg_audio_lame["ath_type"]][thisfile_mpeg_audio_lame["lowpass_frequency"]])):
                encoder_options = KnownEncoderValues["**"][thisfile_mpeg_audio_lame["vbr_quality"]][thisfile_mpeg_audio_lame["raw"]["vbr_method"]][thisfile_mpeg_audio_lame["raw"]["noise_shaping"]][thisfile_mpeg_audio_lame["raw"]["stereo_mode"]][thisfile_mpeg_audio_lame["ath_type"]][thisfile_mpeg_audio_lame["lowpass_frequency"]]
            elif info["audio"]["bitrate_mode"] == "vbr":
                #// http://gabriel.mp3-tech.org/mp3infotag.html
                #// int    Quality = (100 - 10 * gfp->VBR_q - gfp->quality)h
                LAME_V_value = 10 - ceil(thisfile_mpeg_audio_lame["vbr_quality"] / 10)
                LAME_q_value = 100 - thisfile_mpeg_audio_lame["vbr_quality"] - LAME_V_value * 10
                encoder_options = "-V" + LAME_V_value + " -q" + LAME_q_value
            elif info["audio"]["bitrate_mode"] == "cbr":
                encoder_options = php_strtoupper(info["audio"]["bitrate_mode"]) + ceil(info["audio"]["bitrate"] / 1000)
            else:
                encoder_options = php_strtoupper(info["audio"]["bitrate_mode"])
            # end if
        elif (not php_empty(lambda : thisfile_mpeg_audio_lame["bitrate_abr"])):
            encoder_options = "ABR" + thisfile_mpeg_audio_lame["bitrate_abr"]
        elif (not php_empty(lambda : info["audio"]["bitrate"])):
            if info["audio"]["bitrate_mode"] == "cbr":
                encoder_options = php_strtoupper(info["audio"]["bitrate_mode"]) + ceil(info["audio"]["bitrate"] / 1000)
            else:
                encoder_options = php_strtoupper(info["audio"]["bitrate_mode"])
            # end if
        # end if
        if (not php_empty(lambda : thisfile_mpeg_audio_lame["bitrate_min"])):
            encoder_options += " -b" + thisfile_mpeg_audio_lame["bitrate_min"]
        # end if
        if (not php_empty(lambda : thisfile_mpeg_audio_lame["encoding_flags"]["nogap_prev"])) or (not php_empty(lambda : thisfile_mpeg_audio_lame["encoding_flags"]["nogap_next"])):
            encoder_options += " --nogap"
        # end if
        if (not php_empty(lambda : thisfile_mpeg_audio_lame["lowpass_frequency"])):
            ExplodedOptions = php_explode(" ", encoder_options, 4)
            if ExplodedOptions[0] == "--r3mix":
                ExplodedOptions[1] = "r3mix"
            # end if
            for case in Switch(ExplodedOptions[0]):
                if case("--preset"):
                    pass
                # end if
                if case("--alt-preset"):
                    pass
                # end if
                if case("--r3mix"):
                    if ExplodedOptions[1] == "fast":
                        ExplodedOptions[1] += " " + ExplodedOptions[2]
                    # end if
                    for case in Switch(ExplodedOptions[1]):
                        if case("portable"):
                            pass
                        # end if
                        if case("medium"):
                            pass
                        # end if
                        if case("standard"):
                            pass
                        # end if
                        if case("extreme"):
                            pass
                        # end if
                        if case("insane"):
                            pass
                        # end if
                        if case("fast portable"):
                            pass
                        # end if
                        if case("fast medium"):
                            pass
                        # end if
                        if case("fast standard"):
                            pass
                        # end if
                        if case("fast extreme"):
                            pass
                        # end if
                        if case("fast insane"):
                            pass
                        # end if
                        if case("r3mix"):
                            ExpectedLowpass = Array({"insane|20500": 20500, "insane|20600": 20600, "medium|18000": 18000, "fast medium|18000": 18000, "extreme|19500": 19500, "extreme|19600": 19600, "fast extreme|19500": 19500, "fast extreme|19600": 19600, "standard|19000": 19000, "fast standard|19000": 19000, "r3mix|19500": 19500, "r3mix|19600": 19600, "r3mix|18000": 18000})
                            if (not (php_isset(lambda : ExpectedLowpass[ExplodedOptions[1] + "|" + thisfile_mpeg_audio_lame["lowpass_frequency"]]))) and thisfile_mpeg_audio_lame["lowpass_frequency"] < 22050 and round(thisfile_mpeg_audio_lame["lowpass_frequency"] / 1000) < round(thisfile_mpeg_audio["sample_rate"] / 2000):
                                encoder_options += " --lowpass " + thisfile_mpeg_audio_lame["lowpass_frequency"]
                            # end if
                            break
                        # end if
                        if case():
                            break
                        # end if
                    # end for
                    break
                # end if
            # end for
        # end if
        if (php_isset(lambda : thisfile_mpeg_audio_lame["raw"]["source_sample_freq"])):
            if thisfile_mpeg_audio["sample_rate"] == 44100 and thisfile_mpeg_audio_lame["raw"]["source_sample_freq"] != 1:
                encoder_options += " --resample 44100"
            elif thisfile_mpeg_audio["sample_rate"] == 48000 and thisfile_mpeg_audio_lame["raw"]["source_sample_freq"] != 2:
                encoder_options += " --resample 48000"
            elif thisfile_mpeg_audio["sample_rate"] < 44100:
                for case in Switch(thisfile_mpeg_audio_lame["raw"]["source_sample_freq"]):
                    if case(0):
                        break
                    # end if
                    if case(1):
                        pass
                    # end if
                    if case(2):
                        pass
                    # end if
                    if case(3):
                        #// 48000+
                        ExplodedOptions = php_explode(" ", encoder_options, 4)
                        for case in Switch(ExplodedOptions[0]):
                            if case("--preset"):
                                pass
                            # end if
                            if case("--alt-preset"):
                                for case in Switch(ExplodedOptions[1]):
                                    if case("fast"):
                                        pass
                                    # end if
                                    if case("portable"):
                                        pass
                                    # end if
                                    if case("medium"):
                                        pass
                                    # end if
                                    if case("standard"):
                                        pass
                                    # end if
                                    if case("extreme"):
                                        pass
                                    # end if
                                    if case("insane"):
                                        encoder_options += " --resample " + thisfile_mpeg_audio["sample_rate"]
                                        break
                                    # end if
                                    if case():
                                        ExpectedResampledRate = Array({"phon+/lw/mw-eu/sw|16000": 16000, "mw-us|24000": 24000, "mw-us|32000": 32000, "mw-us|16000": 16000, "phone|16000": 16000, "phone|11025": 11025, "radio|32000": 32000, "fm/radio|32000": 32000, "fm|32000": 32000, "voice|32000": 32000})
                                        if (not (php_isset(lambda : ExpectedResampledRate[ExplodedOptions[1] + "|" + thisfile_mpeg_audio["sample_rate"]]))):
                                            encoder_options += " --resample " + thisfile_mpeg_audio["sample_rate"]
                                        # end if
                                        break
                                    # end if
                                # end for
                                break
                            # end if
                            if case("--r3mix"):
                                pass
                            # end if
                            if case():
                                encoder_options += " --resample " + thisfile_mpeg_audio["sample_rate"]
                                break
                            # end if
                        # end for
                        break
                    # end if
                # end for
            # end if
        # end if
        if php_empty(lambda : encoder_options) and (not php_empty(lambda : info["audio"]["bitrate"])) and (not php_empty(lambda : info["audio"]["bitrate_mode"])):
            #// $encoder_options = strtoupper($info['audio']['bitrate_mode']).ceil($info['audio']['bitrate'] / 1000);
            encoder_options = php_strtoupper(info["audio"]["bitrate_mode"])
        # end if
        return encoder_options
    # end def guessencoderoptions
    #// 
    #// @param int   $offset
    #// @param array $info
    #// @param bool  $recursivesearch
    #// @param bool  $ScanAsCBR
    #// @param bool  $FastMPEGheaderScan
    #// 
    #// @return bool
    #//
    def decodempegaudioheader(self, offset=None, info=None, recursivesearch=True, ScanAsCBR=False, FastMPEGheaderScan=False):
        
        MPEGaudioVersionLookup = None
        MPEGaudioLayerLookup = None
        MPEGaudioBitrateLookup = None
        MPEGaudioFrequencyLookup = None
        MPEGaudioChannelModeLookup = None
        MPEGaudioModeExtensionLookup = None
        MPEGaudioEmphasisLookup = None
        if php_empty(lambda : MPEGaudioVersionLookup):
            MPEGaudioVersionLookup = self.mpegaudioversionarray()
            MPEGaudioLayerLookup = self.mpegaudiolayerarray()
            MPEGaudioBitrateLookup = self.mpegaudiobitratearray()
            MPEGaudioFrequencyLookup = self.mpegaudiofrequencyarray()
            MPEGaudioChannelModeLookup = self.mpegaudiochannelmodearray()
            MPEGaudioModeExtensionLookup = self.mpegaudiomodeextensionarray()
            MPEGaudioEmphasisLookup = self.mpegaudioemphasisarray()
        # end if
        if self.fseek(offset) != 0:
            self.error("decodeMPEGaudioHeader() failed to seek to next offset at " + offset)
            return False
        # end if
        #// $headerstring = $this->fread(1441); // worst-case max length = 32kHz @ 320kbps layer 3 = 1441 bytes/frame
        headerstring = self.fread(226)
        #// LAME header at offset 36 + 190 bytes of Xing/LAME data
        #// MP3 audio frame structure:
        #// $aa $aa $aa $aa [$bb $bb] $cc...
        #// where $aa..$aa is the four-byte mpeg-audio header (below)
        #// $bb $bb is the optional 2-byte CRC
        #// and $cc... is the audio data
        head4 = php_substr(headerstring, 0, 4)
        head4_key = getid3_lib.printhexbytes(head4, True, False, False)
        MPEGaudioHeaderDecodeCache = Array()
        if (php_isset(lambda : MPEGaudioHeaderDecodeCache[head4_key])):
            MPEGheaderRawArray = MPEGaudioHeaderDecodeCache[head4_key]
        else:
            MPEGheaderRawArray = self.mpegaudioheaderdecode(head4)
            MPEGaudioHeaderDecodeCache[head4_key] = MPEGheaderRawArray
        # end if
        MPEGaudioHeaderValidCache = Array()
        if (not (php_isset(lambda : MPEGaudioHeaderValidCache[head4_key]))):
            #// Not in cache
            #// $MPEGaudioHeaderValidCache[$head4_key] = self::MPEGaudioHeaderValid($MPEGheaderRawArray, false, true);  // allow badly-formatted freeformat (from LAME 3.90 - 3.93.1)
            MPEGaudioHeaderValidCache[head4_key] = self.mpegaudioheadervalid(MPEGheaderRawArray, False, False)
        # end if
        #// shortcut
        if (not (php_isset(lambda : info["mpeg"]["audio"]))):
            info["mpeg"]["audio"] = Array()
        # end if
        thisfile_mpeg_audio = info["mpeg"]["audio"]
        if MPEGaudioHeaderValidCache[head4_key]:
            thisfile_mpeg_audio["raw"] = MPEGheaderRawArray
        else:
            self.error("Invalid MPEG audio header (" + getid3_lib.printhexbytes(head4) + ") at offset " + offset)
            return False
        # end if
        if (not FastMPEGheaderScan):
            thisfile_mpeg_audio["version"] = MPEGaudioVersionLookup[thisfile_mpeg_audio["raw"]["version"]]
            thisfile_mpeg_audio["layer"] = MPEGaudioLayerLookup[thisfile_mpeg_audio["raw"]["layer"]]
            thisfile_mpeg_audio["channelmode"] = MPEGaudioChannelModeLookup[thisfile_mpeg_audio["raw"]["channelmode"]]
            thisfile_mpeg_audio["channels"] = 1 if thisfile_mpeg_audio["channelmode"] == "mono" else 2
            thisfile_mpeg_audio["sample_rate"] = MPEGaudioFrequencyLookup[thisfile_mpeg_audio["version"]][thisfile_mpeg_audio["raw"]["sample_rate"]]
            thisfile_mpeg_audio["protection"] = (not thisfile_mpeg_audio["raw"]["protection"])
            thisfile_mpeg_audio["private"] = php_bool(thisfile_mpeg_audio["raw"]["private"])
            thisfile_mpeg_audio["modeextension"] = MPEGaudioModeExtensionLookup[thisfile_mpeg_audio["layer"]][thisfile_mpeg_audio["raw"]["modeextension"]]
            thisfile_mpeg_audio["copyright"] = php_bool(thisfile_mpeg_audio["raw"]["copyright"])
            thisfile_mpeg_audio["original"] = php_bool(thisfile_mpeg_audio["raw"]["original"])
            thisfile_mpeg_audio["emphasis"] = MPEGaudioEmphasisLookup[thisfile_mpeg_audio["raw"]["emphasis"]]
            info["audio"]["channels"] = thisfile_mpeg_audio["channels"]
            info["audio"]["sample_rate"] = thisfile_mpeg_audio["sample_rate"]
            if thisfile_mpeg_audio["protection"]:
                thisfile_mpeg_audio["crc"] = getid3_lib.bigendian2int(php_substr(headerstring, 4, 2))
            # end if
        # end if
        if thisfile_mpeg_audio["raw"]["bitrate"] == 15:
            #// http://www.hydrogenaudio.org/?act=ST&f=16&t=9682&st=0
            self.warning("Invalid bitrate index (15), this is a known bug in free-format MP3s encoded by LAME v3.90 - 3.93.1")
            thisfile_mpeg_audio["raw"]["bitrate"] = 0
        # end if
        thisfile_mpeg_audio["padding"] = php_bool(thisfile_mpeg_audio["raw"]["padding"])
        thisfile_mpeg_audio["bitrate"] = MPEGaudioBitrateLookup[thisfile_mpeg_audio["version"]][thisfile_mpeg_audio["layer"]][thisfile_mpeg_audio["raw"]["bitrate"]]
        if thisfile_mpeg_audio["bitrate"] == "free" and offset == info["avdataoffset"]:
            #// only skip multiple frame check if free-format bitstream found at beginning of file
            #// otherwise is quite possibly simply corrupted data
            recursivesearch = False
        # end if
        #// For Layer 2 there are some combinations of bitrate and mode which are not allowed.
        if (not FastMPEGheaderScan) and thisfile_mpeg_audio["layer"] == "2":
            info["audio"]["dataformat"] = "mp2"
            for case in Switch(thisfile_mpeg_audio["channelmode"]):
                if case("mono"):
                    if thisfile_mpeg_audio["bitrate"] == "free" or thisfile_mpeg_audio["bitrate"] <= 192000:
                        pass
                    else:
                        self.error(thisfile_mpeg_audio["bitrate"] + "kbps not allowed in Layer 2, " + thisfile_mpeg_audio["channelmode"] + ".")
                        return False
                    # end if
                    break
                # end if
                if case("stereo"):
                    pass
                # end if
                if case("joint stereo"):
                    pass
                # end if
                if case("dual channel"):
                    if thisfile_mpeg_audio["bitrate"] == "free" or thisfile_mpeg_audio["bitrate"] == 64000 or thisfile_mpeg_audio["bitrate"] >= 96000:
                        pass
                    else:
                        self.error(php_intval(round(thisfile_mpeg_audio["bitrate"] / 1000)) + "kbps not allowed in Layer 2, " + thisfile_mpeg_audio["channelmode"] + ".")
                        return False
                    # end if
                    break
                # end if
            # end for
        # end if
        if info["audio"]["sample_rate"] > 0:
            thisfile_mpeg_audio["framelength"] = self.mpegaudioframelength(thisfile_mpeg_audio["bitrate"], thisfile_mpeg_audio["version"], thisfile_mpeg_audio["layer"], php_int(thisfile_mpeg_audio["padding"]), info["audio"]["sample_rate"])
        # end if
        nextframetestoffset = offset + 1
        if thisfile_mpeg_audio["bitrate"] != "free":
            info["audio"]["bitrate"] = thisfile_mpeg_audio["bitrate"]
            if (php_isset(lambda : thisfile_mpeg_audio["framelength"])):
                nextframetestoffset = offset + thisfile_mpeg_audio["framelength"]
            else:
                self.error("Frame at offset(" + offset + ") is has an invalid frame length.")
                return False
            # end if
        # end if
        ExpectedNumberOfAudioBytes = 0
        #// 
        #// Variable-bitrate headers
        if php_substr(headerstring, 4 + 32, 4) == "VBRI":
            #// Fraunhofer VBR header is hardcoded 'VBRI' at offset 0x24 (36)
            #// specs taken from http://minnie.tuhs.org/pipermail/mp3encoder/2001-January/001800.html
            thisfile_mpeg_audio["bitrate_mode"] = "vbr"
            thisfile_mpeg_audio["VBR_method"] = "Fraunhofer"
            info["audio"]["codec"] = "Fraunhofer"
            SideInfoData = php_substr(headerstring, 4 + 2, 32)
            FraunhoferVBROffset = 36
            thisfile_mpeg_audio["VBR_encoder_version"] = getid3_lib.bigendian2int(php_substr(headerstring, FraunhoferVBROffset + 4, 2))
            #// VbriVersion
            thisfile_mpeg_audio["VBR_encoder_delay"] = getid3_lib.bigendian2int(php_substr(headerstring, FraunhoferVBROffset + 6, 2))
            #// VbriDelay
            thisfile_mpeg_audio["VBR_quality"] = getid3_lib.bigendian2int(php_substr(headerstring, FraunhoferVBROffset + 8, 2))
            #// VbriQuality
            thisfile_mpeg_audio["VBR_bytes"] = getid3_lib.bigendian2int(php_substr(headerstring, FraunhoferVBROffset + 10, 4))
            #// VbriStreamBytes
            thisfile_mpeg_audio["VBR_frames"] = getid3_lib.bigendian2int(php_substr(headerstring, FraunhoferVBROffset + 14, 4))
            #// VbriStreamFrames
            thisfile_mpeg_audio["VBR_seek_offsets"] = getid3_lib.bigendian2int(php_substr(headerstring, FraunhoferVBROffset + 18, 2))
            #// VbriTableSize
            thisfile_mpeg_audio["VBR_seek_scale"] = getid3_lib.bigendian2int(php_substr(headerstring, FraunhoferVBROffset + 20, 2))
            #// VbriTableScale
            thisfile_mpeg_audio["VBR_entry_bytes"] = getid3_lib.bigendian2int(php_substr(headerstring, FraunhoferVBROffset + 22, 2))
            #// VbriEntryBytes
            thisfile_mpeg_audio["VBR_entry_frames"] = getid3_lib.bigendian2int(php_substr(headerstring, FraunhoferVBROffset + 24, 2))
            #// VbriEntryFrames
            ExpectedNumberOfAudioBytes = thisfile_mpeg_audio["VBR_bytes"]
            previousbyteoffset = offset
            i = 0
            while i < thisfile_mpeg_audio["VBR_seek_offsets"]:
                
                Fraunhofer_OffsetN = getid3_lib.bigendian2int(php_substr(headerstring, FraunhoferVBROffset, thisfile_mpeg_audio["VBR_entry_bytes"]))
                FraunhoferVBROffset += thisfile_mpeg_audio["VBR_entry_bytes"]
                thisfile_mpeg_audio["VBR_offsets_relative"][i] = Fraunhofer_OffsetN * thisfile_mpeg_audio["VBR_seek_scale"]
                thisfile_mpeg_audio["VBR_offsets_absolute"][i] = Fraunhofer_OffsetN * thisfile_mpeg_audio["VBR_seek_scale"] + previousbyteoffset
                previousbyteoffset += Fraunhofer_OffsetN
                i += 1
            # end while
        else:
            #// Xing VBR header is hardcoded 'Xing' at a offset 0x0D (13), 0x15 (21) or 0x24 (36)
            #// depending on MPEG layer and number of channels
            VBRidOffset = self.xingvbridoffset(thisfile_mpeg_audio["version"], thisfile_mpeg_audio["channelmode"])
            SideInfoData = php_substr(headerstring, 4 + 2, VBRidOffset - 4)
            if php_substr(headerstring, VBRidOffset, php_strlen("Xing")) == "Xing" or php_substr(headerstring, VBRidOffset, php_strlen("Info")) == "Info":
                #// 'Xing' is traditional Xing VBR frame
                #// 'Info' is LAME-encoded CBR (This was done to avoid CBR files to be recognized as traditional Xing VBR files by some decoders.)
                #// 'Info' *can* legally be used to specify a VBR file as well, however.
                #// http://www.multiweb.cz/twoinches/MP3inside.htm
                #// 00..03 = "Xing" or "Info"
                #// 04..07 = Flags:
                #// 0x01  Frames Flag     set if value for number of frames in file is stored
                #// 0x02  Bytes Flag      set if value for filesize in bytes is stored
                #// 0x04  TOC Flag        set if values for TOC are stored
                #// 0x08  VBR Scale Flag  set if values for VBR scale is stored
                #// 08..11  Frames: Number of frames in file (including the first Xing/Info one)
                #// 12..15  Bytes:  File length in Bytes
                #// 16..115  TOC (Table of Contents):
                #// Contains of 100 indexes (one Byte length) for easier lookup in file. Approximately solves problem with moving inside file.
                #// Each Byte has a value according this formula:
                #// (TOC[i] / 256) * fileLenInBytes
                #// So if song lasts eg. 240 sec. and you want to jump to 60. sec. (and file is 5 000 000 Bytes length) you can use:
                #// TOC[(60/240)*100] = TOC[25]
                #// and corresponding Byte in file is then approximately at:
                #// (TOC[25]/256) * 5000000
                #// 116..119  VBR Scale
                #// should be safe to leave this at 'vbr' and let it be overriden to 'cbr' if a CBR preset/mode is used by LAME
                #// if (substr($headerstring, $VBRidOffset, strlen('Info')) == 'Xing') {
                thisfile_mpeg_audio["bitrate_mode"] = "vbr"
                thisfile_mpeg_audio["VBR_method"] = "Xing"
                #// } else {
                #// $ScanAsCBR = true;
                #// $thisfile_mpeg_audio['bitrate_mode'] = 'cbr';
                #// }
                thisfile_mpeg_audio["xing_flags_raw"] = getid3_lib.bigendian2int(php_substr(headerstring, VBRidOffset + 4, 4))
                thisfile_mpeg_audio["xing_flags"]["frames"] = php_bool(thisfile_mpeg_audio["xing_flags_raw"] & 1)
                thisfile_mpeg_audio["xing_flags"]["bytes"] = php_bool(thisfile_mpeg_audio["xing_flags_raw"] & 2)
                thisfile_mpeg_audio["xing_flags"]["toc"] = php_bool(thisfile_mpeg_audio["xing_flags_raw"] & 4)
                thisfile_mpeg_audio["xing_flags"]["vbr_scale"] = php_bool(thisfile_mpeg_audio["xing_flags_raw"] & 8)
                if thisfile_mpeg_audio["xing_flags"]["frames"]:
                    thisfile_mpeg_audio["VBR_frames"] = getid3_lib.bigendian2int(php_substr(headerstring, VBRidOffset + 8, 4))
                    pass
                # end if
                if thisfile_mpeg_audio["xing_flags"]["bytes"]:
                    thisfile_mpeg_audio["VBR_bytes"] = getid3_lib.bigendian2int(php_substr(headerstring, VBRidOffset + 12, 4))
                # end if
                #// if (($thisfile_mpeg_audio['bitrate'] == 'free') && !empty($thisfile_mpeg_audio['VBR_frames']) && !empty($thisfile_mpeg_audio['VBR_bytes'])) {
                #// if (!empty($thisfile_mpeg_audio['VBR_frames']) && !empty($thisfile_mpeg_audio['VBR_bytes'])) {
                if (not php_empty(lambda : thisfile_mpeg_audio["VBR_frames"])):
                    used_filesize = 0
                    if (not php_empty(lambda : thisfile_mpeg_audio["VBR_bytes"])):
                        used_filesize = thisfile_mpeg_audio["VBR_bytes"]
                    elif (not php_empty(lambda : info["filesize"])):
                        used_filesize = info["filesize"]
                        used_filesize -= php_intval(info["id3v2"]["headerlength"]) if (php_isset(lambda : info["id3v2"]["headerlength"])) else 0
                        used_filesize -= 128 if (php_isset(lambda : info["id3v1"])) else 0
                        used_filesize -= info["tag_offset_end"] - info["tag_offset_start"] if (php_isset(lambda : info["tag_offset_end"])) else 0
                        self.warning("MP3.Xing header missing VBR_bytes, assuming MPEG audio portion of file is " + number_format(used_filesize) + " bytes")
                    # end if
                    framelengthfloat = used_filesize / thisfile_mpeg_audio["VBR_frames"]
                    if thisfile_mpeg_audio["layer"] == "1":
                        #// BitRate = (((FrameLengthInBytes / 4) - Padding) * SampleRate) / 12
                        #// $info['audio']['bitrate'] = ((($framelengthfloat / 4) - intval($thisfile_mpeg_audio['padding'])) * $thisfile_mpeg_audio['sample_rate']) / 12;
                        info["audio"]["bitrate"] = framelengthfloat / 4 * thisfile_mpeg_audio["sample_rate"] * 2 / info["audio"]["channels"] / 12
                    else:
                        #// Bitrate = ((FrameLengthInBytes - Padding) * SampleRate) / 144
                        #// $info['audio']['bitrate'] = (($framelengthfloat - intval($thisfile_mpeg_audio['padding'])) * $thisfile_mpeg_audio['sample_rate']) / 144;
                        info["audio"]["bitrate"] = framelengthfloat * thisfile_mpeg_audio["sample_rate"] * 2 / info["audio"]["channels"] / 144
                    # end if
                    thisfile_mpeg_audio["framelength"] = floor(framelengthfloat)
                # end if
                if thisfile_mpeg_audio["xing_flags"]["toc"]:
                    LAMEtocData = php_substr(headerstring, VBRidOffset + 16, 100)
                    i = 0
                    while i < 100:
                        
                        thisfile_mpeg_audio["toc"][i] = php_ord(LAMEtocData[i])
                        i += 1
                    # end while
                # end if
                if thisfile_mpeg_audio["xing_flags"]["vbr_scale"]:
                    thisfile_mpeg_audio["VBR_scale"] = getid3_lib.bigendian2int(php_substr(headerstring, VBRidOffset + 116, 4))
                # end if
                #// http://gabriel.mp3-tech.org/mp3infotag.html
                if php_substr(headerstring, VBRidOffset + 120, 4) == "LAME":
                    #// shortcut
                    thisfile_mpeg_audio["LAME"] = Array()
                    thisfile_mpeg_audio_lame = thisfile_mpeg_audio["LAME"]
                    thisfile_mpeg_audio_lame["long_version"] = php_substr(headerstring, VBRidOffset + 120, 20)
                    thisfile_mpeg_audio_lame["short_version"] = php_substr(thisfile_mpeg_audio_lame["long_version"], 0, 9)
                    if thisfile_mpeg_audio_lame["short_version"] >= "LAME3.90":
                        thisfile_mpeg_audio_lame["long_version"] = None
                        #// It the LAME tag was only introduced in LAME v3.90
                        #// http://www.hydrogenaudio.org/?act=ST&f=15&t=9933
                        #// Offsets of various bytes in http://gabriel.mp3-tech.org/mp3infotag.html
                        #// are assuming a 'Xing' identifier offset of 0x24, which is the case for
                        #// MPEG-1 non-mono, but not for other combinations
                        LAMEtagOffsetContant = VBRidOffset - 36
                        #// shortcuts
                        thisfile_mpeg_audio_lame["RGAD"] = Array({"track": Array(), "album": Array()})
                        thisfile_mpeg_audio_lame_RGAD = thisfile_mpeg_audio_lame["RGAD"]
                        thisfile_mpeg_audio_lame_RGAD_track = thisfile_mpeg_audio_lame_RGAD["track"]
                        thisfile_mpeg_audio_lame_RGAD_album = thisfile_mpeg_audio_lame_RGAD["album"]
                        thisfile_mpeg_audio_lame["raw"] = Array()
                        thisfile_mpeg_audio_lame_raw = thisfile_mpeg_audio_lame["raw"]
                        thisfile_mpeg_audio["VBR_scale"] = None
                        thisfile_mpeg_audio_lame["vbr_quality"] = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 155, 1))
                        #// bytes $9C-$A4  Encoder short VersionString
                        thisfile_mpeg_audio_lame["short_version"] = php_substr(headerstring, LAMEtagOffsetContant + 156, 9)
                        #// byte $A5  Info Tag revision + VBR method
                        LAMEtagRevisionVBRmethod = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 165, 1))
                        thisfile_mpeg_audio_lame["tag_revision"] = LAMEtagRevisionVBRmethod & 240 >> 4
                        thisfile_mpeg_audio_lame_raw["vbr_method"] = LAMEtagRevisionVBRmethod & 15
                        thisfile_mpeg_audio_lame["vbr_method"] = self.lamevbrmethodlookup(thisfile_mpeg_audio_lame_raw["vbr_method"])
                        thisfile_mpeg_audio["bitrate_mode"] = php_substr(thisfile_mpeg_audio_lame["vbr_method"], 0, 3)
                        #// usually either 'cbr' or 'vbr', but truncates 'vbr-old / vbr-rh' to 'vbr'
                        #// byte $A6  Lowpass filter value
                        thisfile_mpeg_audio_lame["lowpass_frequency"] = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 166, 1)) * 100
                        #// bytes $A7-$AE  Replay Gain
                        #// http://privatewww.essex.ac.uk/~djmrob/replaygain/rg_data_format.html
                        #// bytes $A7-$AA : 32 bit floating point "Peak signal amplitude"
                        if thisfile_mpeg_audio_lame["short_version"] >= "LAME3.94b":
                            #// LAME 3.94a16 and later - 9.23 fixed point
                            #// ie 0x0059E2EE / (2^23) = 5890798 / 8388608 = 0.7022378444671630859375
                            thisfile_mpeg_audio_lame_RGAD["peak_amplitude"] = php_float(getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 167, 4)) / 8388608)
                        else:
                            #// LAME 3.94a15 and earlier - 32-bit floating point
                            #// Actually 3.94a16 will fall in here too and be WRONG, but is hard to detect 3.94a16 vs 3.94a15
                            thisfile_mpeg_audio_lame_RGAD["peak_amplitude"] = getid3_lib.littleendian2float(php_substr(headerstring, LAMEtagOffsetContant + 167, 4))
                        # end if
                        if thisfile_mpeg_audio_lame_RGAD["peak_amplitude"] == 0:
                            thisfile_mpeg_audio_lame_RGAD["peak_amplitude"] = None
                        else:
                            thisfile_mpeg_audio_lame_RGAD["peak_db"] = getid3_lib.rgadamplitude2db(thisfile_mpeg_audio_lame_RGAD["peak_amplitude"])
                        # end if
                        thisfile_mpeg_audio_lame_raw["RGAD_track"] = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 171, 2))
                        thisfile_mpeg_audio_lame_raw["RGAD_album"] = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 173, 2))
                        if thisfile_mpeg_audio_lame_raw["RGAD_track"] != 0:
                            thisfile_mpeg_audio_lame_RGAD_track["raw"]["name"] = thisfile_mpeg_audio_lame_raw["RGAD_track"] & 57344 >> 13
                            thisfile_mpeg_audio_lame_RGAD_track["raw"]["originator"] = thisfile_mpeg_audio_lame_raw["RGAD_track"] & 7168 >> 10
                            thisfile_mpeg_audio_lame_RGAD_track["raw"]["sign_bit"] = thisfile_mpeg_audio_lame_raw["RGAD_track"] & 512 >> 9
                            thisfile_mpeg_audio_lame_RGAD_track["raw"]["gain_adjust"] = thisfile_mpeg_audio_lame_raw["RGAD_track"] & 511
                            thisfile_mpeg_audio_lame_RGAD_track["name"] = getid3_lib.rgadnamelookup(thisfile_mpeg_audio_lame_RGAD_track["raw"]["name"])
                            thisfile_mpeg_audio_lame_RGAD_track["originator"] = getid3_lib.rgadoriginatorlookup(thisfile_mpeg_audio_lame_RGAD_track["raw"]["originator"])
                            thisfile_mpeg_audio_lame_RGAD_track["gain_db"] = getid3_lib.rgadadjustmentlookup(thisfile_mpeg_audio_lame_RGAD_track["raw"]["gain_adjust"], thisfile_mpeg_audio_lame_RGAD_track["raw"]["sign_bit"])
                            if (not php_empty(lambda : thisfile_mpeg_audio_lame_RGAD["peak_amplitude"])):
                                info["replay_gain"]["track"]["peak"] = thisfile_mpeg_audio_lame_RGAD["peak_amplitude"]
                            # end if
                            info["replay_gain"]["track"]["originator"] = thisfile_mpeg_audio_lame_RGAD_track["originator"]
                            info["replay_gain"]["track"]["adjustment"] = thisfile_mpeg_audio_lame_RGAD_track["gain_db"]
                        else:
                            thisfile_mpeg_audio_lame_RGAD["track"] = None
                        # end if
                        if thisfile_mpeg_audio_lame_raw["RGAD_album"] != 0:
                            thisfile_mpeg_audio_lame_RGAD_album["raw"]["name"] = thisfile_mpeg_audio_lame_raw["RGAD_album"] & 57344 >> 13
                            thisfile_mpeg_audio_lame_RGAD_album["raw"]["originator"] = thisfile_mpeg_audio_lame_raw["RGAD_album"] & 7168 >> 10
                            thisfile_mpeg_audio_lame_RGAD_album["raw"]["sign_bit"] = thisfile_mpeg_audio_lame_raw["RGAD_album"] & 512 >> 9
                            thisfile_mpeg_audio_lame_RGAD_album["raw"]["gain_adjust"] = thisfile_mpeg_audio_lame_raw["RGAD_album"] & 511
                            thisfile_mpeg_audio_lame_RGAD_album["name"] = getid3_lib.rgadnamelookup(thisfile_mpeg_audio_lame_RGAD_album["raw"]["name"])
                            thisfile_mpeg_audio_lame_RGAD_album["originator"] = getid3_lib.rgadoriginatorlookup(thisfile_mpeg_audio_lame_RGAD_album["raw"]["originator"])
                            thisfile_mpeg_audio_lame_RGAD_album["gain_db"] = getid3_lib.rgadadjustmentlookup(thisfile_mpeg_audio_lame_RGAD_album["raw"]["gain_adjust"], thisfile_mpeg_audio_lame_RGAD_album["raw"]["sign_bit"])
                            if (not php_empty(lambda : thisfile_mpeg_audio_lame_RGAD["peak_amplitude"])):
                                info["replay_gain"]["album"]["peak"] = thisfile_mpeg_audio_lame_RGAD["peak_amplitude"]
                            # end if
                            info["replay_gain"]["album"]["originator"] = thisfile_mpeg_audio_lame_RGAD_album["originator"]
                            info["replay_gain"]["album"]["adjustment"] = thisfile_mpeg_audio_lame_RGAD_album["gain_db"]
                        else:
                            thisfile_mpeg_audio_lame_RGAD["album"] = None
                        # end if
                        if php_empty(lambda : thisfile_mpeg_audio_lame_RGAD):
                            thisfile_mpeg_audio_lame["RGAD"] = None
                        # end if
                        #// byte $AF  Encoding flags + ATH Type
                        EncodingFlagsATHtype = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 175, 1))
                        thisfile_mpeg_audio_lame["encoding_flags"]["nspsytune"] = php_bool(EncodingFlagsATHtype & 16)
                        thisfile_mpeg_audio_lame["encoding_flags"]["nssafejoint"] = php_bool(EncodingFlagsATHtype & 32)
                        thisfile_mpeg_audio_lame["encoding_flags"]["nogap_next"] = php_bool(EncodingFlagsATHtype & 64)
                        thisfile_mpeg_audio_lame["encoding_flags"]["nogap_prev"] = php_bool(EncodingFlagsATHtype & 128)
                        thisfile_mpeg_audio_lame["ath_type"] = EncodingFlagsATHtype & 15
                        #// byte $B0  if ABR {specified bitrate} else {minimal bitrate}
                        thisfile_mpeg_audio_lame["raw"]["abrbitrate_minbitrate"] = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 176, 1))
                        if thisfile_mpeg_audio_lame_raw["vbr_method"] == 2:
                            #// Average BitRate (ABR)
                            thisfile_mpeg_audio_lame["bitrate_abr"] = thisfile_mpeg_audio_lame["raw"]["abrbitrate_minbitrate"]
                        elif thisfile_mpeg_audio_lame_raw["vbr_method"] == 1:
                            pass
                        elif thisfile_mpeg_audio_lame["raw"]["abrbitrate_minbitrate"] > 0:
                            #// Variable BitRate (VBR) - minimum bitrate
                            thisfile_mpeg_audio_lame["bitrate_min"] = thisfile_mpeg_audio_lame["raw"]["abrbitrate_minbitrate"]
                        # end if
                        #// bytes $B1-$B3  Encoder delays
                        EncoderDelays = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 177, 3))
                        thisfile_mpeg_audio_lame["encoder_delay"] = EncoderDelays & 16773120 >> 12
                        thisfile_mpeg_audio_lame["end_padding"] = EncoderDelays & 4095
                        #// byte $B4  Misc
                        MiscByte = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 180, 1))
                        thisfile_mpeg_audio_lame_raw["noise_shaping"] = MiscByte & 3
                        thisfile_mpeg_audio_lame_raw["stereo_mode"] = MiscByte & 28 >> 2
                        thisfile_mpeg_audio_lame_raw["not_optimal_quality"] = MiscByte & 32 >> 5
                        thisfile_mpeg_audio_lame_raw["source_sample_freq"] = MiscByte & 192 >> 6
                        thisfile_mpeg_audio_lame["noise_shaping"] = thisfile_mpeg_audio_lame_raw["noise_shaping"]
                        thisfile_mpeg_audio_lame["stereo_mode"] = self.lamemiscstereomodelookup(thisfile_mpeg_audio_lame_raw["stereo_mode"])
                        thisfile_mpeg_audio_lame["not_optimal_quality"] = php_bool(thisfile_mpeg_audio_lame_raw["not_optimal_quality"])
                        thisfile_mpeg_audio_lame["source_sample_freq"] = self.lamemiscsourcesamplefrequencylookup(thisfile_mpeg_audio_lame_raw["source_sample_freq"])
                        #// byte $B5  MP3 Gain
                        thisfile_mpeg_audio_lame_raw["mp3_gain"] = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 181, 1), False, True)
                        thisfile_mpeg_audio_lame["mp3_gain_db"] = getid3_lib.rgadamplitude2db(2) / 4 * thisfile_mpeg_audio_lame_raw["mp3_gain"]
                        thisfile_mpeg_audio_lame["mp3_gain_factor"] = pow(2, thisfile_mpeg_audio_lame["mp3_gain_db"] / 6)
                        #// bytes $B6-$B7  Preset and surround info
                        PresetSurroundBytes = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 182, 2))
                        #// Reserved                                                    = ($PresetSurroundBytes & 0xC000);
                        thisfile_mpeg_audio_lame_raw["surround_info"] = PresetSurroundBytes & 14336
                        thisfile_mpeg_audio_lame["surround_info"] = self.lamesurroundinfolookup(thisfile_mpeg_audio_lame_raw["surround_info"])
                        thisfile_mpeg_audio_lame["preset_used_id"] = PresetSurroundBytes & 2047
                        thisfile_mpeg_audio_lame["preset_used"] = self.lamepresetusedlookup(thisfile_mpeg_audio_lame)
                        if (not php_empty(lambda : thisfile_mpeg_audio_lame["preset_used_id"])) and php_empty(lambda : thisfile_mpeg_audio_lame["preset_used"]):
                            self.warning("Unknown LAME preset used (" + thisfile_mpeg_audio_lame["preset_used_id"] + ") - please report to info@getid3.org")
                        # end if
                        if thisfile_mpeg_audio_lame["short_version"] == "LAME3.90." and (not php_empty(lambda : thisfile_mpeg_audio_lame["preset_used_id"])):
                            #// this may change if 3.90.4 ever comes out
                            thisfile_mpeg_audio_lame["short_version"] = "LAME3.90.3"
                        # end if
                        #// bytes $B8-$BB  MusicLength
                        thisfile_mpeg_audio_lame["audio_bytes"] = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 184, 4))
                        ExpectedNumberOfAudioBytes = thisfile_mpeg_audio_lame["audio_bytes"] if thisfile_mpeg_audio_lame["audio_bytes"] > 0 else thisfile_mpeg_audio["VBR_bytes"]
                        #// bytes $BC-$BD  MusicCRC
                        thisfile_mpeg_audio_lame["music_crc"] = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 188, 2))
                        #// bytes $BE-$BF  CRC-16 of Info Tag
                        thisfile_mpeg_audio_lame["lame_tag_crc"] = getid3_lib.bigendian2int(php_substr(headerstring, LAMEtagOffsetContant + 190, 2))
                        #// LAME CBR
                        if thisfile_mpeg_audio_lame_raw["vbr_method"] == 1:
                            thisfile_mpeg_audio["bitrate_mode"] = "cbr"
                            thisfile_mpeg_audio["bitrate"] = self.closeststandardmp3bitrate(thisfile_mpeg_audio["bitrate"])
                            info["audio"]["bitrate"] = thisfile_mpeg_audio["bitrate"]
                            pass
                        # end if
                    # end if
                # end if
            else:
                #// not Fraunhofer or Xing VBR methods, most likely CBR (but could be VBR with no header)
                thisfile_mpeg_audio["bitrate_mode"] = "cbr"
                if recursivesearch:
                    thisfile_mpeg_audio["bitrate_mode"] = "vbr"
                    if self.recursiveframescanning(offset, nextframetestoffset, True):
                        recursivesearch = False
                        thisfile_mpeg_audio["bitrate_mode"] = "cbr"
                    # end if
                    if thisfile_mpeg_audio["bitrate_mode"] == "vbr":
                        self.warning("VBR file with no VBR header. Bitrate values calculated from actual frame bitrates.")
                    # end if
                # end if
            # end if
        # end if
        if ExpectedNumberOfAudioBytes > 0 and ExpectedNumberOfAudioBytes != info["avdataend"] - info["avdataoffset"]:
            if ExpectedNumberOfAudioBytes > info["avdataend"] - info["avdataoffset"]:
                if self.isdependencyfor("matroska") or self.isdependencyfor("riff"):
                    pass
                elif ExpectedNumberOfAudioBytes - info["avdataend"] - info["avdataoffset"] == 1:
                    self.warning("Last byte of data truncated (this is a known bug in Meracl ID3 Tag Writer before v1.3.5)")
                else:
                    self.warning("Probable truncated file: expecting " + ExpectedNumberOfAudioBytes + " bytes of audio data, only found " + info["avdataend"] - info["avdataoffset"] + " (short by " + ExpectedNumberOfAudioBytes - info["avdataend"] - info["avdataoffset"] + " bytes)")
                # end if
            else:
                if info["avdataend"] - info["avdataoffset"] - ExpectedNumberOfAudioBytes == 1:
                    #// $prenullbytefileoffset = $this->ftell();
                    #// $this->fseek($info['avdataend']);
                    #// $PossibleNullByte = $this->fread(1);
                    #// $this->fseek($prenullbytefileoffset);
                    #// if ($PossibleNullByte === "\x00") {
                    info["avdataend"] -= 1
                    pass
                else:
                    self.warning("Too much data in file: expecting " + ExpectedNumberOfAudioBytes + " bytes of audio data, found " + info["avdataend"] - info["avdataoffset"] + " (" + info["avdataend"] - info["avdataoffset"] - ExpectedNumberOfAudioBytes + " bytes too many)")
                # end if
            # end if
        # end if
        if thisfile_mpeg_audio["bitrate"] == "free" and php_empty(lambda : info["audio"]["bitrate"]):
            if offset == info["avdataoffset"] and php_empty(lambda : thisfile_mpeg_audio["VBR_frames"]):
                framebytelength = self.freeformatframelength(offset, True)
                if framebytelength > 0:
                    thisfile_mpeg_audio["framelength"] = framebytelength
                    if thisfile_mpeg_audio["layer"] == "1":
                        #// BitRate = (((FrameLengthInBytes / 4) - Padding) * SampleRate) / 12
                        info["audio"]["bitrate"] = framebytelength / 4 - php_intval(thisfile_mpeg_audio["padding"]) * thisfile_mpeg_audio["sample_rate"] / 12
                    else:
                        #// Bitrate = ((FrameLengthInBytes - Padding) * SampleRate) / 144
                        info["audio"]["bitrate"] = framebytelength - php_intval(thisfile_mpeg_audio["padding"]) * thisfile_mpeg_audio["sample_rate"] / 144
                    # end if
                else:
                    self.error("Error calculating frame length of free-format MP3 without Xing/LAME header")
                # end if
            # end if
        # end if
        if thisfile_mpeg_audio["VBR_frames"] if (php_isset(lambda : thisfile_mpeg_audio["VBR_frames"])) else "":
            for case in Switch(thisfile_mpeg_audio["bitrate_mode"]):
                if case("vbr"):
                    pass
                # end if
                if case("abr"):
                    bytes_per_frame = 1152
                    if thisfile_mpeg_audio["version"] == "1" and thisfile_mpeg_audio["layer"] == 1:
                        bytes_per_frame = 384
                    elif thisfile_mpeg_audio["version"] == "2" or thisfile_mpeg_audio["version"] == "2.5" and thisfile_mpeg_audio["layer"] == 3:
                        bytes_per_frame = 576
                    # end if
                    thisfile_mpeg_audio["VBR_bitrate"] = thisfile_mpeg_audio["VBR_bytes"] / thisfile_mpeg_audio["VBR_frames"] * 8 * info["audio"]["sample_rate"] / bytes_per_frame if (php_isset(lambda : thisfile_mpeg_audio["VBR_bytes"])) else 0
                    if thisfile_mpeg_audio["VBR_bitrate"] > 0:
                        info["audio"]["bitrate"] = thisfile_mpeg_audio["VBR_bitrate"]
                        thisfile_mpeg_audio["bitrate"] = thisfile_mpeg_audio["VBR_bitrate"]
                        pass
                    # end if
                    break
                # end if
            # end for
        # end if
        #// End variable-bitrate headers
        #//
        if recursivesearch:
            if (not self.recursiveframescanning(offset, nextframetestoffset, ScanAsCBR)):
                return False
            # end if
        # end if
        #// if (false) {
        #// experimental side info parsing section - not returning anything useful yet
        #// 
        #// $SideInfoBitstream = getid3_lib::BigEndian2Bin($SideInfoData);
        #// $SideInfoOffset = 0;
        #// 
        #// if ($thisfile_mpeg_audio['version'] == '1') {
        #// if ($thisfile_mpeg_audio['channelmode'] == 'mono') {
        #// MPEG-1 (mono)
        #// $thisfile_mpeg_audio['side_info']['main_data_begin'] = substr($SideInfoBitstream, $SideInfoOffset, 9);
        #// $SideInfoOffset += 9;
        #// $SideInfoOffset += 5;
        #// } else {
        #// MPEG-1 (stereo, joint-stereo, dual-channel)
        #// $thisfile_mpeg_audio['side_info']['main_data_begin'] = substr($SideInfoBitstream, $SideInfoOffset, 9);
        #// $SideInfoOffset += 9;
        #// $SideInfoOffset += 3;
        #// }
        #// } else { // 2 or 2.5
        #// if ($thisfile_mpeg_audio['channelmode'] == 'mono') {
        #// MPEG-2, MPEG-2.5 (mono)
        #// $thisfile_mpeg_audio['side_info']['main_data_begin'] = substr($SideInfoBitstream, $SideInfoOffset, 8);
        #// $SideInfoOffset += 8;
        #// $SideInfoOffset += 1;
        #// } else {
        #// MPEG-2, MPEG-2.5 (stereo, joint-stereo, dual-channel)
        #// $thisfile_mpeg_audio['side_info']['main_data_begin'] = substr($SideInfoBitstream, $SideInfoOffset, 8);
        #// $SideInfoOffset += 8;
        #// $SideInfoOffset += 2;
        #// }
        #// }
        #// 
        #// if ($thisfile_mpeg_audio['version'] == '1') {
        #// for ($channel = 0; $channel < $info['audio']['channels']; $channel++) {
        #// for ($scfsi_band = 0; $scfsi_band < 4; $scfsi_band++) {
        #// $thisfile_mpeg_audio['scfsi'][$channel][$scfsi_band] = substr($SideInfoBitstream, $SideInfoOffset, 1);
        #// $SideInfoOffset += 2;
        #// }
        #// }
        #// }
        #// for ($granule = 0; $granule < (($thisfile_mpeg_audio['version'] == '1') ? 2 : 1); $granule++) {
        #// for ($channel = 0; $channel < $info['audio']['channels']; $channel++) {
        #// $thisfile_mpeg_audio['part2_3_length'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 12);
        #// $SideInfoOffset += 12;
        #// $thisfile_mpeg_audio['big_values'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 9);
        #// $SideInfoOffset += 9;
        #// $thisfile_mpeg_audio['global_gain'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 8);
        #// $SideInfoOffset += 8;
        #// if ($thisfile_mpeg_audio['version'] == '1') {
        #// $thisfile_mpeg_audio['scalefac_compress'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 4);
        #// $SideInfoOffset += 4;
        #// } else {
        #// $thisfile_mpeg_audio['scalefac_compress'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 9);
        #// $SideInfoOffset += 9;
        #// }
        #// $thisfile_mpeg_audio['window_switching_flag'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 1);
        #// $SideInfoOffset += 1;
        #// 
        #// if ($thisfile_mpeg_audio['window_switching_flag'][$granule][$channel] == '1') {
        #// 
        #// $thisfile_mpeg_audio['block_type'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 2);
        #// $SideInfoOffset += 2;
        #// $thisfile_mpeg_audio['mixed_block_flag'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 1);
        #// $SideInfoOffset += 1;
        #// 
        #// for ($region = 0; $region < 2; $region++) {
        #// $thisfile_mpeg_audio['table_select'][$granule][$channel][$region] = substr($SideInfoBitstream, $SideInfoOffset, 5);
        #// $SideInfoOffset += 5;
        #// }
        #// $thisfile_mpeg_audio['table_select'][$granule][$channel][2] = 0;
        #// 
        #// for ($window = 0; $window < 3; $window++) {
        #// $thisfile_mpeg_audio['subblock_gain'][$granule][$channel][$window] = substr($SideInfoBitstream, $SideInfoOffset, 3);
        #// $SideInfoOffset += 3;
        #// }
        #// 
        #// } else {
        #// 
        #// for ($region = 0; $region < 3; $region++) {
        #// $thisfile_mpeg_audio['table_select'][$granule][$channel][$region] = substr($SideInfoBitstream, $SideInfoOffset, 5);
        #// $SideInfoOffset += 5;
        #// }
        #// 
        #// $thisfile_mpeg_audio['region0_count'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 4);
        #// $SideInfoOffset += 4;
        #// $thisfile_mpeg_audio['region1_count'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 3);
        #// $SideInfoOffset += 3;
        #// $thisfile_mpeg_audio['block_type'][$granule][$channel] = 0;
        #// }
        #// 
        #// if ($thisfile_mpeg_audio['version'] == '1') {
        #// $thisfile_mpeg_audio['preflag'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 1);
        #// $SideInfoOffset += 1;
        #// }
        #// $thisfile_mpeg_audio['scalefac_scale'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 1);
        #// $SideInfoOffset += 1;
        #// $thisfile_mpeg_audio['count1table_select'][$granule][$channel] = substr($SideInfoBitstream, $SideInfoOffset, 1);
        #// $SideInfoOffset += 1;
        #// }
        #// }
        #// }
        return True
    # end def decodempegaudioheader
    #// 
    #// @param int $offset
    #// @param int $nextframetestoffset
    #// @param bool $ScanAsCBR
    #// 
    #// @return bool
    #//
    def recursiveframescanning(self, offset=None, nextframetestoffset=None, ScanAsCBR=None):
        
        info = self.getid3.info
        firstframetestarray = Array({"error": Array(), "warning": Array(), "avdataend": info["avdataend"], "avdataoffset": info["avdataoffset"]})
        self.decodempegaudioheader(offset, firstframetestarray, False)
        i = 0
        while i < GETID3_MP3_VALID_CHECK_FRAMES:
            
            #// check next GETID3_MP3_VALID_CHECK_FRAMES frames for validity, to make sure we haven't run across a false synch
            if nextframetestoffset + 4 >= info["avdataend"]:
                #// end of file
                return True
            # end if
            nextframetestarray = Array({"error": Array(), "warning": Array(), "avdataend": info["avdataend"], "avdataoffset": info["avdataoffset"]})
            if self.decodempegaudioheader(nextframetestoffset, nextframetestarray, False):
                if ScanAsCBR:
                    #// force CBR mode, used for trying to pick out invalid audio streams with valid(?) VBR headers, or VBR streams with no VBR header
                    if (not (php_isset(lambda : nextframetestarray["mpeg"]["audio"]["bitrate"]))) or (not (php_isset(lambda : firstframetestarray["mpeg"]["audio"]["bitrate"]))) or nextframetestarray["mpeg"]["audio"]["bitrate"] != firstframetestarray["mpeg"]["audio"]["bitrate"]:
                        return False
                    # end if
                # end if
                #// next frame is OK, get ready to check the one after that
                if (php_isset(lambda : nextframetestarray["mpeg"]["audio"]["framelength"])) and nextframetestarray["mpeg"]["audio"]["framelength"] > 0:
                    nextframetestoffset += nextframetestarray["mpeg"]["audio"]["framelength"]
                else:
                    self.error("Frame at offset (" + offset + ") is has an invalid frame length.")
                    return False
                # end if
            elif (not php_empty(lambda : firstframetestarray["mpeg"]["audio"]["framelength"])) and nextframetestoffset + firstframetestarray["mpeg"]["audio"]["framelength"] > info["avdataend"]:
                #// it's not the end of the file, but there's not enough data left for another frame, so assume it's garbage/padding and return OK
                return True
            else:
                #// next frame is not valid, note the error and fail, so scanning can contiue for a valid frame sequence
                self.warning("Frame at offset (" + offset + ") is valid, but the next one at (" + nextframetestoffset + ") is not.")
                return False
            # end if
            i += 1
        # end while
        return True
    # end def recursiveframescanning
    #// 
    #// @param int  $offset
    #// @param bool $deepscan
    #// 
    #// @return int|false
    #//
    def freeformatframelength(self, offset=None, deepscan=False):
        
        info = self.getid3.info
        self.fseek(offset)
        MPEGaudioData = self.fread(32768)
        SyncPattern1 = php_substr(MPEGaudioData, 0, 4)
        #// may be different pattern due to padding
        SyncPattern2 = SyncPattern1[0] + SyncPattern1[1] + chr(php_ord(SyncPattern1[2]) | 2) + SyncPattern1[3]
        if SyncPattern2 == SyncPattern1:
            SyncPattern2 = SyncPattern1[0] + SyncPattern1[1] + chr(php_ord(SyncPattern1[2]) & 253) + SyncPattern1[3]
        # end if
        framelength = False
        framelength1 = php_strpos(MPEGaudioData, SyncPattern1, 4)
        framelength2 = php_strpos(MPEGaudioData, SyncPattern2, 4)
        if framelength1 > 4:
            framelength = framelength1
        # end if
        if framelength2 > 4 and framelength2 < framelength1:
            framelength = framelength2
        # end if
        if (not framelength):
            #// LAME 3.88 has a different value for modeextension on the first frame vs the rest
            framelength1 = php_strpos(MPEGaudioData, php_substr(SyncPattern1, 0, 3), 4)
            framelength2 = php_strpos(MPEGaudioData, php_substr(SyncPattern2, 0, 3), 4)
            if framelength1 > 4:
                framelength = framelength1
            # end if
            if framelength2 > 4 and framelength2 < framelength1:
                framelength = framelength2
            # end if
            if (not framelength):
                self.error("Cannot find next free-format synch pattern (" + getid3_lib.printhexbytes(SyncPattern1) + " or " + getid3_lib.printhexbytes(SyncPattern2) + ") after offset " + offset)
                return False
            else:
                self.warning("ModeExtension varies between first frame and other frames (known free-format issue in LAME 3.88)")
                info["audio"]["codec"] = "LAME"
                info["audio"]["encoder"] = "LAME3.88"
                SyncPattern1 = php_substr(SyncPattern1, 0, 3)
                SyncPattern2 = php_substr(SyncPattern2, 0, 3)
            # end if
        # end if
        if deepscan:
            ActualFrameLengthValues = Array()
            nextoffset = offset + framelength
            while True:
                
                if not (nextoffset < info["avdataend"] - 6):
                    break
                # end if
                self.fseek(nextoffset - 1)
                NextSyncPattern = self.fread(6)
                if php_substr(NextSyncPattern, 1, php_strlen(SyncPattern1)) == SyncPattern1 or php_substr(NextSyncPattern, 1, php_strlen(SyncPattern2)) == SyncPattern2:
                    #// good - found where expected
                    ActualFrameLengthValues[-1] = framelength
                elif php_substr(NextSyncPattern, 0, php_strlen(SyncPattern1)) == SyncPattern1 or php_substr(NextSyncPattern, 0, php_strlen(SyncPattern2)) == SyncPattern2:
                    #// ok - found one byte earlier than expected (last frame wasn't padded, first frame was)
                    ActualFrameLengthValues[-1] = framelength - 1
                    nextoffset -= 1
                elif php_substr(NextSyncPattern, 2, php_strlen(SyncPattern1)) == SyncPattern1 or php_substr(NextSyncPattern, 2, php_strlen(SyncPattern2)) == SyncPattern2:
                    #// ok - found one byte later than expected (last frame was padded, first frame wasn't)
                    ActualFrameLengthValues[-1] = framelength + 1
                    nextoffset += 1
                else:
                    self.error("Did not find expected free-format sync pattern at offset " + nextoffset)
                    return False
                # end if
                nextoffset += framelength
            # end while
            if php_count(ActualFrameLengthValues) > 0:
                framelength = php_intval(round(array_sum(ActualFrameLengthValues) / php_count(ActualFrameLengthValues)))
            # end if
        # end if
        return framelength
    # end def freeformatframelength
    #// 
    #// @return bool
    #//
    def getonlympegaudioinfobruteforce(self):
        
        MPEGaudioHeaderDecodeCache = Array()
        MPEGaudioHeaderValidCache = Array()
        MPEGaudioHeaderLengthCache = Array()
        MPEGaudioVersionLookup = self.mpegaudioversionarray()
        MPEGaudioLayerLookup = self.mpegaudiolayerarray()
        MPEGaudioBitrateLookup = self.mpegaudiobitratearray()
        MPEGaudioFrequencyLookup = self.mpegaudiofrequencyarray()
        MPEGaudioChannelModeLookup = self.mpegaudiochannelmodearray()
        MPEGaudioModeExtensionLookup = self.mpegaudiomodeextensionarray()
        MPEGaudioEmphasisLookup = self.mpegaudioemphasisarray()
        LongMPEGversionLookup = Array()
        LongMPEGlayerLookup = Array()
        LongMPEGbitrateLookup = Array()
        LongMPEGpaddingLookup = Array()
        LongMPEGfrequencyLookup = Array()
        Distribution["bitrate"] = Array()
        Distribution["frequency"] = Array()
        Distribution["layer"] = Array()
        Distribution["version"] = Array()
        Distribution["padding"] = Array()
        info = self.getid3.info
        self.fseek(info["avdataoffset"])
        max_frames_scan = 5000
        frames_scanned = 0
        previousvalidframe = info["avdataoffset"]
        while True:
            
            if not (self.ftell() < info["avdataend"]):
                break
            # end if
            set_time_limit(30)
            head4 = self.fread(4)
            if php_strlen(head4) < 4:
                break
            # end if
            if head4[0] != "ÿ":
                i = 1
                while i < 4:
                    
                    if head4[i] == "ÿ":
                        self.fseek(i - 4, SEEK_CUR)
                        continue
                    # end if
                    i += 1
                # end while
                continue
            # end if
            if (not (php_isset(lambda : MPEGaudioHeaderDecodeCache[head4]))):
                MPEGaudioHeaderDecodeCache[head4] = self.mpegaudioheaderdecode(head4)
            # end if
            if (not (php_isset(lambda : MPEGaudioHeaderValidCache[head4]))):
                MPEGaudioHeaderValidCache[head4] = self.mpegaudioheadervalid(MPEGaudioHeaderDecodeCache[head4], False, False)
            # end if
            if MPEGaudioHeaderValidCache[head4]:
                if (not (php_isset(lambda : MPEGaudioHeaderLengthCache[head4]))):
                    LongMPEGversionLookup[head4] = MPEGaudioVersionLookup[MPEGaudioHeaderDecodeCache[head4]["version"]]
                    LongMPEGlayerLookup[head4] = MPEGaudioLayerLookup[MPEGaudioHeaderDecodeCache[head4]["layer"]]
                    LongMPEGbitrateLookup[head4] = MPEGaudioBitrateLookup[LongMPEGversionLookup[head4]][LongMPEGlayerLookup[head4]][MPEGaudioHeaderDecodeCache[head4]["bitrate"]]
                    LongMPEGpaddingLookup[head4] = php_bool(MPEGaudioHeaderDecodeCache[head4]["padding"])
                    LongMPEGfrequencyLookup[head4] = MPEGaudioFrequencyLookup[LongMPEGversionLookup[head4]][MPEGaudioHeaderDecodeCache[head4]["sample_rate"]]
                    MPEGaudioHeaderLengthCache[head4] = self.mpegaudioframelength(LongMPEGbitrateLookup[head4], LongMPEGversionLookup[head4], LongMPEGlayerLookup[head4], LongMPEGpaddingLookup[head4], LongMPEGfrequencyLookup[head4])
                # end if
                if MPEGaudioHeaderLengthCache[head4] > 4:
                    WhereWeWere = self.ftell()
                    self.fseek(MPEGaudioHeaderLengthCache[head4] - 4, SEEK_CUR)
                    next4 = self.fread(4)
                    if next4[0] == "ÿ":
                        if (not (php_isset(lambda : MPEGaudioHeaderDecodeCache[next4]))):
                            MPEGaudioHeaderDecodeCache[next4] = self.mpegaudioheaderdecode(next4)
                        # end if
                        if (not (php_isset(lambda : MPEGaudioHeaderValidCache[next4]))):
                            MPEGaudioHeaderValidCache[next4] = self.mpegaudioheadervalid(MPEGaudioHeaderDecodeCache[next4], False, False)
                        # end if
                        if MPEGaudioHeaderValidCache[next4]:
                            self.fseek(-4, SEEK_CUR)
                            getid3_lib.safe_inc(Distribution["bitrate"][LongMPEGbitrateLookup[head4]])
                            getid3_lib.safe_inc(Distribution["layer"][LongMPEGlayerLookup[head4]])
                            getid3_lib.safe_inc(Distribution["version"][LongMPEGversionLookup[head4]])
                            getid3_lib.safe_inc(Distribution["padding"][php_intval(LongMPEGpaddingLookup[head4])])
                            getid3_lib.safe_inc(Distribution["frequency"][LongMPEGfrequencyLookup[head4]])
                            frames_scanned += 1
                            if max_frames_scan and frames_scanned >= max_frames_scan:
                                pct_data_scanned = self.ftell() - info["avdataoffset"] / info["avdataend"] - info["avdataoffset"]
                                self.warning("too many MPEG audio frames to scan, only scanned first " + max_frames_scan + " frames (" + number_format(pct_data_scanned * 100, 1) + "% of file) and extrapolated distribution, playtime and bitrate may be incorrect.")
                                for key1,value1 in Distribution:
                                    for key2,value2 in value1:
                                        Distribution[key1][key2] = round(value2 / pct_data_scanned)
                                    # end for
                                # end for
                                break
                            # end if
                            continue
                        # end if
                    # end if
                    next4 = None
                    self.fseek(WhereWeWere - 3)
                # end if
            # end if
        # end while
        for key,value in Distribution:
            ksort(Distribution[key], SORT_NUMERIC)
        # end for
        ksort(Distribution["version"], SORT_STRING)
        info["mpeg"]["audio"]["bitrate_distribution"] = Distribution["bitrate"]
        info["mpeg"]["audio"]["frequency_distribution"] = Distribution["frequency"]
        info["mpeg"]["audio"]["layer_distribution"] = Distribution["layer"]
        info["mpeg"]["audio"]["version_distribution"] = Distribution["version"]
        info["mpeg"]["audio"]["padding_distribution"] = Distribution["padding"]
        if php_count(Distribution["version"]) > 1:
            self.error("Corrupt file - more than one MPEG version detected")
        # end if
        if php_count(Distribution["layer"]) > 1:
            self.error("Corrupt file - more than one MPEG layer detected")
        # end if
        if php_count(Distribution["frequency"]) > 1:
            self.error("Corrupt file - more than one MPEG sample rate detected")
        # end if
        bittotal = 0
        for bitratevalue,bitratecount in Distribution["bitrate"]:
            if bitratevalue != "free":
                bittotal += bitratevalue * bitratecount
            # end if
        # end for
        info["mpeg"]["audio"]["frame_count"] = array_sum(Distribution["bitrate"])
        if info["mpeg"]["audio"]["frame_count"] == 0:
            self.error("no MPEG audio frames found")
            return False
        # end if
        info["mpeg"]["audio"]["bitrate"] = bittotal / info["mpeg"]["audio"]["frame_count"]
        info["mpeg"]["audio"]["bitrate_mode"] = "vbr" if php_count(Distribution["bitrate"]) > 0 else "cbr"
        info["mpeg"]["audio"]["sample_rate"] = getid3_lib.array_max(Distribution["frequency"], True)
        info["audio"]["bitrate"] = info["mpeg"]["audio"]["bitrate"]
        info["audio"]["bitrate_mode"] = info["mpeg"]["audio"]["bitrate_mode"]
        info["audio"]["sample_rate"] = info["mpeg"]["audio"]["sample_rate"]
        info["audio"]["dataformat"] = "mp" + getid3_lib.array_max(Distribution["layer"], True)
        info["fileformat"] = info["audio"]["dataformat"]
        return True
    # end def getonlympegaudioinfobruteforce
    #// 
    #// @param int  $avdataoffset
    #// @param bool $BitrateHistogram
    #// 
    #// @return bool
    #//
    def getonlympegaudioinfo(self, avdataoffset=None, BitrateHistogram=False):
        
        #// looks for synch, decodes MPEG audio header
        info = self.getid3.info
        MPEGaudioVersionLookup = None
        MPEGaudioLayerLookup = None
        MPEGaudioBitrateLookup = None
        if php_empty(lambda : MPEGaudioVersionLookup):
            MPEGaudioVersionLookup = self.mpegaudioversionarray()
            MPEGaudioLayerLookup = self.mpegaudiolayerarray()
            MPEGaudioBitrateLookup = self.mpegaudiobitratearray()
        # end if
        self.fseek(avdataoffset)
        sync_seek_buffer_size = php_min(128 * 1024, info["avdataend"] - avdataoffset)
        if sync_seek_buffer_size <= 0:
            self.error("Invalid $sync_seek_buffer_size at offset " + avdataoffset)
            return False
        # end if
        header = self.fread(sync_seek_buffer_size)
        sync_seek_buffer_size = php_strlen(header)
        SynchSeekOffset = 0
        while True:
            
            if not (SynchSeekOffset < sync_seek_buffer_size):
                break
            # end if
            if avdataoffset + SynchSeekOffset < info["avdataend"] and (not php_feof(self.getid3.fp)):
                if SynchSeekOffset > sync_seek_buffer_size:
                    #// if a synch's not found within the first 128k bytes, then give up
                    self.error("Could not find valid MPEG audio synch within the first " + round(sync_seek_buffer_size / 1024) + "kB")
                    if (php_isset(lambda : info["audio"]["bitrate"])):
                        info["audio"]["bitrate"] = None
                    # end if
                    if (php_isset(lambda : info["mpeg"]["audio"])):
                        info["mpeg"]["audio"] = None
                    # end if
                    if php_empty(lambda : info["mpeg"]):
                        info["mpeg"] = None
                    # end if
                    return False
                elif php_feof(self.getid3.fp):
                    self.error("Could not find valid MPEG audio synch before end of file")
                    if (php_isset(lambda : info["audio"]["bitrate"])):
                        info["audio"]["bitrate"] = None
                    # end if
                    if (php_isset(lambda : info["mpeg"]["audio"])):
                        info["mpeg"]["audio"] = None
                    # end if
                    if (php_isset(lambda : info["mpeg"])) and (not php_is_array(info["mpeg"])) or php_count(info["mpeg"]) == 0:
                        info["mpeg"] = None
                    # end if
                    return False
                # end if
            # end if
            if SynchSeekOffset + 1 >= php_strlen(header):
                self.error("Could not find valid MPEG synch before end of file")
                return False
            # end if
            if header[SynchSeekOffset] == "ÿ" and header[SynchSeekOffset + 1] > "à":
                #// synch detected
                FirstFrameAVDataOffset = None
                if (not (php_isset(lambda : FirstFrameThisfileInfo))) and (not (php_isset(lambda : info["mpeg"]["audio"]))):
                    FirstFrameThisfileInfo = info
                    FirstFrameAVDataOffset = avdataoffset + SynchSeekOffset
                    if (not self.decodempegaudioheader(FirstFrameAVDataOffset, FirstFrameThisfileInfo, False)):
                        FirstFrameThisfileInfo = None
                    # end if
                # end if
                dummy = info
                #// only overwrite real data if valid header found
                if self.decodempegaudioheader(avdataoffset + SynchSeekOffset, dummy, True):
                    info = dummy
                    info["avdataoffset"] = avdataoffset + SynchSeekOffset
                    for case in Switch(info["fileformat"] if (php_isset(lambda : info["fileformat"])) else ""):
                        if case(""):
                            pass
                        # end if
                        if case("id3"):
                            pass
                        # end if
                        if case("ape"):
                            pass
                        # end if
                        if case("mp3"):
                            info["fileformat"] = "mp3"
                            info["audio"]["dataformat"] = "mp3"
                            break
                        # end if
                    # end for
                    if (php_isset(lambda : FirstFrameThisfileInfo)) and (php_isset(lambda : FirstFrameThisfileInfo["mpeg"]["audio"]["bitrate_mode"])) and FirstFrameThisfileInfo["mpeg"]["audio"]["bitrate_mode"] == "vbr":
                        if (not abs(info["audio"]["bitrate"] - FirstFrameThisfileInfo["audio"]["bitrate"]) <= 1):
                            #// If there is garbage data between a valid VBR header frame and a sequence
                            #// of valid MPEG-audio frames the VBR data is no longer discarded.
                            info = FirstFrameThisfileInfo
                            info["avdataoffset"] = FirstFrameAVDataOffset
                            info["fileformat"] = "mp3"
                            info["audio"]["dataformat"] = "mp3"
                            dummy = info
                            dummy["mpeg"]["audio"] = None
                            GarbageOffsetStart = FirstFrameAVDataOffset + FirstFrameThisfileInfo["mpeg"]["audio"]["framelength"]
                            GarbageOffsetEnd = avdataoffset + SynchSeekOffset
                            if self.decodempegaudioheader(GarbageOffsetEnd, dummy, True, True):
                                info = dummy
                                info["avdataoffset"] = GarbageOffsetEnd
                                self.warning("apparently-valid VBR header not used because could not find " + GETID3_MP3_VALID_CHECK_FRAMES + " consecutive MPEG-audio frames immediately after VBR header (garbage data for " + GarbageOffsetEnd - GarbageOffsetStart + " bytes between " + GarbageOffsetStart + " and " + GarbageOffsetEnd + "), but did find valid CBR stream starting at " + GarbageOffsetEnd)
                            else:
                                self.warning("using data from VBR header even though could not find " + GETID3_MP3_VALID_CHECK_FRAMES + " consecutive MPEG-audio frames immediately after VBR header (garbage data for " + GarbageOffsetEnd - GarbageOffsetStart + " bytes between " + GarbageOffsetStart + " and " + GarbageOffsetEnd + ")")
                            # end if
                        # end if
                    # end if
                    if (php_isset(lambda : info["mpeg"]["audio"]["bitrate_mode"])) and info["mpeg"]["audio"]["bitrate_mode"] == "vbr" and (not (php_isset(lambda : info["mpeg"]["audio"]["VBR_method"]))):
                        #// VBR file with no VBR header
                        BitrateHistogram = True
                    # end if
                    if BitrateHistogram:
                        info["mpeg"]["audio"]["stereo_distribution"] = Array({"stereo": 0, "joint stereo": 0, "dual channel": 0, "mono": 0})
                        info["mpeg"]["audio"]["version_distribution"] = Array({"1": 0, "2": 0, "2.5": 0})
                        if info["mpeg"]["audio"]["version"] == "1":
                            if info["mpeg"]["audio"]["layer"] == 3:
                                info["mpeg"]["audio"]["bitrate_distribution"] = Array({"free": 0, 32000: 0, 40000: 0, 48000: 0, 56000: 0, 64000: 0, 80000: 0, 96000: 0, 112000: 0, 128000: 0, 160000: 0, 192000: 0, 224000: 0, 256000: 0, 320000: 0})
                            elif info["mpeg"]["audio"]["layer"] == 2:
                                info["mpeg"]["audio"]["bitrate_distribution"] = Array({"free": 0, 32000: 0, 48000: 0, 56000: 0, 64000: 0, 80000: 0, 96000: 0, 112000: 0, 128000: 0, 160000: 0, 192000: 0, 224000: 0, 256000: 0, 320000: 0, 384000: 0})
                            elif info["mpeg"]["audio"]["layer"] == 1:
                                info["mpeg"]["audio"]["bitrate_distribution"] = Array({"free": 0, 32000: 0, 64000: 0, 96000: 0, 128000: 0, 160000: 0, 192000: 0, 224000: 0, 256000: 0, 288000: 0, 320000: 0, 352000: 0, 384000: 0, 416000: 0, 448000: 0})
                            # end if
                        elif info["mpeg"]["audio"]["layer"] == 1:
                            info["mpeg"]["audio"]["bitrate_distribution"] = Array({"free": 0, 32000: 0, 48000: 0, 56000: 0, 64000: 0, 80000: 0, 96000: 0, 112000: 0, 128000: 0, 144000: 0, 160000: 0, 176000: 0, 192000: 0, 224000: 0, 256000: 0})
                        else:
                            info["mpeg"]["audio"]["bitrate_distribution"] = Array({"free": 0, 8000: 0, 16000: 0, 24000: 0, 32000: 0, 40000: 0, 48000: 0, 56000: 0, 64000: 0, 80000: 0, 96000: 0, 112000: 0, 128000: 0, 144000: 0, 160000: 0})
                        # end if
                        dummy = Array({"error": info["error"], "warning": info["warning"], "avdataend": info["avdataend"], "avdataoffset": info["avdataoffset"]})
                        synchstartoffset = info["avdataoffset"]
                        self.fseek(info["avdataoffset"])
                        #// you can play with these numbers:
                        max_frames_scan = 50000
                        max_scan_segments = 10
                        #// don't play with these numbers:
                        FastMode = False
                        SynchErrorsFound = 0
                        frames_scanned = 0
                        this_scan_segment = 0
                        frames_scan_per_segment = ceil(max_frames_scan / max_scan_segments)
                        pct_data_scanned = 0
                        current_segment = 0
                        while current_segment < max_scan_segments:
                            
                            frames_scanned_this_segment = 0
                            if self.ftell() >= info["avdataend"]:
                                break
                            # end if
                            scan_start_offset[current_segment] = php_max(self.ftell(), info["avdataoffset"] + round(current_segment * info["avdataend"] - info["avdataoffset"] / max_scan_segments))
                            if current_segment > 0:
                                self.fseek(scan_start_offset[current_segment])
                                buffer_4k = self.fread(4096)
                                j = 0
                                while j < php_strlen(buffer_4k) - 4:
                                    
                                    if buffer_4k[j] == "ÿ" and buffer_4k[j + 1] > "à":
                                        #// synch detected
                                        if self.decodempegaudioheader(scan_start_offset[current_segment] + j, dummy, False, False, FastMode):
                                            calculated_next_offset = scan_start_offset[current_segment] + j + dummy["mpeg"]["audio"]["framelength"]
                                            if self.decodempegaudioheader(calculated_next_offset, dummy, False, False, FastMode):
                                                scan_start_offset[current_segment] += j
                                                break
                                            # end if
                                        # end if
                                    # end if
                                    j += 1
                                # end while
                            # end if
                            synchstartoffset = scan_start_offset[current_segment]
                            while True:
                                
                                if not (synchstartoffset < info["avdataend"] and self.decodempegaudioheader(synchstartoffset, dummy, False, False, FastMode)):
                                    break
                                # end if
                                FastMode = True
                                thisframebitrate = MPEGaudioBitrateLookup[MPEGaudioVersionLookup[dummy["mpeg"]["audio"]["raw"]["version"]]][MPEGaudioLayerLookup[dummy["mpeg"]["audio"]["raw"]["layer"]]][dummy["mpeg"]["audio"]["raw"]["bitrate"]]
                                if php_empty(lambda : dummy["mpeg"]["audio"]["framelength"]):
                                    SynchErrorsFound += 1
                                    synchstartoffset += 1
                                else:
                                    getid3_lib.safe_inc(info["mpeg"]["audio"]["bitrate_distribution"][thisframebitrate])
                                    getid3_lib.safe_inc(info["mpeg"]["audio"]["stereo_distribution"][dummy["mpeg"]["audio"]["channelmode"]])
                                    getid3_lib.safe_inc(info["mpeg"]["audio"]["version_distribution"][dummy["mpeg"]["audio"]["version"]])
                                    synchstartoffset += dummy["mpeg"]["audio"]["framelength"]
                                # end if
                                frames_scanned += 1
                                frames_scanned_this_segment += 1
                                if frames_scan_per_segment and frames_scanned_this_segment >= frames_scan_per_segment:
                                    this_pct_scanned = self.ftell() - scan_start_offset[current_segment] / info["avdataend"] - info["avdataoffset"]
                                    if current_segment == 0 and this_pct_scanned * max_scan_segments >= 1:
                                        #// file likely contains < $max_frames_scan, just scan as one segment
                                        max_scan_segments = 1
                                        frames_scan_per_segment = max_frames_scan
                                    else:
                                        pct_data_scanned += this_pct_scanned
                                        break
                                    # end if
                                # end if
                            # end while
                            current_segment += 1
                        # end while
                        if pct_data_scanned > 0:
                            self.warning("too many MPEG audio frames to scan, only scanned " + frames_scanned + " frames in " + max_scan_segments + " segments (" + number_format(pct_data_scanned * 100, 1) + "% of file) and extrapolated distribution, playtime and bitrate may be incorrect.")
                            for key1,value1 in info["mpeg"]["audio"]:
                                if (not php_preg_match("#_distribution$#i", key1)):
                                    continue
                                # end if
                                for key2,value2 in value1:
                                    info["mpeg"]["audio"][key1][key2] = round(value2 / pct_data_scanned)
                                # end for
                            # end for
                        # end if
                        if SynchErrorsFound > 0:
                            self.warning("Found " + SynchErrorsFound + " synch errors in histogram analysis")
                            pass
                        # end if
                        bittotal = 0
                        framecounter = 0
                        for bitratevalue,bitratecount in info["mpeg"]["audio"]["bitrate_distribution"]:
                            framecounter += bitratecount
                            if bitratevalue != "free":
                                bittotal += bitratevalue * bitratecount
                            # end if
                        # end for
                        if framecounter == 0:
                            self.error("Corrupt MP3 file: framecounter == zero")
                            return False
                        # end if
                        info["mpeg"]["audio"]["frame_count"] = getid3_lib.castasint(framecounter)
                        info["mpeg"]["audio"]["bitrate"] = bittotal / framecounter
                        info["audio"]["bitrate"] = info["mpeg"]["audio"]["bitrate"]
                        #// Definitively set VBR vs CBR, even if the Xing/LAME/VBRI header says differently
                        distinct_bitrates = 0
                        for bitrate_value,bitrate_count in info["mpeg"]["audio"]["bitrate_distribution"]:
                            if bitrate_count > 0:
                                distinct_bitrates += 1
                            # end if
                        # end for
                        if distinct_bitrates > 1:
                            info["mpeg"]["audio"]["bitrate_mode"] = "vbr"
                        else:
                            info["mpeg"]["audio"]["bitrate_mode"] = "cbr"
                        # end if
                        info["audio"]["bitrate_mode"] = info["mpeg"]["audio"]["bitrate_mode"]
                    # end if
                    break
                    pass
                # end if
            # end if
            SynchSeekOffset += 1
            if avdataoffset + SynchSeekOffset >= info["avdataend"]:
                #// end of file/data
                if php_empty(lambda : info["mpeg"]["audio"]):
                    self.error("could not find valid MPEG synch before end of file")
                    if (php_isset(lambda : info["audio"]["bitrate"])):
                        info["audio"]["bitrate"] = None
                    # end if
                    if (php_isset(lambda : info["mpeg"]["audio"])):
                        info["mpeg"]["audio"] = None
                    # end if
                    if (php_isset(lambda : info["mpeg"])) and (not php_is_array(info["mpeg"])) or php_empty(lambda : info["mpeg"]):
                        info["mpeg"] = None
                    # end if
                    return False
                # end if
                break
            # end if
        # end while
        info["audio"]["channels"] = info["mpeg"]["audio"]["channels"]
        info["audio"]["channelmode"] = info["mpeg"]["audio"]["channelmode"]
        info["audio"]["sample_rate"] = info["mpeg"]["audio"]["sample_rate"]
        return True
    # end def getonlympegaudioinfo
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudioversionarray(self):
        
        MPEGaudioVersion = Array("2.5", False, "2", "1")
        return MPEGaudioVersion
    # end def mpegaudioversionarray
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudiolayerarray(self):
        
        MPEGaudioLayer = Array(False, 3, 2, 1)
        return MPEGaudioLayer
    # end def mpegaudiolayerarray
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudiobitratearray(self):
        
        MPEGaudioBitrate = None
        if php_empty(lambda : MPEGaudioBitrate):
            MPEGaudioBitrate = Array({"1": Array({1: Array("free", 32000, 64000, 96000, 128000, 160000, 192000, 224000, 256000, 288000, 320000, 352000, 384000, 416000, 448000), 2: Array("free", 32000, 48000, 56000, 64000, 80000, 96000, 112000, 128000, 160000, 192000, 224000, 256000, 320000, 384000), 3: Array("free", 32000, 40000, 48000, 56000, 64000, 80000, 96000, 112000, 128000, 160000, 192000, 224000, 256000, 320000)})}, {"2": Array({1: Array("free", 32000, 48000, 56000, 64000, 80000, 96000, 112000, 128000, 144000, 160000, 176000, 192000, 224000, 256000), 2: Array("free", 8000, 16000, 24000, 32000, 40000, 48000, 56000, 64000, 80000, 96000, 112000, 128000, 144000, 160000)})})
            MPEGaudioBitrate["2"][3] = MPEGaudioBitrate["2"][2]
            MPEGaudioBitrate["2.5"] = MPEGaudioBitrate["2"]
        # end if
        return MPEGaudioBitrate
    # end def mpegaudiobitratearray
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudiofrequencyarray(self):
        
        MPEGaudioFrequency = None
        if php_empty(lambda : MPEGaudioFrequency):
            MPEGaudioFrequency = Array({"1": Array(44100, 48000, 32000), "2": Array(22050, 24000, 16000), "2.5": Array(11025, 12000, 8000)})
        # end if
        return MPEGaudioFrequency
    # end def mpegaudiofrequencyarray
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudiochannelmodearray(self):
        
        MPEGaudioChannelMode = Array("stereo", "joint stereo", "dual channel", "mono")
        return MPEGaudioChannelMode
    # end def mpegaudiochannelmodearray
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudiomodeextensionarray(self):
        
        MPEGaudioModeExtension = None
        if php_empty(lambda : MPEGaudioModeExtension):
            MPEGaudioModeExtension = Array({1: Array("4-31", "8-31", "12-31", "16-31"), 2: Array("4-31", "8-31", "12-31", "16-31"), 3: Array("", "IS", "MS", "IS+MS")})
        # end if
        return MPEGaudioModeExtension
    # end def mpegaudiomodeextensionarray
    #// 
    #// @return array
    #//
    @classmethod
    def mpegaudioemphasisarray(self):
        
        MPEGaudioEmphasis = Array("none", "50/15ms", False, "CCIT J.17")
        return MPEGaudioEmphasis
    # end def mpegaudioemphasisarray
    #// 
    #// @param string $head4
    #// @param bool   $allowBitrate15
    #// 
    #// @return bool
    #//
    @classmethod
    def mpegaudioheaderbytesvalid(self, head4=None, allowBitrate15=False):
        
        return self.mpegaudioheadervalid(self.mpegaudioheaderdecode(head4), False, allowBitrate15)
    # end def mpegaudioheaderbytesvalid
    #// 
    #// @param array $rawarray
    #// @param bool  $echoerrors
    #// @param bool  $allowBitrate15
    #// 
    #// @return bool
    #//
    @classmethod
    def mpegaudioheadervalid(self, rawarray=None, echoerrors=False, allowBitrate15=False):
        
        if rawarray["synch"] & 4094 != 4094:
            return False
        # end if
        MPEGaudioVersionLookup = None
        MPEGaudioLayerLookup = None
        MPEGaudioBitrateLookup = None
        MPEGaudioFrequencyLookup = None
        MPEGaudioChannelModeLookup = None
        MPEGaudioModeExtensionLookup = None
        MPEGaudioEmphasisLookup = None
        if php_empty(lambda : MPEGaudioVersionLookup):
            MPEGaudioVersionLookup = self.mpegaudioversionarray()
            MPEGaudioLayerLookup = self.mpegaudiolayerarray()
            MPEGaudioBitrateLookup = self.mpegaudiobitratearray()
            MPEGaudioFrequencyLookup = self.mpegaudiofrequencyarray()
            MPEGaudioChannelModeLookup = self.mpegaudiochannelmodearray()
            MPEGaudioModeExtensionLookup = self.mpegaudiomodeextensionarray()
            MPEGaudioEmphasisLookup = self.mpegaudioemphasisarray()
        # end if
        if (php_isset(lambda : MPEGaudioVersionLookup[rawarray["version"]])):
            decodedVersion = MPEGaudioVersionLookup[rawarray["version"]]
        else:
            php_print("\n" + "invalid Version (" + rawarray["version"] + ")" if echoerrors else "")
            return False
        # end if
        if (php_isset(lambda : MPEGaudioLayerLookup[rawarray["layer"]])):
            decodedLayer = MPEGaudioLayerLookup[rawarray["layer"]]
        else:
            php_print("\n" + "invalid Layer (" + rawarray["layer"] + ")" if echoerrors else "")
            return False
        # end if
        if (not (php_isset(lambda : MPEGaudioBitrateLookup[decodedVersion][decodedLayer][rawarray["bitrate"]]))):
            php_print("\n" + "invalid Bitrate (" + rawarray["bitrate"] + ")" if echoerrors else "")
            if rawarray["bitrate"] == 15:
                #// known issue in LAME 3.90 - 3.93.1 where free-format has bitrate ID of 15 instead of 0
                #// let it go through here otherwise file will not be identified
                if (not allowBitrate15):
                    return False
                # end if
            else:
                return False
            # end if
        # end if
        if (not (php_isset(lambda : MPEGaudioFrequencyLookup[decodedVersion][rawarray["sample_rate"]]))):
            php_print("\n" + "invalid Frequency (" + rawarray["sample_rate"] + ")" if echoerrors else "")
            return False
        # end if
        if (not (php_isset(lambda : MPEGaudioChannelModeLookup[rawarray["channelmode"]]))):
            php_print("\n" + "invalid ChannelMode (" + rawarray["channelmode"] + ")" if echoerrors else "")
            return False
        # end if
        if (not (php_isset(lambda : MPEGaudioModeExtensionLookup[decodedLayer][rawarray["modeextension"]]))):
            php_print("\n" + "invalid Mode Extension (" + rawarray["modeextension"] + ")" if echoerrors else "")
            return False
        # end if
        if (not (php_isset(lambda : MPEGaudioEmphasisLookup[rawarray["emphasis"]]))):
            php_print("\n" + "invalid Emphasis (" + rawarray["emphasis"] + ")" if echoerrors else "")
            return False
        # end if
        #// These are just either set or not set, you can't mess that up :)
        #// $rawarray['protection'];
        #// $rawarray['padding'];
        #// $rawarray['private'];
        #// $rawarray['copyright'];
        #// $rawarray['original'];
        return True
    # end def mpegaudioheadervalid
    #// 
    #// @param string $Header4Bytes
    #// 
    #// @return array|false
    #//
    @classmethod
    def mpegaudioheaderdecode(self, Header4Bytes=None):
        
        #// AAAA AAAA  AAAB BCCD  EEEE FFGH  IIJJ KLMM
        #// A - Frame sync (all bits set)
        #// B - MPEG Audio version ID
        #// C - Layer description
        #// D - Protection bit
        #// E - Bitrate index
        #// F - Sampling rate frequency index
        #// G - Padding bit
        #// H - Private bit
        #// I - Channel Mode
        #// J - Mode extension (Only if Joint stereo)
        #// K - Copyright
        #// L - Original
        #// M - Emphasis
        if php_strlen(Header4Bytes) != 4:
            return False
        # end if
        MPEGrawHeader["synch"] = getid3_lib.bigendian2int(php_substr(Header4Bytes, 0, 2)) & 65504 >> 4
        MPEGrawHeader["version"] = php_ord(Header4Bytes[1]) & 24 >> 3
        #// BB
        MPEGrawHeader["layer"] = php_ord(Header4Bytes[1]) & 6 >> 1
        #// CC
        MPEGrawHeader["protection"] = php_ord(Header4Bytes[1]) & 1
        #// D
        MPEGrawHeader["bitrate"] = php_ord(Header4Bytes[2]) & 240 >> 4
        #// EEEE
        MPEGrawHeader["sample_rate"] = php_ord(Header4Bytes[2]) & 12 >> 2
        #// FF
        MPEGrawHeader["padding"] = php_ord(Header4Bytes[2]) & 2 >> 1
        #// G
        MPEGrawHeader["private"] = php_ord(Header4Bytes[2]) & 1
        #// H
        MPEGrawHeader["channelmode"] = php_ord(Header4Bytes[3]) & 192 >> 6
        #// II
        MPEGrawHeader["modeextension"] = php_ord(Header4Bytes[3]) & 48 >> 4
        #// JJ
        MPEGrawHeader["copyright"] = php_ord(Header4Bytes[3]) & 8 >> 3
        #// K
        MPEGrawHeader["original"] = php_ord(Header4Bytes[3]) & 4 >> 2
        #// L
        MPEGrawHeader["emphasis"] = php_ord(Header4Bytes[3]) & 3
        #// MM
        return MPEGrawHeader
    # end def mpegaudioheaderdecode
    #// 
    #// @param int|string $bitrate
    #// @param string     $version
    #// @param string     $layer
    #// @param bool       $padding
    #// @param int        $samplerate
    #// 
    #// @return int|false
    #//
    @classmethod
    def mpegaudioframelength(self, bitrate=None, version=None, layer=None, padding=None, samplerate=None):
        
        AudioFrameLengthCache = Array()
        if (not (php_isset(lambda : AudioFrameLengthCache[bitrate][version][layer][padding][samplerate]))):
            AudioFrameLengthCache[bitrate][version][layer][padding][samplerate] = False
            if bitrate != "free":
                if version == "1":
                    if layer == "1":
                        #// For Layer I slot is 32 bits long
                        FrameLengthCoefficient = 48
                        SlotLength = 4
                    else:
                        #// Layer 2 / 3
                        #// for Layer 2 and Layer 3 slot is 8 bits long.
                        FrameLengthCoefficient = 144
                        SlotLength = 1
                    # end if
                else:
                    #// MPEG-2 / MPEG-2.5
                    if layer == "1":
                        #// For Layer I slot is 32 bits long
                        FrameLengthCoefficient = 24
                        SlotLength = 4
                    elif layer == "2":
                        #// for Layer 2 and Layer 3 slot is 8 bits long.
                        FrameLengthCoefficient = 144
                        SlotLength = 1
                    else:
                        #// layer 3
                        #// for Layer 2 and Layer 3 slot is 8 bits long.
                        FrameLengthCoefficient = 72
                        SlotLength = 1
                    # end if
                # end if
                #// FrameLengthInBytes = ((Coefficient * BitRate) / SampleRate) + Padding
                if samplerate > 0:
                    NewFramelength = FrameLengthCoefficient * bitrate / samplerate
                    NewFramelength = floor(NewFramelength / SlotLength) * SlotLength
                    #// round to next-lower multiple of SlotLength (1 byte for Layer 2/3, 4 bytes for Layer I)
                    if padding:
                        NewFramelength += SlotLength
                    # end if
                    AudioFrameLengthCache[bitrate][version][layer][padding][samplerate] = php_int(NewFramelength)
                # end if
            # end if
        # end if
        return AudioFrameLengthCache[bitrate][version][layer][padding][samplerate]
    # end def mpegaudioframelength
    #// 
    #// @param float|int $bit_rate
    #// 
    #// @return int|float|string
    #//
    @classmethod
    def closeststandardmp3bitrate(self, bit_rate=None):
        
        standard_bit_rates = Array(320000, 256000, 224000, 192000, 160000, 128000, 112000, 96000, 80000, 64000, 56000, 48000, 40000, 32000, 24000, 16000, 8000)
        bit_rate_table = Array({0: "-"})
        round_bit_rate = php_intval(round(bit_rate, -3))
        if (not (php_isset(lambda : bit_rate_table[round_bit_rate]))):
            if round_bit_rate > php_max(standard_bit_rates):
                bit_rate_table[round_bit_rate] = round(bit_rate, 2 - php_strlen(bit_rate))
            else:
                bit_rate_table[round_bit_rate] = php_max(standard_bit_rates)
                for standard_bit_rate in standard_bit_rates:
                    if round_bit_rate >= standard_bit_rate + bit_rate_table[round_bit_rate] - standard_bit_rate / 2:
                        break
                    # end if
                    bit_rate_table[round_bit_rate] = standard_bit_rate
                # end for
            # end if
        # end if
        return bit_rate_table[round_bit_rate]
    # end def closeststandardmp3bitrate
    #// 
    #// @param string $version
    #// @param string $channelmode
    #// 
    #// @return int
    #//
    @classmethod
    def xingvbridoffset(self, version=None, channelmode=None):
        
        XingVBRidOffsetCache = Array()
        if php_empty(lambda : XingVBRidOffsetCache):
            XingVBRidOffsetCache = Array({"1": Array({"mono": 21, "stereo": 36, "joint stereo": 36, "dual channel": 36})}, {"2": Array({"mono": 13, "stereo": 21, "joint stereo": 21, "dual channel": 21})}, {"2.5": Array({"mono": 21, "stereo": 21, "joint stereo": 21, "dual channel": 21})})
        # end if
        return XingVBRidOffsetCache[version][channelmode]
    # end def xingvbridoffset
    #// 
    #// @param int $VBRmethodID
    #// 
    #// @return string
    #//
    @classmethod
    def lamevbrmethodlookup(self, VBRmethodID=None):
        
        LAMEvbrMethodLookup = Array({0: "unknown", 1: "cbr", 2: "abr", 3: "vbr-old / vbr-rh", 4: "vbr-new / vbr-mtrh", 5: "vbr-mt", 6: "vbr (full vbr method 4)", 8: "cbr (constant bitrate 2 pass)", 9: "abr (2 pass)", 15: "reserved"})
        return LAMEvbrMethodLookup[VBRmethodID] if (php_isset(lambda : LAMEvbrMethodLookup[VBRmethodID])) else ""
    # end def lamevbrmethodlookup
    #// 
    #// @param int $StereoModeID
    #// 
    #// @return string
    #//
    @classmethod
    def lamemiscstereomodelookup(self, StereoModeID=None):
        
        LAMEmiscStereoModeLookup = Array({0: "mono", 1: "stereo", 2: "dual mono", 3: "joint stereo", 4: "forced stereo", 5: "auto", 6: "intensity stereo", 7: "other"})
        return LAMEmiscStereoModeLookup[StereoModeID] if (php_isset(lambda : LAMEmiscStereoModeLookup[StereoModeID])) else ""
    # end def lamemiscstereomodelookup
    #// 
    #// @param int $SourceSampleFrequencyID
    #// 
    #// @return string
    #//
    @classmethod
    def lamemiscsourcesamplefrequencylookup(self, SourceSampleFrequencyID=None):
        
        LAMEmiscSourceSampleFrequencyLookup = Array({0: "<= 32 kHz", 1: "44.1 kHz", 2: "48 kHz", 3: "> 48kHz"})
        return LAMEmiscSourceSampleFrequencyLookup[SourceSampleFrequencyID] if (php_isset(lambda : LAMEmiscSourceSampleFrequencyLookup[SourceSampleFrequencyID])) else ""
    # end def lamemiscsourcesamplefrequencylookup
    #// 
    #// @param int $SurroundInfoID
    #// 
    #// @return string
    #//
    @classmethod
    def lamesurroundinfolookup(self, SurroundInfoID=None):
        
        LAMEsurroundInfoLookup = Array({0: "no surround info", 1: "DPL encoding", 2: "DPL2 encoding", 3: "Ambisonic encoding"})
        return LAMEsurroundInfoLookup[SurroundInfoID] if (php_isset(lambda : LAMEsurroundInfoLookup[SurroundInfoID])) else "reserved"
    # end def lamesurroundinfolookup
    #// 
    #// @param array $LAMEtag
    #// 
    #// @return string
    #//
    @classmethod
    def lamepresetusedlookup(self, LAMEtag=None):
        
        if LAMEtag["preset_used_id"] == 0:
            #// no preset used (LAME >=3.93)
            #// no preset recorded (LAME <3.93)
            return ""
        # end if
        LAMEpresetUsedLookup = Array()
        #// THIS PART CANNOT BE STATIC .
        i = 8
        while i <= 320:
            
            for case in Switch(LAMEtag["vbr_method"]):
                if case("cbr"):
                    LAMEpresetUsedLookup[i] = "--alt-preset " + LAMEtag["vbr_method"] + " " + i
                    break
                # end if
                if case("abr"):
                    pass
                # end if
                if case():
                    #// other VBR modes shouldn't be here(?)
                    LAMEpresetUsedLookup[i] = "--alt-preset " + i
                    break
                # end if
            # end for
            i += 1
        # end while
        #// named old-style presets (studio, phone, voice, etc) are handled in GuessEncoderOptions()
        #// named alt-presets
        LAMEpresetUsedLookup[1000] = "--r3mix"
        LAMEpresetUsedLookup[1001] = "--alt-preset standard"
        LAMEpresetUsedLookup[1002] = "--alt-preset extreme"
        LAMEpresetUsedLookup[1003] = "--alt-preset insane"
        LAMEpresetUsedLookup[1004] = "--alt-preset fast standard"
        LAMEpresetUsedLookup[1005] = "--alt-preset fast extreme"
        LAMEpresetUsedLookup[1006] = "--alt-preset medium"
        LAMEpresetUsedLookup[1007] = "--alt-preset fast medium"
        #// LAME 3.94 additions/changes
        LAMEpresetUsedLookup[1010] = "--preset portable"
        #// 3.94a15 Oct 21 2003
        LAMEpresetUsedLookup[1015] = "--preset radio"
        #// 3.94a15 Oct 21 2003
        LAMEpresetUsedLookup[320] = "--preset insane"
        #// 3.94a15 Nov 12 2003
        LAMEpresetUsedLookup[410] = "-V9"
        LAMEpresetUsedLookup[420] = "-V8"
        LAMEpresetUsedLookup[440] = "-V6"
        LAMEpresetUsedLookup[430] = "--preset radio"
        #// 3.94a15 Nov 12 2003
        LAMEpresetUsedLookup[450] = "--preset " + "fast " if LAMEtag["raw"]["vbr_method"] == 4 else "" + "portable"
        #// 3.94a15 Nov 12 2003
        LAMEpresetUsedLookup[460] = "--preset " + "fast " if LAMEtag["raw"]["vbr_method"] == 4 else "" + "medium"
        #// 3.94a15 Nov 12 2003
        LAMEpresetUsedLookup[470] = "--r3mix"
        #// 3.94b1  Dec 18 2003
        LAMEpresetUsedLookup[480] = "--preset " + "fast " if LAMEtag["raw"]["vbr_method"] == 4 else "" + "standard"
        #// 3.94a15 Nov 12 2003
        LAMEpresetUsedLookup[490] = "-V1"
        LAMEpresetUsedLookup[500] = "--preset " + "fast " if LAMEtag["raw"]["vbr_method"] == 4 else "" + "extreme"
        #// 3.94a15 Nov 12 2003
        return LAMEpresetUsedLookup[LAMEtag["preset_used_id"]] if (php_isset(lambda : LAMEpresetUsedLookup[LAMEtag["preset_used_id"]])) else "new/unknown preset: " + LAMEtag["preset_used_id"] + " - report to info@getid3.org"
    # end def lamepresetusedlookup
# end class getid3_mp3
