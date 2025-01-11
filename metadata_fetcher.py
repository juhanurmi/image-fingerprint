"""
This script retrieves all images from a given URL and downloads:
1. The EXIF metadata from the beginning of the image file.
2. A 5KB sample of the binary content.
The metadata are saved in JSON format.
"""
import io
import os
import json
import hashlib
import datetime
from urllib.parse import urljoin, urlparse
import requests
from PIL import Image
from PIL.ExifTags import TAGS
from bs4 import BeautifulSoup

def download_image_metadata(url):
    """Fetch image metadata."""
    if not os.path.isdir("./data/"):
        os.makedirs("./data/")
    domain_main = urlparse(url).netloc.split('.')[-2]
    if not os.path.isdir(f"./data/{domain_main}"):
        os.makedirs(f"./data/{domain_main}")
    response = requests.get(url, timeout=180)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch URL: {url}")
    soup = BeautifulSoup(response.content, "html.parser")
    img_tags = soup.find_all("img")
    results = fetch_images(img_tags, url)
    filename = hashlib.sha256(url.encode("utf-8")).hexdigest()[0:10]
    filepath = f"./data/{domain_main}/{filename}.json"
    save_results(results, filepath)

def save_results(results, filepath):
    """Save results to JSON."""
    with open(filepath, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Metadata saved to {filepath}")

def fetch_images(img_tags, base_url):
    """Process images one by one."""
    results = []
    for img_tag in img_tags:
        img_url = img_tag.get("src")
        if img_url:
            img_url = urljoin(base_url, img_url)  # Resolve full image URL
            print(f"Processing image: {img_url}")
            try:
                # Fetch only the first 5KB
                img_response = requests.get(img_url, stream=True, timeout=180,
                                            headers={"Range": "bytes=0-5120"})
                if img_response.status_code not in [200, 206]:  # 206 indicates partial content
                    continue
                img_bytes = img_response.content

                # Extract EXIF metadata
                exif_data = {}
                try:
                    img = Image.open(io.BytesIO(img_bytes))
                    exif_raw = img._getexif()
                    if exif_raw:
                        for tag, value in exif_raw.items():
                            # Convert EXIF values to JSON-serializable types
                            if isinstance(value, (bytes, bytearray)):
                                value = value.decode(errors="ignore")  # Decode bytes if possible
                            else:
                                value = str(value)  # Convert other types to string
                            exif_data[TAGS.get(tag, tag)] = value
                except Exception as error:
                    exif_data = f"Failed to extract EXIF: {str(error)}"

                # Fetch full image size (if available)
                full_size = int(img_response.headers.get("Content-Length", 0))

                # Append result
                results.append({
                    "url": img_url,
                    "image_size": full_size,
                    "exif": exif_data,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "sha256_test_5000_bytes": hashlib.sha256(img_bytes).hexdigest(),
                    #"binary_test_download": img_bytes.hex(),
                })
            except Exception as error:
                print(f"Failed to process image {img_url}: {error}")
    return results

def read_urls_from_file(file_path):
    """Reads URLs from a file and returns them as a list"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            urls = [line.strip() for line in file if line.startswith('http')]
        return urls
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as error:
        print(f"Error reading file: {error}")
        return []

if __name__ == "__main__":
    for target_url in read_urls_from_file("urls.txt"):
        download_image_metadata(target_url)
