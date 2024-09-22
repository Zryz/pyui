from typing import Any, Dict, List
from collections import defaultdict
import curses

KEYS = {'bs':263, 'up':259, 'left':curses.KEY_LEFT, 'right':curses.KEY_RIGHT, 'down':258, 'enter':'\\n', 'esc':'\x1b'}

def nested_controls():
    return defaultdict(nested_controls)

class Controls:
    """
    Controls are a nested Dictionary in the form 
    { control_name : { key_press :: [[ function , *kargs {} ]] }
    NOTE The double nested list value for 'key_press' so that mutiple functinos can be executed with one keystroke

    To point controls to class functions you can use the example method below

    Example Class:

    class Test:
        def __init__():
            pass
        
        def function1(self, name):
            self.name = name

    Example function (can be housed in external module)

    def ui_controls(instance):
    
        return {'test_control' : [[ instance.function1 , {'name':'test'} ]]}

    self.controls_db:: the main database to house controls
    self.active_controls:: currently active control set
    self.quit_keys:: keys that are set to quit the program
    self.quit_flag:: a switch to turn on / off the use of quit keys

    """
    def __init__(self) -> None:
        """Controls have a control name to use as selection
            Within these you can specify a page_name for them to apply on"""
        
        #The main control database with a name and then control lookup
        self.db: Dict[str, Dict[str, List[function, Dict[str, str]]]] = {}
        #Specify what the active controls are - set with select function
        self.active_controls: Dict[str, List[function, Dict[str, str]]]
        #Define app quit keys useable throughout when quit_flag is True
        self.quit_keys:List[str] = []
        #Flag to define use of quit keys
        self.quit_flag:bool = True

    """Calling the controls will search for a keypress and then return the next set of tasks to complete
        NOTE This is the main calling block for logic within an app"""
    
    def __call__(self) -> Any:
        """keys should always be single press - when they are given greater than 1 in length we lookup what they are in the KEY dictionary"""
        input = -1
        while input == -1:
            input = self.get_keypress()
            if input not in self.active_controls:
                input = -1
        return self.active_controls[input]
    
    def get_keypress(self, key=-1):
        curses.noecho()
        while key == -1:
            window = curses.newwin(1,1,0,0)
            window.keypad(True)
            key = window.getch()
        return key
        #return chr(key).__repr__().replace("'", '')
    
    def set_quit_keys(self, *keys):
        for key in keys:
            self.quit_keys.append(key)

    def toggle_quit(self):
        self.quit_flag = not self.quit_flag

    def key_check(self, controls:dict):
        for page_name, value in controls.items():
            #We check if a key is included in the lookup table
            for key in list(value.keys()):
                if len(key) > 1 and key in KEYS:
                    r = KEYS[key]  
                else:
                    r = ord(key)
                controls[page_name][r] = controls[page_name].pop(key)
        return controls

    def set_controls_db(self, controls:dict):
        self.db = self.key_check(controls)

    def set_prev_controls(self):
        if hasattr(self, 'active_controls'):
            tmp = self.active_controls
            self.active_controls = self.prev_controls
            self.prev_controls = tmp
    
    """ Allows you to concatenate controls into a single database when calling from different instances 
        NOTE the last duplicate key takes precedence over pre-existing assignments"""

    def merge_set_controls(self, *args):
        for controls in args:
            self.db = {**self.db, **controls}

    def add(self, control:dict):
        self.db.update(control)

    """ Sets the active controls and inserts quit keys when self.quit_flag is on
        NOTE This will overwrite any existing binding using a quit key so be mindful"""
    def select(self, control_name):
        self.active_controls = self.db[control_name]
        #Check for use of quit keys and insert them into the current dicitionary
        if self.quit_flag and self.quit_keys:
            for key in self.quit_keys:
                self.active_controls[ord(key)] = [[exit]]
        if self.db.get('universal'):
            for key, value in self.db['universal'].items():
                self.active_controls[key] = value

    def attach_binding(self, control_name, key, *args):
        if not isinstance(key, int):
            if len(key) > 1 and KEYS.get(key): key = KEYS[key]
            else: key = ord(key)
        
        if control_name not in self.db:
            self.db[control_name] = {}
        if key not in self.db[control_name]:
            self.db[control_name][key] = []
        for task in args:
            if isinstance(task, list):
                self.db[control_name][key].append(task)   
            else:
                self.db[control_name][key].append([task])
        
    def get_controls(self):
        return self.active_controls