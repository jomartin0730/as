# **** MAVIZ MAIN*****
import pathlib
import random
import tempfile
import bpy
import math
import os 
import sys
import mathutils
from bpy.types import Operator
from bl_ui_label import *
from bl_ui_button import *
from bl_ui_checkbox import *
from bl_ui_slider import *
from bl_ui_up_down import *
from bl_ui_drag_panel import *
from bl_op_data import Bl_Op_Data as bod
from bl_op_flag import Bl_Op_Flag as bof
from bl_ui_draw_pose import Bl_Ui_Draw_Pose as budp
from bl_op_multiple_thread import Bl_Op_Multiple_Thread as bomt
from bl_op_server import URxMoveToPoseOperator

from IkMover import IKMover

class TMobj:
    def __init__(self, bl_obj,bl_glow_control):
        print('item')

class PoseObj:
    def __init__(self, bl_obj):
        print('│ pose                                │')
        self.dimensions = bl_obj.dimensions
        self.location = bl_obj.location
        self.direction = bl_obj.rotation_euler
        self.position = [0,0,0]

    def _set_new_pos(self, new_pos):
        self.position[0] = new_pos[0]
        self.position[1] = new_pos[1]
        self.position[2] = new_pos[2]
    
    def _set_rotation(self, new_dir):
        self.direction[0] = new_dir[0]
        self.direction[1] = new_dir[1]
        self.direction[2] = new_dir[2]

class MotionDisplay:
    def __init__(sel, bl_obj):
        print('Motion')

class Maviz:
    INITIAL_MOTION_SPEED = 8
    INITIAL_MOVER_SPEED = 10
    _mouseX = 0
    _mouseY = 0

    @staticmethod
    def setup_item(blender_object_name ):
        tmp_obj = bpy.data.objects[blender_object_name]
        item = PoseObj(tmp_obj)
        return item

    @staticmethod
    def setup_ik_mover(blender_object_name, glow_control_name):
        tmp_obj = bpy.data.objects[blender_object_name]
        glow_control_obj = bpy.data.objects[glow_control_name]
        mvt = IKMover(tmp_obj, glow_control_obj)
        return mvt

    def __init__(self, item: 'item', mover: 'IKMover'):
        self.mover = mover
        self.item = item
        self.mover.speed = self.INITIAL_MOVER_SPEED
        # 현재 커서 위치를 불러 와야 함. 
        self.mover._setCurPos(self.mover.cur_location[0],self.mover.cur_location[1],self.mover.cur_location[2])
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_drag = False
        self.is_rotation = False # mouse tracking mode

        ### NOTE : 0 >> x rot / 1 >> y rot / 2 >> z rot / 3 >> scale
        self.point_Cloud_Edit = 0

        self.zoom_Ratio = 0
        self.length = 0.01
        self.euler = 3.141592 / 100

        self.command_for_key_type = {
            'J': IKMover.CMD_LEFT,
            'L': IKMover.CMD_RIGHT,
            'I': IKMover.CMD_UP,
            'K': IKMover.CMD_DOWN,
            'U': IKMover.CMD_LFET_ROT,
            'O': IKMover.CMD_RIGHT_ROT,
            'NUMPAD_4' : IKMover.CMD_NUM_4,
            'NUMPAD_5' : IKMover.CMD_NUM_5,
            'NUMPAD_6' : IKMover.CMD_NUM_6,
            'NUMPAD_7' : IKMover.CMD_NUM_7,
            'NUMPAD_8' : IKMover.CMD_NUM_8,
            'NUMPAD_9' : IKMover.CMD_NUM_9,
        }
        self.action_for_key_state = {
            'PRESS': self.mover.start_command,
            'RELEASE': self.mover.stop_command,
        }
        print('│ MAVIZ created                       │')
        print("└─────────────────────────────────────┘")

        self.multiple_Thread = bomt()
        if (bod.data_Ui_Pre_Process):
            self.data_Set_Modify_Modeling_Environment(bod.data_Info_Curr_Pc_Ip_Adress)

        self.urManualControlFlag = False
        self.urManualControlMoveValue = 0.01
        self._urChangePoseY = 0.01
        bof.FLAG_REVEAL_PANEL = True

    def setMover(self, location, rotation):
        try:
            self.mover._setLocation(location[0], location[1], location[2])
            self.mover._setRotate(rotation[0], rotation[1], rotation[2])
        except Exception as e:
            print("setMover : ", e)

    def update(self, time_delta):
        self.mover.update(time_delta)

    def set_event(self, event, context, budpm):
        if event.type == 'R' and event.value == 'PRESS':
            bof.FLAG_RESTRICT_EVENT = False

        if (bof.FLAG_RESTRICT_EVENT == False):
            if event.type == 'H':
                if event.value == 'PRESS':
                    location_Vector = bod.data_Set_Ikcontrol_Home_Location()
                    self.mover.position = location_Vector
                    bpy.context.view_layer.update()

            # ======================================================================================================== #
            # NOTE : Create Pose
            # ======================================================================================================== #
            if event.type == 'NUMPAD_0':
                if event.value == 'PRESS':
                    bod.data_Draw_Curr_Ply_Axis_Loc = bod.data_Draw_plyAxis_Obj.location.x
                    bof.FLAG_RESTRICT_TRACKING_OFF = True
                    max_Pose_Number = budp.draw_Pose_List_Count + 1
                    pos_Length = bod.data_Motion_Length
                    ict = bpy.data.objects['ik_control_Tracking']

                    # NOTE : current_Pose_Number >> The number the slide bar points to.
                    current_Pose_Number = int(bod.data_Ui_Slidebar_Motion_Rate / 5)

                    # NOTE : Limit the maximum number of motion to 30
                    if (bod.data_Draw_Check_Pose_Num_Max == 1):
                        if (pos_Length < 30):
                            bod.data_Draw_Check_Pose_Num_Max = 0

                    ### Information # ================================================================================ #
                    '''로봇의 목표 지점 간 속도보장은 로봇 6축 기준. 로봇엔드팁이 로봇의 6축과 거리가 있는 경우 6축만 돌렸을 때
                    6축이 해당 Pose로 이동하면 6축이 목표지점으로 가기 전에 로봇엔드가 먼저(혹은 늦게) 도착하게 되어 엔드 기준으로는
                    속도보장이 되지 않기 때문에 이를 보정하기 위한 메소드
                    ┌───────────────────────────────────────────────────────────────────────────────────────────────┐
                    │ The speed guarantee between the target points of the robot is based on the robot's six axis.  │ 
                    │ If the robot end-tip is far from the robot's 6 axis, if the 6 axis moves to the corresponding │
                    │ position when the 6 axis is turned, the robot end will arrive first (or later) before         │ 
                    │ the target point, so the speed is not guaranteed by the end tip.                              │
                    └──────────────────────────────────────────────────────────────────────────────────────────── '''
                    # ================================================================================================ #
                    try:
                        # NOTE : When revising motion
                        if ((bof.FLAG_EDIT_ONE_POSE == True or bof.FLAG_ADD_ONE_POSE == True or bof.FLAG_DELETE_ONE_POSE == True)):
                            if (current_Pose_Number == 1):
                                bod.data_Op_Converted_Robot_Speed = bod.data_Motion_List[current_Pose_Number - 1].robot_Operate_Data_Velocity
                            else:
                                bod.data_Calculate_Length_Between_Revised_Motions(ict, (current_Pose_Number - 2), 0)

                        # NOTE : When teaching motion
                        else:
                            if (pos_Length == 0):
                                bod.data_Op_Converted_Robot_Speed = bod.data_Op_Robot_Speed
                            elif (pos_Length > 0):
                                bod.data_Calculate_Length_Between_Revised_Motions(ict, (current_Pose_Number - 2), 1)
                    except Exception as e:
                        print("data_Calculate_Convert_Robot_Speed : ", e)
                    # ================================================================================================ #

                    ### Information # ================================================================================ #
                    '''(max_Pose_Number <= current_Pose_Number)
                            : 현재 슬라이드 바가 가리키는 숫자가 기존 작성된 Pose의 수보다 클 때 새 Pose를 생성할 수 있게 하는 조건.
                       (else)
                            : 현재 슬라이드바의 위치가 기존에 생성된 Pose의 번호와 겹치기 때문에 모션을 revise하거나 슬라이드바를 
                              우측으로 이동해야한다.
                    ┌───────────────────────────────────────────────────────────────────────────────────────────────┐
                    │ * (max_Pose_Number <= current_Pose_Number) : Create a new pose when the number that the       │ 
                    │   current slide bar points to is greater than the number of the existing created pose.        │
                    │ * (else) : Current slide bar's pointing number overlaps with that of the existing number of   │ 
                    │   created pose, so you need to modify the motion or move the slide bar to the right.          │
                    └──────────────────────────────────────────────────────────────────────────────────────────── '''
                    # ================================================================================================ #
                    if (max_Pose_Number <= current_Pose_Number or (bof.FLAG_EDIT_ONE_POSE == True or bof.FLAG_ADD_ONE_POSE == True or bof.FLAG_DELETE_ONE_POSE == True)):
                        bod.data_Draw_Curr_Revising_Point_Number = int(bod.data_Ui_Slidebar_Motion_Rate / 5) - 1
                        bod.data_Draw_Pose_Count = 0

                        # NOTE : Motion의 길이(Pose의 개수)가 current_Pose_Number보다 클 때
                        if (current_Pose_Number <= bod.data_Motion_Length):

                            # ======================================================================================== #
                            # TAG : Edit mode
                            # ======================================================================================== #
                            if (bof.FLAG_EDIT_ONE_POSE == True):
                                flag = bof.FLAG_MOTION_LOADED
                                motion_Elapsed_Time = bod.data_Ui_Motion_Elapsed_Time
                                budp.draw_Del_Pose()
                                bod.data_Ui_Motion_Elapsed_Time = motion_Elapsed_Time
                                if (flag == True):
                                    bof.FLAG_MOTION_LOADED = flag

                                text_Name = 'Editmode_text'
                                bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
                                budpm.slider_Bar.set_value(budp.draw_Pose_List_Count + 1)

                                bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                                bof.FLAG_EDIT_ONE_POSE = False
                                bof.FLAG_POSE_EDITING_MODAL_OPEN = True
                            ############################################################################################

                            # ======================================================================================== #
                            # TAG : Add mode
                            # ======================================================================================== #
                            elif (bof.FLAG_ADD_ONE_POSE == True):
                                # NOTE :  This condition is made to use adding mode when number of point is under 30.
                                if (bod.data_Motion_Length < 30):
                                    if (current_Pose_Number == 1):
                                        bod.data_Draw_Ply_Axis_First_Loc = bod.data_Draw_plyAxis_Obj.location.x

                                    flag = bof.FLAG_MOTION_LOADED
                                    motion_Elapsed_Time = bod.data_Ui_Motion_Elapsed_Time
                                    budp.draw_Del_Pose()
                                    bod.data_Ui_Motion_Elapsed_Time = motion_Elapsed_Time
                                    if (flag == True):
                                        bof.FLAG_MOTION_LOADED = flag

                                    text_Name = 'Addmode_text'
                                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
                                    budpm.slider_Bar.set_value(budp.draw_Pose_List_Count + 1)

                                    bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                                    bof.FLAG_ADD_ONE_POSE = False
                                    bof.FLAG_ADDING_STATE_MOVE_PLYAXIS_AUX = True
                                    bof.FLAG_POSE_ADDING_MODAL_OPEN = True
                                else:
                                    print("You can't add more point")
                                    bof.FLAG_ADD_ONE_POSE = False
                                    text_Name = 'Addmode_text'
                                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
                            ############################################################################################

                            # ======================================================================================== #
                            # TAG : Delete mode
                            # ======================================================================================== #
                            elif (bof.FLAG_DELETE_ONE_POSE == True):
                                if (bod.data_Motion_Length < 3):
                                    print("Pose should exist at least two points")
                                    text_Name = 'Deletemode_text'
                                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
                                    bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                                    bof.FLAG_DELETE_ONE_POSE = False
                                else:
                                    flag = bof.FLAG_MOTION_LOADED
                                    motion_Elapsed_Time = bod.data_Ui_Motion_Elapsed_Time
                                    budp.draw_Del_Pose()
                                    bod.data_Ui_Motion_Elapsed_Time = motion_Elapsed_Time
                                    if (flag == True):
                                        bof.FLAG_MOTION_LOADED = flag

                                    text_Name = 'Deletemode_text'
                                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
                                    budpm.slider_Bar.set_value(budp.draw_Pose_List_Count + 1)

                                    bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                                    bof.FLAG_DELETE_ONE_POSE = False
                                    bof.FLAG_POSE_DELETING_MODAL_OPEN = True
                            ############################################################################################

                            # TAG : Convert speed
                            # NOTE : revise한 후 다음 point의 속도를 보정하기 위한 조건 >> (현재 point의 pose가 바뀌면 다음 point의 속도에도 영향을 미치기 때문)
                            if (current_Pose_Number < pos_Length):
                                # NOTE : Delete mode 시 첫번째 모션이면 속도재산정 미이행
                                if (bof.FLAG_POSE_DELETING_MODAL_OPEN == True and current_Pose_Number == 1):
                                    pass
                                else:
                                    bod.data_Draw_Revised_Point_Number = current_Pose_Number
                                    # ======================================================== #
                                    # NOTE : 현재 revise한 Pose 뒤에 남은 Pose가 있으면 True. >> FLAG_AUTO_CHANGE_SPEED_OF_REST_POINT를 바꿔준다.
                                    bof.FLAG_REST_POINT_EXIST = True
                                    # ======================================================== #
                            elif (bof.FLAG_POSE_ADDING_MODAL_OPEN == True and current_Pose_Number == pos_Length):
                                # NOTE : Add mode시 마지막 point 전에 모션을 추가할 때 필요한 조건
                                bod.data_Draw_Revised_Point_Number = current_Pose_Number
                                bof.FLAG_REST_POINT_EXIST = True
                            else:
                                # NOTE : 마지막 모션이면 속도재산정 미이행
                                pass

                        # NOTE : current_Pose_Number가 Motion의 길이(Pose의 개수)보다 클 때
                        else:
                            if (bof.FLAG_EDIT_ONE_POSE == False and bof.FLAG_ADD_ONE_POSE == False and bof.FLAG_DELETE_ONE_POSE == False):
                                # NOTE : Check if the Pose data is full. [1]
                                if (bod.data_Draw_Check_Pose_Num_Max == 0):
                                    # NOTE : 최초로 Pose가 30개된 것을 감지. 이후엔 아래 else([2])로 이동
                                    if (bod.data_Ui_Slidebar_Motion_Rate > 150):
                                        bod.data_Draw_Check_Pose_Num_Max = 1
                                        print("You can't add more point")
                                    else:
                                        # NOTE : current_Pose_Number가 Motion의 길이(Pose의 개수)보다 '1'만큼 클 때
                                        if (current_Pose_Number <= bod.data_Motion_Length + 1):
                                            if (bof.FLAG_PLYAXIS_ANCHOR_DROPPED == True and current_Pose_Number == 1):
                                                current_Ply_Axis_Location = bod.data_Draw_plyAxis_Obj.location.x
                                                bod.data_Draw_Atmp_Length = bod.data_Draw_Anchored_Location - current_Ply_Axis_Location
                                            bod.data_Draw_Select_Robot_Getting_Joint = 0
                                            loc = bod.data_Get_Ik_Control_Vector()
                                            rot = bod.data_Get_Ik_Control_Euler()

                                            # TAG : Create new mesh
                                            budp.draw_Ui_Ur_Add_Pose(loc, rot, budpm)
                                            bod.data_Set_New_Motion_Elapsed_Time_On_Panel()
                                            bod.data_Draw_Pre_Loc_For_Cancel_Tracking = bod.data_Draw_plyAxis_Obj.location.x
                                        else:
                                            print("Please move slide bar")
                                            text_Name = "Move_slidebar_text"
                                            bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                                            bod.data_Set_Selected_Menu_Text_Location(text_Name)
                                            bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                                else:
                                    # NOTE : After confirming that the Pose data is full. [2]
                                    print("You can't add more point")
                            else:
                                # NOTE : current_Pose_Number가 Motion길이보다 크기 때문에 Motion revise를 수행할 수 없음을 나타내는 조건
                                if (bod.data_Draw_Check_Pose_Num_Max == 0):
                                    print("Please move slide bar")
                                    text_Name = "Move_slidebar_text"
                                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                                    bod.data_Set_Selected_Menu_Text_Location(text_Name)
                                    bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False

                        if (budp.draw_Pose_List_Count > 1):
                            if (bof.FLAG_DELETE_ONE_POSE == True and bod.data_Motion_Length < current_Pose_Number):
                                print("Move slide bar to delete pose")
                            else:
                                try:
                                    length = bod.data_Calculate_Length(current_Pose_Number - 1)
                                    print("Length of xyz : ", length)
                                    if (length > 3.0):
                                        if (bof.FLAG_ADD_OVER_LENGTH_ERROR == False):
                                            text_Name = 'Warning_text'
                                            bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                                            bod.data_Set_Selected_Menu_Text_Location(text_Name)
                                            bof.FLAG_ADD_ONE_POSE = False
                                            bof.FLAG_EDIT_ONE_POSE = False
                                            bof.FLAG_DELETE_ONE_POSE = False
                                            bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                                        else:
                                            bof.FLAG_ADD_OVER_LENGTH_ERROR = False
                                except:
                                    if (bod.data_Draw_Check_Pose_Num_Max == 0):
                                        print("move slide bar")
                                        text_Name = "Move_slidebar_text"
                                        bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                                        bod.data_Set_Selected_Menu_Text_Location(text_Name)
                                        bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                                    else:
                                        print("Delete or edit one pose")
                    else:
                        text_Name = "Select_edit_pose"
                        bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                        bod.data_Set_Selected_Menu_Text_Location(text_Name)
                        bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                        print("Select edit mode")
            ############################################################################################################



            ############################################################################################################
            # Information # ========================================================================================== #
            # NOTE : Motion revising is unavailable when there are more than one task.
            # NOTE : Motion revising is available when the Tracking mode is running or when Point cloud is not loaded.
            # ======================================================================================================== #
            # TAG : Edit mode
            if event.type == 'E' and event.value == 'PRESS':
                if (bod.bl_def_task.task_Length < 2):
                    if (bof.FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT == True or bof.FLAG_POINT_CLOUD_IS_LOADED == False):
                        pos_Length = bod.data_Motion_Length
                        current_Pose_Number = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
                        if (current_Pose_Number <= pos_Length):
                            text_Name = 'Editmode_text'
                            bod.data_Set_Selected_Menu_Text_Location(text_Name)
                            if (bof.FLAG_EDIT_ONE_POSE == False and pos_Length != 1):
                                if (bof.FLAG_PLYAXIS_ANCHOR_DROPPED == False):
                                    if (bod.data_Draw_Pre_Loc_For_Cancel_Tracking is not None):
                                        bod.data_Draw_plyAxis_Obj.location.x = bod.data_Draw_Pre_Loc_For_Cancel_Tracking
                                        bod.data_Draw_Curr_Ply_Axis_Loc = bod.data_Draw_plyAxis_Obj.location.x
                                    if (current_Pose_Number != 1):
                                        bod.date_Set_Cancel_Teach_Mode()
                                    ### Notice # ============================================================================= #
                                    ''' ───────────────────────────────────────────────────────────────────────────────────────┐
                                    │  When the 'E' button is pressed, measure the product position again with the information │
                                    │  between the pos currently pointed by the slider and the previous pos.                   │
                                    └─────────────────────────────────────────────────────────────────────────────────────── '''
                                    # ======================================================================================== #
                                    if (bod.data_Op_Speed_Or_Time == 0):
                                        point_Number = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
                                        curnum = point_Number - 1
                                        befnum = curnum - 1
                                        bod.data_Set_Revise_Product_Location_With_Teaching(curnum, befnum)
                                    else:
                                        point_Number = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
                                        curnum = point_Number - 1
                                        bod.data_Set_Revise_Product_Location_With_Teaching_Second(curnum)
                                    # ========================================================================================= #

                                bof.FLAG_EDIT_MODE = True
                                bof.FLAG_EDIT_ONE_POSE = True
                                bof.FLAG_ADD_ONE_POSE = False
                                bof.FLAG_DELETE_ONE_POSE = False
                                bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                                bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                            else:
                                if (bof.FLAG_POINT_CLOUD_IS_LOADED == True):
                                    if (bof.FLAG_PLYAXIS_ANCHOR_DROPPED == False and pos_Length != 1):
                                        bod.data_Set_Return_To_Original_State()

                                    bof.FLAG_EDIT_MODE = False
                                    bof.FLAG_EDIT_ONE_POSE = False
                                    bof.FLAG_ADD_ONE_POSE = False
                                    bof.FLAG_DELETE_ONE_POSE = False
                                    bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)


            # TAG : Add mode
            if event.type == 'Q' and event.value == 'PRESS':
                if (bod.bl_def_task.task_Length < 2):
                    if (bof.FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT == True or bof.FLAG_POINT_CLOUD_IS_LOADED == False):
                        pos_Length = bod.data_Motion_Length
                        current_Pose_Number = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
                        if (current_Pose_Number <= pos_Length):
                            text_Name = 'Addmode_text'
                            bod.data_Set_Selected_Menu_Text_Location(text_Name)
                            if (bof.FLAG_ADD_ONE_POSE == False):
                                if (bof.FLAG_PLYAXIS_ANCHOR_DROPPED == False):
                                    if (bod.data_Draw_Pre_Loc_For_Cancel_Tracking is not None):
                                        bod.data_Draw_plyAxis_Obj.location.x = bod.data_Draw_Pre_Loc_For_Cancel_Tracking
                                        bod.data_Draw_Curr_Ply_Axis_Loc = bod.data_Draw_plyAxis_Obj.location.x
                                    if (current_Pose_Number != 1):
                                        bod.date_Set_Cancel_Teach_Mode()
                                    ### Notice # ============================================================================= #
                                    ''' ───────────────────────────────────────────────────────────────────────────────────────┐
                                    │  When the 'Q' button is pressed, measure the product position again with the information │
                                    │  between the pos currently pointed by the slider and the previous pos.                   │
                                    └─────────────────────────────────────────────────────────────────────────────────────── '''
                                    # ======================================================================================== #
                                    if (bod.data_Op_Speed_Or_Time == 0):
                                        point_Number = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
                                        curnum = point_Number - 1
                                        befnum = curnum - 1
                                        bod.data_Set_Revise_Product_Location_With_Teaching(curnum, befnum)
                                    else:
                                        point_Number = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
                                        curnum = point_Number - 1
                                        bod.data_Set_Revise_Product_Location_With_Teaching_Second(curnum)
                                    # ======================================================================================== #

                                bof.FLAG_ADD_ONE_POSE = True
                                bof.FLAG_EDIT_ONE_POSE = False
                                bof.FLAG_DELETE_ONE_POSE = False
                                bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                                bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                            else:
                                if (bof.FLAG_POINT_CLOUD_IS_LOADED == True):
                                    if (bof.FLAG_PLYAXIS_ANCHOR_DROPPED == False):
                                        bod.data_Set_Return_To_Original_State()

                                    bof.FLAG_ADD_ONE_POSE = False
                                    bof.FLAG_EDIT_ONE_POSE = False
                                    bof.FLAG_DELETE_ONE_POSE = False
                                    bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)



            # TAG : Delete mode
            if event.type == 'W' and event.value == 'PRESS':
                if (bod.bl_def_task.task_Length < 2):
                    if (bof.FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT == True or bof.FLAG_POINT_CLOUD_IS_LOADED == False):
                        pos_Length = bod.data_Motion_Length
                        current_Pose_Number = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
                        if (current_Pose_Number <= pos_Length):
                            text_Name = 'Deletemode_text'
                            bod.data_Set_Selected_Menu_Text_Location(text_Name)
                            if (bof.FLAG_DELETE_ONE_POSE == False):
                                if (bof.FLAG_PLYAXIS_ANCHOR_DROPPED == False):
                                    if (bod.data_Draw_Pre_Loc_For_Cancel_Tracking is not None):
                                        bod.data_Draw_plyAxis_Obj.location.x = bod.data_Draw_Pre_Loc_For_Cancel_Tracking
                                        bod.data_Draw_Curr_Ply_Axis_Loc = bod.data_Draw_plyAxis_Obj.location.x
                                    if (current_Pose_Number != 1):
                                        bod.date_Set_Cancel_Teach_Mode()
                                    ### Notice # ============================================================================= #
                                    ''' ───────────────────────────────────────────────────────────────────────────────────────┐
                                    │  When the 'W' button is pressed, measure the product position again with the information │
                                    │  between the pos currently pointed by the slider and the previous pos.                   │
                                    └─────────────────────────────────────────────────────────────────────────────────────── '''
                                    # ======================================================================================== #
                                    if (bod.data_Op_Speed_Or_Time == 0):
                                        point_Number = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
                                        if (point_Number == 1):
                                            curnum = point_Number
                                            befnum = curnum - 1
                                            bod.data_Set_Revise_Product_Location_With_Teaching(curnum, befnum)
                                            bod.data_Draw_Ply_Axis_First_Loc = bod.data_Draw_Curr_Ply_Axis_Loc
                                        else:
                                            curnum = point_Number - 1
                                            befnum = curnum - 1
                                            bod.data_Set_Revise_Product_Location_With_Teaching(curnum, befnum)
                                    else:
                                        point_Number = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
                                        if (point_Number == 1):
                                            curnum = point_Number - 1
                                            bod.data_Set_Revise_Product_Location_With_Teaching_Second(curnum)
                                            bod.data_Draw_Ply_Axis_First_Loc = bod.data_Draw_Curr_Ply_Axis_Loc
                                        else:
                                            curnum = point_Number - 2
                                            bod.data_Set_Revise_Product_Location_With_Teaching_Second(curnum)
                                    # ======================================================================================== #

                                bof.FLAG_DELETE_ONE_POSE = True
                                bof.FLAG_EDIT_ONE_POSE = False
                                bof.FLAG_ADD_ONE_POSE = False
                                bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                                bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                            else:
                                if (bof.FLAG_POINT_CLOUD_IS_LOADED == True):
                                    if (bof.FLAG_PLYAXIS_ANCHOR_DROPPED == False):
                                        bod.data_Set_Return_To_Original_State()

                                    bof.FLAG_DELETE_ONE_POSE = False
                                    bof.FLAG_EDIT_ONE_POSE = False
                                    bof.FLAG_ADD_ONE_POSE = False
                                    bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
            ############################################################################################################



        ################################################################################################################
        ### Predict locaion of product =============================================================================== #
        ################################################################################################################
            # NOTE : Enable tracking mode
            # TAG : Product Tracking
            if event.type == 'S' and event.value == 'PRESS':
                if (bof.FLAG_POINT_CLOUD_IS_LOADED == True and bof.FLAG_PLYAXIS_ANCHOR_DROPPED == False and budp.draw_Pose_List_Count > 0):
                    pos_Length = bod.data_Motion_Length
                    current_Pose_Number = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
                    if (bof.FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT == False and current_Pose_Number <= pos_Length + 1):
                        bof.FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT = True

                        if (bof.FLAG_EDIT_ONE_POSE == False and bof.FLAG_ADD_ONE_POSE == False and bof.FLAG_DELETE_ONE_POSE == False ):
                            ### Notice # ========================================================================= #
                            ''' ─────────────────────────────────────────────────────────────────┐
                            │ The only case in which the first location of the ply can be saved. │
                            └───────────────────────────────────────────────────────────────── '''
                            if (budp.draw_Pose_List_Count == 1):
                                bod.data_Draw_Ply_Axis_First_Loc = bod.data_Draw_plyAxis_Obj.location.x
                                bod.data_Draw_Curr_Ply_Axis_Loc = bod.data_Draw_Ply_Axis_First_Loc
                            # ==================================================================================== #
                            text_Name = "plytracking_text"
                            bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                            bod.data_Draw_Pre_Loc_For_Cancel_Tracking = bod.data_Draw_plyAxis_Obj.location.x
                    elif (bof.FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT == False and current_Pose_Number > pos_Length + 1):
                        print("move slide bar")
                        text_Name = "Move_slidebar_text"
                        bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                        bod.data_Set_Selected_Menu_Text_Location(text_Name)
                        bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                    elif (bof.FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT == True):
                        if (budp.draw_Pose_List_Count == 1):
                            bod.data_Draw_plyAxis_Obj.location.x = bod.data_Draw_Ply_Axis_First_Loc
                        else:
                            if (bod.data_Draw_Pre_Loc_For_Cancel_Tracking is not None):
                                bod.data_Draw_plyAxis_Obj.location.x = bod.data_Draw_Pre_Loc_For_Cancel_Tracking
                                bod.data_Draw_Curr_Ply_Axis_Loc = bod.data_Draw_plyAxis_Obj.location.x
                        bof.FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT = False
                        text_Name = "plytracking_text"
                        bod.data_Set_Selected_Menu_Text_Location(text_Name)
                        bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
                        bof.FLAG_EDIT_MODE = False
                        bof.FLAG_EDIT_ONE_POSE = False
                        bof.FLAG_ADD_ONE_POSE = False
                        bof.FLAG_DELETE_ONE_POSE = False
                        bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False



            ############################################################################################################
            # Information ============================================================================================ #
            # NOTE : Check that the point number is increasing or decreasing (Infinite loop)
            ''' ────────────────────────────────────────────────────────────────────────────────────────────────────────
                Tracking mode = on일 때 Slidebar의 값이 변하는지 체크하는 메소드 (cur/befpos = Current/Before Pose)
                Slidebar 값이 이전보다 크다 : 현재 Pose(curnum) > 이전 Pose(befnum)
                Slidebar 값이 이전보다 작다 : 현재 Pose(curnum) < 이전 Pose(befnum)
                curpos, befpos 각각의 위치 데이터를 가져와 Pose 사이의 3차원 공간 상 거리를 측정하고 curpos의 속도 data를 가져와
                측정한 거리를 현재 Pose의 속도로 나누었을 때 나오는 duration을 Conveyor belt의 속도에 곱하여 로봇이 befpos에서
                curpos까지 이동하는 동안 움직인 Product의 예상 이동량(moved_Length)을 계산하여 plyAxis에 적용.
            ──────────────────────────────────────────────────────────────────────────────────────────────────────── '''
            # ======================================================================================================== #
            ### NOTE : Tracking mode can only be executed when the anchor is dropped.
            # TAG : Product Tracking
            if (bof.FLAG_PLYAXIS_ANCHOR_DROPPED == False):
                if (budp.draw_Pose_List_Count > 0):
                    point_Number = bod.data_Ui_Slidebar_Motion_Rate
                    if (bof.FLAG_RESTRICT_TRACKING_OFF == False):

                        # NOTE : The value of the slide bar is larger than before
                        if (point_Number > bod.data_Ui_Pre_Point_Number):
                            try:
                                bod.data_Draw_plyAxis_Obj.location.x = bod.data_Draw_Curr_Ply_Axis_Loc
                            except:
                                print("Reference error in bod.data_Draw_Curr_Ply_Axis_Loc")

                            ### NOTE : Exit tracking mode when moving the slidebar
                            bof.FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT = False
                            text_Name = "plytracking_text"
                            bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
                            ### NOTE : bod.data_Op_Speed_Or_Time = 0 >> Control with Speed / 1 >> Control with Time
                            if (bod.data_Op_Speed_Or_Time == 0):
                                try:
                                    curnum = int(point_Number / 5) - 1
                                    befnum = curnum - 1

                                    obj = bod.data_Motion_List
                                    robot_V = (obj[curnum].robot_Operate_Data_Velocity / 1000)
                                    befpos = bpy.data.objects['pos{}'.format(befnum)].location
                                    curpos = bpy.data.objects['pos{}'.format(curnum)].location
                                    length = bod.data_Calculate_Duration(befpos, curpos)
                                    duration = length / robot_V                                     # s (= m / m/s)
                                    moved_Length = (bod.data_Op_Conveyor_Velocity / 60) * duration  # 0.116m/s (7 M/min)
                                    if (bod.data_Info_Curr_Pc_Ip_Adress == bod.data_Info_Pc_One_Ip):
                                        bod.data_Draw_plyAxis_Obj.location.x -= moved_Length
                                    else:
                                        bod.data_Draw_plyAxis_Obj.location.x += moved_Length

                                    bpy.context.view_layer.update()
                                    bod.data_Draw_Curr_Ply_Axis_Loc = bod.data_Draw_plyAxis_Obj.location.x
                                except:
                                    pass
                            else:
                                try:
                                    curnum = int(point_Number / 5) - 1
                                    obj = bod.data_Motion_List
                                    robot_V = obj[curnum].robot_Operate_Data_Velocity
                                    duration = robot_V                                              # s
                                    moved_Length = (bod.data_Op_Conveyor_Velocity / 60) * duration  # 0.116m/s (7 M/min)
                                    if (bod.data_Info_Curr_Pc_Ip_Adress == bod.data_Info_Pc_One_Ip):
                                        bod.data_Draw_plyAxis_Obj.location.x -= moved_Length
                                    else:
                                        bod.data_Draw_plyAxis_Obj.location.x += moved_Length
                                    bpy.context.view_layer.update()
                                    bod.data_Draw_Curr_Ply_Axis_Loc = bod.data_Draw_plyAxis_Obj.location.x
                                except:
                                    pass

                        # NOTE : The value of the slide bar is smaller than before
                        elif (point_Number < bod.data_Ui_Pre_Point_Number and (budp.draw_Pose_List_Count * 5) > point_Number):
                            try:
                                bod.data_Draw_plyAxis_Obj.location.x = bod.data_Draw_Curr_Ply_Axis_Loc
                            except:
                                print("Reference error in bod.data_Draw_Curr_Ply_Axis_Loc")

                            ### NOTE : Exit tracking mode when moving the slidebar
                            bof.FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT = False
                            text_Name = "plytracking_text"
                            bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
                            ### NOTE : bod.data_Op_Speed_Or_Time = 0 >> Control with Speed / 1 >> Control with Time
                            if (bod.data_Op_Speed_Or_Time == 0):
                                try:
                                    curnum = int(point_Number / 5) - 1
                                    befnum = curnum + 1

                                    obj = bod.data_Motion_List
                                    robot_V = (obj[befnum].robot_Operate_Data_Velocity / 1000)
                                    befpos = bpy.data.objects['pos{}'.format(befnum)].location
                                    curpos = bpy.data.objects['pos{}'.format(curnum)].location
                                    length = bod.data_Calculate_Duration(befpos, curpos)
                                    duration = length / robot_V                                     # s (= m / m/s)
                                    moved_Length = (bod.data_Op_Conveyor_Velocity / 60) * duration  # 0.116m/s (7 M/min)
                                    if (bod.data_Info_Curr_Pc_Ip_Adress == bod.data_Info_Pc_One_Ip):
                                        bod.data_Draw_plyAxis_Obj.location.x -= moved_Length
                                    else:
                                        bod.data_Draw_plyAxis_Obj.location.x += moved_Length
                                    bpy.context.view_layer.update()
                                    bod.data_Draw_Curr_Ply_Axis_Loc = bod.data_Draw_plyAxis_Obj.location.x
                                except:
                                    pass
                            else:
                                try:
                                    curnum = int(point_Number / 5)
                                    obj = bod.data_Motion_List
                                    robot_V = obj[curnum].robot_Operate_Data_Velocity
                                    duration = robot_V                                              # s
                                    moved_Length = (bod.data_Op_Conveyor_Velocity / 60) * duration  # 0.116m/s (7 M/min)
                                    if (bod.data_Info_Curr_Pc_Ip_Adress == bod.data_Info_Pc_One_Ip):
                                        bod.data_Draw_plyAxis_Obj.location.x += moved_Length
                                    else:
                                        bod.data_Draw_plyAxis_Obj.location.x -= moved_Length
                                    bpy.context.view_layer.update()
                                    bod.data_Draw_Curr_Ply_Axis_Loc = bod.data_Draw_plyAxis_Obj.location.x
                                except:
                                    pass
                        else:
                            pass

                    bof.FLAG_RESTRICT_TRACKING_OFF = False
                    bod.data_Ui_Pre_Point_Number = point_Number
            ############################################################################################################




# ==================================================================================================================== #

            # NOTE : Anchored at the current location of "plyAxis"
            if event.type == 'P' and event.value == 'PRESS':
                if (bof.FLAG_POINT_CLOUD_IS_LOADED == True):
                    bof.FLAG_PLYAXIS_ANCHOR_DROPPED = True
                    text_Name = 'Anchor_text'
                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                    text_Name = 'Drop_anchor_text'
                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)
                    print(" > Ply anchor is dropped!")
                    bod.data_Draw_Anchored_Location = bod.data_Draw_plyAxis_Obj.location.x
                else:
                    print("Call ply first")

            if event.type == 'V' and event.value == 'PRESS':
                if (bof.FLAG_MODIFY_SPEED == False):
                    bof.FLAG_MODIFY_SPEED = True

                    bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                    bof.FLAG_EDIT_ONE_POSE = False
                    bof.FLAG_ADD_ONE_POSE = False
                    bof.FLAG_DELETE_ONE_POSE = False
                    bod.data_Set_Text_Appear_Or_Hide('Speed_text', 0)
                    bod.data_Set_Text_Appear_Or_Hide('Slidebar_text', 1)
                else:
                    bof.FLAG_MODIFY_SPEED = False
                    bod.data_Set_Text_Appear_Or_Hide('Speed_text', 1)

            # TAG : Slidebar
            # ======================================================================================================== #
            # NOTE : Enable slide bar control function
            # ======================================================================================================== #
            if event.type == 'T' and event.value == 'PRESS':
                text_Name = 'Slidebar_text'
                bod.data_Set_Selected_Menu_Text_Location(text_Name)
                if (bof.FLAG_CHANGE_SLIDEBAR_NUMBER == False):
                    bof.FLAG_CHANGE_SLIDEBAR_NUMBER = True
                    bof.FLAG_EDIT_ONE_POSE = False
                    bof.FLAG_ADD_ONE_POSE = False
                    bof.FLAG_DELETE_ONE_POSE = False
                    bof.FLAG_MODIFY_SPEED = False
                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                else:
                    bof.FLAG_CHANGE_SLIDEBAR_NUMBER = False
                    bof.FLAG_EDIT_ONE_POSE = False
                    bof.FLAG_ADD_ONE_POSE = False
                    bof.FLAG_DELETE_ONE_POSE = False
                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)

            if event.type == 'NUMPAD_PLUS':
                if event.value == 'PRESS':
                    if (bof.FLAG_CHANGE_SLIDEBAR_NUMBER == True):
                        if (bod.data_Ui_Slidebar_Motion_Rate < 150):
                            bod.data_Ui_Slidebar_Motion_Rate += 5
                            motion_Rate = (bod.data_Ui_Slidebar_Motion_Rate / 5)
                            budpm.slider_Bar.set_value(motion_Rate)
                    else:
                        if (bof.FLAG_MODIFY_SPEED == True):
                            bod.widgets_panel.func_Modify_Speed_Up()
                        else:
                            pass

            elif event.type == 'NUMPAD_MINUS':
                if event.value == 'PRESS':
                    if (bof.FLAG_CHANGE_SLIDEBAR_NUMBER == True):
                        if (bod.data_Ui_Slidebar_Motion_Rate > 5):
                            bod.data_Ui_Slidebar_Motion_Rate -= 5
                            motion_Rate = (bod.data_Ui_Slidebar_Motion_Rate / 5)
                            budpm.slider_Bar.set_value(motion_Rate)
                    else:
                        if (bof.FLAG_MODIFY_SPEED == True):
                            bod.widgets_panel.func_Modify_Speed_Down()
                        else:
                            pass
            ############################################################################################################

            # NOTE : Change the weight that moves "ik_control".
            if event.type == 'LEFT_CTRL' and event.value == 'PRESS':
                if (bof.FLAG_CHANGE_MOVEMENT_RATIO == False):
                    bof.FLAG_CHANGE_MOVEMENT_RATIO = True
                    self.mover.urManualControlMoveValue = 0.001
                    bod.data_Ui_Update_rate = 1 / 90
                else:
                    bof.FLAG_CHANGE_MOVEMENT_RATIO = False
                    self.mover.urManualControlMoveValue = 0.01
                    bod.data_Ui_Update_rate = 1 / 30

            # NOTE : Delete motions only
            if event.type == 'A' and event.value == 'PRESS':
                bof.FLAG_DELETE_MOTION_ONLY = True
                budp.draw_Del_Pose()
                bod.data_Reset_Pose()
                bod.data_Ui_Slidebar_Motion_Rate = 5
                budpm.slider_Bar.set_value(1)



            # ======================================================================================================== #
            # NOTE : Change location of plyaxis when point cloud is loaded.
            # ======================================================================================================== #
            if (bof.FLAG_POINT_CLOUD_IS_LOADED == True):
                if event.type == 'LEFT_BRACKET' and event.value == 'PRESS':
                    if (bof.FLAG_GET_CORE_PRODUCT_PLY == True):
                        bpy.data.objects['{}'.format(bod.data_Pc_Ply_Name)].location.x -= 0.01
                        bod.data_Draw_plyAxis_Obj.location.x -= 0.01
                    else:
                        bod.data_Draw_plyAxis_Obj.location.x -= 0.01

                if event.type == 'RIGHT_BRACKET' and event.value == 'PRESS':
                    if (bof.FLAG_GET_CORE_PRODUCT_PLY == True):
                        bpy.data.objects['{}'.format(bod.data_Pc_Ply_Name)].location.x += 0.01
                        bod.data_Draw_plyAxis_Obj.location.x += 0.01
                    else:
                        bod.data_Draw_plyAxis_Obj.location.x += 0.01

                if event.type == 'COMMA' and event.value == 'PRESS':
                    if (bof.FLAG_GET_CORE_PRODUCT_PLY == True):
                        bpy.data.objects['{}'.format(bod.data_Pc_Ply_Name)].location.x -= 0.064285714
                        bod.data_Draw_plyAxis_Obj.location.x -= 0.064285714
                    else:
                        bod.data_Draw_plyAxis_Obj.location.x -= 0.064285714
                        bod.data_Draw_Curr_Ply_Axis_Loc = bod.data_Draw_plyAxis_Obj.location.x

                if event.type == 'PERIOD' and event.value == 'PRESS':
                    if (bof.FLAG_GET_CORE_PRODUCT_PLY == True):
                        bpy.data.objects['{}'.format(bod.data_Pc_Ply_Name)].location.x += 0.064285714
                        bod.data_Draw_plyAxis_Obj.location.x += 0.064285714
                    else:
                        bod.data_Draw_plyAxis_Obj.location.x += 0.064285714
            ############################################################################################################



            # ======================================================================================================== #
            # NOTE : Change camera view
            # ======================================================================================================== #
            if event.type == 'NINE' and event.value == 'PRESS':
                idx = bod.data_Ui_Camera_Properties[event.type]
                bod.data_Ui_Camera_Direction = event.type
                bod.data_Set_Text_Information_According_To_Camera_Direction(bod.data_Ui_Current_Text_Name)
                bod.data_Set_Camera_Loc_Rot_Value(idx[0], idx[1], idx[2], idx[3], idx[4], idx[5])

            if event.type == 'ZERO' and event.value == 'PRESS':
                idx = bod.data_Ui_Camera_Properties[event.type]
                bod.data_Ui_Camera_Direction = event.type
                bod.data_Set_Text_Information_According_To_Camera_Direction(bod.data_Ui_Current_Text_Name)
                bod.data_Set_Camera_Loc_Rot_Value(idx[0], idx[1], idx[2], idx[3], idx[4], idx[5])

            if event.type == 'MINUS' and event.value == 'PRESS':
                idx = bod.data_Ui_Camera_Properties[event.type]
                bod.data_Ui_Camera_Direction = event.type
                bod.data_Set_Text_Information_According_To_Camera_Direction(bod.data_Ui_Current_Text_Name)
                bod.data_Set_Camera_Loc_Rot_Value(idx[0], idx[1], idx[2], idx[3], idx[4], idx[5])

            if event.type == 'EIGHT' and event.value == 'PRESS':
                idx = bod.data_Ui_Camera_Properties[event.type]
                bod.data_Ui_Camera_Direction = event.type
                bod.data_Set_Text_Information_According_To_Camera_Direction(bod.data_Ui_Current_Text_Name)
                bod.data_Set_Camera_Loc_Rot_Value(idx[0], idx[1], idx[2], idx[3], idx[4], idx[5])

            if event.type == 'SEVEN' and event.value == 'PRESS':
                idx = bod.data_Ui_Camera_Properties[event.type]
                bod.data_Ui_Camera_Direction = event.type
                bod.data_Set_Text_Information_According_To_Camera_Direction(bod.data_Ui_Current_Text_Name)
                bod.data_Set_Camera_Loc_Rot_Value(idx[0], idx[1], idx[2], idx[3], idx[4], idx[5])

            ############################################################################################################
            # Information # ========================================================================================== #
            ''' "Modify bbox information"메소드에서 Key event 'SIX'를 사용하고 있기 때문에 
                해당 메소드를 사용할 때는 6번 뷰를 사용할 수 없다. (검색 : FLAG_MODIFY_BBOX_INFORMATION)
            ┌──────────────────────────────────────────────────────────────────────┐
            │ View 6 is not available when using the "Modify bbox information"     │ 
            │ function, because this method uses key event 'SIX'.                  │
            └─────────────────────────────────────────────────────────────────── '''
            # ======================================================================================================== #
            if (bof.FLAG_MODIFY_BBOX_INFORMATION == False):
                if event.type == 'SIX' and event.value == 'PRESS':
                    idx = bod.data_Ui_Camera_Properties[event.type]
                    bod.data_Ui_Camera_Direction = event.type
                    bod.data_Set_Text_Information_According_To_Camera_Direction(bod.data_Ui_Current_Text_Name)
                    bod.data_Set_Camera_Loc_Rot_Value(idx[0], idx[1], idx[2], idx[3], idx[4], idx[5])
            ############################################################################################################
            # ======================================================================================================== #




            # ======================================================================================================== #
            # NOTE : Methods that support zoom-in, zoom-out.
            # ======================================================================================================== #
            if event.type == 'SLASH' and event.value == 'PRESS':
                if (bof.FLAG_ZOOM_CAMERA == False):
                    bof.FLAG_ZOOM_CAMERA = True
                    print("FLAG_ZOOM_CAMERA " , bof.FLAG_ZOOM_CAMERA)
                else:
                    bof.FLAG_ZOOM_CAMERA = False
                    print("FLAG_ZOOM_CAMERA ", bof.FLAG_ZOOM_CAMERA)

            if (bof.FLAG_ZOOM_CAMERA == True):
                if event.type == 'WHEELUPMOUSE':
                    self.zoom_Ratio += 1
                    camera_Ortho_Weight = -0.1
                    zoom_In_Weigth = 0
                    camera = bpy.data.cameras['Camera']
                    bod.data_Set_Camera_Zoom(event, camera, camera_Ortho_Weight, zoom_In_Weigth)

                if event.type == 'WHEELDOWNMOUSE':
                    if (self.zoom_Ratio == 0):
                        bod.data_Set_Camera_Location_With_Camera_Direction()
                    elif (self.zoom_Ratio > 0):
                        self.zoom_Ratio -= 1
                        camera_Ortho_Weight = 0.1
                        zoom_Out_Weigth = 1
                        camera = bpy.data.cameras['Camera']
                        bod.data_Set_Camera_Zoom(event, camera, camera_Ortho_Weight, zoom_Out_Weigth)
            ############################################################################################################


            # ====================================================================================== #
            # NOTE :  Code for initial setup of Point cloud when MAVIZ is applied in a new location.
            # ====================================================================================== #
            self.init_Setup_For_Point_Cloud(event, context)
            ##########################################################################################

        if event.type in self.command_for_key_type:
            action = self.action_for_key_state[event.value]
            action(self.command_for_key_type[event.type])




    def data_Set_Modify_Modeling_Environment(self, PC):
        vector = mathutils.Vector
        euler = mathutils.Euler
        if (PC == bod.data_Info_Pc_One_Ip):
            bod.data_Set_Camera_Loc_Rot_Value(0, -4, 0.73, 90, 0, 0)
            bpy.data.objects['Area1'].location = vector((-0.00021, 0.23972, 0.66520))
            bpy.data.objects['Area1'].scale = vector((0.450, 0.147, 0.676))
            bpy.data.objects['Area2'].location = vector((-0.00021, 0.86722, 0.6652))
            bpy.data.objects['Area2'].scale = vector((0.450, 0.48, 0.676))
            bod.data_Draw_plyAxis_Obj.location = vector((0.0007, -0.6223, 1.3521))
            bod.data_Draw_plyAxis_Obj.rotation_euler = euler((1.1903, 3.1451, 3.1312))
            bod.data_Draw_plyAxis_Obj.scale = vector((0.964, 0.964, 0.964))
            bpy.data.objects['pcedit_plyAxis'].location = bod.data_Draw_plyAxis_Obj.location
            bpy.data.objects['pcedit_plyAxis'].rotation_euler = bod.data_Draw_plyAxis_Obj.rotation_euler
            bpy.data.objects['pcedit_plyAxis'].scale = bod.data_Draw_plyAxis_Obj.scale
            bpy.data.objects['state_9'].location = vector((0.19, 0.094719, 0.665034))
            bpy.data.objects['state_10'].location = vector((0.14, 0.094719, 0.665034))
            bpy.data.objects['state_11'].location = vector((0.09, 0.094719, 0.665034))
            bpy.data.objects['state_Start_9'].location = vector((0.03, 0.094719, 0.665034))
            bpy.data.objects['state_Start_10'].location = vector((-0.02, 0.094719, 0.665034))
            bpy.data.objects['state_Start_11'].location = vector((-0.07, 0.094719, 0.665034))

            # bpy.data.objects['Region_0.4'].location = vector((0.00034, 0.4, 0.66706))
            # bpy.data.objects['Region_0.4'].scale = vector((0.89, 0.003, 1.340))
            # bpy.data.objects['Region_0.5'].location = vector((0.00034, 0.5, 0.66706))
            # bpy.data.objects['Region_0.5'].scale = vector((0.89, 0.003, 1.340))
            # bpy.data.objects['Region_0.6'].location = vector((0.00034, 0.6, 0.66706))
            # bpy.data.objects['Region_0.6'].scale = vector((0.89, 0.003, 1.340))
            # bpy.data.objects['Region_0.7'].location = vector((0.00034, 0.7, 0.66706))
            # bpy.data.objects['Region_0.7'].scale = vector((0.89, 0.003, 1.340))
            # bpy.data.objects['Region_0.8'].location = vector((0.00034, 0.8, 0.66706))
            # bpy.data.objects['Region_0.8'].scale = vector((0.89, 0.003, 1.340))
            # bpy.data.objects['Region_0.9'].location = vector((0.00034, 0.9, 0.66706))
            # bpy.data.objects['Region_0.9'].scale = vector((0.89, 0.003, 1.340))
        else:
            bod.data_Set_Camera_Loc_Rot_Value(0, -4, 0.73, 90, 0, 0)
            bpy.data.objects['Area1'].location = vector((0.0, 0.24386, 0.6652))
            bpy.data.objects['Area1'].scale = vector((0.495, 0.147, 0.676))
            bpy.data.objects['Area2'].location = vector((0.0, 0.87136, 0.6652))
            bpy.data.objects['Area2'].scale = vector((0.495, 0.48, 0.676))
            bod.data_Draw_plyAxis_Obj.location = vector((0.0307, -0.6023, 1.2421))
            bod.data_Draw_plyAxis_Obj.rotation_euler = euler((1.1903, 3.1451, 3.1939))
            bod.data_Draw_plyAxis_Obj.scale = vector((0.964, 0.964, 0.964))
            bpy.data.objects['pcedit_plyAxis'].location = bod.data_Draw_plyAxis_Obj.location
            bpy.data.objects['pcedit_plyAxis'].rotation_euler = bod.data_Draw_plyAxis_Obj.rotation_euler
            bpy.data.objects['pcedit_plyAxis'].scale = bod.data_Draw_plyAxis_Obj.scale
            bpy.data.objects['state_9'].location = vector((-0.18, 0.094719, 0.665034))
            bpy.data.objects['state_10'].location = vector((-0.13, 0.094719, 0.665034))
            bpy.data.objects['state_11'].location = vector((-0.08, 0.094719, 0.665034))
            bpy.data.objects['state_Start_9'].location = vector((-0.02, 0.094719, 0.665034))
            bpy.data.objects['state_Start_10'].location = vector((0.03, 0.094719, 0.665034))
            bpy.data.objects['state_Start_11'].location = vector((0.08, 0.094719, 0.665034))

            # bpy.data.objects['Region_0.4'].location = vector((-0.05188, 0.4, 0.66706))
            # bpy.data.objects['Region_0.4'].scale = vector((0.89, 0.003, 1.340))
            # bpy.data.objects['Region_0.5'].location = vector((-0.05188, 0.5, 0.66706))
            # bpy.data.objects['Region_0.5'].scale = vector((0.89, 0.003, 1.340))
            # bpy.data.objects['Region_0.6'].location = vector((-0.05188, 0.6, 0.66706))
            # bpy.data.objects['Region_0.6'].scale = vector((0.89, 0.003, 1.340))
            # bpy.data.objects['Region_0.7'].location = vector((-0.05188, 0.7, 0.66706))
            # bpy.data.objects['Region_0.7'].scale = vector((0.89, 0.003, 1.340))
            # bpy.data.objects['Region_0.8'].location = vector((-0.05188, 0.8, 0.66706))
            # bpy.data.objects['Region_0.8'].scale = vector((0.89, 0.003, 1.340))
            # bpy.data.objects['Region_0.9'].location = vector((-0.05188, 0.9, 0.66706))
            # bpy.data.objects['Region_0.9'].scale = vector((0.89, 0.003, 1.340))

            for ele in bod.core_Product:
                try:
                    bpy.data.objects['{}'.format(ele)].rotation_euler.z += math.pi
                except:
                    pass
                    # print("There is no modeling for this product. : ", ele)





    def init_Setup_For_Point_Cloud(self, event, context):
        # Information # ========================================================================================== #
        # NOTE : Modify clipping plane number
        # ======================================================================================================== #
        if event.type == 'M' and event.value == 'PRESS':
            if (bof.FLAG_MODIFY_BBOX_INFORMATION == False):
                bof.FLAG_MODIFY_BBOX_INFORMATION = True
            else:
                bof.FLAG_MODIFY_BBOX_INFORMATION = False
            print("Enable to modify clipping plane number : ", bof.FLAG_MODIFY_BBOX_INFORMATION)

        if (bof.FLAG_MODIFY_BBOX_INFORMATION == True):
            if (bod.data_Info_Curr_Pc_Ip_Adress == bod.data_Info_Pc_One_Ip):
                # NOTE : PC 1
                pc_Num = 0
            else:
                # NOTE : PC 2
                pc_Num = 1
            if event.type == 'NUMPAD_PLUS' and event.value == 'PRESS':
                clipping_Weight = bod.data_Draw_Restrict_Value[pc_Num][bod.data_Draw_Clipping_Plane_Number]
                bod.data_Draw_Restrict_Value[pc_Num][bod.data_Draw_Clipping_Plane_Number] = round(clipping_Weight + 0.1, 2)
                print("value : ", bod.data_Draw_Restrict_Value[pc_Num])

            if event.type == 'NUMPAD_MINUS' and event.value == 'PRESS':
                clipping_Weight = bod.data_Draw_Restrict_Value[pc_Num][bod.data_Draw_Clipping_Plane_Number]
                bod.data_Draw_Restrict_Value[pc_Num][bod.data_Draw_Clipping_Plane_Number] = round(clipping_Weight - 0.1, 2)
                print("value : ", bod.data_Draw_Restrict_Value[pc_Num])

            ############################################################################################################
            # Information # ========================================================================================== #
            ''' ──────────────────────────────────────────────────────────────────────────────────────────────────────
                "Clipping plane local axis"
                 >> 해당 축 방향으로 clipping_Weight가 커지면 Point cloud를 현시하는 경계선이 (0, 0, 0)에서 멀어진다
                    = 더 많은 범위에 대해 Point cloud를 현시한다.
                    
                        (plus z)
                            Z    (plus y)
                            ↑      Y
                            │    ↗
                            │  /
                (minus x)   │/_______→ X (plus x)
                
                    (minus y)
                
                        (minus z)
            ────────────────────────────────────────────────────────────────────────────────────────────────────── '''
            # ======================================================================================================== #
            if event.type == 'ONE' and event.value == 'PRESS':
                # NOTE : plus y
                bod.data_Draw_Clipping_Plane_Number = 0

            if event.type == 'TWO' and event.value == 'PRESS':
                # NOTE : minus y
                bod.data_Draw_Clipping_Plane_Number = 1

            if event.type == 'THREE' and event.value == 'PRESS':
                # NOTE : minus z
                bod.data_Draw_Clipping_Plane_Number = 2

            if event.type == 'FOUR' and event.value == 'PRESS':
                # NOTE : plus z
                bod.data_Draw_Clipping_Plane_Number = 3

            if event.type == 'FIVE' and event.value == 'PRESS':
                # NOTE : minus x
                bod.data_Draw_Clipping_Plane_Number = 4

            if event.type == 'SIX' and event.value == 'PRESS':
                # NOTE : plus x
                bod.data_Draw_Clipping_Plane_Number = 5
            ############################################################################################################
        # ======================================================================================================== #

        # Information # ========================================================================================== #
        # NOTE : plyAxis Control
        # ======================================================================================================== #
        if event.type == 'N' and event.value == 'PRESS':
            if (bof.FLAG_MODIFY_PLYAXIS_INFORMATION == False):
                bof.FLAG_MODIFY_PLYAXIS_INFORMATION = True
            else:
                bof.FLAG_MODIFY_PLYAXIS_INFORMATION = False
            print("Enable to modify {} infromation : ".format(bod.data_Draw_plyAxis_Obj.name), bof.FLAG_MODIFY_PLYAXIS_INFORMATION)

        if (bof.FLAG_MODIFY_PLYAXIS_INFORMATION == True):
            if event.type == 'DEL' and event.value == 'PRESS':
                bod.data_Draw_plyAxis_Obj.location.x -= self.length

            if event.type == 'PAGE_DOWN' and event.value == 'PRESS':
                bod.data_Draw_plyAxis_Obj.location.x += self.length

            if event.type == 'INSERT' and event.value == 'PRESS':
                bod.data_Draw_plyAxis_Obj.location.y += self.length

            if event.type == 'PAGE_UP' and event.value == 'PRESS':
                bod.data_Draw_plyAxis_Obj.location.y -= self.length

            if event.type == 'HOME' and event.value == 'PRESS':
                bod.data_Draw_plyAxis_Obj.location.z += self.length

            if event.type == 'END' and event.value == 'PRESS':
                bod.data_Draw_plyAxis_Obj.location.z -= self.length

            if event.type == 'X' and event.value == 'PRESS':
                self.point_Cloud_Edit = 0
                print("Rotating by X-axis")

            if event.type == 'Y' and event.value == 'PRESS':
                self.point_Cloud_Edit = 1
                print("Rotating by Y-axis")

            if event.type == 'Z' and event.value == 'PRESS':
                self.point_Cloud_Edit = 2
                print("Rotating by Z-axis")

            if event.type == 'S' and event.value == 'PRESS':
                self.point_Cloud_Edit = 3
                print("Modify scale")

            if event.type == 'NUMPAD_PLUS' and event.value == 'PRESS':
                if (self.point_Cloud_Edit == 0):
                    bod.data_Draw_plyAxis_Obj.rotation_euler.x += self.euler
                elif (self.point_Cloud_Edit == 1):
                    bod.data_Draw_plyAxis_Obj.rotation_euler.y += self.euler
                elif (self.point_Cloud_Edit == 2):
                    bod.data_Draw_plyAxis_Obj.rotation_euler.z += self.euler
                elif (self.point_Cloud_Edit == 3):
                    bod.data_Draw_plyAxis_Obj.scale[0] += self.length
                    bod.data_Draw_plyAxis_Obj.scale[1] += self.length
                    bod.data_Draw_plyAxis_Obj.scale[2] += self.length

            if event.type == 'NUMPAD_MINUS' and event.value == 'PRESS':
                if (self.point_Cloud_Edit == 0):
                    bod.data_Draw_plyAxis_Obj.rotation_euler.x -= self.euler
                elif (self.point_Cloud_Edit == 1):
                    bod.data_Draw_plyAxis_Obj.rotation_euler.y -= self.euler
                elif (self.point_Cloud_Edit == 2):
                    bod.data_Draw_plyAxis_Obj.rotation_euler.z -= self.euler
                elif (self.point_Cloud_Edit == 3):
                    bod.data_Draw_plyAxis_Obj.scale[0] -= self.length
                    bod.data_Draw_plyAxis_Obj.scale[1] -= self.length
                    bod.data_Draw_plyAxis_Obj.scale[2] -= self.length

            if event.type == 'NUMPAD_ASTERIX' and event.value == 'PRESS':
                empty_loc_rot = self.data_Get_Ply_Axis_loc_rot()
                print("Information of {}\n".format(bod.data_Draw_plyAxis_Obj.name))
                print("loc : ", empty_loc_rot[0], empty_loc_rot[1], empty_loc_rot[2])
                print("rot : ", empty_loc_rot[3], empty_loc_rot[4], empty_loc_rot[5])
                print("scl : ", empty_loc_rot[6], empty_loc_rot[7], empty_loc_rot[8])
                print(" ")

    def data_Get_Ply_Axis_loc_rot(self):
        obj = bod.data_Draw_plyAxis_Obj
        lx = round(obj.location.x, 4)
        ly = round(obj.location.y, 4)
        lz = round(obj.location.z, 4)
        rx = round(obj.rotation_euler.x, 4)
        ry = round(obj.rotation_euler.y, 4)
        rz = round(obj.rotation_euler.z, 4)
        sx = round(obj.scale[0], 4)
        sy = round(obj.scale[1], 4)
        sz = round(obj.scale[2], 4)
        return [lx, ly, lz, rx, ry, rz, sx, sy, sz]
    ####################################################################################################################