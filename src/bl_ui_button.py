# context.area: USER_PREFERENCES
from bl_ui_widget import *

import blf
import bpy
from bl_op_data import Bl_Op_Data as bod

class BL_UI_Button(BL_UI_Widget):
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._text_color        = (1.0, 1.0, 1.0, 1.0)
        self._hover_bg_color    = (0.5, 0.5, 0.5, 1.0)
        self._select_bg_color   = (0.7, 0.7, 0.7, 1.0)
        
        self._text = " "
        self._text_size = 16
        self._textpos = (x, y)
        self.__inrect = False

        self.__state = 0
        self.__image = None
        self.__image_size = (24, 24)
        self.__image_position = (4, 2)

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
        self.name = value
                
    @property
    def text_size(self):
        return self._text_size

    @text_size.setter
    def text_size(self, value):
        self._text_size = value

    @property
    def hover_bg_color(self):
        return self._hover_bg_color

    @hover_bg_color.setter
    def hover_bg_color(self, value):
        self._hover_bg_color = value

    @property
    def select_bg_color(self):
        return self._select_bg_color

    @select_bg_color.setter
    def select_bg_color(self, value):
        self._select_bg_color = value 
        
    def set_image_size(self, imgage_size):
        self.__image_size = imgage_size

    def set_image_position(self, image_position):
        self.__image_position = image_position

    def set_image(self, rel_filepath, file_Name):
        try:
            self.__image = bpy.data.images.load("{}{}".format(rel_filepath, file_Name), check_existing=True)
            bpy.data.images[file_Name].colorspace_settings.name = 'sRGB'
            self.__image.gl_load()
        except Exception as e:
            print("Error is occured : ", e)

    def update(self, x, y):        
        super().update(x, y)
        self._textpos = [x, y]

        area_height = self.get_area_height()
        
        y_screen_flip = area_height - self.y_screen
        
        off_x, off_y =  self.__image_position
        sx, sy = self.__image_size

        # bottom left, top left, top right, bottom right
        vertices = (
                    (self.x_screen + off_x, y_screen_flip - off_y), 
                    (self.x_screen + off_x, y_screen_flip - sy - off_y), 
                    (self.x_screen + off_x + sx, y_screen_flip - sy - off_y),
                    (self.x_screen + off_x + sx, y_screen_flip - off_x))
        
        self.shader_img = gpu.shader.from_builtin('2D_IMAGE')
        self.batch_img = batch_for_shader(self.shader_img, 'TRI_FAN', 
        { "pos" : vertices, 
          "texCoord": ((0, 1), (0, 0), (1, 0), (1, 1)) 
        },)
        
    def draw(self):

        area_height = self.get_area_height()
        self.shader.bind()
        self.set_colors()
        bgl.glEnable(bgl.GL_BLEND)
        self.batch_panel.draw(self.shader) 
        self.draw_image()
        bgl.glDisable(bgl.GL_BLEND)

        # Draw text
        self.draw_text(area_height)

    def set_colors(self):
        color = self._bg_color
        text_color = self._text_color

        # NOTE : pressed
        if self.__state == 1:
            color = self._select_bg_color

        # NOTE : hover
        elif self.__state == 2:
            color = self._hover_bg_color

        self.shader.uniform_float("color", color)

    def draw_text(self, area_height):
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

        textpos_y = area_height - self._textpos[1] - (self.height + size[1]) / 2.0
        blf.position(font_id, self._textpos[0] + (self.width - size[0]) / 2.0, textpos_y + 1, 0)

        r, g, b, a = self._text_color
        blf.color(font_id, r, g, b, a)

        blf.draw(font_id, self._text)

    def draw_image(self):
        if self.__image is not None:
            try:
                file_Name = self.__image.name
                if self.__state == 2:
                    self.load_Image(file_Name, self.__state)
                else:
                    self.load_Image(file_Name, self.__state)

                self.image_Draw_With_Binding()
            except Exception as e:
                print("Error is occured : ", e)

        return False

    def load_Image(self, file_Name, state):
        if (state == 0):
            self.__image = bpy.data.images.load("{}/{}".format(bod.data_Ui_Panel_Image_Path, file_Name), check_existing=True)
            bpy.data.images["{}".format(file_Name)].colorspace_settings.name = 'sRGB'
            self.__image.gl_load()
        elif (state == 2):
            self.__image = bpy.data.images.load("{}/{}".format(bod.data_Ui_Panel_Image_Path, file_Name), check_existing=True)
            bpy.data.images["{}".format(file_Name)].colorspace_settings.name = 'Linear ACES'
            self.__image.gl_load()

    def image_Draw_With_Binding(self):
        bgl.glActiveTexture(bgl.GL_TEXTURE0)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.__image.bindcode)

        self.shader_img.bind()
        self.shader_img.uniform_int("image", 0)
        self.batch_img.draw(self.shader_img)
        return True
        
    def set_mouse_down(self, mouse_down_func):
        self.mouse_down_func = mouse_down_func   
             
    def mouse_down(self, x, y):    
        if self.is_in_rect(x,y):
            self.__state = 1
            try:
                self.mouse_down_func(self)
            except:
                pass
                
            return True
        
        return False
    
    def mouse_move(self, x, y):
        if self.is_in_rect(x,y):
            if(self.__state != 1):
                
                # hover state
                self.__state = 2
        else:
            self.__state = 0
 
    def mouse_up(self, x, y):
        if self.is_in_rect(x,y):
            self.__state = 2
        else:
            self.__state = 0           
