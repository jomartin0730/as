# ============ Save to database ============ #

import bpy
from bl_op_data import Bl_Op_Data as bod
from bl_op_flag import Bl_Op_Flag as bof
from bl_ui_draw_pose import Bl_Ui_Draw_Pose_Operator
                                                                # bl_idname에 대문자 쓰면 안됨
class DialogOperatorvelochanger(bpy.types.Operator):
    bl_idname = "object.velo_changeing_dialog_operator"
    bl_label = "Change velocity of conveyor belt"

    velocity: bpy.props.StringProperty(name = "변경할 컨베이어벨트 속도를 입력하세요.")

    def execute(self, context):
        message = ("What you typed : {}".format(self.velocity))
        self.report({'INFO'}, message)
        bod.data_Op_Conveyor_Velocity = float(self.velocity)
        data_Op_Conveyor_Velocity = str(bod.data_Op_Conveyor_Velocity)
        print("현재 conveyor belt 속도 : ", bod.data_Op_Conveyor_Velocity)
        bod.widgets_panel.conv_Velo.text = f'컨베이어 속도 : {data_Op_Conveyor_Velocity}'
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

# ==================================================================================================================== #

# ============ Save to database ============ #

# import os
# import bpy
# from bl_op_server import *
# from bl_op_data import Bl_Op_Data as bod
# from bl_op_flag import Bl_Op_Flag as bof
#
# class DialogOperator(bpy.types.Operator):
#     bl_idname = "object.dialog_operator"
#     bl_label = "Motion Save"
#     DataPath = os.path.abspath('./Data')
#
#     Name: bpy.props.StringProperty(name = "저장할 이름을 입력하세요")
#
#     def execute(self, context):
#         message = ("What you typed : {}".format(self.Name))
#         self.report({'INFO'}, message)
#         save_Motion_Data = bod.data_Get_Save_To_File()
#         print(save_Motion_Data)
#
#         if save_Motion_Data: # Datas => jointangle_Datas
#             write_File = open("{}/{}.txt".format(self.DataPath, self.Name), 'w')
#             write_File.write(str(save_Motion_Data))
#             write_File.close()
#
#         return {'FINISHED'}
#
#     def invoke(self, context, event):
#         wm = context.window_manager
#         return wm.invoke_props_dialog(self)