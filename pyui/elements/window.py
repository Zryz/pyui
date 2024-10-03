import curses, logging
from .image import UIImage

from ..common.colours import BODY_TEXT_COLOR, define_image_colours, rgb_colour_pair

from ..elements.title import Title
from ..elements.menu import Menu

from ..ascii.fonts import generate_ascii_letter, get_word_width, get_ascii_height, get_ascii_width, get_space_width

"""The Window class is an expanded wrapper to the curses window to provide more features and attributes.
    It houses a writer to apply content to the window to unify window drawing to one place"""

class Window:
    def __init__(self, nlines, ncols, start_y, start_x, b_size, b_char) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        if nlines == 1 or ncols == 1:
            self.b_size = 0
        self.window:curses._CursesWindow = curses.newwin(nlines, ncols, start_y, start_x)

        self.b_size: int = b_size
        self.b_char: str = b_char

        #We avoid writing to and using the last line of a window to avoid a curses.err when writting to the lower right cell
        self.height = nlines-1
        self.width = ncols

        #can be used to specify a minimum amount to shift content by
        self.x_pad: int = 0
        self.y_pad: int = 0

        #Specify the next line to write from - this is to handle multiple content within one window
        self.write_line: int = self.b_size+1
        self.write_end: int = self.height - self.b_size

        #Add lower right window to pad window
        self.window.addch(self.height, self.width-2," ", curses.color_pair(1))

        if self.b_size > 0:
            self.attach_border()
        
    """ Border modifications """

    def remove_border(self):
        self.b_size = 0

    def set_write_line(self, val):
        if val >= self.height-1: return
        self.write_line = val

    def increment_border(self):
        self.b_size += 1
    
    def decremenet_border(self):
        if self.b_size == 0: return
        self.b_size -= 1

    def set_background(self, rgb, fg=curses.COLOR_BLACK):
        self.rgb = rgb
        self.fg = fg

    def apply_properties(self, properties:dict, state:dict):
        if not properties: return 0
        for key, value in properties.items():
            if key == 'bg':
                state['color_total']+=1
                self.apply_background(state, bg=value, fg=properties.get('fg'))
    
    def apply_background(self, state, bg, fg=None)->int:
        if not fg: fg = curses.COLOR_BLACK
        rgb_colour_pair(fg, bg, state)
        self.window.bkgd(' ', curses.color_pair(state['color_total']))

    """Fill the furtherest bottom right cell with space for consistent rendering"""
    def fill_window(self):
        for line in range(self.height):
            for col in range(self.width):
                self.window.addch(line, col, " ", curses.color_pair(1))

    #Attach borders to windows and then return the adjusted b_size if window height is smaller than total border height
    def attach_border(self)->int:
        b_size = self.b_size

        #Handle if the self is smaller than the border and reduce accordingly
        while self.height <= (b_size*2):
            b_size -= 1

        border = self.b_char * self.width

        for _ in range(b_size):
            self.window.addstr(_,0,border, curses.color_pair(1))
        for _ in range(self.height-b_size, self.height):
            self.window.addstr(_,0,border, curses.color_pair(1))
            
        return b_size
    
    def title_color(self, color_int, rgb):
            curses.init_color(color_int, int((rgb[0] / 255)*1000), int((rgb[1] / 255)*1000), int((rgb[2] / 255)*1000))
            curses.init_pair(color_int, color_int, curses.COLOR_BLACK)
    
    """The renderer will be fed a list of content to write to the windows
        These will need formatting to a str and applying the correct window writer techniques
        It also will handle the application of colours to use and keep track of how many pairs are added"""
    
    def window_render(self, content_list:list, state:dict, write_line=None, x=None)->None:
        start_line = self.write_line

        self.logger.info('Colour count ' + str(state['color_total']))

        for content in content_list:
            if self.write_line != start_line: self.write_line += 2
            if isinstance(content, UIImage):
                self.image_writer(content)
                continue
            elif isinstance(content, Title):
                #Set witdth and export title to str
                if not content.source: self.writer(content.content)
                else: self.ascii_writer(content, state)
                continue
                #We can easily y centre here by halving the total height - content lines
            elif isinstance(content, Menu):
                setattr(content, 'width', self.width)
                content = content.export()
            elif isinstance(content, dict):
                content = content.__repr__()
            if not isinstance(content, str):
                raise ValueError('Invalid type sent to window writer, received: ' + str(type(content)))   

            self.writer(content, write_line, x)

        self.window.noutrefresh()

    """Write content to the window via curses and applies any colours and formatting - returns the current colour count"""
    def writer(self, content, color_int=None, write_line=None, x=None):
        if not color_int: color_int = 1 #Init to 1 when color not provided
        if write_line: self.write_line = write_line 
        if not x: x = 0 + self.x_pad 
        i = 0  #Content iterator

        while self.write_line < self.write_end and i < len(content):
            #If the content is a new line adjust the write line and x accordingly
            if content[i] == '\n':
                self.write_line +=1
                x = 0 + self.x_pad
                i+=1
                continue
            #Handle words that can't fit in remaining width
            elif content[i:].count(' ') > 0 and content[i:].index(' ') > (self.width - x):
                self.write_line +=1
                x = 0 + self.x_pad
            
            if x >= self.width:
                x = 0
            try:
                self.window.addstr(self.write_line, x, content[i], curses.color_pair(color_int))   
            except curses.error as e:
                self.logger.info(str(self.write_line) + ' ' + str(x) + ' ' + content[i] + ' ' + str(self.height) + ' ' + str(self.width))

            x += 1
            i += 1

    # Originall the Title class pre-built the entire ascii string but this became bloated and inefficient to manage
    # To make over-wrapping easier I'm switching to a word by word generation and application system

    def ascii_writer(self, title:Title, state:dict):
        # TODO Correctly calculate centring of font - will need to take into account widths between chars and what's already in library
        total_width = sum([get_word_width(x, title.source) + get_space_width(title.source) for x in title.words])

        if total_width < self.width:
            x = (self.width - total_width) // 2
        else:
            x = 0 + self.x_pad

        #content = title.export()
        #if title.y_center: self.write_line = (self.height - content.count('\n'))//2
        if hasattr(title, 'write_line'): self.write_line = title.write_line

        if title.rgb != (255,255,255):
            state['color_total'] += 1
            self.title_color(state['color_total'], title.rgb)
            color_int = state['color_total']
        else:
            color_int = 1

        for word in title.words:
            if x + get_word_width(word, title.source) > self.width:
                x = 0 + self.x_pad
                self.write_line += get_ascii_height(title.source) + 1
                if self.write_line >= self.write_end: return
            for letter in word:
                ascii = generate_ascii_letter(letter, title.source)
                #logging.info(ascii)
                #if not ascii: continue
                letter_width = get_ascii_width(letter, title.source)
                i = 0
                y = 0
                char_x = 0
                while self.write_line + y < self.write_end and i < len(ascii):
                    if ascii[i] == '\n':
                        y += 1
                        char_x = 0
                        i+=1
                        continue
                    try:
                        self.window.addstr(self.write_line + y, x + char_x, ascii[i], curses.color_pair(color_int))
                    except curses.error as e:
                        self.logger.info(self.logger.info(str(self.write_line) + ' ' + str(x) + ' ' + ascii[i] + ' ' + str(self.height) + ' ' + str(self.width)))
                    char_x+=1
                    i+=1
                x += letter_width+1
            x += 2

    def image_writer(self, image:UIImage):
        img = image.create_image((self.height, self.width))
        if not img: return
        define_image_colours(image.colors)
        y = 0
        #Set the image to the y-centre of the window and set this to starting value
        self.write_line = start = ((self.height - image.img.size[1])//2)+1

        #Check for a centre tag on the UIImage and shift to the middle of the page
        if image.center:
            m = window_x = max((self.width - image.width*2) // 2, 0)
        else:
            m = window_x = 0
        #Keep write line within starting place and image height, keep write line within window size (inlcuding bottom border) and keep y within size of image.height
        while self.write_line < start + image.height and self.write_line < self.write_end and y < image.height:
            window_x = m
            for x in range(image.width):
                if window_x >= self.width:
                    x = image.width
                    continue
                pixel = image.img.getpixel((x, y))
                #try:
                self.window.addstr(self.write_line, window_x, "  ", curses.color_pair(pixel+17))
                #except curses.error as e:
                #    self.logger.info(str(window_x) + ' ' + str(x) + ' ' + str(y) + ' ' + str (self.height) + ' ' + str(self.width))
                #    pass
                window_x += 2
            self.write_line += 1
            y+=1

        