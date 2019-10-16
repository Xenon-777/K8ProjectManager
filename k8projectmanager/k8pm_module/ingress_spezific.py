#


class Spezific(object):
    """Specialisirungen für Kubernetes Ingress Objecte"""

    def __init__(self):
        super().__init__()
        self.config = None
        self.language = None
        self.k8pg_option_to_section.update({"ingress": {"whitelist":    [True,
                                                                         False,
                                                                         "IP_List"],
                                                        "ssl_backends": [True,
                                                                         False,
                                                                         "Text"]}})

    def insert_ssl_backend(self):
        """Handhabung für ein Ingress Object mit SSL Backend"""
        service = self.config.get_object("ingress", "ssl_backends")
        if service.startswith("@s"):
            self.config.copy_option_to_option(service[1:], "ingress", "name", to_option="ssl_backends", change=True, iteral=False)
        elif service.startswith("@r"):
            self.config.copy_option_to_option_in_section("ingress", service[1:], from_pre="_servicename", to_option="ssl_backends", change=True, iteral=False)
        service = self.config.get_object("ingress", "ssl_backends")
        if service.startswith("@"):
            return None

        return {"kubernetes.io/ingress.allow-http":             "false",
                "nginx.org/ssl-backends":                       service,
                "nginx.ingress.kubernetes.io/backend-protocol": "HTTPS"}

    def insert_whitelist(self):
        """Handhabung für ein Ingress Object mit Whitelist"""
        return {"nginx.ingress.kubernetes.io/whitelist-source-range": self.config.get_object("ingress", "whitelist")}
