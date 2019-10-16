#

from kubernetes.client import V1ObjectMeta as K8Meta
from kubernetes.client import V1PersistentVolume as K8Volume
from kubernetes.client import V1PersistentVolumeSpec as K8Spec

from k8projectmanager.k8pm_module.volume_drives import VolumeDrives
from k8projectmanager.k8pm_sub_methoden.sub_methodes import ErrorHandling


class Volumes(VolumeDrives):
    """Erstelle Kubernetes Persistent Volume Objecte"""

    def __init__(self):
        super().__init__()
        self.k8pg_option_to_section.update({"volumes": {"__section__": [True],
                                                        "name":        [False,
                                                                        False,
                                                                        "Text"],
                                                        "label":       [False,
                                                                        False,
                                                                        "Text_List"],
                                                        "accessmodes": [False,
                                                                        False,
                                                                        "ReadWriteOnce,ReadOnlyMany,ReadWriteMany"],
                                                        "capacity":    [False,
                                                                        False,
                                                                        "Text.i"],
                                                        "class":       [False,
                                                                        False,
                                                                        "Text"],
                                                        "drive":       [False,
                                                                        False,
                                                                        "nfs"],
                                                        "server":      [False,
                                                                        False,
                                                                        "URL/IP"],
                                                        "path":        [False,
                                                                        False,
                                                                        "Path"]}})

    def set_volumes(self):
        """Handhabung von scalirten Volume Definitionen in der Config"""
        self.config.activ_modul = "volumes"
        volumes = []
        for volume in self.config.config_iteral("volume"):
            volumes.append(self.set_volume(volume))

        if not volumes:
            return None
        return volumes

    def set_volume(self, volume):
        """Erstelle ein Volume Object"""
        if self.config.has_option(volume, "label"):
            label = self.config.get_object(volume, "label").split(",")
            if len(label) < 2:
                label = ["volume", label[0]]
                self.config.set(volume, "label", ",".join(label))
            label = {label[0]: label[1]}
        else:
            label = None

        k8_drive = self.k8_drives.get(self.config.get_object(volume, "drive"), None)
        if k8_drive is None:
            self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["vol01"], locals(), bold=True)
            return None
        drive = k8_drive(self.config, volume)
        if drive is None:
            self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["vol02"], locals(), bold=True)
            return None

        metadata = K8Meta(annotations=drive["metadata"].annotations,
                          name=self.config.get_object(volume, "name"),
                          labels=label)
        spec = K8Spec(storage_class_name=self.config.get_object(volume, "class"),
                      capacity={"storage": self.config.get_object(volume, "capacity")},
                      access_modes=[self.config.get_object(volume, "accessmodes")],
                      nfs=drive["spec"].nfs)

        if metadata.name is None or spec.storage_class_name is None or spec.capacity["storage"] is None or spec.access_modes is None:
            self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["vol03"], locals(), bold=True)
            return None

        return K8Volume(metadata=metadata, spec=spec)
