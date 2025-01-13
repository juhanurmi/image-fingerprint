# Image fingerprinting without downloading the image content

This script retrieves all images from a given URL and downloads samples of the file from the beginning and the end.
The EXIF metadata is located at the beginning of the image file.
The system generates fingerprints by utilizing the image data.
Ignore small images.
The system generates a JSON file to store both the fingerprint and its metadata.

## Install

```sh
python3.6 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```sh
# Edit urls.txt url list, url line by line
python metadata_fetcher.py
ls ./data/
```

## Output

```json
[
    {
        "url": "https://exiv2.org/include/img_1771.jpg",
        "image_size": 32764,
        "exif": {
            "ResolutionUnit": "2",
            "ExifOffset": "196",
            "Make": "Canon",
            "Model": "Canon PowerShot S40",
            "Orientation": "1",
            "DateTime": "2003:12:14 12:01:44",
            "YCbCrPositioning": "1",
            "XResolution": "180.0",
            "YResolution": "180.0",
            "ExifVersion": "0220",
            "ComponentsConfiguration": "\u0001\u0002\u0003\u0000",
            "CompressedBitsPerPixel": "5.0",
            "DateTimeOriginal": "2003:12:14 12:01:44",
            "DateTimeDigitized": "2003:12:14 12:01:44",
            "ShutterSpeedValue": "8.96875",
            "ApertureValue": "4.65625",
            "ExposureBiasValue": "0.0",
            "MaxApertureValue": "2.970855712890625",
            "MeteringMode": "2",
            "Flash": "24",
            "FocalLength": "21.3125",
            "UserComment": "...",
            "ColorSpace": "1",
            "ExifImageWidth": "2272",
            "FocalPlaneXResolution": "8114.285714285715",
            "ExifImageHeight": "1704",
            "FocalPlaneYResolution": "8114.285714285715",
            "FocalPlaneResolutionUnit": "2",
            "SensingMethod": "2",
            "FileSource": "\u0003",
            "ExposureTime": "0.002",
            "ExifInteroperabilityOffset": "1416",
            "FNumber": "4.9",
            "CustomRendered": "0",
            "ExposureMode": "0",
            "FlashPixVersion": "0100",
            "WhiteBalance": "0",
            "DigitalZoomRatio": "1.0",
            "MakerNote": "...",
            "SceneCaptureType": "0"
        },
        "timestamp": "2025-01-12T10:54:29",
        "sha256_first_10240_bytes": "c629c7247153f59599727db141ee1f3c5e4a5a3cc90fa88e2e97d3d78c2fc823",
        "sha256_last_1024_bytes": "52efda24efb2b1e1534f898b382b9ecbc0747f96d7da554602bdf295a486e47b",
        "random_128_bytes_sample_start": "ef4345790e09c77cf4a2e3cc14721b0143423972c493ee4d28cb372fa5712079472efdeb8f9463f31e7e95007123e51c87eb4f18501bed9a62ef9276039d389c8c9fa52602861c8f3a7863a800dcb9e2859017511bf4a407a8a2e80b4b7b8182adb8ebfde9ceaca79e41dc11d45572394218019a9f04c258b436c7a1ec6b6c73",
         "random_128_bytes_sample_end": "cb44f02d651b15cd558b9320531417c8c9cd6b67e13138cae2ab1f819d648cd161664256f0ae0eae46a54572855551b2073a3f1fe1cd6ba1b1b1e75516e02d62f860c0b29dcf4142ce49c5757566fa3906eea7239f7a53a5d7070adfcdd0fbd7575480cc323608debb39fef5d5d4843082a46723b114a59643863a5bf9bbfbd7"
    }
]
```

# Test images

Using two random 128-byte samples (one from the start and one from the end) of an image to determine whether the image is the same is a **reasonable heuristic**, but it is not a foolproof method.

```sh
wget "https://exiv2.org/include/img_1771.jpg"

xxd -p img_1771.jpg | tr -d '\n' | grep -o "cb44f02d651b15cd558b9320531417c8c9cd6b67e13138cae2ab1f819d648cd161664256f0ae0eae46a54572855551b2073a3f1fe1cd6ba1b1b1e75516e02d62f860c0b29dcf4142ce49c5757566fa3906eea7239f7a53a5d7070adfcdd0fbd7575480cc323608debb39fef5d5d4843082a46723b114a59643863a5bf9bbfbd7"

xxd -p img_1771.jpg | tr -d '\n' | grep -o "ef4345790e09c77cf4a2e3cc14721b0143423972c493ee4d28cb372fa5712079472efdeb8f9463f31e7e95007123e51c87eb4f18501bed9a62ef9276039d389c8c9fa52602861c8f3a7863a800dcb9e2859017511bf4a407a8a2e80b4b7b8182adb8ebfde9ceaca79e41dc11d45572394218019a9f04c258b436c7a1ec6b6c73"
```

# Handle onion addresses

Install Tor and ensure the SOCKS5 proxy is available on localhost:9050.
The software will then automatically use this Tor process for onion addresses.
