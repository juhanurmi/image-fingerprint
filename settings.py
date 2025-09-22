""" Settings for the image downloading and processing """
# Minimun image size: ignore images smaller than 20KB
MIN_IMAGE_SIZE = 20480 # 20480 bytes
assert MIN_IMAGE_SIZE > 20000

# Tor SOCKS proxy for onion addresses
PROXIES = [ # socks5h or http or https
    {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"},
    #{"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"},
    ]

#PROXIES = []
#for port in range(15000, 15100):
#    PROXIES.append({"http": f"http://127.0.0.1:{port}",
#                    "https": f"http://127.0.0.1:{port}"})

# Data folder
DATA_FOLDER = "./data/" # end with a "/"
assert DATA_FOLDER.endswith("/")

# Define archive directories, ensuring they end with a "/"
ARCHIVE = ["./archive", "./sample"]  # Initial list
ARCHIVE = [dir if dir.endswith("/") else f"{dir}/" for dir in ARCHIVE]

# Only images, no HTML parsing
HTML_PARSING = True

# URL list file
URL_FILE = "urls.txt"

# List of local image files to test
TEST_IMAGES_FOLDER = "./test_images/"
assert TEST_IMAGES_FOLDER.endswith("/")

# Define the number of parallel download threads
MAX_THREADS = 10
assert MAX_THREADS > 0
assert MAX_THREADS < 50

# Max images per a domain to download
MAX_IMG_PER_DOMAIN = 30
