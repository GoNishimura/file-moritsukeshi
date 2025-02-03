import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk, UnidentifiedImageError
import os
import threading
from file_types import is_image

class ImageViewer(tk.Toplevel):
  def __init__(self, parent, image_path):
    super().__init__(parent)
    self.parent = parent
    self.initial_size = (800, 800)
    self.focus_set()
    
    self.image_path = image_path
    self.original_image = None
    self.img_tk = None
    self.cached_images = {}  # 3段階のキャッシュ
    self.dirname = os.path.dirname(image_path)
    self.image_paths = [
        os.path.join(self.dirname, f) for f in os.listdir(self.dirname) if is_image(os.path.join(self.dirname, f))
    ]
    self.current_index = self.image_paths.index(image_path)
    self.title(self.dirname)
    
    self.canvas = tk.Canvas(self, bg="#ffffff", width=self.initial_size[0], height=self.initial_size[1])
    self.canvas.pack(fill="both", expand=True)
    
    self.footer = tk.Frame(self)
    self.footer.pack(fill="x", side="bottom")
    
    self.zoom_factor = 1.0
    self.min_zoom = 1.0
    self.max_zoom = 8.0
    self.offset_x = 0
    self.offset_y = 0
    self.start_x = 0
    self.start_y = 0
    self.image_id = None
    
    # フッターの1行目（ナビゲーション）
    self.footer_row1 = tk.Frame(self.footer)
    self.footer_row1.pack(side="left")
    self.prev_button = tk.Button(self.footer_row1, text="< 前", command=self.show_prev_image)
    self.filename_label = tk.Label(self.footer_row1, text=os.path.basename(image_path), font=("Arial", 12))
    self.next_button = tk.Button(self.footer_row1, text="次 >", command=self.show_next_image)
    self.prev_button.pack(side="left", padx=5, pady=5)
    self.filename_label.pack(side="left", padx=5, pady=5)
    self.next_button.pack(side="left", padx=5, pady=5)
    
    # フッターの2行目（拡大縮小）
    self.footer_row2 = tk.Frame(self.footer)
    self.footer_row2.pack(side="right")
    self.zoom_out_button = tk.Button(self.footer_row2, text="ー", command=self.zoom_out)
    self.zoom_label = tk.Label(self.footer_row2, text="100%")
    self.fit_button = tk.Button(self.footer_row2, text="全体表示", command=self.fit_to_window)
    self.zoom_in_button = tk.Button(self.footer_row2, text="＋", command=self.zoom_in)
    self.zoom_out_button.pack(side="left", padx=5, pady=5)
    self.zoom_label.pack(side="left", padx=5, pady=5)
    self.fit_button.pack(side="left", padx=5, pady=5)
    self.zoom_in_button.pack(side="left", padx=5, pady=5)

    # フッターの3行目（画像情報）
    self.footer_row3 = tk.Frame(self.footer)
    self.footer_row3.pack(fill="x")
    self.image_info_label = tk.Label(self.footer_row3, text="", font=("Arial", 10))
    self.image_info_label.pack(side="left", padx=5, pady=5)

    self.bind("<Left>", self.show_prev_image)
    self.bind("<Right>", self.show_next_image)
    self.bind("<MouseWheel>", self.mouse_zoom)
    self.bind("<Configure>", self.on_resize)
    
    self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
    self.canvas.bind("<B1-Motion>", self.on_drag_motion)
    
    self.load_image(self.image_paths[self.current_index])
    self.fit_to_window()
  
  def load_image(self, image_path):
    try:
      img = Image.open(image_path)
      self.original_image = img
      self.cached_images.clear()
      self.filename_label.config(text=os.path.basename(image_path))
      
      self.update_image_info()
      self.create_image_cache(min_zoom_only=True)
      threading.Thread(target=self.create_image_cache, args=(False,), daemon=True).start()
      
    except UnidentifiedImageError:
      messagebox.showerror("エラー", "この画像形式はサポートされていません。")
      return
    except Exception as e:
      messagebox.showerror("エラー", f"画像を開けませんでした: {e}")
      return

  def update_image_info(self):
    width, height = self.original_image.size
    dpi = self.original_image.info.get("dpi", ("N/A", "N/A"))
    self.image_info_label.config(text=f"{width} x {height} px | DPI: {dpi[0]}, {dpi[1]}")

  # 初回に4つのキャッシュを作成する（非同期で拡大倍率を処理）
  def create_image_cache(self, min_zoom_only=False):
    canvas_width, canvas_height = self.get_canvas_size()
    img_width, img_height = self.original_image.size
    scale_x = canvas_width / img_width
    scale_y = canvas_height / img_height

    self.min_zoom = min(scale_x, scale_y)
    self.max_zoom = self.min_zoom * 8

    zoom_levels = [self.min_zoom] if min_zoom_only else [self.min_zoom * 2, self.min_zoom * 4, self.max_zoom]

    for factor in zoom_levels:
      img = self.original_image.copy()
      new_size = (int(img.width * factor), int(img.height * factor))
      img = img.resize(new_size, Image.LANCZOS)
      self.cached_images[factor] = ImageTk.PhotoImage(img)

    if min_zoom_only:
      self.zoom_factor = self.min_zoom
      self.resize_image()

  def get_canvas_size(self):
    initial_add = 4
    canvas_width, canvas_height = self.initial_size
    if self.canvas.winfo_width() > 1 and self.canvas.winfo_height() > 1:
      canvas_width = self.canvas.winfo_width()
      canvas_height = self.canvas.winfo_height()
    else:
      canvas_width += initial_add
      canvas_height += initial_add
    return [canvas_width, canvas_height]

  def fit_to_window(self):
    self.zoom_factor = self.min_zoom
    self.offset_x = 0
    self.offset_y = 0
    self.resize_image()

  def resize_image(self):
    if self.zoom_factor in self.cached_images:
      self.img_tk = self.cached_images[self.zoom_factor]
    else:
      return  # それ以外の倍率は使わないので処理しない

    if self.zoom_factor == self.min_zoom:
      self.offset_x = 0
      self.offset_y = 0

    self.canvas.delete("all")
    self.image_id = self.canvas.create_image(
      self.get_canvas_size()[0] // 2 + self.offset_x, 
      self.get_canvas_size()[1] // 2 + self.offset_y, 
      image=self.img_tk, anchor="center"
    )
    self.zoom_label.config(text=f"{int(self.zoom_factor * 100)}%")

  def zoom_in(self):
    if self.zoom_factor * 2 <= self.max_zoom:
      self.zoom_factor *= 2
      self.resize_image()

  def zoom_out(self):
    if self.zoom_factor / 2 >= self.min_zoom:
      self.zoom_factor /= 2
      self.resize_image()

  def mouse_zoom(self, event):
    canvas_width, canvas_height = self.get_canvas_size()
    cursor_x = event.x - canvas_width // 2
    cursor_y = event.y - canvas_height // 2

    scale = 2 if event.delta > 0 and self.zoom_factor * 2 <= self.max_zoom else \
            0.5 if event.delta < 0 and self.zoom_factor / 2 >= self.min_zoom else 1

    if scale != 1:
      new_zoom = self.zoom_factor * scale
      self.offset_x = int(self.offset_x * scale - cursor_x * (scale - 1))
      self.offset_y = int(self.offset_y * scale - cursor_y * (scale - 1))
      self.zoom_factor = new_zoom
      self.resize_image()

  def on_drag_start(self, event):
    self.start_x = event.x
    self.start_y = event.y

  def on_drag_motion(self, event):
    dx = event.x - self.start_x
    dy = event.y - self.start_y
    self.offset_x += dx
    self.offset_y += dy
    self.start_x = event.x
    self.start_y = event.y
    self.canvas.move(self.image_id, dx, dy)  # 画像を直接移動

  def on_resize(self, event=None):
    # なんか処理が重すぎる
    # self.load_image(self.image_paths[self.current_index])
    self.resize_image()

  def show_prev_image(self, event=None):
    self.current_index = (self.current_index - 1) % len(self.image_paths)
    self.load_image(self.image_paths[self.current_index])
    self.resize_image()
    self.update_navigation_buttons()

  def show_next_image(self, event=None):
    self.current_index = (self.current_index + 1) % len(self.image_paths)
    self.load_image(self.image_paths[self.current_index])
    self.resize_image()
    self.update_navigation_buttons()

  def update_navigation_buttons(self):
    self.prev_button.config(state="normal" if self.current_index > 0 else "disabled")
    self.next_button.config(state="normal" if self.current_index < len(self.image_paths) - 1 else "disabled")
