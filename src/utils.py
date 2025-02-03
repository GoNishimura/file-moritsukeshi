# src/utils.py

# ウィジェット一覧をリストで取得
# https://qiita.com/noelgld13/items/c3355566d37553ea0b82
def get_all_widget (wid, finList=None) -> list:
    if finList is None:
        finList = []
    _list = wid.winfo_children()        
    for item in _list :
        finList.append(item)
        get_all_widget(item,finList)   
    return finList

# common tooltips

# src/file_types.py
