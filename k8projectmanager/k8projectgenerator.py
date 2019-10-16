#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace as ParserObject
from configparser import ConfigParser, NoOptionError, NoSectionError
from glob import glob
from locale import getdefaultlocale
from pprint import pprint
from time import sleep

from kubernetes.client.rest import ApiException

from k8projectmanager.k8pm_module.k8projectmanager_module import K8pgModule
from k8projectmanager.k8pm_sub_methoden.sub_methodes import Color, ErrorHandling, SubMethodes

# vorgegebene Sprache falls die System Sprache nicht existirt
alter_language = "de"


def start():
    """Consolen Start Methode"""
    project = K8ProjectGenerator()
    project.run_projects()


class ConfigObject(ConfigParser):
    def __init__(self, project_name, k8_option_to_section, verbose=False):
        super().__init__()
        self.project_name = project_name
        self.verbose = verbose
        self.config_status = True
        self.activ_modul = ""
        self.k8_option_to_section = k8_option_to_section

    def get_object(self, selector, key, pre=None, integer=False, booled=False, noconfig=False, modul=None):
        """get() mit Überprüfung"""
        active_modul = modul or self.activ_modul
        key = SubMethodes.get_index_str(key, text2=pre)
        try:
            if integer:
                value = self.getint(selector, key)
            elif booled:
                value = self.getboolean(selector, key)
            else:
                value = self.get(selector, key)
        except (NoSectionError, NoOptionError, ValueError) as e:
            self.config_status = ErrorHandling.print_error("%s (Project %s)" % (e, self.project_name), verbose=self.verbose)
            if noconfig or self.verbose:
                self.format_print()
            return None
        rawkey = ""
        for index in key:
            if not index.isdigit():
                rawkey = rawkey + index
        if not ErrorHandling.check_parameter(value, self.k8_option_to_section[active_modul][rawkey][2]) or value is None:
            ErrorHandling.print_error("Parameter Fail: Parameter: %s / required: %s" % (value, self.k8_option_to_section[active_modul][rawkey][2]))
            return None
        return value

    def set_sections_from_sections_iteral(self, from_section, to_section, index=0, iteral=True):
        """Erstellt Sections abhängig von der existens anderer Sections"""
        if not self.has_section(SubMethodes.get_index_str(to_section, index)) and self.has_section(SubMethodes.get_index_str(from_section, index)):
            self.add_section(SubMethodes.get_index_str(to_section, index))
        index = index + 1
        if (self.has_section(SubMethodes.get_index_str(from_section, index)) or self.has_section(SubMethodes.get_index_str(to_section, index))) and iteral:
            self.set_sections_from_sections_iteral(from_section, to_section, index, iteral)

    def copy_option_to_option(self, from_section, to_section, from_option, to_option=None, index=0, from_pre=None, to_pre=None, add=False, change=False, iteral=True):
        """Kopiert Options von einer Section zu einer anderen (Section Iteral)"""
        to_option = to_option or from_option
        if not self.has_option(to_section, SubMethodes.get_index_str(to_option, index, to_pre)) or change:
            if self.has_option(from_section, SubMethodes.get_index_str(from_option, index, from_pre)):
                if not self.has_section(to_section):
                    self.add_section(to_section)
                value = self.get(from_section, SubMethodes.get_index_str(from_option, index, from_pre))
                if add:
                    if from_section == to_section:
                        value = "%s-%s" % (value, to_option)
                    else:
                        value = "%s-%s" % (value, to_section)
                self.set(to_section, SubMethodes.get_index_str(to_option, index, to_pre), value)
        index = index + 1
        if self.has_option(to_section, SubMethodes.get_index_str(to_option, index, to_pre)) or self.has_option(from_section, SubMethodes.get_index_str(from_option, index, from_pre)) and iteral:
            self.copy_option_to_option(from_section, to_section, from_option, to_option, index, from_pre, to_pre, add, change)

    def copy_option_to_option_in_section(self, section, from_option, to_option=None, index=0, from_pre=None, to_pre=None, add=False, change=False, iteral=True):
        """Kopiert Options inerhalb einer Section"""
        return self.copy_option_to_option(section, section, from_option, to_option, index, from_pre, to_pre, add, change, iteral)

    def copy_option_in_section_to_option(self, from_section, to_section, from_option, to_option=None, index=0, from_pre=None, to_pre=None, add=False, change=False, iteral=True):
        """Kopiert Options von einer Section zu einer anderen (Options Iteral)"""
        to_option = to_option or from_option
        to_pre = to_pre or from_pre
        if not self.has_option(to_section, SubMethodes.get_index_str(to_option, index, to_pre)) or change:
            if self.has_option(SubMethodes.get_index_str(from_section, index), SubMethodes.get_index_str(from_option, text2=from_pre)):
                if not self.has_section(to_section):
                    self.add_section(to_section)
                value = self.get(SubMethodes.get_index_str(from_section, index), SubMethodes.get_index_str(from_option, text2=from_pre))
                if add:
                    value = "%s-%s" % (value, to_section)
                self.set(to_section, SubMethodes.get_index_str(to_option, index, to_pre), value)
        index = index + 1
        if (self.has_option(to_section, SubMethodes.get_index_str(to_option, index, to_pre)) or self.has_option(SubMethodes.get_index_str(from_section, index), SubMethodes.get_index_str(from_option, text2=from_pre))) and iteral:
            self.copy_option_in_section_to_option(from_section, to_section, from_option, to_option, index, from_pre, to_pre, add, change, iteral)

    def set_section_from_option(self, from_section, to_section, from_option, index=0, from_pre=None, iteral=True):
        """Erstelt Sections abhängig von der existens eines Option in einer anderen Section"""
        if not self.has_section(SubMethodes.get_index_str(to_section, index)):
            if self.has_option(from_section, SubMethodes.get_index_str(from_option, index, from_pre)):
                self.add_section(SubMethodes.get_index_str(to_section, index))
        index = index + 1
        if (self.has_section(SubMethodes.get_index_str(to_section, index)) or self.has_option(from_section, SubMethodes.get_index_str(from_option, index, from_pre))) and iteral:
            self.set_section_from_option(from_section, to_section, from_option, index, from_pre, iteral)

    def config_iteral(self, section, option=None, pre=None, no=None):
        """Gibt eine Liste aller existirenden Sections oder Options aus die den Suchparameter entspricht"""
        pre = pre or ""
        no = no or " "
        iteral_list = []
        if option is None:
            for config_section in self.sections():
                if config_section.startswith(section) and config_section.endswith(pre) and config_section.find(no) == -1:
                    iteral_list.append(config_section)
        else:
            if self.has_section(section):
                for config_option in self.options(section):
                    if config_option.startswith(option) and config_option.endswith(pre) and config_option.find(no) == -1:
                        iteral_list.append(config_option)
        return iteral_list

    def format_print(self):
        """Gibt das momentane Config Object formatirt aus"""
        text = " START Config "
        print(text.center(60, "-"))
        for section in self.sections():
            print("[%s]" % section)
            for option in self.options(section):
                print("\t%s: %s" % (option, self.get(section, option)))
        text = " END Config "
        print(text.center(60, "-"))


class K8ProjectGenerator(K8pgModule):
    def __init__(self):
        self.k8pg_option_to_section = {}
        super().__init__()
        self.language = SubMethodes.language(getdefaultlocale()[0].split("_")[0], alter_language)
        self.k8_object = {}
        self.arg = ParserObject()
        self.parser()

    def parser(self):
        """Parameter Liste"""
        parser = ArgumentParser(prog="k8projectgenerator.py", description=self.language["par01"])
        parser.add_argument("-o", "--getconfigfile", action="store_true", help=self.language["par02"])
        parser.add_argument("-f", "--configfile", metavar="<File>", help=self.language["par03"])
        parser.add_argument("-r", "--run", action="store_true", help=self.language["par04"])
        parser.add_argument("-v", "--verbose", action="store_true", help=self.language["par05"])
        parser.add_argument("-p", "--printconfig", action="store_true", help=self.language["par06"])
        parser.parse_args(namespace=self.arg)

    def run_projects(self):
        """Start Methode der Classe"""
        if self.arg.printconfig:
            self.print_config()
        if self.arg.configfile:
            # Handling wenn eine Config Datei angegeben wird
            if self.arg.configfile.endswith(".conf"):
                project_name = self.arg.configfile.split("/")[-1][:-5]
            else:
                project_name = self.arg.configfile.split("/")[-1]
            self.set_project(self.arg.configfile, project_name)
            if self.arg.run:
                self.generate_project()
            else:
                self.get_object()
            if self.arg.getconfigfile:
                fh = open("%s_out.config" % self.config.project_name, "w")
                self.config.write(fh)
                fh.close()
        else:
            for config_file in glob("*.conf"):
                # Handling wenn der K8ProjectGenerater in einen Verzeichnis mit Config Dateien ausgefürt wird
                self.config = None
                self.k8_object = {}
                if not self.arg.run:
                    print(Color.color_text(" %s " % config_file, Color.BOLD, 70, "-"))
                project_name = config_file[:-5]
                self.set_project(config_file, project_name)
                if self.arg.run:
                    self.generate_project()
                else:
                    self.get_object()
                    print(Color.color_text(" END %s " % config_file, Color.BOLD, 70, "-"))
                if self.arg.getconfigfile:
                    fh = open("%s_out.config" % self.config.project_name, "w")
                    self.config.write(fh)
                    fh.close()
        if not self.k8_activ:
            # Handling wenn Kubernetes nicht in System gefunden wird
            print(Color.color_text(" Warrning ", Color.PURPLE, long=70, fill="!"))
            ErrorHandling.print_error(self.language["main02"], bold=True, verbose=self.arg.verbose)
            print(Color.color_text(" Warrning ", Color.PURPLE, long=70, fill="!"))

    def set_project(self, file, project_name):
        """Erstelle die Kubernetes Body und K8PojectGenerator Objecte"""
        self.config = ConfigObject(project_name, self.k8pg_option_to_section, self.arg.verbose)
        self.config.read(file)
        for k8pg_modul in self.k8_modul_interal:
            self.k8_object[k8pg_modul] = self.k8_modul[k8pg_modul]["k8pg_methode"]()

    def generate_project(self):
        """Erstele die Kubernetes Objecte in Kubernetes"""
        if not self.config.config_status:
            # Handling wenn ein Congig Fehler gefunden wurde
            print(Color.color_text(" FAIL ", Color.BLINK, long=70, fill="!"))
            ErrorHandling.print_error(self.language["main01"], bold=True, verbose=self.config.verbose)
            print(Color.color_text(" FAIL ", Color.BLINK, long=70, fill="!"))
            return

        if self.k8_activ:
            for k8pg_modul in self.k8_modul_interal:
                if self.k8_object[k8pg_modul] is not None:
                    if type(self.k8_object[k8pg_modul]) is list:
                        for body in self.k8_object[k8pg_modul]:
                            self.make_object(k8pg_modul, body)
                    else:
                        self.make_object(k8pg_modul, self.k8_object[k8pg_modul])

    def make_object(self, k8pg_name, body):
        """Sub Methode zu generate_project für die einzelnen Kubernetes Objecte"""
        patch = False
        body_dict = body.to_dict()
        try:
            if k8pg_name in self.k8_modul_no_namespace:
                api_response = self.k8_modul[k8pg_name]["k8_methode"](body=body, pretty="true")
            else:
                api_response = self.k8_modul[k8pg_name]["k8_methode"](namespace=self.config.get_object("namespace", "name"), body=body, pretty="true")
            print("%s Opject: %s (Type: %s)" % (Color.color_text(" CREATE ", color=Color.BOLD, long=20, fill="-"), body_dict["metadata"]["name"], k8pg_name))
            pprint(api_response)
            sleep(1)
        except ApiException as e:
            error_body = eval(e.body)
            if not ErrorHandling.print_K8Exection(self.config, error_body, self.language["main03"], k8pg_name):
                patch = True
        if patch:
            try:
                if k8pg_name in self.k8_modul_no_namespace:
                    api_response = self.k8_patch[k8pg_name]["k8_methode"](name=body_dict["metadata"]["name"], body=body, pretty="true")
                else:
                    api_response = self.k8_patch[k8pg_name]["k8_methode"](name=body_dict["metadata"]["name"], namespace=self.config.get_object("namespace", "name"), body=body, pretty="true")
                print("%s Opject: %s (Type: %s)" % (Color.color_text(" UPDATE ", color=Color.BOLD, long=20, fill="-"), body_dict["metadata"]["name"], k8pg_name))
                pprint(api_response)
                sleep(1)
            except ApiException as e:
                error_body = eval(e.body)
                ErrorHandling.print_K8Exection(self.config, error_body, self.language["main04"], k8pg_name)

    def get_object(self):
        """Gebe die erstelten Kubernetes body Objecte und K8PojectManager Objecte aus"""
        if self.config.verbose or not self.config.config_status:
            # Gibt eine Warnung und die Config Datei mit aus abhängig von Verbose Parameter und ob ein Config Fehler festgestelt worden ist
            if not self.config.config_status:
                print(Color.color_text(" FAIL ", Color.BLINK, long=70, fill="!"))
            self.config.format_print()
        if not self.config.config_status:
            print(Color.color_text(" FAIL ", Color.BLINK, long=70, fill="!"))

        if self.config.config_status:
            # Gibt die Kubernetes Body Objecte nur aus wenn kein Config Fehler festgestelt wurde
            print(Color.color_text(" Project: %s " % self.config.project_name, long=70, fill="*"))
            for k8pg_modul in self.k8_modul_interal:
                if self.k8_object[k8pg_modul] is not None:
                    if type(self.k8_object[k8pg_modul]) is list:
                        if len(self.k8_object[k8pg_modul]) > 1:
                            index = 0
                            for body in self.k8_object[k8pg_modul]:
                                index = index + 1
                                print(Color.color_text(" %s%i " % (k8pg_modul, index), long=60, fill="#"))
                                print(type(body))
                                ErrorHandling.pprint_to_dic(body)
                        else:
                            print(Color.color_text(" %s " % k8pg_modul, long=60, fill="#"))
                            print(type(self.k8_object[k8pg_modul][0]))
                            ErrorHandling.pprint_to_dic(self.k8_object[k8pg_modul][0])
                    else:
                        print(Color.color_text(" %s " % k8pg_modul, long=60, fill="#"))
                        print(type(self.k8_object[k8pg_modul]))
                        ErrorHandling.pprint_to_dic(self.k8_object[k8pg_modul])

    def print_config(self):
        """Gibt die möglichen Config Sectoren mit ihren Optionen und deren Specifikationen aus"""
        sections_key = []
        for modul in self.k8_modul_interal:
            if modul in self.k8pg_option_to_section.keys():
                if modul in self.k8_modul_with_submodul.keys():
                    submodule = [] + self.k8_modul_with_submodul[modul]
                    for submodul in submodule:
                        if submodul not in sections_key:
                            sections_key.append(submodul)
                else:
                    sections_key.append(modul)
        for section in sections_key:
            texts = ""
            if self.k8pg_option_to_section[section]["__section__"][0]:
                texts = " (%s)" % self.language["cfg02"]
            if section == "pot":
                texts = "\n[%s]%s" % ("container", texts)
            else:
                texts = "\n[%s]%s" % (section, texts)
            print(texts)
            options = {}
            options.update(self.k8pg_option_to_section[section])
            del options["__section__"]
            options_keys = sorted(options.keys())
            texth = "".ljust(20, " ")
            texth1 = " %s " % self.language["cfg01"]
            texth2 = " %s " % self.language["cfg02"]
            texth3 = " %s " % self.language["cfg03"]
            print("%s%s%s%s" % (texth, texth1, texth2, texth3))
            for option in options_keys:
                text = option.ljust(20, " ")
                text1 = " ".center(len(texth1))
                text2 = " ".center(len(texth2))
                if options[option][0]:
                    text1 = "x".center(len(texth1))
                if options[option][1]:
                    text2 = "x".center(len(texth2))
                text3 = options[option][2]
                text3 = text3.replace("Text", "%s" % self.language["cfg04"])
                text3 = text3.replace("Zahlen", "%s" % self.language["cfg06"])
                text3 = text3.replace("Zahl", "%s" % self.language["cfg05"])
                text3 = text3.replace("Path", "%s" % self.language["cfg07"])
                text3 = text3.replace("_List", " %s" % self.language["cfg08"])
                text3 = text3.replace(".", " %s " % self.language["cfg09"])
                text3 = text3.replace("@", " %s" % self.language["cfg10"])
                print("%s%s%s  %s" % (text, text1, text2, text3))
        print()
        print(self.language["cfg11"])
        exit(0)


if __name__ == '__main__':
    start()
