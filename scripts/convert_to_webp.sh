#!/bin/bash
# Convert all JPG/PNG images to WebP format for better performance
find static/images -type f \( -iname "*.jpg" -o -iname "*.png" \) | while read img; do
    webp_file="${img%.*}.webp"
    if [ ! -f "$webp_file" ] || [ "$img" -nt "$webp_file" ]; then
        echo "Converting $img to WebP..."
        cwebp -q 85 "$img" -o "$webp_file"
    fi
done
