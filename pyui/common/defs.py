
PAGE_SECTIONS = ('header', 'body', 'footer')  # The breakdown of what a page is made up of

BORDER_CHAR = '-'

TEXT_ALIGN = {
    'center':str.center,
    'left':str.ljust,
    'right':str.rjust
            }
TEXT_FORMAT = {
    'cap':str.capitalize,
    'l':str.lower,
    'u':str.upper,
    't':str.title,
    'n':None
}



"""Q is a reserved keyspace that applies to every page on the app and cannot be overwritten"""

UNIVERSAL_CONTROLS = {'q':[[exit]], 'Q':[[exit]]}

DEFAULT_TEXT = {'end':'\n', 'prefix':'', 'indent':0, 'align':'l'}

VALID_TEXT_PROPERTIES = ['end', 'prefix', 'indent', 'align']

EXCLUDED_CHARS = set('\n\r\t\b\x1b/{}()[]')

CONTENT_Y_PAD = 2

global color_count

color_count = 0