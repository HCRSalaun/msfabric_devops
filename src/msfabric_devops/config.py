import os

SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]
POWERBI_API_BASE = "https://api.powerbi.com/v1.0/myorg"
API_URL = "https://api.fabric.microsoft.com/v1"
RESOURCE_URL = "https://api.fabric.microsoft.com"
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
SEMANTIC_MODEL_ID = os.getenv("SEMANTIC_MODEL_ID")


def print_color(text, color="white", bold=False, bg=None):
    """
    Print colored text using ANSI escape codes.

    Parameters:
        text (str): Text to print
        color (str): Text color ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
        bold (bool): If True, make text bold
        bg (str): Background color (same names as text color)
    """
    colors = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37
    }

    # Text color code
    color_code = colors.get(color.lower(), 37)
    # Bold code
    bold_code = "1;" if bold else ""
    # Background color code
    bg_code = ""
    if bg:
        bg_num = colors.get(bg.lower(), 37) - 30 + 40  # convert fg code to bg code
        bg_code = f";{bg_num}"

    print(f"\033[{bold_code}{color_code}{bg_code}m{text}\033[0m")
