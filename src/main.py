# src/main.py

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import json
from image_viewer import ImageViewer
from submission_side import SubmissionSide
from file_types import detect_item_type, is_image
from icons import create_icon, TYPE_COLORS
from tkinterdnd2 import TkinterDnD
from global_value import item_from_left
from utils import get_all_widget

class Tk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

# メインアプリケーションクラス
class FileOrganizerApp(Tk):
    def __init__(self):
        super().__init__()

        # ウィンドウ設定
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.dnd = Tk()
        self.dnd.withdraw()
        self.title("画像見targa（ファイル盛り付け師γ）")
        self.geometry("1000x800")
        
        # 初期値の設定
        self.current_folder = None
        self.history = []
        self.load_config()

        # 左右の分割フレーム
        # self.left_frame = ctk.CTkFrame(self, width=400)
        self.left_frame = ctk.CTkFrame(self, width=800)
        self.left_frame.pack(side="left", fill="both", expand=True)
        
        # self.right_frame = ctk.CTkFrame(self, width=600)
        # self.right_frame.pack(side="right", fill="both", expand=True)

        # 「既存側」フレーム内のUI
        self.left_label = ctk.CTkLabel(self.left_frame, text="既存側", font=("Arial", 18))
        self.left_label.pack(pady=10)

        # ボタンを配置するためのフレーム0行目
        self.button_frame0 = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.button_frame0.pack(pady=10, fill="x")

        # # フォルダ選択ボタン
        self.select_folder_button = ctk.CTkButton(self.button_frame0, text="フォルダを選択", command=self.select_folder)
        self.select_folder_button.pack(side="left", padx=10, pady=5, expand=True)

        # ボタンを配置するためのフレーム1行目
        self.button_frame1 = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.button_frame1.pack(pady=10, fill="x")
        
        # #「親へ戻る」ラベルのボタンを設定
        self.parent_folder_button = ctk.CTkButton(self.button_frame1, text="親へ戻る", command=self.go_to_parent_folder)
        self.parent_folder_button.pack(side="left", padx=10, pady=5, expand=True)

        # #「前へ戻る」ラベルのボタンを設定
        self.back_button = ctk.CTkButton(self.button_frame1, text="前へ戻る", command=self.go_back_in_history)
        self.back_button.pack(side="left", padx=10, pady=5, expand=True)

        # # 読み込み直しボタン
        self.reload_items_button = ctk.CTkButton(self.button_frame1, text="読み込み直す", command=self.populate_file_list)
        self.reload_items_button.pack(side="left", padx=10, pady=5, expand=True)
        
        # ボタンを配置するためのフレーム2行目
        self.button_frame2 = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.button_frame2.pack(pady=10, fill="x")

        # # アイテム名変更ボタン
        self.change_items_name_button = ctk.CTkButton(self.button_frame2, text="アイテム名を変更", command=self.change_items_name)
        self.change_items_name_button.pack(side="left", padx=10, pady=5, expand=True)
        
        # スクロール可能なファイルリスト表示フレーム
        self.file_list_frame = ctk.CTkScrollableFrame(self.left_frame)
        self.file_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # # 「提出側」フレーム内のUI
        # self.right_label = ctk.CTkLabel(self.right_frame, text="提出側", font=("Arial", 18))
        # self.right_label.pack(pady=10)

        # self.submission = SubmissionSide(self.right_frame, fg_color="transparent")
        # self.submission.pack(fill="both", expand=True)

        # 設定ファイルの読み込み
        if not self.current_folder == None:
            self.populate_file_list()

        # ボタンの有効状態更新
        self.update_back_button_state()
        self.update_parent_button_state()
        self.update_other_buttons_state()
        self.update_link_button_state()


    # 設定ファイルを読み込んで current_folder を設定
    def load_config(self):
        self.current_folder = None  # 初期値
        # config_file = "config.json"
        # try:
        #     with open(config_file, "r", encoding="utf-8") as file:
        #         config = json.load(file)
        #         self.current_folder = config["current_folder"]
        # except FileNotFoundError:
        #     messagebox.showwarning("設定ファイルが見つかりません", f"{config_file} が見つかりませんでした。初期設定を使用します。")
        #     self.current_folder = ""  # 初期値
        # except json.JSONDecodeError:
        #     messagebox.showerror("設定ファイルのエラー", f"{config_file} の読み込みに失敗しました。")
        #     self.current_folder = ""  # 初期値

    def populate_file_list(self):
        # フレームの内容をクリア
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()

        # ファイルリストフレームのヘッダー行を表示
        header_frame = ctk.CTkFrame(self.file_list_frame)  # 背景色を指定
        header_frame.pack(fill="x", padx=5, pady=(10, 0))  # ヘッダー部分の余白調整
        name_header = ctk.CTkLabel(header_frame, text="名前", anchor="w", font=("Arial", 12, "bold"))
        name_header.pack(side="left", fill="x", expand=True)
        date_header = ctk.CTkLabel(header_frame, text="更新日時", anchor="w", font=("Arial", 12, "bold"))
        date_header.pack(side="right", fill="x", expand=True)
        button_header = ctk.CTkLabel(header_frame, text="", anchor="w", font=("Arial", 12, "bold"))
        button_header.pack(side="left", fill="x", expand=True)

        for file_name in os.listdir(self.current_folder):
            full_path = os.path.join(self.current_folder, file_name)
            base_name, ext = os.path.splitext(file_name)
            last_modified_time = time.strftime("%Y/%m/%d %H:%M", time.gmtime(os.path.getmtime(full_path)))

            item_type = detect_item_type(full_path)

            # 名前とアイコン部分のフレーム
            file_name_frame = tk.Frame(self.file_list_frame, background=TYPE_COLORS[item_type])
            file_name_frame.pack(fill="x", padx=5, pady=2)

            # # アイコン
            file_label = ctk.CTkLabel(file_name_frame, text="", image=create_icon(item_type, full_path), compound="left", anchor="w")
            file_label.pack(side="left", fill="x")
            
            # # 名前
            file_name_entry = ctk.CTkEntry(file_name_frame, width=len(base_name) * 20)
            file_name_entry.insert(0, base_name)
            file_name_entry.pack(side="left", fill="x")
            file_ext_label = ctk.CTkLabel(file_name_frame, text=ext if ext else f"({item_type})", compound="left", anchor="w")
            file_ext_label.pack(side="left", fill="x", expand=True)
            # 仕事しない
            # empty_label = ctk.CTkLabel(file_name_frame, text="\t", compound="left", anchor="w")
            # empty_label.pack(side="left", fill="x", expand=True)

            # 更新日時部分
            date_label = ctk.CTkLabel(file_name_frame, text=last_modified_time, anchor="w")
            date_label.pack(side="left", fill="x", expand=True)
        
            # 「これの行先は」ボタン
            # self.link_button = ctk.CTkButton(file_name_frame, command=self.item_select(full_path), hover=False)
            # self.link_button.pack(side="left")

            for child in file_name_frame.winfo_children():
                child.bind("<Double-1>", lambda event, path=full_path: self.on_item_double_click(event, path))

        # ボタンの有効状態更新
        self.update_back_button_state()
        self.update_parent_button_state()
        self.update_link_button_state()
        self.update_other_buttons_state()

    # 選択したパスを取得する
    def item_select(self, full_path):
        # tkinterの仕様で、引数を取るものはこうするしかない
        def inner():
            item_from_left.toggle(full_path)
            # print(item_from_left.get())
            self.update_link_button_state()
        return inner

    # フォルダを選択して内容を表示
    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.current_folder = folder_path
            self.history.clear()  # 選択時は履歴をクリア
            self.populate_file_list()

    # アイテム名変更の適用
    def change_items_name(self):
        all_widget = get_all_widget(self.file_list_frame)
        item_list = os.listdir(self.current_folder)
        entries = []
        new_bases = []
        for widget in all_widget:
            if "ctkentry" in widget.winfo_name():
                entries.append(widget)
                new_bases.append(widget.get())
        for i, new_base in enumerate(new_bases):
            name_now = item_list[i]
            base_now, ext = os.path.splitext(name_now)
            if not base_now == new_base:
                new_name = new_base + ext
                if new_name not in item_list:
                    os.rename(os.path.join(self.current_folder, name_now), os.path.join(self.current_folder, new_name))
                else:
                    entries[i].delete(0, tk.END)
                    entries[i].insert(0, base_now)

    # リストアイテムをダブルクリックした時の動作
    def on_item_double_click(self, event, item_path):
        if os.path.isdir(item_path):
            self.history.append(self.current_folder)
            self.current_folder = item_path  # current_folder を移動先に更新
            self.populate_file_list()
        elif os.path.isfile(item_path) and is_image(item_path):
            self.open_image(item_path)

    # 親フォルダに移動
    def go_to_parent_folder(self):
        if self.current_folder:  # current_folderが設定されているかチェック
            parent_folder = os.path.abspath(os.path.join(self.current_folder, os.pardir))  # os.pardirで親フォルダを取得
            if parent_folder and parent_folder != self.current_folder:
                self.history.append(self.current_folder)
                self.current_folder = parent_folder  # current_folder を親フォルダに更新
                self.populate_file_list()

    # 履歴から戻る
    def go_back_in_history(self):
        if self.history:
            last_folder = self.history.pop()
            self.current_folder = last_folder  # current_folder を履歴のフォルダに更新
            self.populate_file_list()
            self.update_back_button_state()
            self.update_parent_button_state()  # ボタンの有効状態更新

    # 履歴に基づいて戻るボタンの状態を更新
    def update_back_button_state(self):
        self.back_button.configure(state=tk.NORMAL if self.history and self.current_folder else tk.DISABLED)

    # current_folderに基づいて親フォルダボタンの状態を更新
    def update_parent_button_state(self):
        self.parent_folder_button.configure(state=tk.NORMAL if self.current_folder else tk.DISABLED)
    
    # current_folderに基づいてその他ボタンの状態を更新
    def update_other_buttons_state(self):
        self.reload_items_button.configure(state=tk.NORMAL if self.current_folder else tk.DISABLED)
        self.change_items_name_button.configure(state=tk.NORMAL if self.current_folder else tk.DISABLED)
    
    # 紐づけボタンの状態を更新
    def update_link_button_state(self):
        all_widget = get_all_widget(self.file_list_frame)
        button_counter = 0
        for widget in all_widget:
            if "ctkbutton" in widget.winfo_name():
                item_path = os.path.join(self.current_folder, os.listdir(self.current_folder)[button_counter])
                is_same_type = item_from_left.is_same_type(item_path)
                includes = item_from_left.includes(item_path)
                widget.configure(
                    text="これの行き先は" if includes else "選択してね",
                    fg_color="grey" if not is_same_type else "red" if includes else "blue",
                    state=tk.NORMAL if is_same_type else tk.DISABLED)
                button_counter += 1

    # ファイルを開く処理（画像の場合はプレビューウィンドウ）
    def open_image(self, file_path):
        if is_image(file_path):
            ImageViewer(self, file_path)  # 新しいImageViewerウィンドウを開く
        else:
            messagebox.showinfo("ファイル", f"ファイルを開けません: {file_path}")

# アプリの実行
if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()
