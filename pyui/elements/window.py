import curses, logging
from .image import UIImage

from ..common.colors import BODY_TEXT_COLOR, define_image_colors
from ..common.defs import color_count

from ..elements.title import Title
from ..elements.menu import Menu

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

        """Fill the furthest bottom right cell with am empty string for consistent rendering
        You cannot write to y[-1] x[-1] in curses as it generates a curses.err"""

        self.window.addch(self.height-1, self.width-1," ", curses.color_pair(1))

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
    
    """The renderer will be fed a list of content to write to the windows
        These will need formatting to a str and applying the correct window writer techniques
        It also will handle the application of colours to use and keep track of how many pairs are added"""
    
    def window_render(self, content_list, colour_count, write_line=None, x=None, colour_int=None):
        self.logger.info("Content length is " + str(len(content_list)))
        if not colour_int: colour_int = BODY_TEXT_COLOR
        m = self.write_line
        if colour_count == 16:
            colour_count -= 1
        for content in content_list:
            if self.write_line != m: self.write_line += 4
            if isinstance(content, UIImage):
                self.image_render(content)
                continue
            elif isinstance(content, (Title, Menu)):
                setattr(content, 'width', self.width)
                if isinstance(content, Title):
                    #Apply the RGB colour values and register them in curses and set them as a pair
                    if content.rgb != (255,255,255): 
                        curses.init_color(colour_count+1, int((content.rgb[0] / 255)*1000), int((content.rgb[1] / 255)*1000), int((content.rgb[2] / 255)*1000))
                        curses.init_pair(colour_count+1, colour_count+1, curses.COLOR_BLACK)
                        #m = colour_int
                        colour_int = colour_count+1
                        colour_count+=1
                    #We must set the y_center as a window flag for the content of title before it is burnt to a str
                    if content.y_center: setattr(self, 'y_center', True)
                #Export the Title into it's str
                content = content.export()
                #Now we can easily calculate how to vertically centre a title by reference to \n
                if hasattr(self, 'y_center'): self.write_line = (self.height - content.count('\n'))//2
                c_type = 'Title'
                #We can easily y centre here by halving the total height - content lines
            elif isinstance(content, dict):
                content = content.__repr__()
                c_type = 'Dict'
            elif isinstance(content, str):
                c_type = 'Str'
            else:
                raise ValueError('Invalid type sent to writer - type sent ' + str(type(content)))
            #Add a new line between content
            self.writer(content, colour_int, c_type, colour_count, write_line, x)

        #if not isinstance(content, str):
        #    raise TypeError('Invalid type provided to writer. Recieved type ', type(content))
        return colour_count


    """Write content to the window via curses and applies any colours and formatting - returns the current colour count"""
    def writer(self, content, colour_int:int, c_type, colour_count, write_line=None, x=None):
        if write_line:
            self.write_line = write_line
        """Writer"""
        #String iterator
        i = 0 
        #self.write_line = (self.height - content.count('\n'))//2

        #x write co-ordinate
        if not x:
            x = 0 + self.x_pad

        while self.write_line < self.write_end and i < len(content):
            #If the content is a new line adjust the write line and x accordingly
            if content[i] == '\n':
                self.write_line +=1
                x = 0 + self.x_pad
                i+=1
                continue
            #If upcoming content overflows the width of the window or words can't be completed without getting chopped up
            elif content[i:].count(' ') > 0 and content[i:].index(' ') > (self.width - x) and c_type != 'Title':
                self.write_line +=1
                x = 0 + self.x_pad

                """To cope with Title cropping we temporarily shift the write_line and x relative to i and recursively feed this to create a new line with ASCII fonts
                    NOTE needs more refining as it chops off letters and only supports an extra line"""
            elif x == self.width and c_type == 'Title':
                if content[i:].count('\n') > 0:
                    l = i
                    m = self.write_line
                    lines = content.count('\n')
                    while content[i] != '\n':
                        self.window_render([content[i]], colour_count, m+lines+2, i-l, colour_int)
                        i+=1
                    self.write_line = m
                    continue
                else:
                    break
            try:
                self.window.addstr(self.write_line, x, content[i], curses.color_pair(colour_int))
            except curses.error as e:
                pass
                #print(self.write_line, x, self.height, self.width)
            x += 1
            i += 1
            self.window.noutrefresh()


    def image_render(self, image:UIImage):
        img = image.create_image((self.height, self.width))
        if not img: return
        define_image_colors(image.colors)
        
        """Image reference co-ordinates"""
        #Y co-ordinate for reference pixel in image
        y = 0

        """Window write co-ordinates"""
        #Set the image to the y-centre of the window and set this to starting value
        self.write_line  = start = ((self.height - image.img.size[1])//2)+1

        #Check for a centre tag on the UIImage and shift to the middle of the page
        if image.center:
            m = window_x = (self.width - image.width*2) // 2
        else:
            m = window_x = 0

        #m = 0
        #Keep write line within starting place and image height, keep write line within window size (inlcuding bottom border) and keep y within size of image.height
        while self.write_line < start + image.height and self.write_line < self.write_end and y < image.height:
            window_x = m
            for x in range(image.width):
                if window_x >= self.width:
                    continue
                pixel = image.img.getpixel((x, y))
                self.window.addstr(self.write_line, window_x, "  ", curses.color_pair(pixel+17))
                window_x += 2
            self.write_line += 1
            y+=1
        self.window.noutrefresh()

        