import curses, math
from PIL import Image

#Anything that handles curses or helps to initialise the curses windows and it's global namespaces are referenced and defined from here



def generate_xterm_colors():
    colors = []

    # 16 basic colors
    basic_colors = [
        (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), (128, 0, 128), (0, 128, 128), (192, 192, 192),
        (128, 128, 128), (255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255)
    ]
    
    colors.extend(basic_colors)

    # 216 colors (6x6x6 color cube)
    levels = [0, 95, 135, 175, 215, 255]
    for r in levels:
        for g in levels:
            for b in levels:
                colors.append((r, g, b))

    # 24 grayscale colors
    grayscale_levels = [8 + 10 * i for i in range(24)]
    for gray in grayscale_levels:
        colors.append((gray, gray, gray))

    return colors

def init_colors()->int:
    """Initialise the curses color library, define starting colours here"""
    curses.start_color()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) 
    curses.init_color(2, 0, 600, 300)
    curses.init_pair(2, 2, curses.COLOR_BLACK)

    return 2

def define_image_colors(colors):
    for i, (r, g, b) in enumerate(colors):
        if i >= 239:
            break
        curses.init_color(i+17, int(r * 1000 / 255), int(g * 1000 / 255), int(b * 1000 / 255))
        curses.init_pair(i+17, i+17, i+17)

def color_distance(self, c1, c2):
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2)
    
        # Find the nearest color in the predefined collection
def find_nearest_color(self, target_color):
    nearest_index = min(range(len(XTERMCOLOURS)), key=lambda i: self.color_distance(target_color, XTERMCOLOURS[i]))
    return nearest_index+1

def extract_palette(img:Image):
        palette = img.getpalette()
        colors = []
        for i in range(0, len(palette), 3):
            r, g, b = palette[i], palette[i+1], palette[i+2]
            colors.append((r, g, b))
        return colors

XTERMCOLOURS = generate_xterm_colors()

BODY_TEXT_COLOR = 1