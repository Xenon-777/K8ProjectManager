#

from pprint import pprint
from traceback import extract_stack, format_list

from k8projectmanager.k8pm_sub_methoden.sub_color import Color


class ErrorHandling(object):
    @staticmethod
    def print_error(text, error_vars=None, bold=False, verbose=False):
        if verbose:
            frame_list = extract_stack()
            for frame in format_list(frame_list[:-1]):
                frame = frame.split(",", 2)
                frame = frame[:-1] + frame[-1].split("\n")
                if not frame[3].strip().startswith("ErrorHandling."):
                    print("%s in %s %s: %s" % (frame[0].strip(), frame[1].strip(), frame[2].strip(), frame[3].strip()))
        if bold:
            print("\n%s!!! %s !!!%s\n" % (Color.BOLD, text, Color.END))
        else:
            print("\n!!! %s !!!\n" % text)
        if error_vars is not None and verbose:
            print("___ local definirte Variable ___")
            for var in error_vars.keys():
                if not (var == "self" or var == "e"):
                    print("%s: %s" % (var, error_vars[var]))
        return False

    @staticmethod
    def pprint_to_dic(print_object):
        try:
            pprint(print_object.to_dict())
        except AttributeError as e:
            print("Print fail: %s" % e)

    @staticmethod
    def print_error_config(config, text, static_var=None, bold=False):
        ErrorHandling.print_error(text, static_var, bold, config.verbose)
        if config.verbose:
            config.format_print()
        return False

    @staticmethod
    def print_K8Exection(config, error, text, head):
        if error["code"] == 409:
            return False
        print(Color.color_text(" %s " % head, Color.BLINK, long=70, fill="#"))
        ErrorHandling.print_error_config(config, "%s:" % text, locals())
        print("%s Code:%i (API %s)\n" % (error["status"], error["code"], error["apiVersion"]))
        print(error["message"])
        if "details" in error.keys():
            print("\nName: %s (Type: %s)" % (error["details"]["name"], error["details"]["kind"]))
            if "causes" in error["details"].keys():
                for item in error["details"]["causes"]:
                    print("\n  %s in Field: %s\n" % (item["reason"], item["field"]))
                    print(item["message"])
        print("")
        print(Color.color_text("", Color.BLINK, long=70, fill="#"))
        print("")
        return True

    @staticmethod
    def check_parameter(parameter, vorgabe):
        vorgabe_dict = {"Text":        ErrorHandling.test_text,
                        "Zahl":        ErrorHandling.test_zahl,
                        "URL/IP":      ErrorHandling.test_url,
                        "Path":        ErrorHandling.test_path,
                        "Text_List":   ErrorHandling.test_true,
                        "Zahlen_List": ErrorHandling.test_zahl_list,
                        "IP":          ErrorHandling.test_url,
                        "IP_List":     ErrorHandling.test_true,
                        "File":        ErrorHandling.test_true}
        if vorgabe.startswith("Text."):
            methode = vorgabe_dict.get("Text")
            return methode(parameter=parameter, vorgabe=vorgabe)
        elif vorgabe.endswith("@"):
            if str(parameter).startswith("@"):
                methode = vorgabe_dict.get("Text")
                return methode(parameter=parameter, vorgabe=vorgabe)
            else:
                methode = vorgabe_dict.get(vorgabe[:-1])
                return methode(parameter=parameter, vorgabe=vorgabe)
        else:
            methode = vorgabe_dict.get(vorgabe, None)
            if methode is None:
                if parameter in vorgabe.split(","):
                    return True
                else:
                    return False
            return methode(parameter=parameter, vorgabe=vorgabe)

    @staticmethod
    def test_text(**kwargs):
        if kwargs.get("vorgabe").find(".") > -1:
            vorgabe = kwargs.get("vorgabe").split(".")
            if not kwargs.get("parameter").endswith(vorgabe[1]):
                return False
        return True

    @staticmethod
    def test_zahl(**kwargs):
        return str(kwargs.get("parameter")).isnumeric()

    @staticmethod
    def test_url(**kwargs):
        # return kwargs.get("parameter").find(".") < 2
        return True

    @staticmethod
    def test_path(**kwargs):
        return kwargs.get("parameter").find("/") < 1

    @staticmethod
    def test_true(**kwargs):
        return True

    @staticmethod
    def test_zahl_list(**kwargs):
        parameters = kwargs.get("parameter").split(",")
        for parameter in parameters:
            if not parameter.isnumeric():
                return False
        return True
