
from .uielement import UIElement
from ..ascii.fonts import generate_ascii_letter, get_ascii_width, get_ascii_height
import curses

#Titles are always centered with the option to feed in a font format.
#Useful for banners and headings in pages
class Title(UIElement, UIName='Title'):
    def __init__(self, content:str, font_source=None, rgb=(255,255,255), x_center=True, y_centre=False, write_line=None) -> None:
        self.source = font_source
        self.rgb = rgb
        self.centre = x_center
        self.y_center = y_centre
        self.words = content.split(' ')

        #Overide the window writer start line to allow overlaying content
        if write_line: self.write_line = write_line
        
        super().__init__(content)
        self.width:int #set during render time relative to window size

    def __add__(self, other):
        if isinstance(other, Title):
            for x in other.content:
                self.content.append(x)
        elif isinstance(other, str):
            self.content.append({'string':other.split('\n')})
        return self

    def __radd__(self, other):
        if isinstance(other, Title):
            for _ in range(len(other.content)-1, -1, -1):
                self.content.insert(0, other.content[_])
            return self
        elif isinstance(other, str):
            self.content.insert(0, {'string':other.split('\n')})
            return self
        
    def process_by_word(self, word):
        pass

    def apply_color(self, color_int):
        pass

    def export(self)->str:
        if self.centre: return self.content.center(self.width)
        else: return self.content
    
    def old_export(self):
        result = []
        if self.content.get('ascii'):
            #Create a holder for each line of the block art
            maximum_height = max([len(x) for i in self.content['ascii'] for x in i])
            build_lines = ["" for _ in range(maximum_height)]

            for word in self.content['ascii']:
                words = []
                for letter in word:
                    lines = ["" for _ in range(len(letter))]
                    #Unsupported language / blank title content
                    if not lines: return ''
                    for _ in range(len(letter)):
                        lines[_] += letter[_]
                    words = words + lines

            #Capital letters may have different heights to lower case,
            #For this we need to ammend the difference - usually due to hanging letters g, y etc.
                while len(words) < maximum_height:
                    words.append(" "*len(words[0]))
                for a in range(len(words)):
                    build_lines[a] += words[a]

            #Center the content to fit the page
            if self.centre: final = [x.center(self.width-1) for x in build_lines]
            else: final = [x for x in build_lines]

            result.append('\n'.join(final))
