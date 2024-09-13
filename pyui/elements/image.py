import logging

from PIL import Image
from ..common.colors import extract_palette

"""A UIImage houses a PIL image with the correct 256 colours for use in a terminal environment
    These self.colors can then be used to init curses colours when the image is called upon """

def get_orientation(dimensions):
        if dimensions[1] > dimensions[0]:
            return 'landscape'
        elif dimensions[1] == dimensions[0]:
            return 'square'
        else:
            return 'portrait'

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
        self.logger.info('Window size is ' + str(window_size))
        if hasattr(self, 'empty'): return

        img = Image.open(self.image_file)
        img = img.convert('P', palette=Image.ADAPTIVE, colors=240)
        image_size = self.new_resize_to_window(img.size, window_size)
        self.img = img.resize(image_size, Image.Resampling.LANCZOS)

        self.height = self.img.height
        self.width = self.img.width
        self.colors = extract_palette(self.img)

        return True

    """To fit images within a container we do the following:
        Check if the images width is wider than the window - if so set the width the the window and scale a new height
        Check if the new height is taller than the window and repeat the same process so that both dimensions fit
        This approach naturally resolves square images"""
    
    def new_resize_to_window(self, image_size, window_size):
        if image_size[0] > window_size[1]:
            new_width = window_size[1]
            new_height = (new_width * image_size[1]) / image_size[0]
        if new_height > window_size[0]:
            new_height = window_size[0]
            new_width = (new_height * image_size[0]) / image_size[1]
        
        return int(new_width), int(new_height)