from .elements.menu import Menu
from .elements.title import Title
from .elements.page import Page
from .elements.image import UIImage
from .pyui import PYUI

from .common.defs import UNIVERSAL_CONTROLS

from .engine.controls import Controls
from .engine.threading import Threader

UI_ELEMENTS = (Menu, Title, UIImage)
#GUI CONFIG

UIELEMENT_LOOKUP = {
    'Menu': Menu,
    'Title': Title
}

__all__ = ["Menu", "Title", "Page", "UIImage", "PYUI", "UI_ELEMENTS", "UIELEMENT_LOOKUP", "KEYS", "UNIVERSAL_CONTROLS", "Controls", "Threader"]