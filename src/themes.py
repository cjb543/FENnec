class ThemeBase:
    def paint(self,widget,event,painter): pass

class ClassicTheme(ThemeBase):
    def paint(self ,widget,event,painter): pass

class RetroTheme(ThemeBase):
    def paint(self ,widget,event,painter): pass

class CatpuccinTheme(ThemeBase):
    def paint(self ,widget,event,painter): pass

class GruvboxTheme(ThemeBase):
    def paint(self ,widget,event,painter): pass

class GrayscaleTheme(ThemeBase):
    def paint(self ,widget,event,painter): pass

class LetteringTheme(ThemeBase):
    def paint(self ,widget,event,painter): pass

class MinimalistTheme(ThemeBase):
    def paint(self ,widget,event,painter): pass

theme_map = {
    "classic": ClassicTheme(),
    "retro": RetroTheme(),
    "catpuccin": CatpuccinTheme(),
    "gruvbox": GruvboxTheme(),
    "grayscale": GrayscaleTheme(),
    "gray-scale": GrayscaleTheme(),
    "lettering": LetteringTheme(),
    "minimalist": MinimalistTheme(),
}