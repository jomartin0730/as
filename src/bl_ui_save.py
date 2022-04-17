import os
import bpy
from bl_op_data import Bl_Op_Data as bod
from bl_op_flag import Bl_Op_Flag as bof
from bl_ui_draw_pose import Bl_Ui_Draw_Pose_Operator

class DialogOperator(bpy.types.Operator):
    bl_idname = "object.dialog_operator"
    bl_label = "Motion Save"

    motion_Name: bpy.props.StringProperty(name = "저장할 이름을 입력하세요")

    # TAG : Motion save
    def execute(self, context):
        message = ("What you typed : {}".format(self.motion_Name))
        self.report({'INFO'}, message)
        # ========================================================================= #
        # NOTE : When save trimmed point cloud.
        # ========================================================================= #
        if (bof.FLAG_SAVE_TRIMMED_POINT_CLOUD == True):
            motion_List = os.listdir(bod.data_Ui_Image_Data_Path)
            if self.motion_Name in motion_List:
                text_Name = 'Name_that_exists'
                bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                print("Database has same name column")
            else:
                bod.data_Set_Save_Trimed_Compressed_Point_Cloud(bod.data_Pc_Point_Cloud_Data, self.motion_Name)
                bod.data_Pc_Point_Cloud_Data = None
                bod.data_Pc_Point_Cloud_Color_Int_Data = None
                bof.FLAG_CONFIRM_TO_DELETE_UUID = True
                bof.FLAG_CONFIRM_TO_RESET_CORE_PRODUCT = True
                Bl_Ui_Draw_Pose_Operator(0)
                bod.data_Reset_Pose()
                bof.FLAG_RESTRICT_EVENT = False
                text_Name = 'Name_that_exists'
                bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
            bof.FLAG_SAVE_TRIMMED_POINT_CLOUD = False

        else:
            # ========================================================================= #
            # NOTE : When connected to the database.
            # ========================================================================= #
            if (bof.FLAG_SQL_CONNECTION_ERROR == False):
                motion_List = bod.bl_op_sql.load_Pose_Data_Names()
                if self.motion_Name in motion_List:
                    text_Name = 'Name_that_exists'
                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                    print("Database has same name column")
                else:
                    save_Motion_Data = bod.data_Get_Combined_Motion_Data()
                    bof.FLAG_MOTION_LOADED = False
                    bod.bl_op_sql.save_Motion_Data_To_DB(self.motion_Name, save_Motion_Data)
                    Bl_Ui_Draw_Pose_Operator(0)
                    bof.FLAG_RESTRICT_EVENT = False
                    text_Name = 'Name_that_exists'
                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
                    bod.data_Reset_Pose()
            #############################################################################

            # ========================================================================= #
            # NOTE : When the database is not found
            # ========================================================================= #
            else:
                path = bod.data_Ui_Motion_Data_Path
                motion_List = os.listdir(path)
                curr_Motion = self.motion_Name + ".txt"
                if curr_Motion in motion_List:
                    text_Name = 'Name_that_exists'
                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                    print("Motion folder has same name file")
                else:
                    save_Motion_Data = bod.data_Get_Combined_Motion_Data()

                    save_Motion_Data_To_File = open("{}{}.txt".format(path, self.motion_Name), 'w')
                    save_Motion_Data_To_File.write(str(save_Motion_Data))
                    save_Motion_Data_To_File.close()

                    Bl_Ui_Draw_Pose_Operator(0)
                    bof.FLAG_MOTION_LOADED = False
                    bof.FLAG_RESTRICT_EVENT = False
                    text_Name = 'Name_that_exists'
                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
            #############################################################################

        bod.data_Set_Deactivate_Activated_Panel("saving_Panel")
        bod.data_Set_Deactivate_Activated_Panel("modify_Pose_Panel")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)