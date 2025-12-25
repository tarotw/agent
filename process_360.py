#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
from PIL import Image

def resize_image(input_path, output_path):
    """
    Resizes image to 2:1 aspect ratio based on width.
    """
    try:
        img = Image.open(input_path)
        width = img.width
        # Calculate target height for 2:1
        target_height = width // 2

        print(f"Original size: {width}x{img.height}")
        print(f"Target size: {width}x{target_height}")

        resized_img = img.resize((width, target_height), Image.Resampling.LANCZOS)
        # Convert to RGB (in case of PNG) and save as JPG
        resized_img = resized_img.convert('RGB')
        resized_img.save(output_path, quality=95)
        print(f"Saved resized image to {output_path}")
        return width, target_height
    except Exception as e:
        print(f"Error processing image: {e}")
        sys.exit(1)

def inject_metadata(image_path, width, height, exiftool_path="exiftool"):
    """
    Injects Google Photo Sphere XMP metadata using exiftool.
    """
    cmd = [
        exiftool_path,
        "-XMP-GPano:ProjectionType=equirectangular",
        "-XMP-GPano:UsePanoramaViewer=True",
        f"-XMP-GPano:CroppedAreaImageWidthPixels={width}",
        f"-XMP-GPano:CroppedAreaImageHeightPixels={height}",
        f"-XMP-GPano:FullPanoWidthPixels={width}",
        f"-XMP-GPano:FullPanoHeightPixels={height}",
        "-XMP-GPano:CroppedAreaLeftPixels=0",
        "-XMP-GPano:CroppedAreaTopPixels=0",
        "-Make=RICOH",
        "-Model=RICOH THETA S",
        image_path
    ]

    try:
        subprocess.run(cmd, check=True)
        print("Metadata injected successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running exiftool: {e}")
        print("Ensure exiftool is installed and in your PATH.")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: exiftool not found. Please install exiftool.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Fix 360 photo metadata for Facebook.")
    parser.add_argument("input_file", help="Path to input image")
    parser.add_argument("--output", "-o", help="Path to output image (default: <input>_fixed.jpg)")
    parser.add_argument("--exiftool", help="Path to exiftool executable", default="exiftool")

    args = parser.parse_args()

    if not args.output:
        base, _ = os.path.splitext(args.input_file)
        args.output = f"{base}_fixed.jpg"

    width, height = resize_image(args.input_file, args.output)
    inject_metadata(args.output, width, height, args.exiftool)

    # Cleanup exiftool backup file
    backup_file = f"{args.output}_original"
    if os.path.exists(backup_file):
        os.remove(backup_file)

if __name__ == "__main__":
    main()
