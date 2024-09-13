class UIElement:
    def __init_subclass__(cls, UIName, **kargs) -> None:
        cls.UIName = UIName
        super().__init_subclass__(**kargs)

    def __init__(self, content) -> None:
        self.content = content

    def __call__(self):
        return self.export()
    
    def __repr__(self) -> str:
        return self.export()
    
    """    
    @classmethod
    def create(cls, UIName, name, content):
        return UIELEMENT_LOOKUP[UIName](name, content)
    """    

    def update(self, contents):
        while isinstance(self.content, UIElement):
            self = self.content
        self.content = contents

    """All UIElements require a form of str output for a curses window to display"""
    def export(self)->str:
        raise NotImplementedError('uielement: export() method required by uielements')