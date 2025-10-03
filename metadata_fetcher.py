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

def compare_images(new_metadata, start_bytes, last_bytes):
    """ Compare a new image to the collected images """
    # 1. Read all JSON files from the collected metadata
    metadata_files = glob(f'{settings.DATA_FOLDER}*/*.json')
    # Add files from each archive directory
    for archive_dir in settings.ARCHIVE:
        metadata_files.extend(glob(f'{archive_dir}*/*.json'))
    metadata_collection = []
    for file_path in metadata_files:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                metadata = json.load(file)
                if metadata:
                    metadata_collection.append(metadata)
        except Exception as error:
            print(f"Failed to read metadata file {file_path}: {error}")
    # 2. Compare new metadata with the collected metadata
    for existing_metadata in metadata_collection:
        for metadata in existing_metadata:
            # Check if the URL matches
            new_url = new_metadata.get("url")
            url_printed = False
            if metadata.get("url") == new_url:
                if not url_printed:
                    print(f"Found match for: {new_url}")
                    url_printed = True
                print(f"URL match found: {metadata['url']}")
            # Compare SHA256 sums
            if metadata["sha256_first_10240_bytes"] == new_metadata["sha256_first_10240_bytes"]:
                if not url_printed:
                    print(f"Found match for: {new_url}")
                    url_printed = True
                print(f"Duplicate image detected based on start hash: {metadata['url']}")
            if metadata["sha256_last_1024_bytes"] == new_metadata["sha256_last_1024_bytes"]:
                if not url_printed:
                    print(f"Found match for: {new_url}")
                    url_printed = True
                print(f"Duplicate image detected based on end hash: {metadata['url']}")
            # Check if the 128-byte samples are contained within the new image's start or end bytes
            random_128 = metadata.get("random_128_bytes_sample_start", "")
            existing_start_sample = bytes.fromhex(random_128)
            random_128 = metadata.get("random_128_bytes_sample_end", "")
            existing_end_sample = bytes.fromhex(random_128)
            if existing_start_sample in start_bytes:
                if not url_printed:
                    print(f"Found match for: {new_url}")
                    url_printed = True
                print(f"128-byte sample from start matches {metadata['url']}")
            if existing_end_sample in last_bytes:
                if not url_printed:
                    print(f"Found match for: {new_url}")
                    url_printed = True
                print(f"128-byte sample from end matches {metadata['url']}")

def get_session_for_url(url):
    """
    Returns a requests session configured for the given URL.
    If the URL is an onion address, the session will use the Tor proxy.
    """
    session = requests.Session()
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
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
    results = []
    test_head = head(resource_url)
    if "image" in test_head.get("content-type", ""): # Image link
        results = fetch_images([resource_url], resource_url, test_head)
    elif settings.HTML_PARSING and "html" in test_head.get("content-type", ""): # HTML page
        session = get_session_for_url(resource_url)
        response = session.get(resource_url, allow_redirects=True, timeout=60)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch URL: {resource_url}")
        soup = BeautifulSoup(response.content, "html.parser")
        img_tags = soup.find_all("img")
        results = fetch_images(img_tags, resource_url, test_head)
    save_results(results, resource_url)

def file_path_from_url(url):
    """File path from the URL adddress"""
    if url.startswith("http"):
        main = urlparse(url).netloc.split('.')[-2]
    else:
        main = url.split('/')[-2]
    filename = sha256(url.encode("utf-8")).hexdigest()[0:10]
    return main, filename

def save_results(results, url):
    """Save results to JSON."""
    main, filename = file_path_from_url(url)
    os.makedirs(f"{settings.DATA_FOLDER}{main}", exist_ok=True)
    filepath = f"{settings.DATA_FOLDER}{main}/{filename}.json"
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
            return response.headers
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

def fetch_images(img_tags, base_url, test_head):
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
    return results

def fetch_img(img_tag, base_url, test_head):
    """Process a single image URL and return metadata."""
    if img_tag == base_url:
        img_url = base_url
    else:
        img_url = img_tag.get("src")
    if img_url:
        if img_url != base_url:
            img_url = urljoin(base_url, img_url)  # Resolve full image URL
        total_size = int(test_head.get("Content-Length", "0"))
        if total_size < settings.MIN_IMAGE_SIZE:  # Ignore small images
            return None
        start_bytes = partial_download(img_url, 0, 10240)  # First 10KB of the image
        if not start_bytes:
            return None
        print(f"Downloaded a small sample of the image: {img_url}")
        exif_data = extract_metadata(start_bytes)
        start_sample = start_bytes[-128:].hex()  # 128 bytes sample
        last_bytes = partial_download(img_url, total_size - 1024, total_size - 1)  # Last 1KB
        # Generate hashes
        sha256_first_bytes = sha256(start_bytes).hexdigest()
        sha256_last_bytes = sha256(last_bytes).hexdigest() if last_bytes else None
        end_sample = last_bytes[384:512].hex() if last_bytes else None
        metadata = {
            "url": img_url,
            "image_size": total_size,
            "exif": exif_data,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "sha256_first_10240_bytes": sha256_first_bytes,
            "sha256_last_1024_bytes": sha256_last_bytes,
            "random_128_bytes_sample_start": start_sample,
            "random_128_bytes_sample_end": end_sample,
        }
        compare_images(metadata, start_bytes, last_bytes)
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
        with open(image_path, "rb") as file:
            if total_size >= 1024:
                file.seek(total_size - 1024)
                last_bytes = file.read(1024)
            else:
                last_bytes = b""
        sha256_first_bytes = sha256(start_bytes).hexdigest()
        sha256_last_bytes = sha256(last_bytes).hexdigest() if last_bytes else None
        end_sample = last_bytes[384:512].hex() if last_bytes and len(last_bytes) >= 512 else None
        metadata = {
            "url": image_path,
            "image_size": total_size,
            "exif": exif_data,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "sha256_first_10240_bytes": sha256_first_bytes,
            "sha256_last_1024_bytes": sha256_last_bytes,
            "random_128_bytes_sample_start": start_sample,
            "random_128_bytes_sample_end": end_sample,
        }
        compare_images(metadata, start_bytes, last_bytes)
        return metadata
    except Exception as e:
        print(f"Failed to process local image {image_path}: {e}")
        return None

def read_urls_from_file(file_path):
    """Reads URLs from a file and returns them as a list"""
    try:
        urls = []
        with open(file_path, "r", encoding="utf-8") as file:
            urls = []
            for line in file:
                if line.startswith('http'):
                    url = line.strip()
                    main, filename = file_path_from_url(url)
                    if not os.path.isfile(f"{settings.DATA_FOLDER}{main}/{filename}.json"):
                        if not url in urls:
                            urls.append(url)
        if not urls:
            print(f"No new (not already scanned) URLs in a file: {file_path}")
        return urls
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as error:
        print(f"Error reading file: {error}")
        return []

if __name__ == "__main__":
    if settings.TEST_IMAGES_FOLDER and os.path.exists(settings.TEST_IMAGES_FOLDER):
        images = glob(f'{settings.TEST_IMAGES_FOLDER}*')
        if images:
            local_image_metadata_list = []
            for image in images:
                metadata_item = process_image_file(image)
                if metadata_item:
                    local_image_metadata_list.append(metadata_item)
            if local_image_metadata_list:
                save_results(local_image_metadata_list, settings.TEST_IMAGES_FOLDER)
    if settings.URL_FILE and os.path.isfile(settings.URL_FILE):
        url_list = read_urls_from_file(settings.URL_FILE)
        with ThreadPoolExecutor(max_workers=settings.MAX_THREADS) as exe: # Use the thread limit
            future_list = {exe.submit(download_image_metadata, url): url for url in url_list}
            for fut in as_completed(future_list):
                fut.result()
