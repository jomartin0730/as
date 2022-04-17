import bpy
import threading
import mathutils
from bl_ui_label import *
from bl_ui_button import *
from bl_ui_checkbox import *
from bl_ui_slider import *
from bl_ui_draw_pose import Bl_Ui_Draw_Pose_Operator

from bl_op_data import Bl_Op_Data as bod
from bl_op_server import URxMoveToPoseOperator
from bl_op_flag import Bl_Op_Flag as bof
from bl_op_pcm import *

class widget_Container():

    def __init__(self):
        self.widget = []
        self.loc_x = 0
        self.loc_y = 0

class Bl_Ui_Draw_Panel_Menu():

    def __init__(self):
        self.Tasklist = ''
        self.slider_Bar = None

    def draw_Main_Panel_Menu(self):
        self.WinLable = BL_UI_Label(10, 10, 200, 25)
        self.WinLable.text = "MAVIZ | {}".format(bod.data_Info_Robot_Model)
        self.WinLable.text_size = 24
        self.WinLable.text_color = (0.6, 0.9, 0.3, 1.0)

        self.Underline = BL_UI_Label(10, 35, 200, 20)
        self.Underline.text = "────────────"
        self.Underline.text_size = 18
        self.Underline.text_color = (0.6, 0.9, 0.3, 1.0)

        self.Motionremv = BL_UI_Button(165, 65, 135, 30)
        self.Motionremv.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.Motionremv.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Motionremv.text = "초기화"
        self.Motionremv.set_mouse_down(self.button_Draw_Del_Pose)

        # TAG : Motion simulation
        self.Path_simulation = BL_UI_Button(20, 65, 135, 30)
        self.Path_simulation.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.Path_simulation.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Path_simulation.text = "시뮬레이션"
        self.Path_simulation.set_mouse_down(self.button_Run_Simulation)

        self.hide_Robot = BL_UI_Button(20, 105, 135, 30)
        self.hide_Robot.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.hide_Robot.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.hide_Robot.text = "로봇 숨기기"
        self.hide_Robot.set_mouse_down(self.button_Hide_Robot)

        self.PoseSaveA = BL_UI_Button(165, 105, 135, 30)
        self.PoseSaveA.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.PoseSaveA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.PoseSaveA.text = "모션 저장"
        self.PoseSaveA.set_mouse_down(self.button_Reveal_Saving_Panel)

        self.Image_load = BL_UI_Button(20, 145, 135, 30)
        self.Image_load.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.Image_load.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Image_load.text = "사진 불러오기"
        self.Image_load.set_mouse_down(self.button_Get_Image_Data)

        self.PoseLoadA = BL_UI_Button(165, 145, 135, 30)
        self.PoseLoadA.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.PoseLoadA.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.PoseLoadA.text = "모션 불러오기"
        self.PoseLoadA.set_mouse_down(self.button_Load_Robot_Pose_Lists)

        # self.auto_Track_Motion = BL_UI_Button(20, 225, 135, 30)
        # self.auto_Track_Motion.bg_color = (0.2, 0.8, 0.8, 0.8)
        # self.auto_Track_Motion.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        # self.auto_Track_Motion.text = "모션 만들기"
        # self.auto_Track_Motion.set_mouse_down(self.button_Make_Path_Automatically)

        self.robot_Control = BL_UI_Button(20, 185, 135, 30)
        self.robot_Control.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.robot_Control.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.robot_Control.text = "로봇 제어"
        self.robot_Control.set_mouse_down(self.button_Execute_Robot_Control_Menu)

        self.modify_All_Pose = BL_UI_Button(165, 185, 135, 30)
        self.modify_All_Pose.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.modify_All_Pose.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.modify_All_Pose.text = "포즈 수정"
        self.modify_All_Pose.set_mouse_down(self.button_Modify_All_Pose)

        self.conv_Velo_Change = BL_UI_Button(20, 225, 135, 30)
        self.conv_Velo_Change.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.conv_Velo_Change.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.conv_Velo_Change.text = "Conv 속도변경"
        self.conv_Velo_Change.set_mouse_down(self.button_Modify_Conv_Belt_Velo)

        self.select_J_L_MOVE = BL_UI_Button(165, 225, 65, 30)
        self.select_J_L_MOVE.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.select_J_L_MOVE.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.select_J_L_MOVE.text = "JMOVE"
        self.select_J_L_MOVE.set_mouse_down(self.button_Select_L_J_Move)

        self.st_Select = BL_UI_Button(235, 225, 65, 30)
        self.st_Select.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.st_Select.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.st_Select.text = "Time"
        self.st_Select.set_mouse_down(self.button_Select_Speed_Time)

        self.point_Cloud_Streaming = BL_UI_Button(20, 265, 135, 30)
        self.point_Cloud_Streaming.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.point_Cloud_Streaming.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.point_Cloud_Streaming.text = "실시간PointCloud"
        self.point_Cloud_Streaming.text_size = 16
        self.point_Cloud_Streaming.set_mouse_down(self.button_Point_Cloud_Streaming)

        self.edit_Point_Cloud = BL_UI_Button(165, 265, 135, 30)
        self.edit_Point_Cloud.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.edit_Point_Cloud.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        # self.edit_Point_Cloud.set_image(bod.data_Ui_Panel_Image_Path, "button.png")
        # self.edit_Point_Cloud.set_image_size((135, 40))
        # self.edit_Point_Cloud.set_image_position((0, 0))
        self.edit_Point_Cloud.text = "PointCloud 편집"
        self.edit_Point_Cloud.set_mouse_down(self.button_Change_Panel_To_Edit_Pc)

        self.conv_Velo = BL_UI_Label(25, 295, 160, 20)
        self.conv_Velo.color = (0.2, 0.8, 0.8, 0.8)
        self.conv_Velo.text = "컨베이어 속도 : 7.0"
        self.conv_Velo.text_size = 15

        self.loadedProduct = BL_UI_Label(25, 320, 160, 20)
        self.loadedProduct.color = (0.2, 0.8, 0.8, 0.8)
        self.loadedProduct.text = "불러 온 모션 : "
        self.loadedProduct.text_size = 15

        self.pose_Speed = BL_UI_Label(25, 340, 60, 20)
        self.pose_Speed.color = (0.2, 0.8, 0.8, 0.8)
        if (bod.data_Op_Speed_Or_Time == 0):
            if (bof.FLAG_SELECT_LMOVE == False):
                self.pose_Speed.text = "point 1 포즈 속도 : 0 deg/s"
            else:
                self.pose_Speed.text = "point 1 포즈 속도 : 0 mm/s"
        else:
            self.pose_Speed.text = "point 1 포즈 소요시간 : 0.0 s"
        self.pose_Speed.text_size = 15

        self.motion_Elapsed_Time = BL_UI_Label(25, 360, 60, 20)
        self.motion_Elapsed_Time.color = (0.2, 0.8, 0.8, 0.8)
        if (bod.data_Op_Speed_Or_Time == 0):
            if (bof.FLAG_SELECT_LMOVE == False):
                self.motion_Elapsed_Time.text = "모션 소요시간 : 0.0 s"
            else:
                self.motion_Elapsed_Time.text = "모션 소요시간 : 0.0 s"
        else:
            self.motion_Elapsed_Time.text = "모션 소요시간 : 0.0 s"
        self.motion_Elapsed_Time.text_size = 15

        self.slider_Bar = BL_UI_Slider(20, 415, 140, 20)
        self.slider_Bar.color = (0.2, 0.8, 0.8, 0.8)
        self.slider_Bar.hover_color = (0.2, 0.9, 0.9, 1.0)
        self.slider_Bar.min = 1
        self.slider_Bar.max = 30
        self.slider_Bar.decimals = 0
        self.slider_Bar.set_value(1)
        self.slider_Bar.set_value_change(self.slidebar_Fursys_Value_Changer)

        self.pose_Speed_Teaching = BL_UI_Label(175, 385, 60, 20)
        self.pose_Speed_Teaching.color = (0.2, 0.8, 0.8, 0.8)
        if (bod.data_Op_Speed_Or_Time == 0):
            if (bof.FLAG_SELECT_LMOVE == False):
                self.pose_Speed_Teaching.text = "포즈 속도 : 80 deg/s"
            else:
                self.pose_Speed_Teaching.text = "포즈 속도 : 200 mm/s"
        else:
            self.pose_Speed_Teaching.text = "포즈 소요시간 : 0.4 s"
        self.pose_Speed_Teaching.text_size = 14

        self.speedUp = BL_UI_Button(175, 415, 30, 20)
        self.speedUp.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.speedUp.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.speedUp.text = "↑"
        self.speedUp.text_size = 16
        self.speedUp.set_mouse_down(self.button_Send_Speed_Up)

        self.normalSpeed = BL_UI_Button(225, 415, 30, 20)
        self.normalSpeed.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.normalSpeed.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.normalSpeed.text = "0"
        self.normalSpeed.text_size = 14
        self.normalSpeed.set_mouse_down(self.button_Send_Normal_Speed)

        self.speedDown = BL_UI_Button(275, 415, 30, 20)
        self.speedDown.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.speedDown.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.speedDown.text = "↓"
        self.speedDown.text_size = 16
        self.speedDown.set_mouse_down(self.button_Send_Speed_Down)

        self.ik_control_loc = BL_UI_Label(25, 440, 60, 20)
        self.ik_control_loc.color = (0.2, 0.8, 0.8, 0.8)
        self.ik_control_loc.text = "현재위치 (X : 0 m    Y : 0    Z : 0)"
        self.ik_control_loc.text_size = 14

        self.joint_Angle_Value_1 = BL_UI_Label(25, 460, 60, 20)
        self.joint_Angle_Value_1.color = (0.2, 0.8, 0.8, 0.8)
        self.joint_Angle_Value_1.text = "조인트 각도 (0˚, 0˚, 0˚"
        self.joint_Angle_Value_1.text_size = 14

        self.joint_Angle_Value_2 = BL_UI_Label(97, 480, 60, 20)
        self.joint_Angle_Value_2.color = (0.2, 0.8, 0.8, 0.8)
        self.joint_Angle_Value_2.text = "0˚, 0˚, 0˚)"
        self.joint_Angle_Value_2.text_size = 14

        self.ik_control_Curr_loc = BL_UI_Label(25, 500, 60, 20)
        self.ik_control_Curr_loc.color = (0.2, 0.8, 0.8, 0.8)
        self.ik_control_Curr_loc.text = "모션위치 (X : 0 m    Y : 0    Z : 0)"
        self.ik_control_Curr_loc.text_size = 14

        self.Tasklable = BL_UI_Label(10, 540, 200, 25)
        self.Tasklable.text = "Task list"
        self.Tasklable.text_size = 20
        self.Tasklable.text_color = (0.6, 0.9, 0.3, 1.0)

        self.Tasklist = BL_UI_Label(25, 570, 60, 20)
        self.Tasklist.color = (0.2, 0.8, 0.8, 0.8)
        self.Tasklist.text = ""
        self.Tasklist.text_size = 14

        widgets_panel = [self.Underline, self.WinLable, self.Motionremv, self.Tasklable, self.Tasklist, self.edit_Point_Cloud,
                         self.Image_load, self.Path_simulation, self.normalSpeed, self.pose_Speed_Teaching, self.hide_Robot,
                         self.select_J_L_MOVE, self.PoseSaveA, self.PoseLoadA, self.motion_Elapsed_Time, self.pose_Speed,
                         self.speedUp, self.speedDown, self.ik_control_Curr_loc, self.conv_Velo_Change, self.slider_Bar,
                         self.ik_control_loc, self.loadedProduct, self.modify_All_Pose, self.conv_Velo, self.st_Select,
                         self.point_Cloud_Streaming, self.robot_Control, self.joint_Angle_Value_1, self.joint_Angle_Value_2] # self.auto_Track_Motion,

        return widgets_panel


    def draw_Point_Cloud_Editing_Panel_Menu(self):

        self.weight = 0.01
        ### NOTE : 0 >> X / 1 >> Y / 2 >> Z
        self.Axis = 0
        ### NOTE : True >> Rotation / False >> Scale
        self.modify_data_Of_Rotation = True
        ### NOTE : Target object = 'bbox' or 'plyAxis'
        self.modifying_Target_Object = bpy.data.objects['bbox']

        self.pce_Lable = BL_UI_Label(10, 10, 200, 25)
        self.pce_Lable.text = "Point cloud 편집"
        self.pce_Lable.text_size = 24
        self.pce_Lable.text_color = (0.6, 0.9, 0.3, 1.0)

        self.Underline = BL_UI_Label(10, 35, 200, 20)
        self.Underline.text = "──────────"
        self.Underline.text_size = 18
        self.Underline.text_color = (0.6, 0.9, 0.3, 1.0)

        self.return_Main_Menu = BL_UI_Button(230, 25, 50, 30)
        self.return_Main_Menu.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.return_Main_Menu.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.return_Main_Menu.text = "주메뉴"
        self.return_Main_Menu.text_size = 14
        self.return_Main_Menu.set_mouse_down(self.button_Return_Main_Menu)

        self.call_Point_Cloud = BL_UI_Button(20, 60, 125, 30)
        self.call_Point_Cloud.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.call_Point_Cloud.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.call_Point_Cloud.text = "pointcloud 호출"
        self.call_Point_Cloud.set_mouse_down(self.button_Draw_Point_Cloud)

        self.refresh_Pcv_Cache = BL_UI_Button(155, 60, 125, 30)
        self.refresh_Pcv_Cache.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.refresh_Pcv_Cache.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.refresh_Pcv_Cache.text = "초기화"
        self.refresh_Pcv_Cache.set_mouse_down(self.button_Refresh_Pcv_Cache)

        self.plus_X = BL_UI_Button(240, 140, 30, 30)
        self.plus_X.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.plus_X.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.plus_X.text = "→"
        self.plus_X.text_size = 16
        self.plus_X.set_mouse_down(self.button_plus_X)

        self.minus_X = BL_UI_Button(160, 140, 30, 30)
        self.minus_X.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.minus_X.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.minus_X.text = "←"
        self.minus_X.text_size = 16
        self.minus_X.set_mouse_down(self.button_minus_X)

        self.plus_Z = BL_UI_Button(200, 100, 30, 30)
        self.plus_Z.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.plus_Z.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.plus_Z.text = "↑"
        self.plus_Z.text_size = 16
        self.plus_Z.set_mouse_down(self.button_plus_Z)

        self.minus_Z = BL_UI_Button(200, 180, 30, 30)
        self.minus_Z.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.minus_Z.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.minus_Z.text = "↓"
        self.minus_Z.text_size = 16
        self.minus_Z.set_mouse_down(self.button_minus_Z)

        self.plus_Y = BL_UI_Button(240, 100, 30, 30)
        self.plus_Y.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.plus_Y.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.plus_Y.text = "↗"
        self.plus_Y.text_size = 16
        self.plus_Y.set_mouse_down(self.button_plus_Y)

        self.minus_Y = BL_UI_Button(160, 180, 30, 30)
        self.minus_Y.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.minus_Y.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.minus_Y.text = "↙"
        self.minus_Y.text_size = 16
        self.minus_Y.set_mouse_down(self.button_minus_Y)

        self.bbox_Scale_Or_Rot = BL_UI_Button(20, 100, 80, 30)
        self.bbox_Scale_Or_Rot.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.bbox_Scale_Or_Rot.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.bbox_Scale_Or_Rot.text = "Rotation"
        self.bbox_Scale_Or_Rot.text_size = 16
        self.bbox_Scale_Or_Rot.set_mouse_down(self.button_Toggle_Scale_Or_Rot)

        self.target_Object = BL_UI_Button(20, 140, 80, 30)
        self.target_Object.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.target_Object.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.target_Object.text = "bbox"
        self.target_Object.text_size = 16
        self.target_Object.set_mouse_down(self.button_Toggle_Target_Object)

        self.value_Up = BL_UI_Button(110, 100, 30, 30)
        self.value_Up.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.value_Up.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.value_Up.text = "+"
        self.value_Up.text_size = 16
        self.value_Up.set_mouse_down(self.button_Value_Up)

        self.value_Down = BL_UI_Button(110, 140, 30, 30)
        self.value_Down.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.value_Down.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.value_Down.text = "-"
        self.value_Down.text_size = 16
        self.value_Down.set_mouse_down(self.button_Value_Down)

        self.x_Axis = BL_UI_Button(20, 180, 30, 30)
        self.x_Axis.bg_color = (0.2, 0.8, 0.2, 0.8)
        self.x_Axis.hover_bg_color = (0.2, 0.9, 0.2, 1.0)
        self.x_Axis.text = "X"
        self.x_Axis.text_size = 16
        self.x_Axis.set_mouse_down(self.button_Standard_Axis_X)

        self.y_Axis = BL_UI_Button(65, 180, 30, 30)
        self.y_Axis.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.y_Axis.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.y_Axis.text = "Y"
        self.y_Axis.text_size = 16
        self.y_Axis.set_mouse_down(self.button_Standard_Axis_Y)

        self.z_Axis = BL_UI_Button(110, 180, 30, 30)
        self.z_Axis.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.z_Axis.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.z_Axis.text = "Z"
        self.z_Axis.text_size = 16
        self.z_Axis.set_mouse_down(self.button_Standard_Axis_Z)

        self.choose_Detail_Rough = BL_UI_Button(20, 220, 130, 30)
        self.choose_Detail_Rough.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.choose_Detail_Rough.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.choose_Detail_Rough.text = "Detail"
        self.choose_Detail_Rough.text_size = 16
        self.choose_Detail_Rough.set_mouse_down(self.button_Toggle_Detail_Or_Rough)

        self.trim_Point_Cloud = BL_UI_Button(20, 260, 130, 30)
        self.trim_Point_Cloud.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.trim_Point_Cloud.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.trim_Point_Cloud.text = "pc 잘라내기"
        self.trim_Point_Cloud.text_size = 16
        self.trim_Point_Cloud.set_mouse_down(self.button_Trim_Point_Cloud)

        self.save_Trimed_Point_Cloud = BL_UI_Button(160, 260, 130, 30)
        self.save_Trimed_Point_Cloud.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.save_Trimed_Point_Cloud.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.save_Trimed_Point_Cloud.text = "pc 저장하기"
        self.save_Trimed_Point_Cloud.text_size = 16
        self.save_Trimed_Point_Cloud.set_mouse_down(self.button_Save_Trimed_Point_Cloud)

        widgets_panel2 = [self.pce_Lable, self.Underline, self.call_Point_Cloud, self.refresh_Pcv_Cache, self.return_Main_Menu,
                          self.plus_X, self.minus_X, self.plus_Z, self.minus_Z, self.plus_Y, self.minus_Y, self.bbox_Scale_Or_Rot,
                          self.target_Object, self.value_Up, self.value_Down, self.x_Axis, self.y_Axis, self.z_Axis,
                          self.choose_Detail_Rough, self.trim_Point_Cloud, self.save_Trimed_Point_Cloud]

        return widgets_panel2


    def draw_Point_Cloud_Streaming_Panel_Menu(self):

        self.pcs_Lable = BL_UI_Label(10, 10, 200, 25)
        self.pcs_Lable.text = "실시간 Point cloud"
        self.pcs_Lable.text_size = 24
        self.pcs_Lable.text_color = (0.6, 0.9, 0.3, 1.0)

        self.Underline = BL_UI_Label(10, 35, 200, 20)
        self.Underline.text = "────────────"
        self.Underline.text_size = 18
        self.Underline.text_color = (0.6, 0.9, 0.3, 1.0)

        self.cut_Point_Cloud = BL_UI_Button(235, 20, 50, 30)
        self.cut_Point_Cloud.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.cut_Point_Cloud.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.cut_Point_Cloud.text = "부분"
        self.cut_Point_Cloud.set_mouse_down(self.button_Show_Specific_Point_Cloud)

        self.start_Camera = BL_UI_Button(20, 60, 125, 30)
        self.start_Camera.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.start_Camera.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.start_Camera.text = "Camera 실행"
        self.start_Camera.set_mouse_down(self.button_Start_Signal_To_Camera)

        self.stop_Camera = BL_UI_Button(160, 60, 125, 30)
        self.stop_Camera.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.stop_Camera.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.stop_Camera.text = "Camera 종료"
        self.stop_Camera.set_mouse_down(self.button_Stop_Signal_To_Camera)

        self.return_Main_Menu_From_Streaming = BL_UI_Button(160, 100, 125, 30)
        self.return_Main_Menu_From_Streaming.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.return_Main_Menu_From_Streaming.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.return_Main_Menu_From_Streaming.text = "주메뉴"
        self.return_Main_Menu_From_Streaming.text_size = 14
        self.return_Main_Menu_From_Streaming.set_mouse_down(self.button_Return_Main_Menu_From_Streaming)

        self.capture_Point_Cloud = BL_UI_Button(20, 100, 125, 30)
        self.capture_Point_Cloud.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.capture_Point_Cloud.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.capture_Point_Cloud.text = "pointcloud 캡처"
        self.capture_Point_Cloud.set_mouse_down(self.button_Capture_Point_Cloud)

        widgets_panel3 = [self.pcs_Lable, self.Underline, self.cut_Point_Cloud, self.return_Main_Menu_From_Streaming, 
                          self.capture_Point_Cloud, self.start_Camera, self.stop_Camera]

        return widgets_panel3


    def draw_Robot_Control_Panel_Menu(self):

        self.rc_Lable = BL_UI_Label(10, 10, 200, 25)
        self.rc_Lable.text = "로봇 제어"
        self.rc_Lable.text_size = 24
        self.rc_Lable.text_color = (0.6, 0.9, 0.3, 1.0)

        self.Underline = BL_UI_Label(10, 35, 200, 20)
        self.Underline.text = "──────"
        self.Underline.text_size = 18
        self.Underline.text_color = (0.6, 0.9, 0.3, 1.0)

        self.start_Server = BL_UI_Button(20, 60, 125, 30)
        self.start_Server.flag_Server_Started = False
        self.start_Server.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.start_Server.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.start_Server.text = "서버 시작"
        self.start_Server.set_mouse_down(self.button_Start_Server)

        self.start_Motion = BL_UI_Button(20, 100, 125, 30)
        self.start_Motion.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.start_Motion.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.start_Motion.text = "모션 실행"
        self.start_Motion.set_mouse_down(self.button_Send_Execute_Order)

        self.start_Pose = BL_UI_Button(20, 140, 125, 30)
        self.start_Pose.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.start_Pose.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.start_Pose.text = "포즈 실행"
        self.start_Pose.set_mouse_down(self.button_Send_Execute_Pose_Order)

        self.home_Position = BL_UI_Button(160, 60, 125, 110)
        self.home_Position.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.home_Position.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.home_Position.text = "홈 위치"
        self.home_Position.set_mouse_down(self.button_Send_Returning_Home_Order)

        self.load_Motion = BL_UI_Button(20, 180, 125, 30)
        self.load_Motion.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.load_Motion.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.load_Motion.text = "모션 불러오기"
        self.load_Motion.set_mouse_down(self.button_Load_Robot_Pose_Lists)

        self.stop_Robot = BL_UI_Button(160, 180, 125, 110)
        self.stop_Robot.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.stop_Robot.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.stop_Robot.text = "로봇 정지"
        self.stop_Robot.set_mouse_down(self.button_Send_Robot_Stop_Order)

        self.reset_Motion = BL_UI_Button(20, 220, 125, 30)
        self.reset_Motion.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.reset_Motion.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.reset_Motion.text = "초기화"
        self.reset_Motion.set_mouse_down(self.button_Draw_Del_Pose)

        self.rtm_From_Rc = BL_UI_Button(20, 260, 125, 30)
        self.rtm_From_Rc.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.rtm_From_Rc.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.rtm_From_Rc.text = "주메뉴"
        self.rtm_From_Rc.set_mouse_down(self.button_Return_Main_Menu_From_Robot_Control)

        widgets_panel3 = [self.rc_Lable, self.Underline, self.start_Motion, self.home_Position, self.start_Pose,
                          self.reset_Motion, self.load_Motion, self.start_Server, self.stop_Robot, self.rtm_From_Rc]

        return widgets_panel3


    def draw_Modify_All_Pose_Panel_Menu(self):

        self.rc_Lable = BL_UI_Label(10, 10, 200, 25)
        self.rc_Lable.text = "포즈 수정"
        self.rc_Lable.text_size = 24
        self.rc_Lable.text_color = (0.6, 0.9, 0.3, 1.0)

        self.Underline = BL_UI_Label(10, 35, 200, 20)
        self.Underline.text = "──────"
        self.Underline.text_size = 18
        self.Underline.text_color = (0.6, 0.9, 0.3, 1.0)

        self.start_Modifying_Pose = BL_UI_Button(20, 60, 125, 30)
        self.start_Modifying_Pose.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.start_Modifying_Pose.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.start_Modifying_Pose.text = "포즈 수정"
        self.start_Modifying_Pose.set_mouse_down(self.button_Start_Modifying_Pose)

        self.set_Modified_Pose = BL_UI_Button(20, 100, 125, 30)
        self.set_Modified_Pose.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.set_Modified_Pose.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.set_Modified_Pose.text = "변경 확정"
        self.set_Modified_Pose.set_mouse_down(self.button_Set_Modified_Pose)

        self.rtm_From_map = BL_UI_Button(20, 140, 125, 30)
        self.rtm_From_map.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.rtm_From_map.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.rtm_From_map.text = "창닫기"
        self.rtm_From_map.set_mouse_down(self.button_Return_Main_Menu_From_Modify_All_Pose)

        widgets_panel4 = [self.rc_Lable, self.Underline, self.start_Modifying_Pose, self.set_Modified_Pose,
                          self.rtm_From_map]

        return widgets_panel4

    def draw_Saving_Panel_Menu(self):

        self.rc_Lable = BL_UI_Label(10, 10, 200, 25)
        self.rc_Lable.text = "모션 저장"
        self.rc_Lable.text_size = 24
        self.rc_Lable.text_color = (0.6, 0.9, 0.3, 1.0)

        self.Underline = BL_UI_Label(10, 35, 200, 20)
        self.Underline.text = "──────"
        self.Underline.text_size = 18
        self.Underline.text_color = (0.6, 0.9, 0.3, 1.0)

        self.save_Motion = BL_UI_Button(20, 60, 125, 30)
        self.save_Motion.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.save_Motion.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.save_Motion.text = "모션 저장"
        self.save_Motion.set_mouse_down(self.button_Save_Pose_Lists)

        self.replace_Saved_Motion = BL_UI_Button(20, 100, 125, 30)
        self.replace_Saved_Motion.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.replace_Saved_Motion.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.replace_Saved_Motion.text = "모션 수정"
        self.replace_Saved_Motion.set_mouse_down(self.button_Modify_Pose_Lists)

        self.delete_Saved_Motion = BL_UI_Button(20, 140, 125, 30)
        self.delete_Saved_Motion.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.delete_Saved_Motion.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.delete_Saved_Motion.text = "모션 삭제"
        self.delete_Saved_Motion.set_mouse_down(self.button_Delete_Robot_Pose_Lists)

        self.rtm_From_map = BL_UI_Button(20, 180, 125, 30)
        self.rtm_From_map.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.rtm_From_map.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.rtm_From_map.text = "창닫기"
        self.rtm_From_map.set_mouse_down(self.button_Return_Main_Menu_From_Saving_Pose)

        widgets_panel5 = [self.rc_Lable, self.Underline, self.save_Motion, self.replace_Saved_Motion,
                          self.delete_Saved_Motion, self.rtm_From_map]

        return widgets_panel5

########################################################################################################################
# ==================================================================================================================== #
### TAG : Funtions for Main Panel
# ==================================================================================================================== #
    def button_Hide_Robot(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (bof.FLAG_HIDE_IK_ROBOT_MESHES == False):
            bof.FLAG_HIDE_IK_ROBOT_MESHES = True
            for ele in bod.data_Ui_Ik_Robot_Elements:
                bpy.data.materials["{}".format(ele)].node_tree.nodes["Principled BSDF"].inputs[18].default_value = 0.0
        else:
            bof.FLAG_HIDE_IK_ROBOT_MESHES = False
            for ele in bod.data_Ui_Ik_Robot_Elements:
                bpy.data.materials["{}".format(ele)].node_tree.nodes["Principled BSDF"].inputs[18].default_value = 0.6

    def button_Get_Image_Data(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bof.FLAG_RESTRICT_EVENT = True
        bpy.ops.object.load_image_get_operator('INVOKE_DEFAULT')

    def button_Change_Panel_To_Edit_Pc(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bod.data_Set_Deactivate_Activated_Panel("main_Panel")
        bod.data_Set_Activated_Panel_List_Map("pc_Editing_Panel")
        bod.data_Set_Bbox_Appear_Or_Hide(0)

    def button_Point_Cloud_Streaming(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bod.data_Set_Deactivate_Activated_Panel("main_Panel")
        bod.data_Set_Activated_Panel_List_Map("pc_Streaming_Panel")

    def button_Execute_Robot_Control_Menu(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bod.data_Set_Deactivate_Activated_Panel("main_Panel")
        bod.data_Set_Activated_Panel_List_Map("robot_Control_Panel")

    def button_Modify_All_Pose(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        try:
            obj = bod.data_Motion_List[0].mesh_Data
            gun_Length = bod.data_Info_Gun_Length * -0.01
            converted_Loc = bod.data_Set_Shifted_Location_Ik_Control_Tracking(obj, gun_Length)
            bod.data_Draw_Curr_Ikcontrol_Loc = converted_Loc
            bod.data_Draw_Curr_Ikcontrol_Rot = obj.rotation_euler
            bof.FLAG_MOVE_IK_CONTROL = True
            bod.data_Set_Activated_Panel_List_Map("modify_Pose_Panel")
        except:
            print("There is no pose to modify")

    def button_Reveal_Saving_Panel(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bod.data_Set_Activated_Panel_List_Map("saving_Panel")

    def button_Run_Motion(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (bof.FLAG_MOTION_LOADED == True):
            bof.FLAG_ANGLE_DATA_SET_TO_KAWASAKI_PROTOCOL = True
            bof.FLAG_ROBOT_MOTION_TEST = True

    # TAG : Motion simulation
    def button_Run_Simulation(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (bod.data_Motion_Length != 0):
            bod.data_Draw_Simul_Ply_Axis_First_Loc = bpy.data.objects['plyAxis'].location.x
            bpy.ops.screen.animation_play()
            bpy.data.scenes['Scene'].frame_start = 0
            bpy.data.scenes['Scene'].frame_current = 0
            bpy.data.scenes['Scene'].frame_end = 1200
            bof.FLAG_SIMULATION_WITH_ANIMATION = True
        else:
            print("You need to load motion")

    def button_Stop_Emergency(self, widget):
        print("Button '{0}' is pressed".format(widget.text))

    def reset_Slider_Bar_(self):
        bod.data_Ui_Slidebar_Motion_Rate = 5
        bod.widgets_panel.slider_Bar.set_value(1)

    def button_Draw_Del_Pose(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bof.FLAG_CONFIRM_TO_DELETE_UUID = True
        bof.FLAG_CONFIRM_TO_RESET_CORE_PRODUCT = True
        Bl_Ui_Draw_Pose_Operator(0)
        bod.data_Reset_Pose()

        vector = mathutils.Vector
        euler = mathutils.Euler
        if (bod.data_Info_Curr_Pc_Ip_Adress == bod.data_Info_Pc_One_Ip):
            bod.data_Draw_plyAxis_Obj.location = vector((-0.0493, -0.6223, 1.3521))
            bod.data_Draw_plyAxis_Obj.rotation_euler = euler((1.1903, 3.1451, 3.1312))
        else:
            bod.data_Draw_plyAxis_Obj.location = vector((-0.0093, -0.6023, 1.2421))
            bod.data_Draw_plyAxis_Obj.rotation_euler = euler((1.1903, 3.1451, 3.1311))

        self.Tasklist.text = ''                 # Tasklist text 초기화
        bod.data_Ui_Slidebar_Motion_Rate = 5    # Slidebar number 초기화 (5~100 중 5)
        self.slider_Bar.set_value(1)            # Slidebar 1로 초기화
        self.motion_Elapsed_Time.text = "모션 소요시간 : 0 s"
        bod.data_Draw_Check_Pose_Num_Max = 0
        bof.FLAG_MOTION_LOADED = False

    def button_Shut_Down(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bof.FLAG_OP_SHUTDOWN = True

    def button_Load_Robot_Pose_Lists(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        try:
            bof.FLAG_RESTRICT_EVENT = True
            bpy.ops.object.load_enum_operator('INVOKE_DEFAULT')
        except Exception as e:
            print("budpm Load button has an error : ", e)

    def button_Modify_Conv_Belt_Velo(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bpy.ops.object.velo_changeing_dialog_operator('INVOKE_DEFAULT')

    def func_Set_Ik_Control_Location(self):
        ik_Control_xyz = bod.data_Get_Ik_Control_Vector()
        self.ik_control_loc.text = f'현재위치 (X : {round(ik_Control_xyz.x, 2)} m    Y : {round(ik_Control_xyz.y, 2)}    Z : {round(ik_Control_xyz.z, 2)})'

    def func_Set_Fk_Joint_Angle(self):
        joint_Angle = bod.data_Get_Fk_Joint_Angle()
        self.joint_Angle_Value_1.text = f"조인트 각도 ({round(joint_Angle[0], 2)}˚, {round(joint_Angle[1], 2)}˚, {round(joint_Angle[2], 2)}˚, "
        self.joint_Angle_Value_2.text = f"{round(joint_Angle[3], 2)}˚, {round(joint_Angle[4], 2)}˚, {round(joint_Angle[5], 2)}˚)"

    def button_Set_Ik_Control_Current_Location(self):
        ik_Control_xyz = bod.data_Get_Ik_Control_Vector()
        self.ik_control_Curr_loc.text = f'모션위치 (X : {round(ik_Control_xyz.x, 2)} m    Y : {round(ik_Control_xyz.y, 2)}    Z : {round(ik_Control_xyz.z, 2)})'

    # TAG : Slidebar
    def slidebar_Fursys_Value_Changer(self, up_down, value): # up_Down_On_Ur_Accel_Up_Down_Value_Change
        bod.date_Set_Cancel_Teach_Mode()
        bod.data_Set_Ui_Slidebar_Motion_Rate(value * 5)
        motion_Rate = value
        self.button_Get_Speed_Data(int(motion_Rate) - 1)

        ### Notice # ================================================================================================= #
        # TODO : The function that is below here set location of slide bar where it is, After you use edit, add or delete mode.
        # if (bof.FLAG_EDIT_ONE_POSE == True or bof.FLAG_ADD_ONE_POSE == True or bof.FLAG_DELETE_ONE_POSE == True):
        #     bod.data_Draw_Curr_Revising_Pose_Num = bod.data_Ui_Slidebar_Motion_Rate
        # ============================================================================================================ #

        obj = bod.data_Motion_List[int(motion_Rate) - 1].mesh_Data
        gun_Length = bod.data_Info_Gun_Length * -0.01
        converted_Loc = bod.data_Set_Shifted_Location_Ik_Control_Tracking(obj, gun_Length)
        bod.data_Draw_Curr_Ikcontrol_Loc = converted_Loc
        bod.data_Draw_Curr_Ikcontrol_Rot = obj.rotation_euler
        bod.data_Draw_Pre_Loc_For_Cancel_Tracking = bod.data_Draw_plyAxis_Obj.location.x
        bof.FLAG_MOVE_IK_CONTROL = True

    # ================================================================================================================ #
    # NOTE : Change GUI related to speed control when motion is loaded.
    # TAG : Panel context update
    def func_Panel_Context_Update(self):
        value = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
        if (bof.FLAG_SELECT_LMOVE == True):
            bod.data_Op_Moving_State = 'L'
            self.select_J_L_MOVE.bg_color = (0.5, 0.5, 0.5, 0.8)
            self.select_J_L_MOVE.hover_bg_color = (0.5, 0.5, 0.5, 1.0)
            self.select_J_L_MOVE.text = "LMOVE"
            if (bod.data_Op_Speed_Or_Time == 0):
                bod.data_Op_Robot_Speed = 200
                bod.data_Op_Robot_Accel = 100
                self.pose_Speed.text = f'point {str(value)} 포즈 속도 : {str(bod.data_Op_Robot_Speed)} mm/s'
                self.pose_Speed_Teaching.text = f"포즈 속도 : {str(bod.data_Op_Robot_Speed)} mm/s"
            else:
                self.pose_Speed.text = f'point {str(value)} 포즈 소요시간 : 0.0 s'
                self.pose_Speed_Teaching.text = f"포즈 소요시간 : {str(bod.data_Op_Robot_Speed)} s"
        else:
            bod.data_Op_Moving_State = 'J'
            self.select_J_L_MOVE.bg_color = (0.2, 0.8, 0.8, 0.8)
            self.select_J_L_MOVE.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
            self.select_J_L_MOVE.text = "JMOVE"
            if (bod.data_Op_Speed_Or_Time == 0):
                bod.data_Op_Robot_Speed = 80
                bod.data_Op_Robot_Accel = 40
                self.pose_Speed.text = f'point {str(value)} 포즈 속도 : {str(bod.data_Op_Robot_Speed)} deg/s'
                self.pose_Speed_Teaching.text = f"포즈 속도 : {str(bod.data_Op_Robot_Speed)} deg/s"
            else:
                self.pose_Speed.text = f'point {str(value)} 포즈 소요시간 : 0.0 s'
                self.pose_Speed_Teaching.text = f"포즈 소요시간 : {str(bod.data_Op_Robot_Speed)} s"
    ####################################################################################################################

    # ================================================================================================================ #
    # NOTE : This works when slider bar moved.
    # Information # ===================================================== #
    ''' ────────────────────────────────────────────────────────────────┐
    │ Depending on the robot control method used in the current motion, │ 
    │ information is shown on panel whether it is time or speed.        │
    └──────────────────────────────────────────────────────────────── '''
    # =================================================================== #
    def button_Get_Speed_Data(self, value):
        obj = bod.data_Motion_List[value]
        speed = obj.robot_Operate_Data_Velocity
        if (bod.data_Op_Speed_Or_Time == 0):
            if (bof.FLAG_SELECT_LMOVE == False):
                self.pose_Speed.text = f'point {str(value + 1)} 포즈 속도 : {str(speed)} deg/s'
            else:
                self.pose_Speed.text = f'point {str(value + 1)} 포즈 속도 : {str(speed)} mm/s'
        else:
            self.pose_Speed.text = f'point {str(value + 1)} 포즈 소요시간 : {str(speed)} s'
    ####################################################################################################################

    # ================================================================================================================ #
    # NOTE : Press 'Time' or 'Speed' button (Operate robot with Time or Speed)
    def button_Select_Speed_Time(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        value = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
        if (bod.data_Op_Speed_Or_Time == 0):
            bod.data_Op_Speed_Or_Time = 1
            self.st_Select.text = "Time"
            bod.data_Op_Robot_Speed = 0.4
            bod.data_Op_Robot_Accel = 40
            self.pose_Speed.text = f'point {str(value)} 포즈 소요시간 : {str(bod.data_Op_Robot_Speed)} s'
            self.pose_Speed_Teaching.text = f"포즈 소요시간 : {str(bod.data_Op_Robot_Speed)} s"
        else:
            bod.data_Op_Speed_Or_Time = 0
            self.st_Select.text = "Speed"
            if (bof.FLAG_SELECT_LMOVE == False):
                bod.data_Op_Robot_Speed = 80
                bod.data_Op_Robot_Accel = 40
                self.pose_Speed.text = f'point {str(value)} 포즈 속도 : {str(bod.data_Op_Robot_Speed)} deg/s'
                self.pose_Speed_Teaching.text = f"포즈 속도 : {str(bod.data_Op_Robot_Speed)} deg/s"
            else:
                bod.data_Op_Robot_Speed = 200
                bod.data_Op_Robot_Accel = 140
                self.pose_Speed.text = f'point {str(value)} 포즈 속도 : {str(bod.data_Op_Robot_Speed)} mm/s'
                self.pose_Speed_Teaching.text = f"포즈 속도 : {str(bod.data_Op_Robot_Speed)} mm/s"
    ####################################################################################################################

    # ================================================================================================================ #
    # NOTE : Press 'JMOVE' or 'LMOVE' button
    def button_Select_L_J_Move(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        value = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
        if (bof.FLAG_SELECT_LMOVE == False):
            bof.FLAG_SELECT_LMOVE = True
            bod.data_Op_Moving_State = 'L'
            self.select_J_L_MOVE.bg_color = (0.5, 0.5, 0.5, 0.8)
            self.select_J_L_MOVE.hover_bg_color = (0.5, 0.5, 0.5, 1.0)
            self.select_J_L_MOVE.text = "LMOVE"
            if (bod.data_Op_Speed_Or_Time == 0):
                bod.data_Op_Robot_Speed = 200
                bod.data_Op_Robot_Accel = 100
                self.pose_Speed.text = f'point {str(value)} 포즈 속도 : {str(bod.data_Op_Robot_Speed)} mm/s'
                self.pose_Speed_Teaching.text = f"포즈 속도 : {str(bod.data_Op_Robot_Speed)} mm/s"
            else:
                robot_Speed = 0.4
                self.pose_Speed.text = f'point {str(value)} 포즈 소요시간 : 0.0 s'
                self.pose_Speed_Teaching.text = f"포즈 소요시간 : {str(bod.data_Op_Robot_Speed)} s"
        else:
            bof.FLAG_SELECT_LMOVE = False
            bod.data_Op_Moving_State = 'J'
            self.select_J_L_MOVE.bg_color = (0.2, 0.8, 0.8, 0.8)
            self.select_J_L_MOVE.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
            self.select_J_L_MOVE.text = "JMOVE"
            if (bod.data_Op_Speed_Or_Time == 0):
                bod.data_Op_Robot_Speed = 80
                bod.data_Op_Robot_Accel = 40
                self.pose_Speed.text = f'point {str(value)} 포즈 속도 : {str(bod.data_Op_Robot_Speed)} deg/s'
                self.pose_Speed_Teaching.text = f"포즈 속도 : {str(bod.data_Op_Robot_Speed)} deg/s"
            else:
                robot_Speed = 0.4
                self.pose_Speed.text = f'point {str(value)} 포즈 소요시간 : 0.0 s'
                self.pose_Speed_Teaching.text = f"포즈 소요시간 : {str(bod.data_Op_Robot_Speed)} s"
    ####################################################################################################################

    # ================================================================================================================ #
    # NOTE : Speed Up ↑
    def button_Send_Speed_Up(self, widget):
        self.func_Modify_Speed_Up()

    def func_Modify_Speed_Up(self):
        if (bod.data_Op_Speed_Or_Time == 0):
            if (bod.data_Op_Moving_State == 'J'):
                if (bod.data_Op_Robot_Speed < 220):
                    bod.data_Op_Robot_Speed += 10
                    bod.data_Op_Robot_Speed = round(bod.data_Op_Robot_Speed, 1)
                    self.func_Set_Accel_Data(bod.data_Op_Robot_Speed)
                    self.pose_Speed_Teaching.text = f"포즈 속도 : {str(bod.data_Op_Robot_Speed)} deg/s"

            else:
                if (bod.data_Op_Robot_Speed < 1000):
                    bod.data_Op_Robot_Speed += 50
                    bod.data_Op_Robot_Speed = round(bod.data_Op_Robot_Speed, 1)
                    self.func_Set_Accel_Data(bod.data_Op_Robot_Speed)
                    self.pose_Speed_Teaching.text = f"포즈 속도 : {str(bod.data_Op_Robot_Speed)} mm/s"
        else:
            if (bod.data_Op_Robot_Speed < 3):
                bod.data_Op_Robot_Speed += 0.1
                bod.data_Op_Robot_Speed = round(bod.data_Op_Robot_Speed, 1)
                self.pose_Speed_Teaching.text = f"포즈 소요시간 : {str(bod.data_Op_Robot_Speed)} s"
    ####################################################################################################################

    # ================================================================================================================ #
    # NOTE : Normal Speed ─
    def button_Send_Normal_Speed(self, widget):
        if (bod.data_Op_Speed_Or_Time == 0):
            if (bod.data_Op_Moving_State == 'J'):
                bod.data_Op_Robot_Speed = 80
                self.func_Set_Accel_Data(bod.data_Op_Robot_Speed)
                self.pose_Speed_Teaching.text = f"포즈 속도 : {str(bod.data_Op_Robot_Speed)} deg/s"

            else:
                bod.data_Op_Robot_Speed = 200
                self.func_Set_Accel_Data(bod.data_Op_Robot_Speed)
                self.pose_Speed_Teaching.text = f"포즈 속도 : {str(bod.data_Op_Robot_Speed)} mm/s"
        else:
            bod.data_Op_Robot_Speed = 0.4
            self.pose_Speed_Teaching.text = f"포즈 소요시간 : {str(bod.data_Op_Robot_Speed)} s"
    ####################################################################################################################

    # ================================================================================================================ #
    # NOTE : Speed Down ↓
    def button_Send_Speed_Down(self, widget):
        self.func_Modify_Speed_Down()

    def func_Modify_Speed_Down(self):
        if (bod.data_Op_Speed_Or_Time == 0):
            if (bod.data_Op_Moving_State == 'J'):
                if (bod.data_Op_Robot_Speed > 10):
                    bod.data_Op_Robot_Speed -= 10
                    bod.data_Op_Robot_Speed = round(bod.data_Op_Robot_Speed, 1)
                    self.func_Set_Accel_Data(bod.data_Op_Robot_Speed)
                    self.pose_Speed_Teaching.text = f"포즈 속도 : {str(bod.data_Op_Robot_Speed)} deg/s"

            else:
                if (bod.data_Op_Robot_Speed > 50):
                    bod.data_Op_Robot_Speed -= 50
                    bod.data_Op_Robot_Speed = round(bod.data_Op_Robot_Speed, 1)
                    self.func_Set_Accel_Data(bod.data_Op_Robot_Speed)
                    self.pose_Speed_Teaching.text = f"포즈 속도 : {str(bod.data_Op_Robot_Speed)} mm/s"
        else:
            if (bod.data_Op_Robot_Speed > 0):
                bod.data_Op_Robot_Speed -= 0.1
                bod.data_Op_Robot_Speed = round(bod.data_Op_Robot_Speed, 1)
                self.pose_Speed_Teaching.text = f"포즈 소요시간 : {str(bod.data_Op_Robot_Speed)} s"
    ####################################################################################################################

    def func_Set_Motion_Elapsed_Time_On_Panel(self, etime):
        bod.widgets_panel.motion_Elapsed_Time.text = f"모션 소요시간 : {str(round(etime, 1))} s"

    def func_Set_Accel_Data(self, speed):
        if (bod.data_Op_Moving_State == 'J'):
            if (speed < 40):
                bod.data_Op_Robot_Accel = 10
            else:
                std = int(round(speed / 20, 1))
                aim = speed / 10
                delta = aim - std
                bod.data_Op_Robot_Accel = int(delta * 10)
                if (bod.data_Op_Robot_Accel > 80):
                    bod.data_Op_Robot_Accel = 80

        elif (bod.data_Op_Moving_State == 'L'):
            if (speed < 60):
                bod.data_Op_Robot_Accel = 30
            else:
                std = int(round(speed / 30, 1))
                aim = speed / 10
                delta = aim - std
                bod.data_Op_Robot_Accel = int(delta * 10)

    ####################################################################################################################

    # def button_Make_Path_Automatically(self, widget): # 기능 개선 후 재사용 예정 211109
    #     print("Button '{0}' is pressed".format(widget.text))
    #     length = bod.data_Motion_Length
    #     if (bof.FLAG_PLYAXIS_ANCHOR_DROPPED == True and length != 0):
    #         bof.FLAG_PLYAXIS_ANCHOR_DROPPED = False
    #         bof.FLAG_MAKE_MOTION_BUTTON_PRESSED = True
    #         text_Name = "Anchor_text"
    #         bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
    #
    #         # TAG : Auto create motion
    #         self.func_Init_Auto_Create_Motion()
    #         bod.data_Set_Auto_Created_Motion()
    #     else:
    #         print(" > Drop the anchor first")
    #         bof.FLAG_MAKE_MOTION_BUTTON_PRESSED = False
    #         text_Name = 'Drop_anchor_text'
    #         bod.data_Set_Selected_Menu_Text_Location(text_Name)

    # TAG : Auto create motion
    def func_Init_Auto_Create_Motion(self):
        bod.data_Draw_Ply_Axis_First_Loc = bod.data_Draw_Anchored_Location
        bod.data_Draw_plyAxis_Obj.location.x = bod.data_Draw_Ply_Axis_First_Loc
        bod.data_Draw_Curr_Ply_Axis_Loc = bod.data_Draw_plyAxis_Obj.location.x
        self.slider_Bar.set_value(1)
        Bl_Ui_Draw_Pose_Operator(1)
        bpy.ops.object.select_pattern(pattern="point*", extend=False)
        bpy.ops.object.delete()
        bpy.ops.object.select_pattern(pattern="cur_Point_Path*", extend=False)
        bpy.ops.object.delete()
        bod.data_Draw_Path_Point_List = []

    def on_chb_visibility_state_change(self, checkbox, state):
        active_obj = bpy.context.view_layer.objects.active
        if active_obj is not None:
            active_obj.hide_viewport = not state
########################################################################################################################


# ==================================================================================================================== #
### TAG : Funtions for Point Cloud Editing Panel
# ==================================================================================================================== #
    def button_Draw_Point_Cloud(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bof.FLAG_GET_TRIMMED_POINT_CLOUD = True
        bod.data_Draw_plyAxis_Obj = bpy.data.objects['pcedit_plyAxis']
        bpy.ops.object.load_image_get_operator('INVOKE_DEFAULT')

    def button_Return_Main_Menu(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bod.data_Set_Deactivate_Activated_Panel("pc_Editing_Panel")
        bod.data_Set_Activated_Panel_List_Map("main_Panel")
        bod.data_Set_Bbox_Appear_Or_Hide(1)

    def button_Refresh_Pcv_Cache(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bof.FLAG_CONFIRM_TO_DELETE_UUID = True
        bof.FLAG_CONFIRM_TO_RESET_CORE_PRODUCT = True
        Bl_Ui_Draw_Pose_Operator(0)
        bod.data_Reset_Pose()

    def button_plus_X(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        vec = mathutils.Vector
        bod.data_Set_Pc_Editing_Object_Location(self.modifying_Target_Object, vec((self.weight, 0, 0)))

    def button_minus_X(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        vec = mathutils.Vector
        bod.data_Set_Pc_Editing_Object_Location(self.modifying_Target_Object, vec((-self.weight, 0, 0)))

    def button_plus_Z(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        vec = mathutils.Vector
        bod.data_Set_Pc_Editing_Object_Location(self.modifying_Target_Object, vec((0, 0, self.weight)))

    def button_minus_Z(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        vec = mathutils.Vector
        bod.data_Set_Pc_Editing_Object_Location(self.modifying_Target_Object, vec((0, 0, -self.weight)))

    def button_plus_Y(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        vec = mathutils.Vector
        bod.data_Set_Pc_Editing_Object_Location(self.modifying_Target_Object, vec((0, self.weight, 0)))

    def button_minus_Y(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        vec = mathutils.Vector
        bod.data_Set_Pc_Editing_Object_Location(self.modifying_Target_Object, vec((0, -self.weight, 0)))

    def button_Toggle_Scale_Or_Rot(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (self.bbox_Scale_Or_Rot.text == "Rotation"):
            self.bbox_Scale_Or_Rot.bg_color = (0.2, 0.8, 0.2, 0.8)
            self.bbox_Scale_Or_Rot.hover_bg_color = (0.2, 0.9, 0.2, 1.0)
            self.bbox_Scale_Or_Rot.text = "Scale"
            self.modify_data_Of_Rotation = False
        else:
            self.bbox_Scale_Or_Rot.bg_color = (0.2, 0.8, 0.8, 0.8)
            self.bbox_Scale_Or_Rot.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
            self.bbox_Scale_Or_Rot.text = "Rotation"
            self.modify_data_Of_Rotation = True

    def button_Toggle_Target_Object(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (self.target_Object.text == "plyAxis"):
            self.target_Object.bg_color = (0.2, 0.8, 0.8, 0.8)
            self.target_Object.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
            self.target_Object.text = "bbox"
            self.modifying_Target_Object = bpy.data.objects["bbox"]
        else:
            self.target_Object.bg_color = (0.2, 0.8, 0.2, 0.8)
            self.target_Object.hover_bg_color = (0.2, 0.9, 0.2, 1.0)
            self.target_Object.text = "plyAxis"
            self.modifying_Target_Object = bpy.data.objects["pcedit_plyAxis"]


    def button_Value_Up(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (self.Axis == 0):
            if (self.modify_data_Of_Rotation == True):
                eul = mathutils.Euler
                bod.data_Set_Pc_Editing_Object_Rotation(self.modifying_Target_Object, eul((self.weight, 0, 0)))
            else:
                vec = mathutils.Vector
                bod.data_Set_Pc_Editing_Object_Scale(self.modifying_Target_Object, vec((self.weight, 0, 0)))
        elif (self.Axis == 1):
            if (self.modify_data_Of_Rotation == True):
                eul = mathutils.Euler
                bod.data_Set_Pc_Editing_Object_Rotation(self.modifying_Target_Object, eul((0, self.weight, 0)))
            else:
                vec = mathutils.Vector
                bod.data_Set_Pc_Editing_Object_Scale(self.modifying_Target_Object, vec((0, self.weight, 0)))
        elif (self.Axis == 2):
            if (self.modify_data_Of_Rotation == True):
                eul = mathutils.Euler
                bod.data_Set_Pc_Editing_Object_Rotation(self.modifying_Target_Object, eul((0, 0, self.weight)))
            else:
                vec = mathutils.Vector
                bod.data_Set_Pc_Editing_Object_Scale(self.modifying_Target_Object, vec((0, 0, self.weight)))

    def button_Value_Down(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (self.Axis == 0):
            if (self.modify_data_Of_Rotation == True):
                eul = mathutils.Euler
                bod.data_Set_Pc_Editing_Object_Rotation(self.modifying_Target_Object, eul((-self.weight, 0, 0)))
            else:
                vec = mathutils.Vector
                bod.data_Set_Pc_Editing_Object_Scale(self.modifying_Target_Object, vec((-self.weight, 0, 0)))
        elif (self.Axis == 1):
            if (self.modify_data_Of_Rotation == True):
                eul = mathutils.Euler
                bod.data_Set_Pc_Editing_Object_Rotation(self.modifying_Target_Object, eul((0, -self.weight, 0)))
            else:
                vec = mathutils.Vector
                bod.data_Set_Pc_Editing_Object_Scale(self.modifying_Target_Object, vec((0, -self.weight, 0)))
        elif (self.Axis == 2):
            if (self.modify_data_Of_Rotation == True):
                eul = mathutils.Euler
                bod.data_Set_Pc_Editing_Object_Rotation(self.modifying_Target_Object, eul((0, 0, -self.weight)))
            else:
                vec = mathutils.Vector
                bod.data_Set_Pc_Editing_Object_Scale(self.modifying_Target_Object, vec((0, 0, -self.weight)))

    def button_Toggle_Detail_Or_Rough(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (self.choose_Detail_Rough.text == "Detail"):
            self.choose_Detail_Rough.bg_color = (0.2, 0.8, 0.2, 0.8)
            self.choose_Detail_Rough.hover_bg_color = (0.2, 0.9, 0.2, 1.0)
            self.choose_Detail_Rough.text = "Rough"
            self.weight = 0.1
        else:
            self.choose_Detail_Rough.bg_color = (0.2, 0.8, 0.8, 0.8)
            self.choose_Detail_Rough.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
            self.choose_Detail_Rough.text = "Detail"
            self.weight = 0.01

    def button_Standard_Axis_X(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        self.x_Axis.bg_color = (0.2, 0.8, 0.2, 0.8)
        self.x_Axis.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.y_Axis.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.y_Axis.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.z_Axis.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.z_Axis.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Axis = 0

    def button_Standard_Axis_Y(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        self.x_Axis.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.x_Axis.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.y_Axis.bg_color = (0.2, 0.8, 0.2, 0.8)
        self.y_Axis.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.z_Axis.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.z_Axis.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Axis = 1

    def button_Standard_Axis_Z(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        self.x_Axis.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.x_Axis.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.y_Axis.bg_color = (0.2, 0.8, 0.8, 0.8)
        self.y_Axis.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.z_Axis.bg_color = (0.2, 0.8, 0.2, 0.8)
        self.z_Axis.hover_bg_color = (0.2, 0.9, 0.9, 1.0)
        self.Axis = 2

    def button_Trim_Point_Cloud(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (bof.FLAG_POINT_CLOUD_IS_LOADED == True):
            bof.FLAG_TRIM_POINT_CLOUD_BY_BBOX = True
        else:
            print("Load point cloud first")

    # TAG : Save trimmed point cloud
    def button_Save_Trimed_Point_Cloud(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (bod.data_Pc_Point_Cloud_Data is not None):
            bof.FLAG_SAVE_TRIMMED_POINT_CLOUD = True
            bof.FLAG_RESTRICT_EVENT = True
            bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
        else:
            print("Load point cloud first")
########################################################################################################################


# ==================================================================================================================== #
### TAG : Funtions for Point Cloud Streaming Panel
# ==================================================================================================================== #
    def button_Return_Main_Menu_From_Streaming(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bod.data_Set_Deactivate_Activated_Panel("pc_Streaming_Panel")
        bod.data_Set_Activated_Panel_List_Map("main_Panel")

    def button_Show_Specific_Point_Cloud(self, widget):
        if (bod.data_Pc_Show_Specific_Point_Cloud):
            bod.data_Pc_Show_Specific_Point_Cloud = False
            self.cut_Point_Cloud.text = "전체"
            self.cut_Point_Cloud.bg_color = (0.2, 0.8, 0.2, 0.8)
            self.cut_Point_Cloud.hover_bg_color = (0.2, 0.9, 0.2, 1.0)
        else:
            bod.data_Pc_Show_Specific_Point_Cloud = True
            self.cut_Point_Cloud.text = "부분"
            self.cut_Point_Cloud.bg_color = (0.2, 0.8, 0.8, 0.8)
            self.cut_Point_Cloud.hover_bg_color = (0.2, 0.9, 0.9, 1.0)

    # NOTE : Capture and save point cloud that are currently being displayed on the screen.
    # TAG : Capture point cloud
    def button_Capture_Point_Cloud(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (bof.FLAG_KEEP_COLLECT_DEPTH_INFO == True):
            bof.FLAG_CAPTURE_CURRENT_POINT_CLOUD = True
        else:
            print("\nStart point cloud streaming first")

    # NOTE : Enable data reception from depth camera
    # TAG : Point cloud streaming
    def button_Start_Signal_To_Camera(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (bof.FLAG_KEEP_COLLECT_DEPTH_INFO == False):
            bof.FLAG_KEEP_COLLECT_DEPTH_INFO = True
            bof.FLAG_PLY_LOAD_FINISHED = True
        else:
            print("\nCamera is already running.")

    def button_Stop_Signal_To_Camera(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bof.FLAG_KEEP_COLLECT_DEPTH_INFO = False
        bof.FLAG_PLY_LOAD_FINISHED = False
        bod.data_Pc_Point_Cloud_Data = None
        bod.data_Pc_Point_Cloud_Color_Int_Data = None
        del bod.bl_op_cam
########################################################################################################################


# ==================================================================================================================== #
### TAG : Funtions for Robot control panel menu
# ==================================================================================================================== #
    def button_Send_Execute_Order(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bod.bl_op_robot.convert_Joint_Angles_To_Suitable_Protocol(bod.data_Motion_List, '50')
        bof.FLAG_THREAD_SENDING_STATE = True
        bof.FLAG_START_SENDING_JOINT_ANGLE_DATA = True

    def button_Send_Execute_Pose_Order(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        loc = bod.data_Get_Ik_Control_Vector()
        rot = bod.data_Get_Ik_Control_Euler()

        pose = bod.data_Set_Direct_Ordering(loc, rot)
        bod.bl_op_robot.convert_Joint_Angles_To_Suitable_Protocol(pose, '50')
        pose = bod.bl_op_robot.combined_Joint_Angle_Data
        bod.bl_op_robot.order.JMOVE(pose[0])

    # NOTE : Send home returning command to robot.
    def button_Send_Returning_Home_Order(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bod.bl_op_robot.send_Returning_Home_Command()

    def button_Start_Server(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (self.start_Server.flag_Server_Started == False):
            bof.FLAG_SERVER_OPENED = True
            bof.FLAG_ROBOT_DISCONNECTED = False
            self.start_Server.bg_color = (0.2, 0.8, 0.2, 0.8)
            self.start_Server.hover_bg_color = (0.2, 0.9, 0.2, 1.0)
            self.start_Server.text = "서버 종료"
            bod.bl_op_server.run_Server()
            self.start_Server.flag_Server_Started = True
        else:
            bod.bl_op_robot.order.HOME()
            bof.FLAG_SERVER_OPENED = False
            bof.FLAG_ROBOT_DISCONNECTED = True
            self.start_Server.bg_color = (0.2, 0.8, 0.8, 0.8)
            self.start_Server.hover_bg_color = (0.2, 0.9, 0.8, 1.0)
            self.start_Server.text = "서버 시작"
            bod.bl_op_server.close_Server()
            self.start_Server.flag_Server_Started = False

    # NOTE : Send stop command to robot
    def button_Send_Robot_Stop_Order(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bod.bl_op_robot.send_Stop_Command()

    def button_Return_Main_Menu_From_Robot_Control(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        bod.data_Set_Deactivate_Activated_Panel("robot_Control_Panel")
        bod.data_Set_Activated_Panel_List_Map("main_Panel")
########################################################################################################################

# ==================================================================================================================== #
### TAG : Funtions for Modify all pose panel menu
# ==================================================================================================================== #
    # TAG : Modify all pose
    def button_Start_Modifying_Pose(self, widget):
        pose = bod.data_Motion_List[0]
        loc = bod.data_Get_Ik_Control_Vector()
        bod.data_Draw_Modified_Pose_Data = []

        loc_x = pose.mesh_Data.location.x - loc.x
        loc_y = pose.mesh_Data.location.y - loc.y
        loc_z = pose.mesh_Data.location.z - loc.z

        for pose in bod.data_Motion_List:
            lx = pose.mesh_Data.location.x - loc_x
            ly = pose.mesh_Data.location.y - loc_y
            lz = pose.mesh_Data.location.z - loc_z

            bod.data_Draw_Modified_Pose_Data.append([lx, ly, lz])

        bod.data_Draw_Pose_Count = 0
        bof.FLAG_MODIFY_ALL_POSE_AUX = True
        Bl_Ui_Draw_Pose_Operator(2)

    def button_Set_Modified_Pose(self, widget):
        bof.FLAG_RESTRICT_EVENT = True
        bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
        bod.data_Set_Ui_Slidebar_Motion_Rate(5)
        bod.widgets_panel.slider_Bar.set_value(1)

    def button_Return_Main_Menu_From_Modify_All_Pose(self, widget):
        bod.data_Set_Deactivate_Activated_Panel("modify_Pose_Panel")
########################################################################################################################

# ==================================================================================================================== #
### TAG : Funtions for saving panel menu
# ==================================================================================================================== #
    def button_Save_Pose_Lists(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        try:
            if (bod.data_Motion_Length == 0):
                print("There is no motion to save or modify")
            else:
                bof.FLAG_RESTRICT_EVENT = True
                bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
                # Bl_Ui_Draw_Pose_Operator(0)
                bod.data_Set_Ui_Slidebar_Motion_Rate(5)
                bod.widgets_panel.Tasklist.text = ''
                bod.widgets_panel.slider_Bar.set_value(1)
                bod.widgets_panel.motion_Elapsed_Time.text = "모션 소요시간 : 0 s"
        except Exception as e:
            print("budpm Save button has an error : ", e)

    def button_Modify_Pose_Lists(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        if (len(bod.data_Ui_Curr_Loaded_Data_For_modify) != 0):
            try:
                bof.FLAG_RESTRICT_EVENT = True

                save_Motion_Data = bod.data_Get_Combined_Motion_Data()
                bod.data_Reset_Pose()
                bof.FLAG_MOTION_LOADED = False
                bod.bl_op_sql.update_Pose_Data_To_DB(bod.data_Ui_Curr_Loaded_Data_For_modify, save_Motion_Data)

                Bl_Ui_Draw_Pose_Operator(0)
                bof.FLAG_RESTRICT_EVENT = False
                text_Name = 'Name_that_exists'
                bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
                bof.FLAG_MODIFY_MOTION = False
                bod.data_Ui_Curr_Loaded_Data_For_modify = ""
                bod.data_Set_Ui_Slidebar_Motion_Rate(5)
                bod.widgets_panel.Tasklist.text = ''
                bod.widgets_panel.slider_Bar.set_value(1)
                bod.widgets_panel.motion_Elapsed_Time.text = "모션 소요시간 : 0 s"
            except Exception as e:
                print("budpm Save button has an error : ", e)

            bod.data_Set_Deactivate_Activated_Panel("saving_Panel")

        else:
            print("There is no motion to save or modify")

    def button_Delete_Robot_Pose_Lists(self, widget):
        print("Button '{0}' is pressed".format(widget.text))
        try:
            bof.FLAG_RESTRICT_EVENT = True
            bpy.ops.object.delete_enum_operator('INVOKE_DEFAULT')
        except Exception as e:
            print("budpm Load button has an error : ", e)

    def button_Return_Main_Menu_From_Saving_Pose(self, widget):
        bod.data_Set_Deactivate_Activated_Panel("saving_Panel")
########################################################################################################################