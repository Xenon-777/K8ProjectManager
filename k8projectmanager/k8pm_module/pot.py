#

from re import sub

from kubernetes.client import V1Container as K8Container
from kubernetes.client import V1EnvVar as K8Env
from kubernetes.client import V1ContainerPort as K8Port
from kubernetes.client import V1VolumeMount as K8Mount

from k8projectmanager.k8pm_sub_methoden.sub_methodes import ErrorHandling


class Pot(object):
    """Erstellt Kubernetes Pod Objecte"""

    def __init__(self):
        super().__init__()
        self.config = None
        self.language = None
        self.k8pg_option_to_section.update({"pot": {"__section__": [True],
                                                    "name":        [True,
                                                                    False,
                                                                    "Text"],
                                                    "image":       [False,
                                                                    False,
                                                                    "Text"],
                                                    "ports":       [True,
                                                                    False,
                                                                    "Zahlen_List"],
                                                    "env":         [True,
                                                                    True,
                                                                    "Text@"],
                                                    "env_value":   [True,
                                                                    True,
                                                                    "Text@"],
                                                    "command":     [True,
                                                                    False,
                                                                    "Text"],
                                                    "arg":         [True,
                                                                    True,
                                                                    "Text@"],
                                                    "volume":      [True,
                                                                    True,
                                                                    "Text@"],
                                                    "volume_path": [True,
                                                                    True,
                                                                    "Path@"],
                                                    }})

    def set_containers(self):
        """Handhabung von scalirten Pod/Container Definitionen"""
        self.config.activ_modul = "pot"
        container_list = []

        containers = self.config.config_iteral("container")
        for container in containers:
            container_list.append(self.set_container(container))

        if not container_list:
            ErrorHandling.print_error_config(self.config, self.language["con01"], locals(), bold=True)
            return None
        return container_list

    def set_container(self, container):
        """Erstellt ein Pod/Container Object"""

        # Ermittle Image
        image = self.config.get_object(container, "image")
        if image is not None:
            if not self.config.has_option(container, "name"):
                name = sub("[:/.]", "_", self.config.get_object(container, "image"))
                self.config.set(container, "name", name)
        else:
            ErrorHandling.print_error_config(self.config, self.language["con02"], locals(), bold=True)
            return None

        # Ermitle Ports
        ports = []
        if self.config.has_option(container, "ports"):
            pre_ports = self.config.config_iteral("template", "port")
            pre_ports = len(pre_ports)
            if self.config.has_option("template", "port"):
                pre_ports = pre_ports - 1
            for port in self.config.get_object(container, "ports").split(","):
                ports.append(K8Port(container_port=int(port)))
                pre_ports = pre_ports + 1
                self.config.set("template", "port%i" % pre_ports, port)
                if pre_ports == 1:
                    self.config.set("template", "port", port)
        if not ports:
            ports = None

        envs = []
        for env in self.config.config_iteral(container, "env", no="_value"):
            envs.append(self.set_container_env(container, env))
        if not envs:
            envs = None

        if self.config.has_option(container, "command"):
            command = self.config.get_object(container, "command").split(" ")
        else:
            command = None

        args = []
        for arg in self.config.config_iteral(container, "arg"):
            args.append(self.set_container_arg(container, arg))
        if not args:
            args = None

        volumes = []
        for volume in self.config.config_iteral(container, "volume", pre="_path"):
            volumes.append(self.set_container_volume(container, volume))
        if not volumes:
            volumes = None

        return K8Container(name=self.config.get_object(container, "name"),
                           image=self.config.get_object(container, "image"),
                           command=command,
                           args=args,
                           env=envs,
                           volume_mounts=volumes,
                           ports=ports)

    def set_container_env(self, container, env_nr):
        """Ermitlung der ENV Definition in einen Pod/Container Object"""
        env = self.config.get_object(container, env_nr)
        if env.startswith("@"):
            alter_container = env[1:]
            self.config.copy_option_to_option(alter_container, container, env_nr, change=True)
            self.config.copy_option_to_option(alter_container, container, env_nr, to_pre="_value")
        env_value = self.config.get_object(container, env_nr, pre="_value")
        if env_value.startswith("@"):
            alter_container = env_value[1:]
            self.config.copy_option_to_option(alter_container, container, env_nr, from_pre="_value", to_pre="_value", change=True)
        return K8Env(name=self.config.get_object(container, env_nr),
                     value=self.config.get_object(container, env_nr, pre="_value"))

    def set_container_arg(self, container, arg_nr):
        """Ermitlung der Argument Definition in einen Pod/Container Object"""
        arg = self.config.get_object(container, arg_nr)
        if arg.startswith("@"):
            alter_container = arg[1:]
            self.config.copy_option_to_option(alter_container, container, arg_nr, change=True)
            arg = self.config.get_object(container, arg_nr)
        return arg

    def set_container_volume(self, container, volume_path):
        """Ermitlung der persitent Volume Definitionen in einen Pod/Container Object"""
        volume_nr = volume_path.split("_")[0]

        path = self.config.get_object(container, volume_path)
        if path.startswith("@"):
            alter_container = path[1:]
            self.config.copy_option_to_option(alter_container, container, volume_nr, change=True)
            self.config.copy_option_to_option(alter_container, container, volume_path, change=True)

        name = None
        if self.config.has_option(container, volume_nr):
            name = self.config.get_object(container, volume_nr)
            if name.startswith("@"):
                self.config.copy_option_to_option("template", container, name[1:], to_option=volume_nr, iteral=False)
        else:
            if self.config.has_option("template", volume_nr):
                self.config.copy_option_to_option("template", container, volume_nr, iteral=False)
        name = self.config.get_object(container, volume_nr)
        if name is None:
            self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["con03"], locals(), bold=True)
            return None

        return K8Mount(name=name,
                       mount_path=self.config.get_object(container, volume_path))
