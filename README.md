# 画像見targa（ファイル盛り付け師γ）

![preview](https://gyazo.com/dceb17dac88d19bb3b339c4c6bc820a0/raw)

targa形式のものも含めて、フォルダ内の画像閲覧ができるデスクトップ向けソフトです。

本来は先方から指定されたフォルダ構造で成果物を整理するのを助けるソフトのつもりでしたが、
- 注意事項をjsonで記述するための標準的な形式を定めるのが大変
- 形式云々よりもそもそも先方から渡される注意事項を丁寧に読み込んだ方が何かと速い

ということで、せめて.tgaというデフォルトの画像閲覧機能では見られない画像ファイルを簡単に見られるソフトということで作りました。

残念ながらスマホやタブレットからでは使えませんが、ぜひご活用ください。

最適化も甘くて重かったり止まったりもしますが、そこはご勘弁ください。


## プログラミング慣れしている方向け
```
project_env\Scripts\activate
```
```
pip install -r requirements.txt
```
```
python src/main.py;
```

## 初心者向け
- (本ソフトのexeファイル)[]をダウンロードし、これをダブルクリックすると起動できます。
 - 現在、Windows11とMacに対応しています。