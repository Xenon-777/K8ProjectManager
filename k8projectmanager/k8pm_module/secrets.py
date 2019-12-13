#

from k8projectmanager.k8pm_module.secret_system import SecretSystem

from k8projectmanager.k8pm_sub_methoden.sub_methodes import ErrorHandling


class Secrets(SecretSystem):
    """Erstellt Kubernetes Secret Objecte"""

    def __init__(self):
        super().__init__()
        self.k8pg_option_to_section["secret"].update({"__section__": (True,),
                                                      "type":        (False,
                                                                      False,
                                                                      "tls")})

    def set_secrets(self):
        """Esstellt das Secret Object"""
        self.config.activ_modul = "secret"
        secrets = []
        for secret in self.config.config_iteral("secret"):
            k8pg_secret = self.k8_secret.get(self.config.get_object(secret, "type"), None)
            if k8pg_secret is None:
                self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["sec01"], locals(), bold=True)
                continue
            secret = k8pg_secret(secret)
            if secret is None:
                self.config.config_status = ErrorHandling.print_error_config(self.config, self.language["sec03"], locals(), bold=True)
                continue
            secrets.append(secret)

        if not secrets:
            return None
        return secrets
