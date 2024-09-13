
from .uielement import UIElement
from ..ascii.fonts import generate_ascii_letter

#Titles are always centered with the option to feed in a font format.
#Useful for banners and headings in pages
class Title(UIElement, UIName='Title'):
    def __init__(self, content:str, font_source=None, rgb=(255,255,255), x_center=True, y_centre=False) -> None:
        self.source = font_source
        self.rgb = rgb
        self.centre = x_center
        self.y_center = y_centre
        
        if font_source != None:
            content = [{'ascii':[generate_ascii_letter(x, font_source) for x in content if generate_ascii_letter(x, font_source) != None]}] #'source':font_source}]
        else:
            content = [{'string':content.split('\n')}]
        super().__init__(content)

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

    def export(self)->str:
        result = []
        for content in self.content:
            if content.get('ascii'):
                #We have to generate ASCII art as part of the render process
                #Create a holder for each line of the block art
                maximum_height = max([len(i) for i in content['ascii']])
                build_lines = ["" for _ in range(maximum_height)]
                for letter in content['ascii']:
                    holder = ["" for _ in range(len(letter))]
                    for _ in range(len(letter)):
                        holder[_] += letter[_]
                #Capital letters may have different heights to lower case,
                #For this we need to ammend the difference - usually due to hanging letters g, y etc.
                    while len(holder) < maximum_height:
                        holder.append(" "*len(holder[0]))
                    for a in range(len(holder)):
                        build_lines[a] += holder[a]
                                
                #Center the content to fit the page
                if self.centre: final = [x.center(self.width-1) for x in build_lines]
                else: final = [x for x in build_lines]

                result.append('\n'.join(final))

            elif content.get('string'):
                if self.centre: 
                    final = [x.center(self.width-1) for x in content['string']]
                    result.append('\n'.join(final))
                else:
                    final = [x for x in content['string']]
                    result.append('\n'.join(final))
                #result.append('\n'.join([x.center(self.width-1) for x in content['string']]))

        return '\n'.join(result)
