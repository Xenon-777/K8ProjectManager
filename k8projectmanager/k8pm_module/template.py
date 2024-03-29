#

from kubernetes.client import V1ObjectMeta as K8Meta
from kubernetes.client import V1PodTemplateSpec as K8Template
from kubernetes.client import V1PodSpec as K8spec
from kubernetes.client import V1Volume as K8Volume
from kubernetes.client import V1PersistentVolumeClaimVolumeSource as K8VolumeClaim

from k8projectmanager.k8pm_module.pot import Pot
from k8projectmanager.k8pm_sub_methoden.sub_methodes import ErrorHandling


class Template(Pot):
    """Erstellt ein Kubernetes Template Object"""

    def __init__(self):
        super().__init__()
        self.k8pg_option_to_section.update(dict(template={"__section__":  (False,),
                                                          "name":         (True,
                                                                           False,
                                                                           "Text"),
                                                          "label":        (False,
                                                                           False,
                                                                           "Text_List"),
                                                          "restart":      (True,
                                                                           False,
                                                                           "Always"),
                                                          "volume":       (False,
                                                                           True,
                                                                           "Text@"),
                                                          "volume_claim": (True,
                                                                           True,
                                                                           "Text@")}))

    def set_template(self, deploy_index):
        """Erstelt ein Template Object"""
        template = "template%s" % deploy_index
        self.config.activ_modul = 'template'
        spec = {"containers": None}

        label = self.config.get_object(template, "label")
        if label is not None:
            label = label.split(",")
            if len(label) == 2:
                label = {label[0]: label[1]}
            elif len(label) == 1:
                self.config.set(template, "label", "app,%s" % label[0])
                label = {"app": label[0]}
            else:
                self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["tem05"], locals(), bold=True)
                return None
        else:
            self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["tem01"], locals(), bold=True)
            return None

        if self.config.has_section("namespace%s" % deploy_index):
            namespace = self.config.get_object("namespace%s" % deploy_index, "name", modul="namespace")
        else:
            namespace = self.config.get_object("namespace1", "name", modul="namespace")

        if not self.config.has_option(template, "name"):
            self.config.set(template, "name", "%s-%s" % (self.config.project_name, "template%s" % deploy_index))
        metadata = K8Meta(name=self.config.get_object(template, "name"),
                          namespace=namespace,
                          labels=label)

        volumes = self.set_template_volumes(template)

        if self.config.has_option(template, "restart"):
            restart = self.config.get_object(template, "restart")
        else:
            restart = None

        container = self.set_container(deploy_index)
        if container is None:
            self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["tem02"], locals(), bold=True)
            return None

        spec = K8spec(containers=container, volumes=volumes, restart_policy=restart)

        return K8Template(metadata=metadata, spec=spec)

    def set_template_volumes(self, template):
        """Handhabung von scalirten Volume Definitionen des Template Object"""
        volumes = []
        for volume in self.config.config_iteral(template, "volume", no="_claim"):
            volumes.append(self.set_template_volume(volume, template))

        if not volumes:
            return None
        return volumes

    def set_template_volume(self, volume_nr, template):
        """Ermitlung einer Volume Definition für das Template Object"""
        volume_intern = self.config.get_object(template, volume_nr)
        if volume_intern.startswith("@c"):
            self.config.copy_option_to_option(volume_intern[1:], template, "name", to_option=volume_nr, add=True, change=True, iteral=False)
            self.config.copy_option_to_option(volume_intern[1:], template, "name", to_option=volume_nr, to_pre="_claim", change=True, iteral=False)

        if self.config.has_option(template, "%s_claim" % volume_nr):
            claim = self.config.get_object(template, volume_nr, pre="_claim")
            if claim.startswith("@c"):
                claim = self.config.get_object(claim[1:], "name", modul="claims")
                if claim is None:
                    self.config.config_status = ErrorHandling.print_error_config(self.config, "%s (%s)" % (self.language["tem03"], volume_nr), locals(), bold=True)
                    return None
                self.config.set(template, "%s_claim" % volume_nr, claim)
        else:
            self.config.config_status = ErrorHandling.print_error_config(self.config, "%s (%s)" % (self.language["tem04"], volume_nr), locals(), bold=True)
            return None
        volume_claim = K8VolumeClaim(claim_name=claim)
        volume = K8Volume(name=self.config.get_object(template, volume_nr),
                          persistent_volume_claim=volume_claim)

        return volume
