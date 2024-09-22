from .uielement import UIElement
from .title import Title

from ..ascii.fonts import get_ascii_height

class Menu(UIElement, UIName='Menu'):
    selected = None
    def __init__(self, title, content:dict, align='left', end="\n", display='all', title_font=None, text_font=None):
        self.values = [x for x in content.values()]
        self.title = title
        self.end = end
        self.display = display
        self.align = align

        self.selected = -1 #Used to choose a menu item

        self.title_font = title_font
        self.text_font = text_font
        
        super().__init__(content)

    def __add__(self, other):
        r = other
        if isinstance(other, str) and isinstance(self, Menu):
            r = ''
            for key, value in self.content.items():
                r += key + ' : ' + value + ' '
            r + other
        elif isinstance(self.content, (Menu)) and isinstance(other, str):
            r = self.content.content + other
        return r

    def reset(self):
        self.selected = None

    def next(self):
        if self.selected < len(self.values)-1:
            self.selected += 1

    def prev(self):
        if self.selected > 0:
            self.selected -= 1

    def get_value(self):
        return self.values[self.selected]
    
    def choose(self, input=None):
        if input != None:
            if isinstance(input, int):
                if input > -1 and len(self.content) > 0 and input-1 < len(self.content):
                    self.selected = input

    def controls(self)-> dict:
        r = {'[':[[self.prev]],']':[[self.next]], 'r':[[self.reset]]}
        return r
    
    def export(self)->str:
        r = ''
        if self.title_font: 
            title = Title(self.title, self.title_font)
            title.width = self.width
            content = title.export()
            r += content
            r += '\n' * content.count('\n')
        else: r += self.title + '\n\n'

        for idx, val in enumerate(self.content.items()):
            ast = ''
            if idx == self.selected: ast = 'O '
            if self.text_font:
                if self.display == 'key':
                    key = Title(ast + val[0], self.text_font)
                    key.width = self.width
                    r += key.export()
                elif self.display == 'value': 
                    value = Title(ast + val[1], self.text_font)
                    value.width = self.width
                    r += value.export()
                else: 
                    combined = Title(ast + val[0] + ' : ' + val[1], self.text_font)
                    combined.width = self.width
                    r += combined.export()
                r += '\n' * get_ascii_height(self.text_font)
            else:
                if self.selected == idx: r += '[x] '
                else: r += '  '

                if self.display == 'key': r += val[0]
                elif self.display == 'value': r += val[1]
                else: r += val[0] + ': ' + val[1]
                
            r += self.end
        return r