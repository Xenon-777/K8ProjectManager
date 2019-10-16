#


class Color(object):
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    BLINK = '\033[5m'

    @staticmethod
    def color_text(text, color=None, long=0, fill=" "):
        if long > len(text):
            text = text.center(long, fill)
        if color is not None:
            text = color + text + '\033[0m'
        return text
