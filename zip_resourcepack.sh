#!/bin/bash

FOLDERS=("hiragana_resourcepack" "katakana_resourcepack")


for folder in "${FOLDERS[@]}"; do
    OUTPUT_NAME="${folder}"
    zip -r "${OUTPUT_NAME}.zip" "${folder}"
    mv "${OUTPUT_NAME}.zip" "${OUTPUT_NAME}.mcpack"
done
