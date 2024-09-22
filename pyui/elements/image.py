import logging

from PIL import Image
from ..common.colours import extract_palette

""" UI Images are created with the raw image data and created during render call
    Colours are set to 240 so that the terminal has 16 to use for text"""

class UIImage:
    def __init__(self, image_file, center=False) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        if not image_file: 
            self.empty = True
            return
        self.image_file = image_file
        self.center = center

        self.height:int
        self.width:int
        self.img:Image
        self.centre:bool

    """Images are created when required by the engine and only the image_data is housed until then
        We give the creation a window_size and then calculate how best to fit the image
        Returns a boolean flag to indicate succesful creation"""
    def create_image(self, window_size)-> bool:
        if hasattr(self, 'empty'): return False

        img = Image.open(self.image_file)
        img = img.convert('P', palette=Image.ADAPTIVE, colors=240)
        image_size = self.scale_to_window(img.size, window_size)

        self.img = img.resize(image_size, Image.Resampling.LANCZOS)
        self.height = self.img.height
        self.width = self.img.width
        self.colors = extract_palette(self.img.getpalette())

        return True

    def scale_to_window(self, image_size, window_size):
        if image_size[0] > window_size[1]:
            new_width = window_size[1]
            new_height = (new_width * image_size[1]) / image_size[0]
        else: 
            new_width = image_size[0]
            new_height = image_size[1]
            
        if new_height > window_size[0]:
            new_height = window_size[0]
            new_width = (new_height * image_size[0]) / image_size[1]

            
        
        return int(new_width), int(new_height)