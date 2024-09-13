from typing import List
from random import randint
from time import sleep
from math import sqrt

from .common.utils import gen_random_char
from .common.colors import init_colors
from .common.defs import color_count

from .elements.page import Page
from .elements.image import UIImage
from .elements.window import Window
from .elements.uielement import UIElement

from .engine.content import Content
from .engine.controls import Controls
from .engine.threading import Threader

from .test.paths import gen_test_file, dump_object

import curses, signal, logging
 
""" PYUI handles the initilisation of stdscrn for curses and the selection / creation of a Page instance when set as the active page.
    This reduces the amount of memory use and simplies modifications as there is only one active at a time - rather than housing all Pages.

    Page structures are housed in the class variable 'page_struct' in the format {page_name: *page_struct_data} with page_struct_data being an *args into the Page class constructor"""

gen_test_file()

class PYUI:

    def __init__(self, app:object) -> None:
        """@param app: The instantiation of self for the UI to access the app's functions.
            NOTE The app requires a cycle function as the main running process - this is so that window resizing doesn't stop the app"""
        self.logger = logging.getLogger(self.__class__.__name__)

        super().__init__()
        curses.wrapper(self.init_stdsrn)
        curses.curs_set(0)
        curses.cbreak()
        curses.noecho()

        signal.signal(signal.SIGWINCH, self.handle_resize)

        self.content = Content()
        self.controls = Controls()
        self.threader = Threader()
        self.running = app
        self.color_count:int

        #Houses the sizes and dimensions of Pages - called upon when a Page is made active
        self.page_data = {}
        self.active_page: Page = None
        self.active_elements: dict = {}
        
        self.t_height: int
        self.t_width: int
        
        #A dynamic sleep timer to prevent 100% CPU without affecting redraw latency
        self.delay_time = 0
        
        self.decorative: bool = True
        self.decorative_id = 0
        self.decorative_stop = self.threader.new_event()

        """Colours are 1 indexed and we reserve the first 16 to use for text - the remaining 240 are for image rendering"""
        self.color_count = init_colors()

    def handle_resize(self, signum, frame):
        curses.endwin()
        curses.wrapper(self.init_stdsrn)
        curses.curs_set(0)
        curses.cbreak()
        curses.noecho()
        self.color_count = init_colors()
        
        if hasattr(self, 'decorative_thread_id'): self.stop_decoration()
        self.active_page = self.create_page(self.active_page.name, self.page_data[self.active_page.name]['page_struct'])
        #Maintain app cycle post resize
        self.running.cycle()
        
        return

    def init_stdsrn(self, stdsrn:curses.window):
        self.stdsrn = stdsrn
        self.t_height, self.t_width = self.stdsrn.getmaxyx()
    
    #Define the layout of a page and create an assets structure to house content
    def define_page_struct(self, name, structure):
        self.page_data[name] = {'page_struct': structure}
        self.content.build_asset_struct(name, len(structure[2]))

    def import_page_struct(self, page_data):
        for page_name, structure in page_data.items():
            self.define_page_struct(page_name, structure)
         
    def create_page(self, *args):
        instance = Page(self.t_height, self.t_width, args[0], *args[1])
        return instance
    
    def select_page(self, name:str):
        self.decorative_stop.set()
        if name not in self.page_data: 
            raise ValueError('Name not found in page_structure. Name given', name)

        if self.active_page: self.prev_screen = self.active_page.name
        self.active_page = Page(self.t_height, self.t_width, name, *self.page_data[name]['page_struct'])
        self.color_count = init_colors()

    """CONTROL HANDLING"""

    def set_active_element(self, element_name, element):
        self.active_elements[element_name] = element
    
    def start_decoration(self):
        self.decorative_stop.set()
        if self.decorative_id > 0:
            self.threader.stop_thread(self.decorative_id)
        def do_decorate(stop_event):
            decorative = [x for x in self.active_page.windows if x.b_size == -1]
            """Prevent threading with empty lists"""
            if not decorative: return
            while not stop_event.is_set():
                for window in decorative:
                    y, x = window.window.getmaxyx()
                    if y == 2 and x == 1:
                        return
                    """For efficiency we generate a series of co-ordinates that scales to the square root of the size of the cell
                        This prevents smaller windows getting filled faster than larger areas as it consistently scales changes accordingly"""
                    co_ords = [(y-1, x-1)]
                    #Prevent against writing the bottom right cell
                    while (y-1, x-1) in co_ords:
                        co_ords = [(randint(0,y-1),randint(0,x-1)) for _ in range(int(sqrt((x*y))))]
                    for _ in range(len(co_ords)):
                        window.window.addch(co_ords[_][0], co_ords[_][1], gen_random_char(), curses.color_pair(2))
                    window.window.noutrefresh()
                    curses.doupdate()
                    sleep(0.001)
                curses.napms(self.delay_time)
        #Reset the stop_event flag
        self.decorative_stop.clear()
        #Restart the thread
        self.decorative_id = self.threader.new_thread(do_decorate, self.decorative_stop)

    #Create a window over the entire terminal and clear it
    #A more efficient and less buggy way of starting afresh
    def refresh(self):
        window = curses.newwin(self.t_height, self.t_width, 0, 0)
        window.clear()
        window.noutrefresh()
        return


    def render(self):
        self.delay_time = 0
        self.start_decoration()
        #Clear the screen ready to redraw changes to content
        self.refresh()
        #Draw the content to the windows
        for _ in range(len(self.active_page.windows)):
            #Skips empty content
            #if not self.content.get(self.active_page.name, _): continue
            #Fetch the current_window and it's content from ui_assets
            current_window:Window = self.active_page.windows[_]
            current_window.window.clear()
            current_window.attach_border()

            self.color_count = current_window.window_render(self.content.get(self.active_page.name, _), self.color_count)
            #content:list = self.content.get(self.active_page.name, _)
            #if content: self.color_count = current_window.writer(content, self.color_count)
            current_window.window.noutrefresh()

        self.active_page.reset_write_line()
        curses.doupdate()
        #We increase the delay time here to prevent 100% CPU usage on threaded tasks
        self.delay_time = 10
