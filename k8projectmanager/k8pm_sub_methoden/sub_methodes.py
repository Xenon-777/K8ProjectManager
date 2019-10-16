#

from configparser import ConfigParser

from k8projectmanager.k8pm_sub_methoden.sub_language import lang_text
from k8projectmanager.k8pm_sub_methoden.sub_color import Color
from k8projectmanager.k8pm_sub_methoden.sub_error import ErrorHandling


class SubMethodes(object):
    @staticmethod
    def get_index_str(text1, index=0, text2=None):
        text2 = text2 or ""
        if index == 0:
            output = "%s%s" % (text1, text2)
        else:
            output = "%s%i%s" % (text1, index, text2)
        return output

    @staticmethod
    def language(lang, alter_lang, configfile=None):
        configfile = configfile or "language.cfg"
        out_lang = {}
        lang_config = ConfigParser()
        lang_config.read_string(lang_text)
        lang_config.read(configfile)
        if not lang_config.has_section(lang):
            lang_config.add_section(lang)
        for option in lang_config.options(alter_lang):
            if lang_config.has_option(lang, option):
                out_lang[option] = lang_config.get(lang, option)
            else:
                out_lang[option] = lang_config.get(alter_lang, option)
        return out_lang
