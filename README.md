# Image fingerprinting without downloading the image content

This script retrieves all images from a given URL and downloads samples of the file from the beginning.
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
# Edit settings.py
# Edit urls.txt url list, url line by line
python metadata_fetcher.py
ls ./data/
```

## Outputs

```json
[
    {
        "url": "https://exiv2.org/include/img_1771.jpg",
        "image_size": 32764,
        "etag": "68b420a9-7ffc",
        "timestamp": "2025-11-03T10:14:42",
        "exif": {
            "Image Make": "Canon",
            "Image Model": "Canon PowerShot S40",
            "Image Orientation": "Horizontal (normal)",
            "Image XResolution": "180",
            "Image YResolution": "180",
            "Image ResolutionUnit": "Pixels/Inch",
            "Image DateTime": "2003:12:14 12:01:44",
            "Image YCbCrPositioning": "Centered",
            "Image ExifOffset": "196",
            "Thumbnail Compression": "JPEG (old-style)",
            "Thumbnail XResolution": "180",
            "Thumbnail YResolution": "180",
            "Thumbnail ResolutionUnit": "Pixels/Inch",
            "Thumbnail JPEGInterchangeFormat": "2036",
            "Thumbnail JPEGInterchangeFormatLength": "5448",
            "EXIF ExposureTime": "1/500",
            "EXIF FNumber": "49/10",
            "EXIF ExifVersion": "0220",
            "EXIF DateTimeOriginal": "2003:12:14 12:01:44",
            "EXIF DateTimeDigitized": "2003:12:14 12:01:44",
            "EXIF ComponentsConfiguration": "YCbCr",
            "EXIF CompressedBitsPerPixel": "5",
            "EXIF ShutterSpeedValue": "287/32",
            "EXIF ApertureValue": "149/32",
            "EXIF ExposureBiasValue": "0",
            "EXIF MaxApertureValue": "97349/32768",
            "EXIF MeteringMode": "CenterWeightedAverage",
            "EXIF Flash": "Flash did not fire, auto mode",
            "EXIF FocalLength": "341/16",
            "EXIF FlashPixVersion": "0100",
            "EXIF ColorSpace": "sRGB",
            "EXIF ExifImageWidth": "2272",
            "EXIF ExifImageLength": "1704",
            "Interoperability InteroperabilityIndex": "R98",
            "Interoperability InteroperabilityVersion": "[48, 49, 48, 48]",
            "Interoperability RelatedImageWidth": "2272",
            "Interoperability RelatedImageLength": "1704",
            "EXIF InteroperabilityOffset": "1416",
            "EXIF FocalPlaneXResolution": "56800/7",
            "EXIF FocalPlaneYResolution": "56800/7",
            "EXIF FocalPlaneResolutionUnit": "2",
            "EXIF SensingMethod": "One-chip color area",
            "EXIF FileSource": "Digital Camera",
            "EXIF CustomRendered": "Normal",
            "EXIF ExposureMode": "Auto Exposure",
            "EXIF WhiteBalance": "Auto",
            "EXIF DigitalZoomRatio": "1",
            "EXIF SceneCaptureType": "Standard"
        },
        "sha256_first_10240_bytes": "c629c7247153f59599727db141ee1f3c5e4a5a3cc90fa88e2e97d3d78c2fc823",
        "random_128_bytes_sample_start": "ef4345790e09c77cf4a2e3cc14721b0143423972c493ee4d28cb372fa5712079472efdeb8f9463f31e7e95007123e51c87eb4f18501bed9a62ef9276039d389c8c9fa52602861c8f3a7863a800dcb9e2859017511bf4a407a8a2e80b4b7b8182adb8ebfde9ceaca79e41dc11d45572394218019a9f04c258b436c7a1ec6b6c73"
    }
]
```

```json
[
    {
        "url": "http://natural3jytxrhh5wqmpcz67yumyptr7pn2c52hppvn3vanmqzjlkryd.onion/images/printer-3D-gun.jpg",
        "image_size": 1104883,
        "etag": "801ca4a79531db1:0",
        "timestamp": "2025-11-03T10:14:44",
        "exif": {
            "Image ImageWidth": "4032",
            "Image ImageLength": "3024",
            "Image BitsPerSample": "[8, 8, 8]",
            "Image PhotometricInterpretation": "2",
            "Image Make": "Apple",
            "Image Model": "iPhone 7",
            "Image Orientation": "Horizontal (normal)",
            "Image SamplesPerPixel": "3",
            "Image XResolution": "72",
            "Image YResolution": "72",
            "Image ResolutionUnit": "Pixels/Inch",
            "Image Software": "Adobe Photoshop CC 2014 (Windows)",
            "Image DateTime": "2017:03:01 10:00:35",
            "Image YCbCrPositioning": "Centered",
            "Image ExifOffset": "300",
            "GPS GPSLatitudeRef": "N",
            "GPS GPSLatitude": "[40, 56, 3829/100]",
            "GPS GPSLongitudeRef": "W",
            "GPS GPSLongitude": "[74, 32, 159/5]",
            "GPS GPSAltitudeRef": "0",
            "GPS GPSAltitude": "94177/345",
            "GPS GPSTimeStamp": "[21, 3, 1137/100]",
            "GPS GPSSpeedRef": "K",
            "GPS GPSSpeed": "0",
            "GPS GPSImgDirectionRef": "T",
            "GPS GPSImgDirection": "96419/335",
            "GPS GPSDestBearingRef": "T",
            "GPS GPSDestBearing": "96419/335",
            "GPS GPSDate": "2016:11:16",
            "GPS Tag 0x001F": "165",
            "Image GPSInfo": "856",
            "Thumbnail Compression": "JPEG (old-style)",
            "Thumbnail XResolution": "72",
            "Thumbnail YResolution": "72",
            "Thumbnail ResolutionUnit": "Pixels/Inch",
            "Thumbnail JPEGInterchangeFormat": "1262",
            "Thumbnail JPEGInterchangeFormatLength": "5231",
            "EXIF ExposureTime": "1/30",
            "EXIF FNumber": "9/5",
            "EXIF ExposureProgram": "Program Normal",
            "EXIF ISOSpeedRatings": "25",
            "EXIF ExifVersion": "0221",
            "EXIF DateTimeOriginal": "2016:11:16 16:03:15",
            "EXIF DateTimeDigitized": "2016:11:16 16:03:15",
            "EXIF ComponentsConfiguration": "YCbCr",
            "EXIF ShutterSpeedValue": "4143/844",
            "EXIF ApertureValue": "2159/1273",
            "EXIF BrightnessValue": "3110/673",
            "EXIF ExposureBiasValue": "0",
            "EXIF MeteringMode": "Pattern",
            "EXIF Flash": "Flash did not fire, auto mode",
            "EXIF FocalLength": "399/100",
            "EXIF SubjectArea": "[2015, 1511, 2217, 1330]",
            "EXIF SubSecTimeOriginal": "468",
            "EXIF SubSecTimeDigitized": "468",
            "EXIF FlashPixVersion": "0100",
            "EXIF ColorSpace": "Uncalibrated",
            "EXIF ExifImageWidth": "2000",
            "EXIF ExifImageLength": "1500",
            "EXIF SensingMethod": "One-chip color area",
            "EXIF SceneType": "Directly Photographed",
            "EXIF ExposureMode": "Auto Exposure",
            "EXIF WhiteBalance": "Auto",
            "EXIF FocalLengthIn35mmFilm": "28",
            "EXIF SceneCaptureType": "Standard",
            "EXIF LensSpecification": "[399/100, 399/100, 9/5, 9/5]",
            "EXIF LensMake": "Apple",
            "EXIF LensModel": "iPhone 7 back camera 3.99mm f/1.8"
        },
        "sha256_first_10240_bytes": "adf9ea1f2265b3d56827be6b29397c5e6c430bfda8d1e29869fe920a7fa2e114",
        "random_128_bytes_sample_start": "43848e755a2e68417b279494e6fd9d80c8099cdd215c7307282f6a0a7fffd0e1acc6b8badaf5add537d4075dbb810c6b1da96fe967d8e5a7d0f1727af5f8d43b1dce762d8c36643d93536a6387ab4e46f1b2cf6eeaf1ebff00ac7f33fcc56ce7e6f4fc815651f49f582df49fa308fa2e0dfccb1abb3fa8983d43ec77e45adb2a"
    }
]
```

# Test images

Using a random 128-byte sample of an image to determine whether the image is the same is a **reasonable heuristic**,
but it is not a foolproof method to fingerprint the images and compare them as duplicates.

```sh
wget "https://exiv2.org/include/img_1771.jpg"

xxd -p img_1771.jpg | tr -d '\n' | grep -o "ef4345790e09c77cf4a2e3cc14721b0143423972c493ee4d28cb372fa5712079472efdeb8f9463f31e7e95007123e51c87eb4f18501bed9a62ef9276039d389c8c9fa52602861c8f3a7863a800dcb9e2859017511bf4a407a8a2e80b4b7b8182adb8ebfde9ceaca79e41dc11d45572394218019a9f04c258b436c7a1ec6b6c73"
```

**The raw 128-byte sample is effectively random data and do not provide a human-readable or visually interpreted representation of the image.**
The script only processes images larger than 20 KB (20,480 bytes), saving metadata and only a 128-byte sample, representing a small fraction of the total image size, less than 1%.
It contains compressed image data, not raw pixel values, and are not directly interpreted as pixels.
Depending on the compression algorithm, this may include encoded color or luminance information for specific regions of the image.

# Handle onion addresses

Install Tor and ensure the SOCKS5 proxy is available on localhost:9050.
The software will then automatically use this Tor process for onion addresses.

# Test: Is the hash of the beginning of an image data a reliable duplicate detection method?

To evaluate the reliability of using a hash of the first bytes of image files for duplicate detection,
download the **Stanford Dogs Dataset** (20,580 images) from [FishNet.ai](http://vision.stanford.edu/aditya86/ImageNetDogs/).
Extract `.jpg` files to the `./test_images/` directory and process with the metadata extraction script.

As expected, the system successfully detected all duplicate images, all of which were true positives. Moreover, it does not produce any false positives. The duplicates originate from identical images appearing under different filenames within the dataset, totaling **178 real confirmed duplicates**.
(I.e., see `n02093428-American_Staffordshire_terrier/n02093428_5635.jpg` and `n02093256-Staffordshire_bullterrier/n02093256_4090.jpg`, these are identical with the same MD5 checksum `b5bf240a9b92914f5bb93b4c703bf97c`).

This experiment demonstrates that, for a heterogeneous image set, the first bytes of image files provide a sufficiently unique fingerprint. Within this dataset, the observed false positive is 0, resulting in a false positive rate of less than **1 in 20,000 (0.005%)**, indicating high discriminative reliability.
