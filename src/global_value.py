# https://qiita.com/minidaruma/items/11eafc95855c007335f6
# 本来は何もなしでいけるのだが、今回は色々使う

# src/global_value.py

from file_types import detect_item_type 

class ItemFromLeft:
    def __init__(self):
        # will be list of strings of path
        self.item_list = []

    def get(self):
        return self.item_list
    
    def item_type(self):
        if len(self.item_list) == 0: return None
        return detect_item_type(self.item_list[0])
        
    def is_same_type(self, item):
        if len(self.item_list) == 0: return True
        return detect_item_type(item) == self.item_type()

    def toggle(self, item):
        if not self.is_same_type(item): return
        if item not in self.item_list: self.item_list.append(item)
        else: self.item_list.remove(item)

    def includes(self, item):
        return item in self.item_list

    def clear(self):
        self.item_list.clear()

# グローバル変数のように使う
item_from_left = ItemFromLeft()


"""
使い方


$ my_function.py
import global_value as g

def func1():
    g.val1 = 1

    
$ main.py
import my_function
import global_value as g

def main():
    func1()
    print(g.val1)

"""