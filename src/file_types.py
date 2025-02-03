# src/file_types.py

import os

# 画像ファイルの拡張子リストを定義
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tga', '.webp')

# ファイルタイプを判別
def detect_item_type(path):
    if os.path.isdir(path):
        return "folder"
    elif is_image(path):
        return "image"
    else:
        return "file"

def is_image(path):
    return path.lower().endswith(IMAGE_EXTENSIONS)
