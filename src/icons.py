from PIL import Image, ImageDraw, ImageTk
import customtkinter as ctk

# https://coolors.co/palette/fbf8cc-fde4cf-ffcfd2-f1c0e8-cfbaf0-a3c4f3-90dbf4-8eecf5-98f5e1-b9fbc0
TYPE_COLORS = {
    "folder": "#fbf8cc",
    "image": "#90dbf4",
    "file": "white",
}

def create_icon(object_type, file_path = ""):
    size = (50, 50)
    if object_type == "folder":
        img = Image.new("RGBA", size, color=TYPE_COLORS["folder"])
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 40, 40], outline="black", width=2)
    elif object_type == "image":
        img = Image.open(file_path)
        img.thumbnail(size)
    elif object_type == "file":
        img = Image.new("RGBA", size, color=TYPE_COLORS["file"])
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 40, 40], outline="black", width=2)
    
    return ctk.CTkImage(light_image=img, dark_image=img)