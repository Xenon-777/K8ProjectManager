#

from kubernetes.client import V1ObjectMeta as K8Meta
from kubernetes.client import V1PersistentVolumeClaim as K8Claim
from kubernetes.client import V1PersistentVolumeClaimSpec as K8Spec
from kubernetes.client import V1ResourceRequirements as K8Resource

from k8projectmanager.k8pm_sub_methoden.sub_methodes import ErrorHandling


class Claims(object):
    """Erstelle Kubernetes Claim Objecte"""

    def __init__(self):
        super().__init__()
        self.config = None
        self.language = None
        self.k8pg_option_to_section.update(dict(claim={"__section__":  (True,),
                                                       "name":         (True,
                                                                        False,
                                                                        "Text@",
                                                                        "name",
                                                                        True,
                                                                        "cla01"),
                                                       "accessmodes":  (True,
                                                                        False,
                                                                        "ReadWriteOnce,ReadOnlyMany,ReadWriteMany",
                                                                        "accessmodes",
                                                                        False,
                                                                        "cla02"),
                                                       "requests":     (True,
                                                                        False,
                                                                        "Text.i",
                                                                        "capacity",
                                                                        False,
                                                                        "cla03"),
                                                       "volume_class": (True,
                                                                        False,
                                                                        "Text@",
                                                                        "class",
                                                                        False,
                                                                        "cla04")}))

    def set_claims(self):
        """Handhabung von scalirten Claim Definitionen in der Config"""
        self.config.activ_modul = "claim"
        claims = []
        if self.config.has_section("claims"):
            self.config.set_sections_from_sections_iteral("volume", "claim")
            self.config.remove_section("claims")

        for claim in self.config.config_iteral("claim"):
            claims.append(self.set_claim(claim))

        if not claims:
            return None
        return claims

    def set_claim(self, claim):
        """Erstelle ein Claim Object"""
        self.config.activ_modul = "claim"
        claim_options = {}
        claim_options.update(self.k8pg_option_to_section["claim"])
        del claim_options["__section__"]
        volume = claim.replace("claim", "volume")
        spec = {"storageClassName": None,
                "accessModes":      None,
                "resources":        {"requests": {"storage": None}}}

        for option in claim_options.keys():
            self.config.copy_option_to_option(volume, claim, claim_options[option][3], to_option=option, add=claim_options[option][4], iteral=False)
            option_value = self.config.get_object(claim, option)
            if option_value is None:
                self.config.config_status = ErrorHandling.print_error_config(self.config, "%s (%s)" % (self.language[claim_options[option][5]], claim), locals(), bold=True)
                return None
            elif option_value.startswith("@v"):
                self.config.copy_option_to_option(option_value[1:], claim, claim_options[option][3], to_option=option, add=claim_options[option][4], change=True, iteral=False)

        metadata = K8Meta(name=self.config.get_object(claim, "name"))
        resource = K8Resource(requests={"storage": self.config.get_object(claim, "requests")})
        spec = K8Spec(access_modes=[self.config.get_object(claim, "accessmodes")],
                      resources=resource,
                      storage_class_name=self.config.get_object(claim, "volume_class"))

        return K8Claim(metadata=metadata, spec=spec)
