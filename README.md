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

```json
[
    {
        "url": "http://natural3jytxrhh5wqmpcz67yumyptr7pn2c52hppvn3vanmqzjlkryd.onion/images/printer-3D-gun.jpg",
        "image_size": 1104883,
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
        "timestamp": "2025-04-09T09:28:06",
        "sha256_first_10240_bytes": "adf9ea1f2265b3d56827be6b29397c5e6c430bfda8d1e29869fe920a7fa2e114",
        "sha256_last_1024_bytes": "480555c07cb1b25815fafffb8f4bde37e87cd32528732f2e7e74b4872896f577",
        "random_128_bytes_sample_start": "43848e755a2e68417b279494e6fd9d80c8099cdd215c7307282f6a0a7fffd0e1acc6b8badaf5add537d4075dbb810c6b1da96fe967d8e5a7d0f1727af5f8d43b1dce762d8c36643d93536a6387ab4e46f1b2cf6eeaf1ebff00ac7f33fcc56ce7e6f4fc815651f49f582df49fa308fa2e0dfccb1abb3fa8983d43ec77e45adb2a",
        "random_128_bytes_sample_end": "bf99b4df6f936ede3f0fd9df4e37e7551d7419a7f9c1fe4a3f99fcf7cd697f3fedecd6f6bfeffebdb8ed3b8545c83f25fc9e7dff00ef7fcd27c9efdb6ddb1bcdddbbdeddbb6edf0b6ee37c6b78561cc3fcdff9bd57cfdbcbf2a3dbb2f6db7f76fe1baf7bdb9e157c230a64c2fc9db07ceecdfe7b5ef7fb3e16b69dad6f0e3e8a"
    }
]
```

# Test images

Using two random 128-byte samples (one from the start and one from the end) of an image to determine whether the image is the same is a **reasonable heuristic**,
but it is not a foolproof method to fingerprint the images and compare are these images duplicates.

```sh
wget "https://exiv2.org/include/img_1771.jpg"

xxd -p img_1771.jpg | tr -d '\n' | grep -o "cb44f02d651b15cd558b9320531417c8c9cd6b67e13138cae2ab1f819d648cd161664256f0ae0eae46a54572855551b2073a3f1fe1cd6ba1b1b1e75516e02d62f860c0b29dcf4142ce49c5757566fa3906eea7239f7a53a5d7070adfcdd0fbd7575480cc323608debb39fef5d5d4843082a46723b114a59643863a5bf9bbfbd7"

xxd -p img_1771.jpg | tr -d '\n' | grep -o "ef4345790e09c77cf4a2e3cc14721b0143423972c493ee4d28cb372fa5712079472efdeb8f9463f31e7e95007123e51c87eb4f18501bed9a62ef9276039d389c8c9fa52602861c8f3a7863a800dcb9e2859017511bf4a407a8a2e80b4b7b8182adb8ebfde9ceaca79e41dc11d45572394218019a9f04c258b436c7a1ec6b6c73"
```

**The raw 128-byte samples are effectively random data and do not provide a human-readable or visually interpreted representation of the image.**
The script only processes images larger than 20 KB (20,480 bytes), two 128-byte samples (one from the start, one from the end) represent a small fraction of the total image size, less than 1.5%.
They contain compressed image data, not raw pixel values, and are not directly interpreted as pixels.
Depending on the compression algorithm, this may include encoded color or luminance information for specific regions of the image.

# Handle onion addresses

Install Tor and ensure the SOCKS5 proxy is available on localhost:9050.
The software will then automatically use this Tor process for onion addresses.
