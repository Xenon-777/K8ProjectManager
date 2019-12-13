#

from kubernetes import client, config

from k8projectmanager.k8pm_module.claims import Claims
from k8projectmanager.k8pm_module.deployment import Deployment
from k8projectmanager.k8pm_module.ingress import Ingress
from k8projectmanager.k8pm_module.namespace import Namespace
from k8projectmanager.k8pm_module.secrets import Secrets
from k8projectmanager.k8pm_module.services import Services
from k8projectmanager.k8pm_module.volumes import Volumes


class K8pgModule(Volumes,
                 Namespace,
                 Deployment,
                 Claims,
                 Secrets,
                 Services,
                 Ingress):

    def __init__(self):
        self.k8pg_option_to_section = {}
        super().__init__()

        try:
            config.load_kube_config()
            self.k8_activ = True
            k8_config = client.Configuration()
        except TypeError:
            self.k8_activ = False
            k8_config = None
        k8_core_instance = client.CoreV1Api(client.ApiClient(k8_config))
        k8_app_instance = client.AppsV1Api(client.ApiClient(k8_config))
        k8_extensions_instance = client.ExtensionsV1beta1Api(client.ApiClient(k8_config))

        self.k8_modul = {"volume":    {"k8pg_methode": self.set_volumes,
                                       "k8_methode":   k8_core_instance.create_persistent_volume},
                         "namespace": {"k8pg_methode": self.set_namespace,
                                       "k8_methode":   k8_core_instance.create_namespace},
                         "secret":    {"k8pg_methode": self.set_secrets,
                                       "k8_methode":   k8_core_instance.create_namespaced_secret},
                         "claim":     {"k8pg_methode": self.set_claims,
                                       "k8_methode":   k8_core_instance.create_namespaced_persistent_volume_claim},
                         "deploy":    {"k8pg_methode": self.set_deploys,
                                       "k8_methode":   k8_app_instance.create_namespaced_deployment},
                         "service":   {"k8pg_methode": self.set_services,
                                       "k8_methode":   k8_core_instance.create_namespaced_service},
                         "ingress":   {"k8pg_methode": self.set_ingress,
                                       "k8_methode":   k8_extensions_instance.create_namespaced_ingress}}

        self.k8_patch = {"volume":    {"k8_methode": k8_core_instance.patch_persistent_volume},
                         "namespace": {"k8_methode": k8_core_instance.patch_namespace},
                         "secret":    {"k8_methode": k8_core_instance.patch_namespaced_secret},
                         "claim":     {"k8_methode": k8_core_instance.patch_namespaced_persistent_volume_claim},
                         "deploy":    {"k8_methode": k8_app_instance.patch_namespaced_deployment},
                         "service":   {"k8_methode": k8_core_instance.patch_namespaced_service},
                         "ingress":   {"k8_methode": k8_extensions_instance.patch_namespaced_ingress}}

        self.k8_delete = {"volume":    {"k8_methode": k8_core_instance.delete_persistent_volume},
                          "namespace": {"k8_methode": k8_core_instance.delete_namespace},
                          "secret":    {"k8_methode": k8_core_instance.delete_namespaced_secret},
                          "claim":     {"k8_methode": k8_core_instance.delete_namespaced_persistent_volume_claim},
                          "deploy":    {"k8_methode": k8_app_instance.delete_namespaced_deployment},
                          "service":   {"k8_methode": k8_core_instance.delete_namespaced_service},
                          "ingress":   {"k8_methode": k8_extensions_instance.delete_namespaced_ingress}}

        self.k8_modul_interal = ["volume",
                                 "namespace",
                                 "secret",
                                 "claim",
                                 "deploy",
                                 "service",
                                 "ingress"]

        self.k8_modul_no_namespace = ["namespace",
                                      "volume"]

        self.k8_modul_with_submodul = {"deploy": ["deploy", "template", "container"]}

    def get_k8_methode(self, k8pg_modul_name):
        return self.k8_modul[k8pg_modul_name]["k8_methode"]

    def set_config_singular(self):
        sections = []
        for modul in self.k8_modul_interal:
            sections.append(modul)
        for key in self.k8_modul_with_submodul.keys():
            for modul in self.k8_modul_with_submodul[key]:
                sections.append(modul)
        for section in self.config.sections():
            if section in sections:
                newsection = "%s1" % section
                self.config.add_section(newsection)
                for option in self.config.options(section):
                    self.config.set(newsection, option, self.config.get(section, option))
                    self.config.remove_option(section, option)
                self.config.remove_section(section)
