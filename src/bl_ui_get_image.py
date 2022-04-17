import bpy
from bpy.props import (EnumProperty,
                        PointerProperty)
from bpy.types import (Operator,
                       AddonPreferences,
                       PropertyGroup)
from bl_op_flag import Bl_Op_Flag as bof
from bl_op_data import Bl_Op_Data as bod
from bl_ui_draw_pose import Bl_Ui_Draw_Pose as budp
from bl_ui_draw_panel_menu import *

import os


def data_Get_Image_List(DataPath):
    try:
        files = os.listdir(DataPath)
        filenum = len(files)
        if filenum < 1:
            print("There is no Coordinate in File")
        else:
            bl_Load_Standard_parameter = []
            for i in range(0, filenum):
                val1 = "{}".format(files[i])
                val2 = "{}".format(files[i])
                val3 = " "
                bl_Search_module_pack = (val1, val2, val3)
                bl_Load_Standard_parameter.append(bl_Search_module_pack)
            return bl_Load_Standard_parameter
    except:
        print("There is no directory to find image")

def my_callback(scene, context):
    file_List = data_Get_Image_List(bod.data_Ui_Image_Data_Path)
    return file_List

class MySetting(PropertyGroup):
    objs = EnumProperty(name="Objects",description="",items=my_callback)

class ImageGetOperator(bpy.types.Operator):
    bl_idname = "object.load_image_get_operator"
    bl_label = "image get Operator"
    bl_property = "select_Name"
    select_Name : MySetting.objs

    def execute(self, context):
        self.report({'INFO'}, "Selected:" + self.select_Name)
        try:
            # TAG : Call point cloud
            try:
                if (len(bod.data_Pc_Ply_Name) > 0):
                    bod.data_Pc_Ply_Name.split('.')[1]
            except:
                bod.data_Set_Core_Product_Home_Position()
            DataPath = bod.data_Ui_Image_Data_Path + "{}/".format(self.select_Name)
            bod.data_Pc_Ply_Path = DataPath
            bod.data_Pc_Ply_Name = self.select_Name + ".npy.gz"
            # NOTE : Just call the point cloud from file
            bof.FLAG_GET_POINT_CLOUD = True
            # NOTE : Flag for functions that should only be performed when Point cloud is called.
            bof.FLAG_POINT_CLOUD_IS_LOADED = True
            bof.FLAG_RESTRICT_EVENT = False
            bof.FLAG_GET_CORE_PRODUCT_PLY = False
        except Exception as e:
            bof.FLAG_GET_POINT_CLOUD = False
            bof.FLAG_POINT_CLOUD_IS_LOADED = False
            bof.FLAG_RESTRICT_EVENT = True
            print(e)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

    def get_Core_Modeling(self):
        if (bod.data_Info_Curr_Pc_Ip_Adress == bod.data_Info_Pc_One_Ip):
            bpy.data.objects['{}'.format(self.select_Name)].location.x = 0.44878
            bod.data_Draw_plyAxis_Obj.location.x = 0.44878
            bpy.data.objects['{}'.format(self.select_Name)].location.y = 1
            bpy.data.objects['{}'.format(self.select_Name)].location.z = 1.4621
        else:
            bpy.data.objects['{}'.format(self.select_Name)].location.x = -0.50094
            bod.data_Draw_plyAxis_Obj.location.x = -0.50094
            bpy.data.objects['{}'.format(self.select_Name)].location.y = 1
            bpy.data.objects['{}'.format(self.select_Name)].location.z = 1.2068


'''
# TAG : Call core product
if (self.select_Name in bod.core_Product):
    if (len(bod.data_Pc_Ply_Name) > 0):
        try:
            bod.data_Pc_Ply_Name.split('.')[1]
            bof.FLAG_DELETE_POINT_CLOUD = True
        except:
            bod.data_Set_Core_Product_Home_Position()
    bof.FLAG_GET_CORE_PRODUCT_PLY = True
    self.get_Core_Modeling()
    bod.data_Pc_Ply_Name = self.select_Name
    bof.FLAG_POINT_CLOUD_IS_LOADED = True
    bof.FLAG_RESTRICT_EVENT = False
'''