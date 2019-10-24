#

from kubernetes.client import V1ObjectMeta as K8Meta
from kubernetes.client import ExtensionsV1beta1Ingress as K8Ingress
from kubernetes.client import ExtensionsV1beta1IngressSpec as K8Spec
from kubernetes.client import ExtensionsV1beta1HTTPIngressPath as K8IngressPath
from kubernetes.client import ExtensionsV1beta1HTTPIngressRuleValue as K8IngressRuleValue
from kubernetes.client import ExtensionsV1beta1IngressBackend as K8IngressBackend
from kubernetes.client import ExtensionsV1beta1IngressRule as K8IngressRule
from kubernetes.client import ExtensionsV1beta1IngressTLS as K8IngressTLS

from k8projectmanager.k8pm_module.ingress_spezific import Spezific
from k8projectmanager.k8pm_sub_methoden.sub_methodes import ErrorHandling


class Ingress(Spezific):
    """Erstelt Kubernetes Ingress Object"""

    def __init__(self):
        super().__init__()
        self.k8pg_option_to_section["ingress"].update({"__section__":      [False],
                                                       "name":             [True,
                                                                            False,
                                                                            "Text"],
                                                       "backend_host":     [True,
                                                                            False,
                                                                            "Text"],
                                                       "backend_port":     [True,
                                                                            False,
                                                                            "Zahl"],
                                                       "rule_host":        [True,
                                                                            True,
                                                                            "Text"],
                                                       "rule_port":        [True,
                                                                            True,
                                                                            "Zahl"],
                                                       "rule_servicename": [True,
                                                                            True,
                                                                            "Text@"],
                                                       "annotation":       [True,
                                                                            True,
                                                                            "Text@"],
                                                       "annotation_value": [True,
                                                                            True,
                                                                            "Text"],
                                                       "tls_hosts":        [True,
                                                                            True,
                                                                            "Text@"],
                                                       "tls_secret":       [True,
                                                                            True,
                                                                            "Text"]})

    def set_ingress(self):
        """Erstelt Ingress Object"""
        self.config.activ_modul = "ingress"
        metadata = {"name": None}
        spec = {}

        if not self.config.has_section("ingress"):
            return None

        if not self.config.has_option("ingress", "name"):
            if self.config.has_option("template", "label"):
                name = self.config.get_object("template", "label", modul="template")
                name = name.split(",")[1]
                self.config.set("ingress", "name", name)
            else:
                self.config.set("ingress", "name", self.config.project_name)

        annotations = {}
        if self.config.has_option("ingress", "whitelist"):
            annotations.update(self.insert_whitelist())

        if len(self.config.config_iteral("ingress", "rule", pre="_host")) > 0:
            rules = self.set_ingress_rules()
        else:
            rules = None

        if self.config.has_option("ingress", "ssl_backends"):
            ssl_backend = self.insert_ssl_backend()
            if ssl_backend is None:
                self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["ing01"], locals(), bold=True)
                return None
            annotations.update(self.insert_ssl_backend())

        if len(self.config.config_iteral("ingress", "annotation", no="_value")) > 0:
            annotations.update(self.set_ingress_annotations())

        if annotations == {}:
            annotations = None

        if self.config.has_option("ingress", "backend_host"):
            backend = K8IngressBackend(self.config.get_object("ingress", "backend_host"),
                                       self.config.get_object("ingress", "backend_port", integer=True))
        else:
            backend = None

        if self.config.has_option("ingress", "tls_hosts") or self.config.has_option("ingress", "tls1_hosts"):
            tls = self.set_ingress_tls_s()
        else:
            tls = None

        if rules is None and backend is None:
            self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["ing02"], locals(), bold=True)
            return None

        metadata = K8Meta(annotations=annotations, name=self.config.get_object("ingress", "name"))
        spec = K8Spec(backend=backend, rules=rules, tls=tls)

        return K8Ingress(metadata=metadata, spec=spec)

    def set_ingress_annotations(self):
        """Ermitlung der Anntations Definitionen für das Ingress Object"""
        annotations = {}
        for annotation in self.config.config_iteral("ingress", "annotation", no="_value"):
            value = self.config.get_object("ingress", annotation, pre="_value")
            if value is not None:
                annotations[annotation] = value
            else:
                self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["ing03"], locals(), bold=True)
                return None
        return annotations

    def set_ingress_rules(self):
        """Handhabung für scalirte Rule Definitionen für das Ingress Object"""
        rules = []
        self.config.copy_option_to_option("service", "ingress", "port", to_option="rule", to_pre="_port")
        for rule in self.config.config_iteral("ingress", "rule", pre="_host"):
            rule_spec = self.set_ingress_rule(rule)
            if rule_spec is not None:
                rules.append(self.set_ingress_rule(rule))
            else:
                self.config.config_status = ErrorHandling.print_error_config(self.config, "%s (%s)" % (self.language["ing06"], rule), locals(), bold=True)
                return None

        return rules

    def set_ingress_rule(self, rule_host):
        """Ermitlung einer Rule Definition für das Ingress Object"""
        rule_nr = rule_host.split("_")[0]
        port_nr = rule_nr.replace("rule", "port")

        self.config.copy_option_to_option("service", "ingress", "name", to_option=rule_nr, to_pre="_servicename", iteral=False)
        self.config.copy_option_to_option("service", "ingress", port_nr, to_option=rule_nr, to_pre="_port", iteral=False)
        service_port = self.config.get_object("ingress", rule_nr, pre="_servicename")
        if service_port is not None:
            if service_port.startswith("@p"):
                self.config.copy_option_to_option("service", "ingress", "name", to_option=rule_nr, to_pre="_servicename", change=True, iteral=False)
                self.config.copy_option_to_option("service", "ingress", service_port[1:], to_option=rule_nr, to_pre="_port", change=True, iteral=False)
            if service_port.startswith("@s"):
                self.config.copy_option_to_option(service_port[1:], "ingress", "name", to_option=rule_nr, to_pre="_servicename", change=True, iteral=False)
                self.config.copy_option_to_option(service_port[1:], "ingress", "port", to_option=rule_nr, to_pre="_port", change=True, iteral=False)
        host = self.config.get_object("ingress", rule_host)
        port = self.config.get_object("ingress", rule_nr, pre="_port", integer=True)
        servicname = self.config.get_object("ingress", rule_nr, pre="_servicename")

        if host is None or port is None or servicname is None:
            self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["ing04"], locals(), bold=True)
            return None
        http = K8IngressBackend(servicname, port)
        http = K8IngressPath(http)
        http = K8IngressRuleValue([http])

        return K8IngressRule(self.config.get_object("ingress", rule_host), http)

    def set_ingress_tls_s(self):
        """Handhabung für scalirte TLS Definitionen für das Ingress Object"""
        tls_list = []
        for tls in self.config.config_iteral("ingress", "tls", pre="_hosts"):
            tls_list.append(self.set_ingress_tls(tls))

        if not tls_list:
            return None
        return tls_list

    def set_ingress_tls(self, tls_hosts):
        """Ermitlung einer TLS Definition für das Ingress Object"""
        tls_nr = tls_hosts.split("_")[0]
        rule_nr = tls_nr.replace("tls", "rule")
        secret_nr = tls_nr.replace("tls", "secret")
        secret = None

        hosts = self.config.get_object("ingress", tls_hosts)
        if hosts.startswith("@"):
            self.config.copy_option_to_option_in_section("ingress", rule_nr, from_pre="_host", to_option=tls_hosts, change=True, iteral=False)
            hosts = self.config.get_object("ingress", tls_hosts).split(",")

        self.config.copy_option_to_option(secret_nr, "ingress", "name", to_option=tls_nr, to_pre="_secret", iteral=False)
        if self.config.has_option("ingress", "%s_secret" % tls_nr):
            secret = self.config.get_object("ingress", tls_nr, pre="_secret")
        else:
            self.config.config_status = ErrorHandling.print_error_config(self.config, "%s (%s)" % (self.language["ing05"], tls_nr), locals(), bold=True)
            return None

        return K8IngressTLS(hosts=hosts,
                            secret_name=secret)
