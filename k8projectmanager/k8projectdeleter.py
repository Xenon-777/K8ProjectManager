#

from argparse import ArgumentParser
from pprint import pprint
from time import sleep

from kubernetes.client.rest import ApiException

from k8projectmanager.k8projectgenerator import K8ProjectGenerator
from k8projectmanager.k8pm_sub_methoden.sub_methodes import Color, ErrorHandling

alter_language = "de"


def start():
    """Consolen Start Methode"""
    deleter = K8ProjectDeleter()
    deleter.delete_project()


class K8ProjectDeleter(K8ProjectGenerator):
    def __init__(self):
        super().__init__()

    def parser(self):
        """Parameter Liste"""
        parser = ArgumentParser(prog="k8projectgenerator.py", description=self.language["par01"])
        parser.add_argument("configfile", metavar="File", help=self.language["par03"])
        parser.add_argument("-o", "--getconfigfile", action="store_true", help=self.language["par02"])
        parser.add_argument("-d", "--delete", action="store_true", help=self.language["par07"])
        parser.add_argument("-D", "--deleteall", action="store_true", help=self.language["par08"])
        parser.add_argument("-v", "--verbose", action="store_true", help=self.language["par05"])
        parser.add_argument("-p", "--printconfig", action="store_true", help=self.language["par06"])
        parser.parse_args(namespace=self.arg)

    def delete_project(self):
        """Start Methode der Classe"""
        if self.arg.printconfig:
            self.print_config()
        if self.arg.configfile.endswith(".conf"):
            project_name = self.arg.configfile.split("/")[-1][:-5]
        else:
            project_name = self.arg.configfile.split("/")[-1]
        self.set_project(self.arg.configfile, project_name)
        self.k8_modul_interal.reverse()
        if self.arg.delete or self.arg.deleteall:
            self.del_project()
        else:
            self.get_object()
        if self.arg.getconfigfile:
            fh = open("%s_out.config" % self.config.project_name, "w")
            self.config.write(fh)
            fh.close()
        if not self.k8_activ:
            # Handling wenn Kubernetes nicht in System gefunden wird
            print(Color.color_text(" Warrning ", Color.PURPLE, long=70, fill="!"))
            ErrorHandling.print_error(self.language["main02"], bold=True, verbose=self.arg.verbose)
            print(Color.color_text(" Warrning ", Color.PURPLE, long=70, fill="!"))

    def del_project(self):
        """geht die zu löschenden Kubernetes Objecte durch"""
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
                            self.del_object(k8pg_modul, body)
                    else:
                        self.del_object(k8pg_modul, self.k8_object[k8pg_modul])

    def del_object(self, k8pg_name, body):
        """Löscht die einzelnene Kubernetes Objecte"""
        body_dict = body.to_dict()
        try:
            if k8pg_name in self.k8_modul_no_namespace and self.arg.deleteall:
                api_response = self.k8_delete[k8pg_name]["k8_methode"](name=body_dict["metadata"]["name"], pretty="true")
            else:
                api_response = self.k8_delete[k8pg_name]["k8_methode"](namespace=self.config.get_object("namespace", "name"), name=body_dict["metadata"]["name"], pretty="true")
            print("%s Opject: %s (Type: %s)" % (Color.color_text(" DELETE ", color=Color.BOLD, long=20, fill="-"), body_dict["metadata"]["name"], k8pg_name))
            pprint(api_response)
            sleep(1)
        except ApiException as e:
            error_body = eval(e.body)
            ErrorHandling.print_K8Exection(self.config, error_body, self.language["main03"], k8pg_name)

    def get_object(self):
        """Gebe die zu löschenden Kubernetes Objecte und K8PojectManager Objecte aus"""
        if self.config.verbose or not self.config.config_status:
            # Gibt eine Warnung und die Config Datei mit aus abhängig von Verbose Parameter und ob ein Config Fehler festgestelt worden ist
            if not self.config.config_status:
                print(Color.color_text(" FAIL ", Color.BLINK, long=70, fill="!"))
            self.config.format_print()
        if not self.config.config_status:
            print(Color.color_text(" FAIL ", Color.BLINK, long=70, fill="!"))

        if self.config.config_status:
            # Gibt die Kubernetes Objecte nur aus wenn kein Config Fehler festgestelt wurde
            print(Color.color_text(" Project: %s " % self.config.project_name, long=70, fill="*"))
            for k8pg_modul in self.k8_modul_interal:
                if self.k8_object[k8pg_modul] is not None:
                    if type(self.k8_object[k8pg_modul]) is list:
                        if len(self.k8_object[k8pg_modul]) > 1:
                            index = 0
                            for body in self.k8_object[k8pg_modul]:
                                body_dict = body.to_dict()
                                index = index + 1
                                print(Color.color_text(" %s%i " % (k8pg_modul, index), long=60, fill="#"))
                                print("Name: %s" % body_dict["metadata"]["name"])
                        else:
                            body_dict = self.k8_object[k8pg_modul][0].to_dict()
                            print(Color.color_text(" %s " % k8pg_modul, long=60, fill="#"))
                            print("Name: %s" % body_dict["metadata"]["name"])
                    else:
                        body_dict = self.k8_object[k8pg_modul].to_dict()
                        print(Color.color_text(" %s " % k8pg_modul, long=60, fill="#"))
                        print("Name: %s" % body_dict["metadata"]["name"])


if __name__ == '__main__':
    start()
