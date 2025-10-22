import os
from PIL import Image

base_dir = '/Users/alex/Desktop/code/Others/SpellSmut/ExtractedAssets/UI/extracted/'

for root, dirs, files in os.walk(base_dir):
    if 'png' in dirs:
        png_dir = os.path.join(root, 'png')
        for file in os.listdir(png_dir):
            if file.endswith('.png'):
                file_path = os.path.join(png_dir, file)
                img = Image.open(file_path)
                rotated = img.rotate(180)
                rotated.save(file_path)
                print(f"Rotated: {file_path}")