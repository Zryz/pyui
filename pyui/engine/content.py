from typing import Dict

""" Content is housed in a simple nested dictionary structure that resolves to a list of content.
    This is to build the core layout of an app.
    For dynamically created content on run you can add and remove content as needed.
    
    The structure is in the form {key(page_name): key{window_idx}: list[content]}
    

    """

class Content:
    def __init__(self) -> None:
        #Static content that would look the same every time rendered
        self.content_db: Dict[str, Dict[int, list]] = {}
        #A store for dynamically created elements that can be accessed by name
        self.live_objects = {}
        
    def select_page_content(self, page_name)-> Dict[int, list]:
        if page_name not in self.content_db: return
        return self.content_db[page_name]

    def build_asset_struct(self, page_name, window_count):
        self.content_db[page_name] = {_:[] for _ in range(window_count)}
    
    def set(self, page_name, window_idx, content):
        self.content_db[page_name][window_idx].append(content)

    def add(self, page_name, window_idx, content):
        self.content_db[page_name][window_idx].append(content)

    def pop(self, page_name, window_idx):
        self.content_db[page_name][window_idx].pop()

    def clear(self, page_name, window_idx=None):
        if not window_idx:
            for key in self.content_db[page_name]:
                self.content_db[page_name][key] = []
        self.content_db[page_name][window_idx] = []

    def get(self, page_name, window_idx):
        if page_name not in self.content_db: return []
        elif self.content_db[page_name][window_idx] == []: return []
        else: return self.content_db[page_name][window_idx]

    def add_live(self, **live_element):
        for name, el in live_element.items():
            self.live_objects[name] = el
    
    def clear_live(self):
        self.live_objects = {}