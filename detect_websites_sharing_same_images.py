"""
Detect shared image files across domains based on 'sha256_first_10240_bytes'
from JSON metadata files (e.g., ./archive/**.json).
Output: groups of domains that share identical image samples.
"""
import json
from glob import glob
from collections import defaultdict
from urllib.parse import urlparse
import settings # Import the settings from settings.py

def extract_domain_from_url(url):
    """Extract main domain part, e.g., 'example.org' -> 'example'"""
    if url.startswith("http"):
        host = urlparse(url).netloc
        parts = host.split(".")
        if len(parts) >= 2:
            return parts[-2]  # main part before TLD
        return parts[0]
    if url.count("/") > 1:
        return host.split("/")[-2]
    print(f"Error with URL/filepath {url}", flush=True)
    return None

def load_hashes():
    """Load sha256_first_10240_bytes from all JSON files and map to domains."""
    hash_to_domains = defaultdict(set)
    folders = settings.ARCHIVE + [settings.DATA_FOLDER]
    json_files = []
    for folder in folders:
        json_files = json_files + glob(f"{folder}/**/*.json", recursive=True)
    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Some files contain a list, others a single dict
            if isinstance(data, dict):
                data = [data]
            for item in data:
                h = item.get("sha256_first_10240_bytes")
                url = item.get("url", "")
                if not h or not url:
                    continue
                domain = extract_domain_from_url(url)
                hash_to_domains[h].add(domain)
        except Exception as e:
            print(f"Failed to parse {file_path}: {e}", flush=True)
    return hash_to_domains

def group_by_domain_sets(hash_to_domains):
    """
    Group hashes that are shared by the exact same set of domains.
    Returns: dict with frozenset(domains) → [hashes].
    """
    groups = defaultdict(list)
    for h, domains in hash_to_domains.items():
        if len(domains) > 1:  # only shared images
            key = frozenset(domains)
            groups[key].append(h)
    return groups

def main():
    """ Main """
    hash_to_domains = load_hashes()
    grouped = group_by_domain_sets(hash_to_domains)
    print(f"\nFound {len(grouped)} domain groups sharing identical images:\n", flush=True)
    for domains, hashes in sorted(grouped.items(), key=lambda x: -len(x[1])):
        print("-" * 80)
        print(f"{len(hashes)} identical images between the domains:", flush=True)
        for h in hashes:
            print(f"image hash: {h}", flush=True)
        print("Domains:", flush=True)
        for d in sorted(domains):
            print(d)
        print("-" * 80)

if __name__ == "__main__":
    main()
