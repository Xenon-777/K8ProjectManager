#

from kubernetes.client import V1ObjectMeta as K8Meta
from kubernetes.client import V1beta2Deployment as K8Deployment
from kubernetes.client import V1LabelSelector as K8Selector
from kubernetes.client import V1DeploymentSpec as K8Spec

from k8projectmanager.k8pm_module.template import Template
from k8projectmanager.k8pm_sub_methoden.sub_methodes import ErrorHandling


class Deployment(Template):
    """Erstelle ein Kubernetes Deployment Objcet"""

    def __init__(self):
        super().__init__()
        self.k8pg_option_to_section.update(dict(deploy={"__section__": (True,),
                                                        "name":        (True,
                                                                        False,
                                                                        "Text"),
                                                        "replicas":    (True,
                                                                        False,
                                                                        "Zahl")}))

    def set_deploys(self):
        """Erstelt ein Deployment Object Liste"""
        deploy_list = []
        for deploy in self.config.config_iteral('deploy'):
            self.config.activ_modul = "deploy"
            deploy_list.append(self.set_deploy(deploy))

        if not deploy_list:
            return None
        return deploy_list

    def set_deploy(self, deploy):
        """Erstelt ein Deployment Object"""
        deploy_index = deploy.replace('deploy', '')
        metadata = None
        if not self.config.has_option(deploy, "name"):
            self.config.set(deploy, "name", "%s-%s" % (self.config.project_name, deploy))
        metadata = K8Meta(name=self.config.get_object(deploy, "name"))

        if not self.config.has_option(deploy, "replicas"):
            self.config.set(deploy, "replicas", "1")
        replicas = self.config.get_object(deploy, "replicas", integer=True)

        template = self.set_template(deploy_index)
        if template is None:
            self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["dep01"], locals(), bold=True)
            return None

        label = self.config.get_object("template%s" % deploy_index, "label", modul="template")
        label = label.split(",")
        selector = K8Selector(match_labels={label[0]: label[1]})

        spec = K8Spec(replicas=replicas,
                      selector=selector,
                      template=template)

        return K8Deployment(metadata=metadata, spec=spec)
