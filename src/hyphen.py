# -*- coding: utf-8

from __future__ import print_function
from __future__ import unicode_literals

from ctypes import cdll, c_char_p, c_int, POINTER, byref
from os.path import exists

def hyphenate(langcode):
    libhyphen = cdll.LoadLibrary(b"libhyphen.so.0")
    langcode = langcode.replace("-", "_")
    dicpath = b"/usr/share/hyphen/hyph_{0}.dic".format(langcode)
    out = []
    if exists(dicpath):
        dic = libhyphen.hnj_hyphen_load(dicpath)
    else:
        dicpath2 = b"/usr/share/hyphen/hyph_{0}_{1}.dic".format(langcode.lower(), langcode.upper())
        if exists(dicpath2):
            dic = libhyphen.hnj_hyphen_load(dicpath)
        else:
            raise IOError(b"couldn't find dictionaries {0} or {1}". format(dicpath, dicpath2))
    
    null_ptr_int = byref(POINTER(c_int)())
    null_prt_char = byref(POINTER(c_char_p)())
    uni = True
    try:
        while True:
            word = (yield out)
            len_word = len(word)
            hyphen =  c_char_p(b"x" * (len_word + 5))
            if type(word) is unicode:
                uni = True
                encoded_word = word.encode("utf-8")
            else:
                uni = False
                encoded_word = word
            libhyphen.hnj_hyphen_hyphenate2(dic, c_char_p(encoded_word), len(word),
                hyphen, None, null_prt_char, null_ptr_int, null_ptr_int)
            val = bytearray(hyphen.value)
            len_val = len(val)
            l = [i + 1 for chr, i in zip(val, range(len_val)) if chr % 2 != 0]
            out = [encoded_word[x:y] for x, y in zip([0] + l, l + [len_val + 1])]
            if uni:
                out = [unicode(w, "utf-8") for w in out]

    except GeneratorExit:
        pass
    finally:
        try:
            libhyphen.hnj_hyphen_free(dic)
        except AttributeError:
            pass
