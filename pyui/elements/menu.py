from .uielement import UIElement

class Menu(UIElement, UIName='Menu'):
    idx = None
    def __init__(self, title, content:dict, align='left', end="\n", display='all'):
        self.values = [x for x in content.values()]
        self.title = title
        self.end = end
        self.display = display
        self.align = align
        self.idx = -1 #Used to choose a menu item
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
        self.idx = None

    def next(self):
        if self.idx < len(self.values)-1:
            self.idx += 1

    def prev(self):
        if self.idx > 0:
            self.idx -= 1

    def get_value(self):
        return self.values[self.idx]
    
    def choose(self, input=None):
        if input != None:
            if isinstance(input, int):
                if input > -1 and len(self.content) > 0 and input-1 < len(self.content):
                    self.idx = input

    def controls(self)-> dict:
        r = {'[':[[self.prev]],']':[[self.next]], 'r':[[self.reset]]}
        return r
    
    def export(self)->str:
        r = ''
        r += self.title + '\n\n'
        for idx, val in enumerate(self.content.items()):
                if self.idx == idx:
                    r += '* '
                else: r += '  '
                if self.display == 'key': r += val[0]
                elif self.display == 'value': r += val[1]
                else: r += val[0] + ': ' + val[1]
                r += self.end
        return r