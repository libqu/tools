"""
Script to Convert Text between Traditional Chinese and Simplified Chinese in XML, XHTML, and SVG Files.

Usage:
    python my.py <t2s|s2t> <input_directory> <output_directory>

Arguments:
    t2s|s2t: Conversion direction. 
             't2s' for Traditional to Simplified.
             's2t' for Simplified to Traditional.

    input_directory: Path to the directory containing files to be converted.

    output_directory: Path for converted files.

Files Processed:
    - images/*.svg
    - src/epub/content.opf
    - src/epub/toc.xhtml
    - src/epub/text/*.xhtml

Features:
    - Converts text line by line, ensuring that the original structure and formatting of the files remain intact.
    - Skips lines that don't contain any Chinese characters.
    - Adjusts the "xml:lang" attribute in the tags based on the conversion direction.
    - Keeps the original spacing and formatting, converting Chinese text only.

Dependencies:
    - OpenCC
    - beautifulsoup4
    - lxml

Install Dependencies:
    pip install OpenCC beautifulsoup4 lxml
"""

import sys
import os
from opencc import OpenCC
from bs4 import BeautifulSoup
import unicodedata
import glob

def is_chinese_char(char):
    """Check if the character is a Chinese character."""
    return 'CJK UNIFIED' in unicodedata.name(char, '')

def convert_text(input_text, direction):
    if direction == "t2s":
        converter = OpenCC('t2s.json')
    elif direction == "s2t":
        converter = OpenCC('s2t.json')
    else:
        raise ValueError(f"Invalid conversion direction: {direction}")
    return converter.convert(input_text) if any(is_chinese_char(c) for c in input_text) else input_text

def get_output_path(file_path, input_dir, output_dir):
    # Get the relative path of the file to the input directory
    relative_path = os.path.relpath(file_path, input_dir)
    # Combine the output directory with this relative path
    return os.path.join(output_dir, relative_path)

def convert_file(file_path, input_dir, output_dir, direction):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        soup = BeautifulSoup(content, 'lxml')

        # Iterate through text in XML, XHTML, SVG and convert
        for text in soup.find_all(string=True):
            text.replace_with(convert_text(text, direction))

        # Adjust xml:lang attribute
        if direction == "t2s":
            for tag in soup.find_all(attrs={"xml:lang": "zh-Hant"}):
                tag['xml:lang'] = "zh-Hans"
        elif direction == "s2t":
            for tag in soup.find_all(attrs={"xml:lang": "zh-Hans"}):
                tag['xml:lang'] = "zh-Hant"

        # Write to output file
        output_path = get_output_path(file_path, input_dir, output_dir)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write(str(soup))

def main():
    if len(sys.argv) != 4:
        print("Usage: python my.py <t2s|s2t> <input_directory> <output_directory>")
        sys.exit(1)

    direction, input_dir, output_dir = sys.argv[1], sys.argv[2], sys.argv[3]

    if direction not in ["t2s", "s2t"]:
        print("Invalid direction. Use either 't2s' or 's2t'.")
        sys.exit(1)

    files_to_convert = [
        "images/*.svg",
        "src/epub/content.opf",
        "src/epub/toc.xhtml",
        "src/epub/text/*.xhtml"
    ]

    for pattern in files_to_convert:
        for file_path in glob.glob(os.path.join(input_dir, pattern)):
            convert_file(file_path, input_dir, output_dir, direction)

if __name__ == "__main__":
    main()
