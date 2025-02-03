# src/submission_side.py

import tkinter as tk
from tkinter import filedialog, messagebox
import json
from customtkinter import CTkFrame, CTkButton, CTkEntry, CTkLabel, CTkScrollableFrame
from icons import TYPE_COLORS  # 各アイテムタイプの背景色を定義
from tkinterdnd2 import DND_FILES
from file_types import detect_item_type
from global_value import item_from_left
from utils import get_all_widget
import shlex

class SubmissionSide(CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<DropEnter>>", self.on_drop_enter)
        self.dragged_item_type = ""
        self.dragged_items = []
        self.output_format = {}
        # 紐づけ管理の辞書
        self.filled_format = {}

        # 提出フォルダ名入力ボックスとラベルの設定
        self.submission_frame = CTkFrame(self)
        self.submission_frame.pack(fill="x", pady=5)

        self.submission_label = CTkLabel(self.submission_frame, text="提出フォルダ名")
        self.submission_label.pack(side="left", anchor="w")  # 左寄せ

        self.submission_name_entry = CTkEntry(self.submission_frame)
        self.submission_name_entry.pack(fill="x")
        
        # 出力形式を読み込むボタン
        self.load_format_button = CTkButton(self, text="出力形式を読み込む", command=self.load_output_format)
        self.load_format_button.pack(fill="x", pady=5)
        
        # スクロール可能なファイルリスト表示フレーム
        self.file_list_frame = CTkScrollableFrame(self)
        self.file_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 配置先のフォルダ選択ボタンとその表示ラベル
        self.folder_button_frame = CTkFrame(self)
        self.folder_button_frame.pack(fill="x", pady=5)

        self.select_folder_button = CTkButton(self.folder_button_frame, text="生成先のフォルダ", command=self.select_destination_folder)
        self.select_folder_button.pack(side="left", padx=5)

        self.folder_path_label = CTkLabel(self.folder_button_frame, text="未選択", anchor="w")
        self.folder_path_label.pack(fill="x", padx=5, side="left")

        self.generate_button = CTkButton(self, text="生成する")
        self.generate_button.pack(fill="x", padx=5, pady=5)

    # 提出側にドラッグアンドドロップされたファイルを確認する
    def on_drop_enter(self, event):
        print("drop enter:", event.data)
        # ドラッグされた文字列のパスを分割する
        try:
            self.dragged_items = shlex.split(event.data)
            print("パスを分割:", self.dragged_items)
        except Exception as e:
            messagebox.showerror("エラー", f"ドロップされたデータの解析に失敗しました: {e}")
            return
        
        # アイテムの型を判別
        item_types = {detect_item_type(item) for item in self.dragged_items}

        if len(item_types) > 1:  # 型が複数混在している場合
            self.dragged_items.clear()
            messagebox.showerror("エラー", "異なる種類のアイテムを一緒に扱うことはできません")
            return

        # 一致する型の行をハイライト
        self.dragged_item_type = next(iter(item_types), None)  # 1種類であることを保証
        # ドラッグアンドドロップ時はボタン操作の方は解除する
        item_from_left.clear()
        matching_found = False

        for widget in get_all_widget(self.file_list_frame):
            if widget.winfo_name() == "ctkframe":
                field_name = widget.cget("text")  # ラベルテキストをキーとして取得

                # フォーマットデータと型が一致するか確認
                if self.output_format.get("folder_structure", {}).get(field_name, {}).get("type") == self.dragged_item_type:
                    matching_found = True

                    # 「ここ」ボタンを追加
                    button = CTkButton(
                        widget, text="ここ",
                        command=lambda w=widget: self.receive_items(field_name, w)
                    )
                    button.pack(side="right", padx=5)

        if not matching_found:
            messagebox.showinfo("情報", "一致する項目がありませんでした")

    def load_output_format(self):
        # ファイルリストをリセット
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()

        format_file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if format_file_path:
            try:
                with open(format_file_path, 'r', encoding="utf-8") as file:
                    self.output_format = json.load(file)
                
                # 提出フォルダ名の設定
                self.submission_name_entry.delete(0, tk.END)
                self.submission_name_entry.insert(0, self.output_format.get("submission_folder_name", ""))
                
                # ファイルリストを表示
                self.display_folder_structure(self.output_format.get("folder_structure", {}))

            except json.JSONDecodeError:
                messagebox.showerror("エラー", "JSONファイルの読み込みに失敗しました。")

    def replace_placeholders(self, text):
        # 出力形式データを使ってプレースホルダーを置換
        if not text:
            return text
        placeholders = {
            "{submission_folder_name}": self.output_format.get("submission_folder_name", ""),
        }
        for key, value in placeholders.items():
            text = text.replace(key, value)
        return text

    def display_folder_structure(self, structure, parent_frame=None):
        if parent_frame is None:
            parent_frame = self.file_list_frame
        
        for name, details in structure.items():
            item_type = details.get("type")
            if item_type not in {"folder", "image", "file"}:
                continue

            # 行のフレームを作成
            item_frame = CTkFrame(parent_frame, fg_color=TYPE_COLORS.get(item_type, "gray"))
            item_frame.pack(fill="x", pady=3)
            item_frame.drop_target_register(DND_FILES)
            item_frame.dnd_bind("<<Drop>>", self.on_file_drop(name, item_frame))

            # 表示名を取得
            displayed_name = self.replace_placeholders(details.get("name", name))

            # ラベルを追加
            item_label = CTkLabel(item_frame, text=displayed_name)
            item_label.pack(side="left", anchor="n", padx=5)

            # ツールチップを表示
            description = details.get("description", "説明なし")
            item_frame.bind("<Enter>", lambda e, desc=description: self.show_tooltip(e, desc))
            item_frame.bind("<Leave>", self.hide_tooltip)
            item_label.bind("<Enter>", lambda e, desc=description: self.show_tooltip(e, desc))
            item_label.bind("<Leave>", self.hide_tooltip)

            # 再帰的にフォルダ内容を表示
            folder_contents = details.get("folder_contents")
            if item_type == "folder" and folder_contents:
                self.display_folder_structure(folder_contents, item_frame)

    # ドロップされたファイルを処理
    def on_file_drop(self, field_name, target_widget):
        # tkinterの仕様で、引数を取るものはこうするしかない
        print("on file drop:", field_name, target_widget)
        def inner(event):
            # print(event.data)
            print(f"dropped at {field_name} in {target_widget.winfo_name()}: {self.dragged_items}, {self.dragged_item_type}")
            if not self.dragged_items:
                messagebox.showwarning("警告", "ドロップされたアイテムがありません")
                return
            self.fill_format(field_name)
            self.dragged_items.clear()
            print(f"dropped finished at {field_name}")
        return inner

    # 既存側から送られたパスを処理
    def receive_items(self, field_name, target_widget):
        def inner(event):
            self.dragged_items = item_from_left.get()
            print(f"{field_name} in {target_widget.winfo_name()}に置く: {self.dragged_items}")
            # 既存の選択アイテムを取得
            if not self.dragged_items:
                messagebox.showwarning("警告", "選択されたアイテムがありません")
                return
            self.fill_format(field_name)
            print(f"receive_items: {field_name} -> {self.dragged_items}")
        return inner

    # 選択された行に紐づけ
    def fill_format(self, field_name):
        # フィールド設定取得
        field_settings = self.output_format.get("folder_structure", {}).get(field_name, {})
        
        # 条件チェック
        if field_settings.get("only_one", False) and len(self.dragged_items) > 1:
            messagebox.showerror("エラー", f"{field_name}には1つのアイテムしか配置できません")
            return

        # 紐づけ
        self.filled_format[field_name] = self.dragged_items if len(self.dragged_items) > 1 else self.dragged_items[0]
        print(f"紐づけ完了: {field_name} -> {self.filled_format[field_name]}")

        # UI更新は後で実装予定

    def show_tooltip(self, event, text):
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        label = tk.Label(self.tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()

    def select_destination_folder(self):
        # 配置先フォルダを選択し、パスをラベルに表示
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path_label.configure(text=folder_path)
