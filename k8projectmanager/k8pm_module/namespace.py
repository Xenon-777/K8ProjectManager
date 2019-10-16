#

from kubernetes.client import V1ObjectMeta as K8Meta
from kubernetes.client import V1Namespace as K8NameSpace


class Namespace(object):
    """Erstellt das Kubernetes NameSpace Object"""

    def __init__(self):
        super().__init__()
        self.config = None
        self.language = None
        self.k8pg_option_to_section.update({"namespace": {"__section__": [False],
                                                          "name":        [True,
                                                                          False,
                                                                          "Text"]}})

    def set_namespace(self):
        """Erstelt das NameSpace Object"""
        self.config.activ_modul = "namespace"
        namespace = False

        for item in self.config.sections():
            if not item.startswith("volume"):
                namespace = True
        if namespace:
            if not self.config.has_section("namespace"):
                self.config.add_section("namespace")
                self.config.set("namespace", "name", self.config.project_name)
            metadata = K8Meta(name=self.config.get_object("namespace", "name"))
        else:
            return None

        return K8NameSpace(metadata=metadata)
