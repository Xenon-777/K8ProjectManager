#

from base64 import b64encode

from kubernetes.client import V1ObjectMeta as K8Meta
from kubernetes.client import V1Secret as K8Secret

from k8projectmanager.k8pm_sub_methoden.sub_methodes import ErrorHandling


class SecretSystem(object):
    """Kubernetes Secret System Listen und deren Handhabung"""

    def __init__(self):
        super().__init__()
        self.config = None
        self.language = None
        self.k8pg_option_to_section.update({"secrets": {"name":    [True,
                                                                    False,
                                                                    "Text"],
                                                        "tls_key": [True,
                                                                    False,
                                                                    "File@"],
                                                        "tls_crt": [False,
                                                                    False,
                                                                    "File"]}})
        self.k8_secret = {"tls": self.tls}

    def set_metadata(self, secret):
        """Ermitellt den Namen des Secret Objectes"""
        metadata = {"name": None}

        if not self.config.has_option(secret, "name"):
            self.config.set(secret, "name", "%s-%s" % (self.config.project_name, secret))
        metadata = K8Meta(name=self.config.get_object(secret, "name"))

        return metadata

    def tls(self, secret):
        """Verfahren für ein TLS Secret System"""
        data = {}
        secret_type = "kubernetes.io/tls"
        metadata = self.set_metadata(secret)

        if self.config.has_option(secret, "tls_key"):
            key_file = self.config.get_object(secret, "tls_key")
            if key_file.startswith("@"):
                self.config.copy_option_to_option(key_file[1:], secret, "tls_key", change=True)
        else:
            self.config.copy_option_to_option("secret", secret, "tls_key")

        tls_key = self.config.get_object(secret, "tls_key")
        tls_crt = self.config.get_object(secret, "tls_crt")

        if tls_key is None:
            self.config.config_status = ErrorHandling.print_error_config(self.config, "%s (%s/secret)" % (self.language["s_s01"], secret), locals(), bold=True)
            return None

        if tls_crt is None:
            self.config.config_status = ErrorHandling.print_error_config(self.config, "%s (%s)" % (self.language["s_s02"], secret), locals(), bold=True)
            return None

        try:
            tls_key = open(tls_key, "rb")
            tls_crt = open(tls_crt, "rb")
        except FileNotFoundError as e:
            self.config.config_status = ErrorHandling.print_error_config(self.config, "%s (%s)" % (self.language["s_s03"], e), locals(), bold=True)
            return None
        data["tls.key"] = b64encode(tls_key.read()).decode("ASCII")
        data["tls.crt"] = b64encode(tls_crt.read()).decode("ASCII")
        tls_key.close()
        tls_crt.close()

        return K8Secret(data=data, metadata=metadata, type=secret_type)
