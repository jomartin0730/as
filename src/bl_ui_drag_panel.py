import bpy
from bl_ui_widget import *
from bl_op_data import Bl_Op_Data as bod
from bl_op_flag import Bl_Op_Flag as bof

class BL_UI_Drag_Panel(BL_UI_Widget):
    
    def __init__(self, x, y, width, height):
        super().__init__(x,y, width, height)
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_drag = False
        self.widgets = []
        self.name = 'panel'

        # TAG : Add panel image
        # self.__image = None
        # self.__image_size = (24, 24)
        # self.__image_position = (4, 2)
        # ============================= #

    def set_location(self, x, y):
        super().set_location(x, y)
        self.layout_widgets()

    def add_widgets(self, widgets):
        self.widgets = widgets
        self.layout_widgets()
        
    def layout_widgets(self):
        for widget in self.widgets:
            widget.update(self.x_screen + widget.x, self.y_screen + widget.y)
    
    def child_widget_focused(self, x, y):
        for widget in self.widgets:
            if widget.is_in_rect(x, y):
                return True       
        return False
    
    def mouse_down(self, x, y):
        if self.child_widget_focused(x, y):
            return False
        
        if self.is_in_rect(x,y):
            height = self.get_area_height()
            self.is_drag = True
            self.drag_offset_x = x - self.x_screen
            self.drag_offset_y = y - (height - self.y_screen)
            return True
        
        return False

    def mouse_move(self, x, y):
        if self.is_drag:
            height = self.get_area_height()
            self.update(x, height - y)
            self.layout_widgets()

    def mouse_up(self, x, y):
        self.is_drag = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def update(self, x, y):
        super().update(x - self.drag_offset_x, y + self.drag_offset_y)

    # TAG : Add panel image
    #     if (self.__image is not None):
    #         self._textpos = [x, y]
    #
    #         area_height = self.get_area_height()
    #
    #         y_screen_flip = area_height - self.y_screen
    #
    #         off_x, off_y = self.__image_position
    #         sx, sy = self.__image_size
    #
    #         # bottom left, top left, top right, bottom right
    #         vertices = (
    #             (self.x_screen + off_x, y_screen_flip - off_y),
    #             (self.x_screen + off_x, y_screen_flip - sy - off_y),
    #             (self.x_screen + off_x + sx, y_screen_flip - sy - off_y),
    #             (self.x_screen + off_x + sx, y_screen_flip - off_x))
    #
    #         self.shader_img = gpu.shader.from_builtin('2D_IMAGE')
    #         self.batch_img = batch_for_shader(self.shader_img, 'TRI_FAN',
    #                                           {"pos": vertices, "texCoord": ((0, 1), (0, 0), (1, 0), (1, 1))}, )
    #
    # def set_image_size(self, imgage_size):
    #     self.__image_size = imgage_size
    #
    # def set_image_position(self, image_position):
    #     self.__image_position = image_position
    #
    # def set_image(self, rel_filepath, file_Name):
    #     self.__image = bpy.data.images.load("{}{}".format(rel_filepath, file_Name), check_existing=True)
    #     bpy.data.images[file_Name].colorspace_settings.name = 'sRGB'
    #     self.__image.gl_load()
    #
    # def draw(self):
    #     if (self.__image is not None):
    #         self.shader.bind()
    #         bgl.glEnable(bgl.GL_BLEND)
    #         self.batch_panel.draw(self.shader)
    #         self.draw_image()
    #         bgl.glDisable(bgl.GL_BLEND)
    #
    # def draw_image(self):
    #     if self.__image is not None:
    #         file_Name = self.__image.name
    #         if (bof.FLAG_PANEL_REFRESH == True):
    #             bof.FLAG_PANEL_REFRESH = False
    #             self.load_Image(file_Name)
    #             self.image_Draw_With_Binding()
    #         else:
    #             self.image_Draw_With_Binding()
    #
    # def load_Image(self, file_Name):
    #     self.__image = bpy.data.images.load("{}/{}".format(bod.data_Ui_Panel_Image_Path, file_Name), check_existing=True)
    #     bpy.data.images["{}".format(file_Name)].colorspace_settings.name = 'sRGB'
    #     self.__image.gl_load()
    #     print("panel_Image is refreshed : ", file_Name)
    #
    # def image_Draw_With_Binding(self):
    #     if (self.__image is not None):
    #         bgl.glActiveTexture(bgl.GL_TEXTURE0)
    #         bgl.glBindTexture(bgl.GL_TEXTURE_2D,
    #                           self.__image.bindcode)
    #
    #         self.shader_img.bind()
    #         self.shader_img.uniform_int("image", 0)
    #         self.batch_img.draw(self.shader_img)
    #         return True
    # ================================================================================================================ #

'''
# NOTE : 동시에 2개 이상의 Panel을 띄울 때 다음 코드를 이용해 Panel image를 새로고침한다.
    def draw_image(self):
        if self.__image is not None:
            file_Name = self.__image.name
            if (bof.FLAG_PANEL_REFRESH == True):
                if (self.panel_Namespace[file_Name] == 1 and bof.FLAG_CLASSIFICATE_PANEL_NAME == False):
                    bof.FLAG_CLASSIFICATE_PANEL_NAME = True
                    self.load_Image(file_Name)
                if (self.panel_Namespace[file_Name] == 2 and bof.FLAG_CLASSIFICATE_PANEL_NAME == True and bof.FLAG_INFORMATION_PANEL_HIDE == False):
                    bof.FLAG_PANEL_REFRESH = False
                    bof.FLAG_CLASSIFICATE_PANEL_NAME = False
                    self.load_Image(file_Name)
                elif (bof.FLAG_CLASSIFICATE_PANEL_NAME == True and bof.FLAG_INFORMATION_PANEL_HIDE == True):
                    bof.FLAG_PANEL_REFRESH = False
                    bof.FLAG_CLASSIFICATE_PANEL_NAME = False
                self.image_Draw_With_Binding()
            else:
                self.image_Draw_With_Binding()
                
    FLAG_CLASSIFICATE_PANEL_NAME = False
    FLAG_INFORMATION_PANEL_HIDE = False
'''