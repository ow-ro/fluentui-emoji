# check_assets.py

"""
Performs several checks on asset folder contents including:
 - metadata content
 - folder content
"""

import argparse
from encodings import utf_8
import json
import math
from multiprocessing.dummy import Array
from pathlib import Path
import sys
from tokenize import String
from typing import List
from typing import Dict
from utils import styles
import codecs

COLOR_CODES = {
    "Default": "",
    "Light Skin Tone": "1f3fb", 
    "Medium-Light Skin Tone": "1f3fc",
    "Medium Skin Tone": "1f3fd",
    "Medium-Dark Skin Tone": "1f3fe",
    "Dark Skin Tone": "1f3ff"
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("assets",
                    help="Path to asset root folder",
                    type=Path)
    ap.add_argument("animated",
                    help="Path to animated asset root folder",
                    type=Path)
    opts = ap.parse_args()

    errors = False

    missingMappings = import_missing_matches()
    colorMappings: Dict[str, str] = {}
    noColorMappings: Dict[str, str] = {}
    defaultColorMappings: Dict[str, str] = {}

    combinedMappings: Dict[str, str] = {}
    missingItems = []

    for jp in opts.assets.rglob("**/metadata.json"):
        folder = jp.parent
        with open(jp, 'r', encoding="utf8") as jf:
            md = json.loads(jf.read())
        
        uc = md.get('unicode')
        sks = md.get('unicodeSkintones')
        cldr = md.get('cldr')

        if sks is not None:
            for colorFolder, colorCode in COLOR_CODES.items():
                match: String
                title = cldr
                if colorFolder == "Default":
                    foundAssets = list(opts.animated.rglob(title + ".png"))
                    if foundAssets is not None:
                        defaultColorMappings[convert_unicode_to_emoji(uc)] = title.title() + ".png"
                else:
                    title = title + " " + colorFolder

                    for s in sks:
                        if colorCode in s:
                            match = s

                    foundAssets = list(opts.animated.rglob(title + ".png"))
                    if not foundAssets:
                        missingItems.append(f"title: {title}.png in folder: {colorFolder}")
                    else:
                        for asset in foundAssets:
                            if match is not None:
                                colorMappings[convert_unicode_to_emoji(match)] = title.title() + ".png"
        else:
            if uc is not None:
                title = cldr
                foundAssets = list(opts.animated.rglob(title + ".png"))
                if foundAssets is not None:
                    noColorMappings[convert_unicode_to_emoji(uc)] = title.title() + ".png"
            
    combinedMappings.update(noColorMappings)
    combinedMappings.update(defaultColorMappings)
    combinedMappings.update(colorMappings)
    combinedMappings.update(missingMappings)

    json_output = json.dumps(combinedMappings, indent = 4, ensure_ascii=False).encode('utf-8').decode('utf-8')

    with open("combinedMappings.json", "w", encoding="utf8") as f:
        f.write(json_output)
    
    with open("missingItems.txt", "w") as f:
        for item in missingItems:
            f.write(item + '\n')

    print(combinedMappings)
    print()
    print("Done!")
    return 1 if errors else 0

def convert_unicode_to_emoji(unicode_str):
    code_points = unicode_str.split()
    emoji_chars = [chr(int(code, 16)) for code in code_points]
    return "".join(emoji_chars)

def import_missing_matches():
    with open('missingEntries.json', "r", encoding="utf8") as f1:
        data = json.load(f1)
        return dict[str, str](data)

if __name__ == '__main__':
    sys.exit(main())