import blf
from bl_ui_widget import *
from bl_op_data import Bl_Op_Data as bod

class BL_UI_Label(BL_UI_Widget):
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        self._text_color        = (1.0, 1.0, 1.0, 1.0)
        self._text = "Label"
        self._text_size = 16

    @property
    def text_color(self):
        return self._text_color

    @text_color.setter
    def text_color(self, value):
        self._text_color = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def text_size(self):
        return self._text_size

    @text_size.setter
    def text_size(self, value):
        self._text_size = value
            
    def is_in_rect(self, x, y):
        return False
        
    def draw(self):
        area_height = self.get_area_height()

        font_info = {
            "font_id": 0,
            "handler": None,
        }

        font_path = bod.data_Ui_Font_Path + bod.data_Ui_Font
        font_info["font_id"] = blf.load(font_path)

        font_id = font_info["font_id"]
        blf.size(font_id, self._text_size, 72)
        size = blf.dimensions(font_id, self._text)
        blf.shadow(font_id, 5, 0.0, 0.0, 0.0, 0.7)
        blf.shadow_offset(font_id, 3, -3)
        blf.enable(font_id, 5)

        textpos_y = area_height - self.y_screen - self.height
        blf.position(font_id, self.x_screen, textpos_y, 0)

        r, g, b, a = self._text_color

        blf.color(font_id, r, g, b, a)

        blf.draw(font_id, self._text)
