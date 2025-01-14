""" Settings for the image downloading and processing """
# Minimun image size: ignore images smaller than 20KB
MIN_IMAGE_SIZE = 20480 # 20480 bytes
assert MIN_IMAGE_SIZE > 20000

# Tor SOCKS proxy for onion addresses
PROXIES = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

# Data folder
DATA_FOLDER = "./data/" # Use the end /
assert DATA_FOLDER.endswith("/")

# URL list file
URL_FILE = "urls.txt"
