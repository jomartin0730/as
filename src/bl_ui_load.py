import os
import bpy
from bpy.props import (EnumProperty,
                        PointerProperty)
from bpy.types import (Operator,
                       AddonPreferences,
                       PropertyGroup)
from bl_op_flag import Bl_Op_Flag as bof
from bl_op_data import Bl_Op_Data as bod
from bl_ui_draw_pose import Bl_Ui_Draw_Pose as budp


def my_callback(scene, context):
    if (bof.FLAG_SQL_CONNECTION_ERROR == False):
        motoin_Data_List = bod.bl_op_sql.print_Motion_List()
    else:
        motoin_Names = os.listdir(bod.data_Ui_Motion_Data_Path)
        motoin_Data_List = print_Motion_List(motoin_Names)

    return motoin_Data_List

def print_Motion_List(motoin_Names):
    list_Value = []
    for name in motoin_Names:
        val1 = "{}".format(name)
        val2 = "{}".format(name)
        val3 = " "
        list_pack = (val1, val2, val3)
        list_Value.append(list_pack)

    return list_Value

class MySetting(PropertyGroup):
    objs = EnumProperty(name = "Objects", description = "", items = my_callback)

class LoadEnumOperator(bpy.types.Operator):
    bl_idname = "object.load_enum_operator"
    bl_label = "Load Enum Operator"
    bl_property = "select_Motion_Name"
    ### Notice # ===================================================================================================== #
    # FIXME : Variable Grammar >> after version 2.8 > X : Y, before version 2.8 > X = Y
    select_Motion_Name : MySetting.objs
    # ================================================================================================================ #

    # TAG : Motion load
    def execute(self, context):
        self.report({'INFO'}, "Selected:" + self.select_Motion_Name)
        bod.data_Draw_Path_Point_List = []
        bod.data_Current_Loaded_Motion_List = []
        bod.data_Ui_Current_Loaded_Data = self.select_Motion_Name
        bod.data_Ui_Curr_Loaded_Data_For_modify = self.select_Motion_Name

        # ===================================================================================== #
        # NOTE : When connected to the database.
        # ===================================================================================== #
        if (bof.FLAG_SQL_CONNECTION_ERROR == False):
            load_Sql_Data = eval(bod.bl_op_sql.load_Pose_Data_From_DB(self.select_Motion_Name))
            budp.draw_Load_Sql_Data_Add_Pose(load_Sql_Data)
        #########################################################################################

        # ===================================================================================== #
        # NOTE : When the database is not found
        # ===================================================================================== #
        else:
            read_File = open("{}{}".format(bod.data_Ui_Motion_Data_Path, self.select_Motion_Name), 'r')
            load_File_Data = eval(read_File.read())
            read_File.close()
            budp.draw_Load_Sql_Data_Add_Pose(load_File_Data)
        #########################################################################################

        bod.data_Draw_Ply_Axis_First_Loc = bod.data_Draw_plyAxis_Obj.location.x
        bod.data_Draw_Curr_Ply_Axis_Loc = bod.data_Draw_Ply_Axis_First_Loc
        bod.widgets_panel.loadedProduct.text = f'불러 온 모션 : {bod.data_Ui_Current_Loaded_Data}'

        text = self.return_Task_Names()
        bod.widgets_panel.Tasklist.text = f'{text}'

        bof.FLAG_MOTION_LOADED = True
        bof.FLAG_RESTRICT_EVENT = False
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

    def return_Keys(self, queue):
        motion_Name = list(queue.keys())[0]
        return motion_Name

    def return_Task_Names(self):
        text = ''
        queue = bod.bl_def_task.scheduled_Task.queue
        length = len(queue)
        if (length == 1):
            text = self.return_Keys(queue[0])
        else:
            for cnt in range(0, length):
                if (cnt == 0):
                    text = self.return_Keys(queue[cnt])
                else:
                    text += ", " + self.return_Keys(queue[cnt])
        return text


    @classmethod
    def poll(cls, context):
        return context.object is not None

# ==================================================================================================================== #

# ============ Load from file ============ #

# import bpy
# from bpy.props import (EnumProperty,
#                         PointerProperty)
# from bpy.types import (Operator,
#                        AddonPreferences,
#                        PropertyGroup)
# from bl_ui_draw_pose import Bl_Ui_Draw_Pose as budp
# from bl_op_data import Bl_Op_Data as bod
#
# import os
#
#
# def my_callback(scene, context):
#     file_List = bod.data_Get_File_List()
#     return file_List
#
# class MySetting(PropertyGroup):
#     objs = EnumProperty(name="Objects",description="",items=my_callback)
#
# class LoadEnumOperator(bpy.types.Operator):
#     bl_idname = "object.load_enum_operator"
#     bl_label = "Load Enum Operator"
#     bl_property = "select_Name"
#     select_Name = MySetting.objs
#     DataPath = os.path.abspath('./Data')
#
#     def execute(self, context):
#         self.report({'INFO'}, "Selected:" + self.select_Name)
#         budp.draw_Del_Pose()
#         read_File = open("{}/{}".format(self.DataPath, self.select_Name), 'r')
#         load_File_Data = eval(read_File.read())
#         load_File_Data.reverse()
#         budp.draw_Load_File_Data_Add_Pose(load_File_Data)
#         read_File.close()
#
#         return {'FINISHED'}
#
#     def invoke(self, context, event):
#         context.window_manager.invoke_search_popup(self)
#         return {'FINISHED'}