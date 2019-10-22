#

from kubernetes.client import V1ObjectMeta as K8Meta
from kubernetes.client import V1Service as K8Service
from kubernetes.client import V1ServiceSpec as K8Spec
from kubernetes.client import V1ServicePort as K8Port

from k8projectmanager.k8pm_sub_methoden.sub_methodes import ErrorHandling


class Services(object):
    """Erstellt Kubernetes Service Objecte"""

    def __init__(self):
        super().__init__()
        self.config = None
        self.language = None
        self.k8pg_option_to_section.update({"services": {"__section__":   [True],
                                                         "name":          [True,
                                                                           False,
                                                                           "Text"],
                                                         "template":      [True,
                                                                           False,
                                                                           "Text_List"],
                                                         "extern_ips":    [True,
                                                                           False,
                                                                           "IP"],
                                                         "port":          [False,
                                                                           True,
                                                                           "Zahl"],
                                                         "port_name":     [True,
                                                                           True,
                                                                           "Text"],
                                                         "port_target":   [True,
                                                                           True,
                                                                           "Zahl@"],
                                                         "port_protocol": [True,
                                                                           True,
                                                                           "TCP,UDP"]}})

    def set_services(self):
        """Handhabung von scalirten Service Definitionen"""
        self.config.activ_modul = "services"
        services = []
        for service in self.config.config_iteral("service"):
            services.append(self.set_service(service))

        if not services:
            return None
        return services

    def set_service(self, service):
        """Erstelt ein Service Object"""
        metadata = {"labels": {"name": None},
                    "name":   None}
        spec = {"ports":    [],
                "selector": None}

        if not self.config.has_option(service, "name"):
            self.config.set(service, "name", "%s-%s" % (self.config.project_name, service))
        name = self.config.get_object(service, "name")

        if not self.config.has_option(service, "template") and self.config.has_option("template", "label"):
            self.config.copy_option_to_option("template", service, "label", to_option="template")
        if self.config.has_option(service, "template"):
            template = self.config.get_object(service, "template")
            template = template.split(",")
            if not len(template) == 2:
                self.config.config_status = ErrorHandling.print_error_config(self.config, "%s (%s)" % (self.language["ser06"], service), locals(), bold=True)
        else:
            self.config.config_status = ErrorHandling.print_error_config(self.config, "%s (%s)" % (self.language["ser01"], service), locals(), bold=True)
            return None

        if self.config.has_option(service, "extern_ips"):
            external_i_ps = self.config.get_object(service, "extern_ips").split(",")
        else:
            external_i_ps = None

        ports = []
        for port in self.config.config_iteral(service, "port", no="_"):
            service_port = self.set_service_port(service, port)
            if service_port is None:
                self.config.config_status = ErrorHandling.print_error("%s (%s)" % (self.language["ser02"], service))
                return None
            ports.append(self.set_service_port(service, port))
        if not ports:
            self.config.config_status = ErrorHandling.print_error_config(self.config, "%s (%s)" % (self.language["ser03"], metadata["name"]), locals(), bold=True)
            ports = self.config.config_iteral(service, "port", no="_")
            if len(ports) == 0:
                self.config.config_status = ErrorHandling.print_error("%s (%s)" % (self.language["ser01"], service))
            return None

        metadata = K8Meta(name=name,
                          labels={"name": name})
        spec = K8Spec(selector={template[0]: template[1]},
                      external_i_ps=external_i_ps,
                      ports=ports)
        return K8Service(metadata=metadata, spec=spec)

    def set_service_port(self, service, port):
        """Port Definitions Ermitlung für das Service Object"""
        port_target = "%s_target" % port

        if self.config.has_option(service, port_target):
            port_intern = self.config.get_object(service, port_target)
            if port_intern.startswith("@c"):
                container_ports = self.config.get_object(port_intern[1:], "ports", modul="pot")
                if container_ports is None:
                    self.config.config_status = ErrorHandling.print_error_config(self.config, "%s ( %s, %s, %s)" % (self.language["ser01"], port_intern, port, service), locals(), bold=True)
                    return None
                container_ports = container_ports.split(",")
                self.config.set(service, port_target, container_ports[0])
        else:
            if self.config.has_option("template", port):
                self.config.copy_option_to_option("template", service, port, to_option=port_target, iteral=False)
            else:
                return None

        if not self.config.has_option(service, "%s_name" % port):
            self.config.set(service, "%s_name" % port, "%s-%s-%s" % (self.config.project_name, service, port))

        if self.config.has_option(service, "%s_protocol" % port):
            protocol = self.config.get_object(service, port, pre="_protocol")
        else:
            protocol = None

        return K8Port(port=self.config.get_object(service, port, integer=True),
                      name=self.config.get_object(service, port, pre="_name"),
                      target_port=self.config.get_object(service, port_target, integer=True),
                      protocol=protocol)
