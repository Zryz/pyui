import curses, math
from PIL import Image

#Anything that handles curses or helps to initialise the curses windows and it's global namespaces are referenced and defined from here

#Colour pair int 1 = str text
#Colour pair int 2 = Decorate text

STARTING_COLOUR_COUNT = 3
BODY_TEXT_COLOR = 1

def generate_xterm_colours():
    colours = []

    # 16 basic colours
    basic_colours = [
        (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), (128, 0, 128), (0, 128, 128), (192, 192, 192),
        (128, 128, 128), (255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255)
    ]
    
    colours.extend(basic_colours)

    # 216 colours (6x6x6 colour cube)
    levels = [0, 95, 135, 175, 215, 255]
    for r in levels:
        for g in levels:
            for b in levels:
                colours.append((r, g, b))

    # 24 grayscale colours
    grayscale_levels = [8 + 10 * i for i in range(24)]
    for gray in grayscale_levels:
        colours.append((gray, gray, gray))

    return colours

#Creates a fg, bg pair based on rgb tuple and returns new colour count
def rgb_colour_pair(fg:tuple, bg:tuple, state:dict)->int:
    state['color_total']+=1
    #FG Color
    curses.init_color(state['color_total'], int((fg[0] / 255)*1000), int((fg[1] / 255)*1000), int((fg[2] / 255)*1000))
    #BG Color
    curses.init_color(state['color_total']+1, int((bg[0] / 255)*1000), int((bg[1] / 255)*1000), int((bg[2] / 255)*1000))
    curses.init_pair(state['color_total'], state['color_total'], state['color_total']+1)

def define_image_colours(colours):
    for i, (r, g, b) in enumerate(colours):
        if i >= 239:
            break
        curses.init_color(i+17, int(r * 1000 / 255), int(g * 1000 / 255), int(b * 1000 / 255))
        curses.init_pair(i+17, i+17, i+17)

def colour_distance(self, c1, c2):
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2)
    
        # Find the nearest colour in the predefined collection
def find_nearest_colour(self, target_colour):
    nearest_index = min(range(len(XTERMCOLOURS)), key=lambda i: self.colour_distance(target_colour, XTERMCOLOURS[i]))
    return nearest_index+1

def extract_palette(palette):
        colours = []
        for i in range(0, len(palette), 3):
            r, g, b = palette[i], palette[i+1], palette[i+2]
            colours.append((r, g, b))
        return colours

XTERMCOLOURS = generate_xterm_colours()

