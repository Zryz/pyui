from typing import List, Dict
from random import randint
from time import sleep
from math import sqrt
from collections import defaultdict

from .common.utils import gen_random_char
from .common.colours import STARTING_COLOUR_COUNT

from .elements.page import Page
from .elements.window import Window

from .engine.content import Content
from .engine.controls import Controls

import curses, signal, logging, threading

def nested_dict():
    return defaultdict(nested_dict)
 
""" PYUI handles the initilisation of stdscrn for curses and the selection / creation of a Page instance when set as the active page.
    This reduces the amount of memory use and simplies modifications as there is only one active at a time - rather than housing all Pages.

    Page structures are housed in the class variable 'page_struct' in the format {page_name: *page_struct_data} with page_struct_data being an *args into the Page class constructor"""

class PYUI:

    def __init__(self, app:object) -> None:
        """@param app: The instantiation of self for the UI to access the app's functions.
            NOTE The app requires a cycle function as the main running process - this is so that window resizing doesn't stop the app"""
        self.logger = logging.getLogger(self.__class__.__name__)

        curses.wrapper(self.init_stdsrn)
        curses.curs_set(0)
        curses.raw()
        curses.noecho()

        signal.signal(signal.SIGWINCH, self.handle_resize)

        self.content = Content()
        self.controls = Controls()

        self.page_data: Dict[str, Dict[str, object]] = nested_dict()
        self.active_page: Page = None
        self.active_elements: dict = {}
        self.state = {'delay_time':0, 'colors_total':0}

        self.delay_time = 0 #Dynamically prevent 100% CPU without slowing redraw
        self.running = app

        self.t_height: int
        self.t_width: int
        
        self.decorative = []
        self.decorative_stop = threading.Event()
        self.decorative_stop.clear()
        self.decorative_thread = None
        self.decorative_flag = True

        self.init_colours()

    def init_colours(self):
        """Initialise the curses colour library, define starting colours here"""
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) 
        curses.init_color(1, 0, 600, 300)
        curses.init_pair(2, 1, curses.COLOR_BLACK)
    
        self.state['color_total'] = STARTING_COLOUR_COUNT

    def handle_resize(self, signum, frame):
        curses.endwin()
        curses.wrapper(self.init_stdsrn)
        curses.curs_set(0)
        curses.cbreak()
        curses.noecho()
        
        if hasattr(self, 'decorative_thread_id'): self.stop_decoration()
        name = self.active_page.name
        self.active_page = Page(self.t_height, self.t_width, name, *self.page_data[name]['page_struct'])
        #Maintain app cycle post resize
        self.running.cycle()

    def init_stdsrn(self, stdsrn:curses.window):
        self.stdsrn = stdsrn
        self.t_height, self.t_width = self.stdsrn.getmaxyx()
    
    #Define the layout of a page and create an assets structure to house content
    def define_page_struct(self, name, structure):
        self.page_data[name]['page_struct'] = structure
        self.content.build_asset_struct(name, len(structure[2]))

    def import_page_struct(self, page_data):
        for page_name, structure in page_data.items():
            self.define_page_struct(page_name, structure)

    def define_page_properties(self, name, structure):
        self.page_data[name]['page_properties'] = structure

    def apply_page_properties(self, properties, page):
        for key, value in properties:
            setattr(page, key, value)

    def define_window_properties(self, name, window_idx, properties):
        self.page_data[name]['window_properties'][window_idx].update(properties)

    def window_properties(self, name, window_idx):
        if not self.page_data[name].get('window_properties'): return
        return self.page_data[name]['window_properties'].get(window_idx)

    def page_properties(self, name):
        return self.page_data[name].get('properties')
         
    def create_page(self, *args):
        instance = Page(self.t_height, self.t_width, args[0], *args[1])
        return instance
    
    def select_page(self, name:str):
        self.stop_decoration()

        if name not in self.page_data: 
            raise ValueError('Name not found in page_structure. Name given', name)

        if self.active_page: self.prev_screen = self.active_page.name
        self.active_page = Page(self.t_height, self.t_width, name, *self.page_data[name]['page_struct'])
        if self.page_properties(name): self.apply_page_properties(self.page_properties(name), self.active_page)

    def register_element(self, element_name, element):
        self.active_elements[element_name] = element

    
    """Decorate windows with random characters for effect"""

    def start_decoration(self):
        def do_decorate():
            while not self.decorative_stop.is_set() and self.decorative:
                for window in self.decorative:
                    y, x = window.window.getmaxyx()
                    #Cancel out of too small windows
                    if y == 2 and x == 1:
                        return
                    
                    #We batch process a series of co-ordinates as this proved more efficient
                    #To then fixed a scalar issue in render we take the square root of the product of area
                    #Otherwise smaller areas update faster than smaller areas due to quantity of cells
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

        self.decorative_stop.clear()
        self.decorative_thread = threading.Thread(target=do_decorate, daemon=True)
        self.decorative_thread.start()
    
    def stop_decoration(self):
        if not self.decorative_thread: return
        self.decorative_stop.set()
        self.decorative_thread.join()

    def pause_decoration(self):
        self.decorative_stop.set()
        self.decorative_flag = False

    def restart_decoration(self):
        self.decorative_stop.clear()
        self.decorative_flag = True

    def window_properties(self, window_idx):
        return self.page_data[self.active_page.name]['window_properties'].get(window_idx)

    #Create a window over the entire terminal and clear it
    #A more efficient and less buggy way of starting afresh
    def refresh(self):
        window = curses.newwin(self.t_height, self.t_width, 0, 0)
        window.clear()
        window.noutrefresh()
        return
    
    #Apply new render state 
    def resets(self):
        self.decorative = []
        self.delay_time = 0
        self.init_colours()
        self.refresh()

    def render(self):
        self.resets()
        #Draw the content to the windows
        for _ in range(len(self.active_page.windows)):
            current_window:Window = self.active_page.windows[_]
            current_window.window.clear()
            if current_window.b_size == -1: self.decorative.append(current_window)
            
            current_window.apply_properties(self.window_properties(_), self.state)
            current_window.window_render(self.content.get(self.active_page.name, _), self.state)

            current_window.attach_border()
            current_window.window.noutrefresh()

        if self.decorative_flag: self.start_decoration()
        self.active_page.reset_write_line()
        curses.doupdate()
        #We increase the delay time here to prevent 100% CPU usage on threaded tasks
        self.delay_time = 10
