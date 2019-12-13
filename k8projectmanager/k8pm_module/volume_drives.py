#

from kubernetes.client import V1ObjectMeta as K8Meta
from kubernetes.client import V1PersistentVolumeSpec as K8Spec
from kubernetes.client import V1NFSVolumeSource as K8NFSDivice

from k8projectmanager.k8pm_sub_methoden.sub_methodes import ErrorHandling


class VolumeDrives(object):
    """Auswahl Liste und Anpasungen zu den Kubernete Persistent Volume Driver"""

    def __init__(self):
        super().__init__()
        self.config = None
        self.language = None
        self.k8_drives = {"nfs": self.set_volume_nfs}

    @staticmethod
    def set_volume_nfs(config, volume):
        """Kubernetes Object Einträge für NFS Server"""
        metadata = K8Meta(annotations={"volume.beta.kubernetes.io/mount-options": "nolock,local_lock=none"})
        server = config.get_object(volume, "server")
        path = config.get_object(volume, "path")
        if server is None or path is None:
            ErrorHandling.print_error("no server info", locals())
            return None
        device = K8NFSDivice(server=config.get_object(volume, "server"),
                             path=config.get_object(volume, "path"))
        spec = K8Spec(nfs=device)
        return {"metadata": metadata, "spec": spec}
