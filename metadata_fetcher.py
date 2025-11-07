"""
This script partially downloads samples of all images from a given URL.
Extracts the EXIF metadata from the beginning of the image file and samples of the content.
Save the metadata in JSON format.
Ignore small images.
"""
import io
import os
import json
from hashlib import sha256, blake2b
import datetime
import threading
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from glob import glob
import requests
import piexif
import exifread
from PIL import Image
from PIL.ExifTags import TAGS
from bs4 import BeautifulSoup
import settings # Import the settings from settings.py

METADATA_CACHE = {} # Global cache of metadata from JSON files
METADATA_LOCK = threading.Lock()

def load_all_metadata(new_metadata=None):
    """Load all JSON metadata files only once into the global cache."""
    global METADATA_CACHE
    # Always protect cache operations with the lock
    with METADATA_LOCK: # Lock
        if METADATA_CACHE:
            if new_metadata and not new_metadata["url"] in METADATA_CACHE:
                METADATA_CACHE[new_metadata["url"]] = [new_metadata]
            return METADATA_CACHE.copy()
        # Else, download from the folder
        metadata_files = glob(f"{settings.DATA_FOLDER}*/*.json")
        for archive_dir in settings.ARCHIVE:
            metadata_files.extend(glob(f"{archive_dir}*/*.json"))
        for json_file_path in metadata_files:
            try:
                with open(json_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    METADATA_CACHE[json_file_path] = data
            except Exception as error:
                print(f"Failed to load {json_file_path}: {error}", flush=True)
        print(f"Loaded {len(METADATA_CACHE)} metadata files into cache.", flush=True)
        if new_metadata and not new_metadata["url"] in METADATA_CACHE:
            METADATA_CACHE[new_metadata["url"]] = [new_metadata]
        # Return a shallow copy so other threads can iterate safely
        return METADATA_CACHE.copy()

def compare_images(new_metadata, start_bytes=None):
    """ Compare a new image to the collected images """
    # Compare new metadata with the collected metadata, read all JSON files
    all_metadata = load_all_metadata(new_metadata)
    url_printed = False
    for file_path, metadata_list in all_metadata.items():
        for metadata in metadata_list:
            # Check if the URL matches
            new_url = new_metadata.get("url")
            if metadata.get("url") == new_url:
                continue # Same URL, same image, do not compare the same images!
            # Compare SHA256 sums
            if metadata.get("sha256_first_10240_bytes", 1) == new_metadata.get("sha256_first_10240_bytes", 2):
                if not url_printed:
                    print(f"\n{'-'*120}", flush=True)
                    print(f"Found match for the new image:\n{new_url}\n", flush=True)
                    url_printed = True
                print(f"Duplicate image based on the hash:\n\t{metadata['url']}  -->  {file_path}", flush=True)
            # Compare etags
            if metadata.get("etag", 1) == new_metadata.get("etag", 2):
                if not url_printed:
                    print(f"\n{'-'*120}", flush=True)
                    print(f"Found match for the new image:\n{new_url}\n", flush=True)
                    url_printed = True
                print(f"Duplicate image detected based on etag:\n\t{metadata['url']}  -->  {file_path}", flush=True)
            # Check if the 128-byte sample is within the new image's start
            random_128 = metadata.get("random_128_bytes_sample_start", "")
            if start_bytes and random_128:
                # Detect if the existing sample is empty padding, mostly zeros
                zero_ratio = random_128.count("0") / len(random_128)
                if zero_ratio < 0.9: # it is not mostly zeros (more than 90% non-zeros)
                    existing_start_sample = bytes.fromhex(random_128)
                    if existing_start_sample in start_bytes:
                        if not url_printed:
                            print(f"\n{'-'*120}", flush=True)
                            print(f"Found match for the new image:\n{new_url}\n", flush=True)
                            url_printed = True
                        print(f"128-byte sample matches:\n\t{metadata['url']}  -->  {file_path}", flush=True)
    if url_printed:
        print(f"{'-'*120}", flush=True)

def get_session_for_url(url):
    """
    Returns a requests session configured for the given URL.
    If the URL is an onion address, the session will use the Tor proxy.
    """
    session = requests.Session()
    ua = getattr(settings, "USER_AGENT", None)
    if ua:
        session.headers.setdefault("User-Agent", ua)
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    if domain.endswith(".onion"):
        # Always select the same proxy for the same onion domain
        # This will keep only one underlining Tor circuit to the onion service
        # Onion addresses form an uniform distribution
        # Deterministic, side-effect-free selection
        h = blake2b(domain.encode('utf-8'), digest_size=8).digest()
        index = int.from_bytes(h, 'big') % len(settings.PROXIES)
        # Always select the same proxy for the same onion address
        session.proxies = settings.PROXIES[index]
    return session

def download_image_metadata(resource_url):
    """Fetch image metadata."""
    test_head = head(resource_url)
    if "image" in test_head.get("content-type", ""): # Image link
        fetch_images([resource_url], resource_url, test_head)
    elif settings.HTML_PARSING and "html" in test_head.get("content-type", ""): # HTML page
        session = get_session_for_url(resource_url)
        response = session.get(resource_url, allow_redirects=True, timeout=60)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch URL: {resource_url}")
        soup = BeautifulSoup(response.content, "html.parser")
        img_tags = soup.find_all("img")
        fetch_images(img_tags, resource_url)

def file_path_from_url(url):
    """File path from the URL adddress"""
    if url.startswith("http"):
        folder = urlparse(url).netloc.split('.')[-2]
    else:
        folder = url.split('/')[-2]
    filename = sha256(url.encode("utf-8")).hexdigest()[0:10]
    return folder, filename

def save_results(results, url):
    """Save results to JSON."""
    folder, filename = file_path_from_url(url)
    os.makedirs(f"{settings.DATA_FOLDER}{folder}", exist_ok=True)
    filepath = f"{settings.DATA_FOLDER}{folder}/{filename}.json"
    with open(filepath, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=4)

def partial_download(img_url, start, end):
    """Download a partial range of bytes from the image."""
    img_bytes = b""
    try:
        session = get_session_for_url(img_url)
        response = session.get(
            img_url,
            stream=True,
            allow_redirects=True,
            timeout=60,
            headers={"Range": f"bytes={start}-{end}"}
        )
        if response.status_code in [200, 206]:  # 206 indicates partial content
            return response.content
        return img_bytes
    except Exception:
        return img_bytes

def head(resource_url):
    """Send a HEAD request to the resource."""
    try:
        session = get_session_for_url(resource_url)
        response = session.head(resource_url, allow_redirects=True, timeout=60)
        if response.status_code in [200, 206]:  # 206 indicates partial content
            return {k.lower(): v for k, v in response.headers.items()}
        return {}
    except Exception:
        return {}

def extract_pil(start_bytes):
    ''' Extract EXIF metadata '''
    exif_data = {}
    try:
        img = Image.open(io.BytesIO(start_bytes))
        exif_raw = img._getexif()
        if exif_raw:
            for tag, value in exif_raw.items():
                # Convert EXIF values to JSON-serializable types
                if isinstance(value, (bytes, bytearray)):
                    value = value.decode(errors="ignore")  # Decode bytes if possible
                else:
                    value = str(value)  # Convert other types to string
                exif_data[TAGS.get(tag, tag)] = value
        return exif_data
    except Exception:
        return exif_data

def clean_etag(etag):
    """Clean etag"""
    if not etag:
        return None
    etag = etag.strip()
    if etag.startswith('W/'):
        etag = etag[2:].strip()
    if etag.startswith('"') and etag.endswith('"'):
        etag = etag[1:-1]
    return etag

def extract_piexif(start_bytes):
    """Extract EXIF metadata using piexif."""
    exif_data = {}
    try:
        exif_dict = piexif.load(start_bytes)
        for ifd_name in exif_dict:
            json_data = sanitize_for_json(exif_dict[ifd_name])
            for tag, value in json_data.items():
                tag_name = piexif.TAGS[ifd_name][tag]["name"]
                # Convert bytes to strings if necessary
                if isinstance(value, bytes):
                    try:
                        value = value.decode(errors="ignore")  # Attempt to decode bytes
                    except Exception:
                        value = str(value)  # Fallback: Convert to string representation
                exif_data[tag_name] = value
        return exif_data
    except Exception:
        return exif_data

def extract_metadata_with_exif_py(start_bytes):
    """Extract EXIF metadata using the exif-py library."""
    exif_data = {}
    try:
        # Parse EXIF tags from the given image bytes
        tags = exifread.process_file(io.BytesIO(start_bytes), details=False)
        for tag, value in tags.items():
            # Convert tag values to strings to ensure JSON serialization
            exif_data[tag] = str(value)
        return exif_data
    except Exception:
        return exif_data

def extract_metadata(start_bytes):
    """Manually extract EXIF metadata from a JPEG """
    exif_data = {}
    exif_data = extract_metadata_with_exif_py(start_bytes)
    if not exif_data:
        exif_data = extract_pil(start_bytes)
    if not exif_data:
        exif_data = extract_piexif(start_bytes)
    if not exif_data:
        if b"Exif" in start_bytes: # Check for APP1 segment containing EXIF metadata
            exif_start = start_bytes.find(b"Exif") + 6 # Start after "Exif\0\0"
            start_bytes = start_bytes[exif_start:] # Extract potential EXIF segment
            exif_data = extract_metadata_with_exif_py(start_bytes)
            if not exif_data:
                exif_data = extract_pil(start_bytes)
            if not exif_data:
                exif_data = extract_piexif(start_bytes)
    return exif_data

def sanitize_for_json(obj):
    """Recursively convert non-JSON-serializable types (like bytes) to strings."""
    if isinstance(obj, bytes):
        return obj.decode(errors="ignore")  # Convert bytes to string
    if isinstance(obj, dict):
        return {key: sanitize_for_json(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    return obj  # Return other types unchanged

def raw_image_data(start_bytes):
    """ Extract the start of the image data """
    image_data = b""
    try:
        img = Image.open(io.BytesIO(start_bytes))
        image_content = io.BytesIO()
        img.save(image_content, format=img.format)
        image_data = image_content.getvalue()
        return image_data
    except Exception:
        return image_data

def fetch_images(img_tags, base_url, test_head=None):
    """Process images concurrently."""
    results = []
    max_workers = settings.MAX_THREADS  # Define the number of parallel threads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks for each image
        max_img = settings.MAX_IMG_PER_DOMAIN
        future_to_img = {
            executor.submit(fetch_img, img, base_url, test_head): img for img in img_tags[:max_img]
        }
        for future in as_completed(future_to_img):
            result = future.result()
            if result:
                results.append(result)
    save_results(results, base_url)

def fetch_img(img_tag, base_url, test_head=None):
    """Process a single image URL and return metadata."""
    if img_tag == base_url:
        img_url = base_url
    else:
        img_url = img_tag.get("src")
    if img_url:
        if img_url != base_url:
            img_url = urljoin(base_url, img_url)  # Resolve full image URL
        if not test_head:
            test_head = head(img_url)
        total_size = int(test_head.get("content-length", "0"))
        metadata = {
            "url": img_url,
            "image_size": total_size,
            "etag": clean_etag(test_head.get("etag", "")),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        }
        start_bytes = None
        if total_size >= settings.MIN_IMAGE_SIZE:  # Ignore small images
            start_bytes = partial_download(img_url, 0, 10240)  # First 10KB of the image
            if start_bytes:
                print(f"Downloaded a small sample of the image: {img_url}", flush=True)
                metadata["exif"] = extract_metadata(start_bytes)
                metadata["sha256_first_10240_bytes"] = sha256(start_bytes).hexdigest()
                # 128 bytes sample
                metadata["random_128_bytes_sample_start"] = start_bytes[-128:].hex()
        compare_images(metadata, start_bytes)
        return metadata
    return None

def process_image_file(image_path):
    """Process a local image file and return metadata."""
    try:
        total_size = os.path.getsize(image_path)
        if total_size < settings.MIN_IMAGE_SIZE: # Ignore small images
            return None
        with open(image_path, "rb") as file:
            start_bytes = file.read(10240)  # First 10KB
        if not start_bytes:
            return None
        exif_data = extract_metadata(start_bytes)
        start_sample = start_bytes[-128:].hex()  # 128 bytes sample from end of start_bytes
        sha256_first_bytes = sha256(start_bytes).hexdigest()
        metadata = {
            "url": image_path,
            "image_size": total_size,
            "exif": exif_data,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "sha256_first_10240_bytes": sha256_first_bytes,
            "random_128_bytes_sample_start": start_sample,
        }
        compare_images(metadata, start_bytes)
        return metadata
    except Exception as e:
        print(f"Failed to process local image {image_path}: {e}", flush=True)
        return None

def read_urls_from_file(file_path):
    """Reads URLs from a file and returns them as a list"""
    try:
        urls = []
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith('http'):
                    url = line.split()[0].strip()
                    folder, filename = file_path_from_url(url)
                    if os.path.isfile(f"{settings.DATA_FOLDER}{folder}/{filename}.json"):
                        continue # Already downloaded
                    urls.append(url)
        urls = list(set(urls))
        if not urls:
            print(f"No new (not already scanned) URLs in a file: {file_path}", flush=True)
        else:
            print(f"Loaded {len(urls)} new URLs from a file: {file_path}", flush=True)
        return urls
    except FileNotFoundError:
        print(f"File not found: {file_path}", flush=True)
        return []
    except Exception as error:
        print(f"Error reading file: {error}", flush=True)
        return []

def main():
    """ Main function """
    if settings.ONLY_COMPARE_EXISTING_DATA:
        all_metadata = load_all_metadata()
        for _, metadata_list in all_metadata.items():
            for metadata in metadata_list:
                compare_images(metadata)
        return
    if settings.TEST_IMAGES_FOLDER and os.path.exists(settings.TEST_IMAGES_FOLDER):
        images = glob(f'{settings.TEST_IMAGES_FOLDER}*')
        for image in images:
            folder, filename = file_path_from_url(image)
            if os.path.isfile(f"{settings.DATA_FOLDER}{folder}/{filename}.json"):
                continue # Already processed
            metadata_item = process_image_file(image)
            if metadata_item:
                save_results([metadata_item], image)
    if settings.URL_FILE and os.path.isfile(settings.URL_FILE):
        url_list = read_urls_from_file(settings.URL_FILE)
        with ThreadPoolExecutor(max_workers=settings.MAX_THREADS) as exe: # Use the thread limit
            future_list = {exe.submit(download_image_metadata, url): url for url in url_list}
            for fut in as_completed(future_list):
                fut.result()

if __name__ == "__main__":
    main()
