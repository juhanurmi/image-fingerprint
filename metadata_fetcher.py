"""
This script partially downloads samples of all images from a given URL.
Extracts the EXIF metadata from the beginning of the image file and samples of the content.
Save the metadata in JSON format.
Ignore small images.
"""
import io
import os
import json
from hashlib import sha256
import datetime
from urllib.parse import urljoin, urlparse
import requests
from PIL import Image
from PIL.ExifTags import TAGS
from bs4 import BeautifulSoup

def download_image_metadata(resource_url):
    """Fetch image metadata."""
    results = []
    if "image" in head(resource_url).get("content-type", ""): # Image link
        results = fetch_images([resource_url], resource_url)
    elif "html" in head(resource_url).get("content-type", ""): # HTML page
        response = requests.get(resource_url, allow_redirects=True, timeout=60)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch URL: {resource_url}")
        soup = BeautifulSoup(response.content, "html.parser")
        img_tags = soup.find_all("img")
        results = fetch_images(img_tags, resource_url)
    save_results(results, resource_url)

def save_results(results, url):
    """Save results to JSON."""
    if not os.path.isdir("./data/"):
        os.makedirs("./data/")
    domain_main = urlparse(url).netloc.split('.')[-2]
    if not os.path.isdir(f"./data/{domain_main}"):
        os.makedirs(f"./data/{domain_main}")
    filename = sha256(url.encode("utf-8")).hexdigest()[0:10]
    filepath = f"./data/{domain_main}/{filename}.json"
    with open(filepath, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Metadata saved to {filepath}")

def partial_download(img_url, start, end):
    """Process images one by one."""
    img_bytes = b""
    try:
        response = requests.get(img_url, stream=True, allow_redirects=True, timeout=60,
                                headers={"Range": f"bytes={start}-{end}"})
        if response.status_code in [200, 206]: # 206 indicates partial content
            return response.content
        print(f"HTTP response code: {response.status_code}")
    except Exception as error:
        print(f"Partial download failed: {str(error)}")
        print(f"Bytes={start}-{end} URL: {img_url}")
    return img_bytes

def head(resource_url):
    """Process images one by one."""
    try:
        response = requests.head(resource_url, allow_redirects=True, timeout=60)
        if response.status_code in [200, 206]: # 206 indicates partial content
            return response.headers
        print(f"HTTP response code: {response.status_code}")
        return {}
    except Exception as error:
        print(f"Head failed: {str(error)}")
        print(f"URL: {resource_url}")
    return {}

def extract_metadata(start_bytes):
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
    except Exception as error:
        print(f"Failed to extract EXIF: {str(error)}")
    return exif_data

def raw_image_data(start_bytes):
    """ Extract the start of the image data """
    image_data = b""
    try:
        img = Image.open(io.BytesIO(start_bytes))
        image_content = io.BytesIO()
        img.save(image_content, format=img.format)
        image_data = image_content.getvalue()
    except Exception as error:
        print(f"Failed to extract raw image data: {str(error)}")
    return image_data

def fetch_images(img_tags, base_url):
    """Process images one by one."""
    results = []
    for img_tag in img_tags:
        if img_tags[0] == base_url:
            img_url = base_url
        else:
            img_url = img_tag.get("src")
        if img_url:
            if img_url != base_url:
                img_url = urljoin(base_url, img_url) # Resolve full image URL
            print(f"Processing image: {img_url}")
            total_size = int(head(img_url).get("Content-Length", "0"))
            if total_size < 20480: # Ignore images smaller than 20KB
                print(f"Ignore images smaller than 20480 bytes: img is {total_size} bytes")
                continue

            start_bytes = partial_download(img_url, 0, 10240) # First 10KB of the image
            if not start_bytes:
                print("Error: no start bytes to process.")
                continue
            exif_data = extract_metadata(start_bytes)
            start_sample = start_bytes[-128:].hex() # 128 bytes sample
            last_bytes = partial_download(img_url, total_size - 1024, total_size - 1) #Last 1KB
            # Generate hashes
            sha256_first_bytes = sha256(start_bytes).hexdigest()
            sha256_last_bytes = sha256(last_bytes).hexdigest() if last_bytes else None
            end_sample = last_bytes[384:512].hex() # 128 bytes sample
            # Append result
            results.append({
                "url": img_url,
                "image_size": total_size,
                "exif": exif_data,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "sha256_first_10240_bytes": sha256_first_bytes,
                "sha256_last_1024_bytes": sha256_last_bytes,
                "random_128_bytes_sample_start": start_sample,
                "random_128_bytes_sample_end": end_sample
            })
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
