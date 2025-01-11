# Image fingerprinting without downloading the image content

This script retrieves all images from a given URL and downloads samples of the file from the beginning and the end.
The EXIF metadata is located at the beginning of the image file.
The system generates fingerprints by utilizing the image data.
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
        "url": "https://github.com/ianare/exif-samples/blob/master/jpg/Ricoh_Caplio_RR330.jpg?raw=true",
        "image_size": 3662,
        "exif": {
            "ResolutionUnit": "2",
            "ExifOffset": "190",
            "Make": "Caplio ",
            "Model": "RR330      ",
            "Software": "GIMP 2.4.5",
            "DateTime": "2008:07:31 17:36:21",
            "YCbCrPositioning": "2",
            "XResolution": "72.0",
            "YResolution": "72.0",
            "ExifVersion": "0220",
            "ComponentsConfiguration": "\u0001\u0002\u0003\u0000",
            "ShutterSpeedValue": "5.1",
            "DateTimeOriginal": "2004:08:31 19:52:58",
            "DateTimeDigitized": "2004:08:31 19:52:58",
            "ApertureValue": "4.0",
            "FlashPixVersion": "0100",
            "ColorSpace": "1",
            "ExifImageWidth": "100",
            "Flash": "16",
            "ExifImageHeight": "75",
            "ExifInteroperabilityOffset": "554",
            "WhiteBalance": "0",
            "SceneCaptureType": "0",
            "Sharpness": "0",
            "SubjectDistanceRange": "3",
            "ExposureTime": "0.030303030303030304",
            "FNumber": "2.88",
            "ImageUniqueID": "00000000000000000000000000000111",
            "ISOSpeedRatings": "100",
            "ExposureMode": "0"
        },
        "timestamp": "2025-01-11T09:20:42",
        "sha256_test_5000_bytes": "e920d750c491f3088eeb0f31fb4659164755af11e4bbbe269430f32c3ae10928"
    }
]
```
