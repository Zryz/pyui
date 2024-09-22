from typing import List, Any
from typing import Any
from .window import Window

from ..common.utils import divide_span
from ..test.paths import dump_object

import logging

class Page:
    """
    Page is a collation of curses windows to form an app UI. The 

    Attributes:
        name (str): The name of the example.
        values (List[int]): A list of integer values.
        description (Optional[str]): An optional description of the example.

    Example:
        >>> example = ExampleClass(name="Sample", values=[1, 2, 3], description="A sample instance")
        >>> print(example.name)
        Sample
        >>> print(example.values)
        [1, 2, 3]
        >>> print(example.description)
        A sample instance
    """
    def __init__(self, t_height, t_width, name, y_div:List[float], x_div:List[float], b_size:List[int]=[], y_length=1, b_char='-') -> None:
        #We handle floating precision issues by rounding (for e.g sum [.2,.7,.1] == .9999)
        self.logger = logging.getLogger(self.__class__.__name__)

        if round(sum(y_div),1) != 1.0:
            raise ValueError("Invalid y_div - confirm totals 1.0 and number of sections set")
        
        #An optional attribute that specifies the x_pad value when windows are created
        self.x_padding:list

        #Tuple house the original instantiation stats for later recalling if terminal resized and rendering
        #self.page_stats = (y_div, x_div, b_size, b_char)

        self.windows: List[Window] = [] #Houses Window instances
        self.name:str = name

        #y_div_len = len(y_div)
        #Establish the number of y divisions
        y_divisions = divide_span(y_div, t_height)
        #Create page windows from top to bottom
        i = x_start = y_start = 0
        
        for _ in range(len(y_divisions)):
            if _ == len(y_divisions)-1: y_div_size = y_divisions[_]+1
            else: y_div_size = y_divisions[_]
        #Determine if we are splitting the current vertical partition horizontally 
            if x_div[_] != None:
                div_x_start = 0
                x_divisions = divide_span(x_div[_],t_width)
                for division in x_divisions:
                    #When a list is provided by divide_space the x_div is being applied to the end of the screen
                    #TODO We could specify an n of how many y_divs to extend to instead of blanket t_height
                    if isinstance(division, list):
                        self.windows.append(Window(sum(y_divisions[_:y_length+1]), division[0], y_start, div_x_start, b_size[i], b_char))
                        div_x_start += division[0]
                    else:
                        self.windows.append(Window(y_div_size, division, y_start, div_x_start, b_size[i], b_char))
                        div_x_start += division
                    i+=1
        #Otherwise we make a fully extended window
            else:
                self.windows.append(Window(y_div_size, t_width, y_start, x_start, b_size[i], b_char))
                i+=1
            y_start += y_div_size
        self.logger.info('Page object ' + name + ' created succesfully')

    def reset_write_line(self):
        for window in self.windows:
            window.write_line = window.b_size+1

    def apply_x_pad(self, x_pad):
        if len(x_pad) != len(self.windows):
            raise ValueError('Page: x_pad length does not match - length given', len(x_pad), 'size needed', len(self.windows))
        for _ in range(len(self.windows)):
            self.windows[_].x_pad = x_pad[_]

    #Return window instances that do not have a border and are not blocked from decoration
    def get_decorate_windows(self):
        return [self.windows[_] for _ in range(len(self.windows)) if self.b_size[_] > 0]
    