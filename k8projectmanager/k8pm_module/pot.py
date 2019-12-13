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
        self.k8pg_option_to_section.update(dict(container={"__section__": (False,),
                                                           "name":        (True,
                                                                           False,
                                                                           "Text"),
                                                           "image":       (False,
                                                                           False,
                                                                           "Text"),
                                                           "ports":       (True,
                                                                           False,
                                                                           "Zahlen_List"),
                                                           "env":         (True,
                                                                           True,
                                                                           "Text@"),
                                                           "env_value":   (True,
                                                                           True,
                                                                           "Text@"),
                                                           "command":     (True,
                                                                           False,
                                                                           "Text"),
                                                           "arg":         (True,
                                                                           True,
                                                                           "Text@"),
                                                           "volume":      (True,
                                                                           True,
                                                                           "Text@"),
                                                           "volume_path": (True,
                                                                           True,
                                                                           "Path@"),
                                                           "pull":        (True,
                                                                           False,
                                                                           "Always,IfNotPresent,Never"),
                                                           }))

    def set_container(self, deploy_index):
        """Erstellt ein Pod/Container Object"""
        pot = "container%s" % deploy_index
        template = "template%s" % deploy_index
        self.config.activ_modul = "container"

        # Ermittle Image
        image = self.config.get_object(pot, "image")
        if image is not None:
            if not self.config.has_option(pot, "name"):
                name = sub("[:/.]", "-", self.config.get_object(pot, "image"))
                self.config.set(pot, "name", name)
        else:
            ErrorHandling.print_error_config(self.config, self.language["con02"], locals(), bold=True)
            return None

        # Ermitle Ports
        ports = []
        if self.config.has_option(pot, "ports"):
            pre_ports = self.config.config_iteral(template, "port")
            pre_ports = len(pre_ports)
            if self.config.has_option(template, "port"):
                pre_ports = pre_ports - 1
            for port in self.config.get_object(pot, "ports").split(","):
                ports.append(K8Port(container_port=int(port)))
                pre_ports = pre_ports + 1
                self.config.set(template, "port%i" % pre_ports, port)
                if pre_ports == 1:
                    self.config.set(template, "port", port)
        if not ports:
            ports = None

        envs = []
        for env in self.config.config_iteral(pot, "env", no="_value"):
            envs.append(self.set_container_env(pot, env))
        if not envs:
            envs = None

        if self.config.has_option(pot, "command"):
            command = self.config.get_object(pot, "command").split(" ")
        else:
            command = None

        if self.config.has_option(pot, "pull"):
            pull = self.config.get_object(pot, "pull")
        else:
            pull = "Always"

        args = []
        for arg in self.config.config_iteral(pot, "arg"):
            args.append(self.set_container_arg(pot, arg))
        if not args:
            args = None

        volumes = []
        for volume in self.config.config_iteral(pot, "volume", pre="_path"):
            volumes.append(self.set_container_volume(pot, volume, deploy_index))
        if not volumes:
            volumes = None

        return [K8Container(name=self.config.get_object(pot, "name"),
                            image=self.config.get_object(pot, "image"),
                            command=command,
                            args=args,
                            env=envs,
                            volume_mounts=volumes,
                            ports=ports,
                            image_pull_policy=pull)]

    def set_container_env(self, container, env_nr):
        """Ermitlung der ENV Definition in einen Pod/Container Object"""
        env = self.config.get_object(container, env_nr)
        if env.startswith("@"):
            alter_container = env[1:]
            self.config.copy_option_to_option(alter_container, container, env_nr, change=True, iteral=False)
            self.config.copy_option_to_option(alter_container, container, env_nr, from_pre="_value", to_pre="_value", iteral=False)
        if self.config.has_option(container, "%s_value" % env_nr):
            env_value = self.config.get_object(container, env_nr, pre="_value")
            if env_value.startswith("@"):
                alter_container = env_value[1:]
                self.config.copy_option_to_option(alter_container, container, env_nr, from_pre="_value", to_pre="_value", change=True, iteral=False)
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

    def set_container_volume(self, container, volume_path, deploy_index):
        """Ermitlung der persitent Volume Definitionen in einen Pod/Container Object"""
        template = "template%s" % deploy_index
        volume_nr = volume_path.split("_")[0]

        path = self.config.get_object(container, volume_path)
        if path.startswith("@co"):
            alter_container = path[1:]
            self.config.copy_option_to_option(alter_container, container, volume_nr, change=True)
            self.config.copy_option_to_option(alter_container, container, volume_path, change=True)

        name = None
        if self.config.has_option(container, volume_nr):
            name = self.config.get_object(container, volume_nr)
            if name.startswith("@vo"):
                self.config.copy_option_to_option(template, container, name[1:], to_option=volume_nr, iteral=False)
        else:
            if self.config.has_option(template, volume_nr):
                self.config.copy_option_to_option(template, container, volume_nr, iteral=False)
            elif self.config.has_option(template, "volume%s" % deploy_index):
                self.config.copy_option_to_option(template, container, "volume%s" % deploy_index, to_option=volume_nr, iteral=False)
        name = self.config.get_object(container, volume_nr)
        if name is None:
            self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["con03"], locals(), bold=True)
            return None

        return K8Mount(name=name,
                       mount_path=self.config.get_object(container, volume_path))
