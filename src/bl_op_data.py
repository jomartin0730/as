import bpy
import os
import math
import queue
import datetime
import random
import gzip
import mathutils
import numpy as np
from bl_def_pose import *
from bl_op_flag import Bl_Op_Flag as bof

class Bl_Op_Data():
    data_Info_Robot_Model = "kawasaki" # Doosan # UR5
    data_Info_Curr_Pc_Ip_Adress = ""
    data_Info_Pc_One_Ip = "192.168.0.101"
    data_Info_Gun_Length = 0.305 # m

    data_Motion_List = []
    data_Current_Loaded_Motion_List = []
    data_Motion_Length = 0
    data_Current_Loaded_Motion_length = 0

    data_Op_Robot_Speed = 0.4
    data_Op_Robot_Accel = 40
    data_Op_Converted_Robot_Speed = 0

    # NOTE : 0 >> Speed, 1 >> Time
    data_Op_Speed_Or_Time = 1

    # NOTE : J >> Jmove, L >> Lmove
    data_Op_Moving_State = 'J'
    data_Op_Conveyor_Velocity = 7.0

    data_Ui_Slidebar_Motion_Rate = 5
    data_Ui_Update_rate = 1 / 30
    data_Ui_Pre_Point_Number = 5
    data_Ui_Window_Width = 0
    data_Ui_Window_Height = 0
    data_Ui_X_Ratio = 0
    data_Ui_Y_Ratio = 0
    data_Ui_Motion_Elapsed_Time = []
    # data_Ui_Pose_Elapsed_Time = 0
    data_Ui_Panel_Widget_List = []
    data_Ui_Panel_Namespace = {}
    data_Ui_Activated_Panel_Map = {}
    data_Ui_Modifying_Panel_Information = []
    data_Ui_Panel_button_Event_Distributor = []
    data_Ui_Pre_Process = False
    data_Ui_Camera_Direction = "NINE"
    data_Ui_Camera_Properties = {}
    data_Ui_Text_Properties = {}
    data_Ui_Ik_Location_Control = []
    data_Ui_Ik_Rotation_Control = []
    data_Ui_Current_Text_Name = ""
    data_Ui_Current_Loaded_Data = ""
    data_Ui_Instance_Panel = []
    data_Ui_Curr_Loaded_Data_For_modify = "" # 210816 data_Ui_Current_Loaded_Data랑 합쳐도 되는지 확인 Deer del
    data_Ui_Font = "NanumBarunGothicBold.ttf"  # CALIFB.TTF, ARIALNB.TTF
    data_Ui_Font_Path = None
    data_Ui_Image_Data_Path = None
    data_Ui_Motion_Data_Path = None
    data_Ui_Point_Cloud_Data_Path = None
    data_Ui_Panel_Image_Path = None

    # NOTE : 현재 Pose와 이전 Pose의 Joint angle간 차이를 이용하여 경로를 그리기 위해 이전 Pose의 Joint angle을 저장
    data_Draw_Previous_Robot_Pose_list = [] # ──────────────────────────────────────────────────────────┘
    data_Draw_Path_Point_List = []
    data_Draw_Path_Point_Mesh_Number = 0
    data_Draw_Received_Joint_To_Modeled_Robot = []

    # Information # ======================================================= #
    ''' ─────────────────────────────────────────────────────────────────── 
    모션 자동생성시 nsg에 처음 인식되는 위치에 Anchor(key event 'P')를 설치하고 
    원하는 위치에서 티칭을 하는데 이 때, plyAxis의 위치와 Anchor간의 거리 차이가 있어 
    nsg가 인식해도 모션의 sync가 맞지 않기 때문에 모든 Pose의 위치를 
    Anchor - plyAxis만큼 보정하기 위해 해당 값을 저장해놓는 변수
    ─────────────────────────────────────────────────────────────────── '''
    data_Draw_Atmp_Length = 0 # Atmp = Anchor To Moved Pose
    # ===================================================================== #
    data_Draw_Revised_Point_Number = 0
    data_Draw_Curr_Revising_Point_Number = 0

    # NOTE : 모션을 수정(edit, add, delete)하거나 Tracking mode 조작 시 첫 번째 위치를 기억하는 변수
    data_Draw_Ply_Axis_First_Loc = bpy.data.objects['plyAxis'].location.x # ──────────────┘
    data_Draw_Curr_Ply_Axis_Loc = bpy.data.objects['plyAxis'].location.x
    data_Draw_Anchored_Location = None

    # 0 >> Get ik joint angle data from Armature_ik ──────┐
    # 1 >> Get ik joint angle data from Armature_Clone_ik │
    data_Draw_Select_Robot_Getting_Joint = 0 # ───────────┘
    data_Draw_plyAxis_Obj = bpy.data.objects['plyAxis']
    data_Draw_Current_Pose_Mesh_Number = 1
    data_Draw_IK_Control_Tracker = ''
    data_Draw_Modified_Pose_Data = []
    data_Draw_Curr_Ikcontrol_Loc = []
    data_Draw_Curr_Ikcontrol_Rot = None
    data_Draw_Repeat_Count = 0
    data_Draw_Pose_Count = 0
    data_Draw_Path_Dividing_Number = 4
    data_Draw_Check_Pose_Num_Max = 0
    data_Draw_Pre_Location = None
    data_Draw_Pre_Loc_For_Cancel_Tracking = None
    # data_Draw_Curr_Revising_Pose_Num = 0 >> budpm.slidebar_Fursys_Value_Changer에서 해당 변수 사용 시 주석해제

    data_Draw_Simul_Product_Convey_Length = 0
    data_Draw_Simul_Ply_Axis_First_Loc = None

    # NOTE : # Keyframe이 삽입된 Pose의 개수를 Count
    data_Draw_Simul_Count_Set_Anim_Keyframe = 0
    data_Draw_Simul_Last_Frame_Number = 0

    data_Pc_Point_Cloud_Name = " "
    data_Pc_Ply_Name = ""
    data_Pc_Ply_Path = " "
    data_Pc_Camera_Type = ""
    data_Pc_Show_Specific_Point_Cloud = True
    data_Pc_Removing_Indexes = []
    data_Pc_Point_Cloud_Data = None

    # Information # ========================================================= #
    ''' ────────────────────────────────────────────────────────────────────── 
    color ndarray >> 화면에 현시 할 땐 각 원소를 255로 나누어(rgb) dtype = float32로 
    이용하지만 Point cloud 편집 후 저장할 땐 int형태로 해야 하기 때문에 dtype = int8인 
    color ndarray를 추가적으로 저장
    ────────────────────────────────────────────────────────────────────── '''
    # TAG : Auto create motion
    data_Pc_Point_Cloud_Color_Int_Data = None
    # ======================================================================= #

    data_Tcp_Clinet_List = {}

    # NOTE : bl_server 통신 관련 코드
    combined_Joint_Angle_Data = []
    motion_Row_Number = 0
    product_Name = []
    old_Process_Value = 0
    old_Product_Name = ""
    scheduler = []

    # TAG : Class instance
    bl_op_server = None
    bl_op_sql = None
    bl_op_cam = None
    bl_op_robot = None
    bl_data_robot = None
    bl_def_task = None
    instance_Panel = None
    widgets_panel = None

    data_Ui_Blender_Text = bpy.data.collections['text'].objects.keys()
    data_Ui_Ik_Robot_Elements = bpy.data.collections['{}(ik_mesh)'.format(data_Info_Robot_Model)].objects.keys()
    core_Product = bpy.data.collections['Core_product'].objects.keys()

    # NOTE : 210812 Point cloud 개발되면 삭제예정
    data_Draw_Restrict_Value = [[2.0, -0.93, -0.04, 3.6, 0.9, 0.55], [2.1, -1.11, 0.78, 0.8, 0.74, 0.59]]
    data_Draw_Clipping_Plane_Number = 0
    data_Pc_Point_Cloud_Edge_Restrict_Value = {}

    # ============================================ #
    # NOTE : List of tag
    # ============================================ #
    # TAG : Motion load
    # TAG : Motion save
    # TAG : Auto create motion
    # TAG : Slidebar
    # TAG : Motion simulation
    # TAG : Call point cloud
    # TAG : Call core product
    # TAG : Point cloud streaming
    # TAG : Capture point cloud
    # TAG : Trim point cloud
    # TAG : Save trimmed point cloud
    # TAG : Delete point cloud
    # TAG : Panel context update
    # TAG : Draw point path
    # TAG : Create new mesh
    # TAG : Edit mode
    # TAG : Add mode
    # TAG : Delete mode
    # TAG : Product Tracking
    # TAG : Convert speed
    # TAG : Modify all pose
    # TAG : Add panel image
    # TAG : Intel L515
    # TAG : Intel D435
    # TAG : Class instance
    # TAG : Funtions for Main Panel
    # TAG : Funtions for Point Cloud Editing Panel
    # TAG : Funtions for Point Cloud Streaming Panel
    # TAG : Funtions for Robot control panel menu
    # TAG : Funtions for Modify all pose panel menu
    # TAG : Funtions for saving panel menu
    # ============================================ #



########################################################################################################################
    # TAG : Motion save
    def data_Get_Combined_Motion_Data():
        objects = Bl_Op_Data.data_Get_Motion_List()

        res_Ik = Bl_Op_Data.data_Convert_Saving_Protocol(objects, 0)
        res_Fk = Bl_Op_Data.data_Convert_Saving_Protocol(objects, 1)
        motion_Data_Pack = [res_Ik, res_Fk]

        return motion_Data_Pack

    # TAG : Motion save
    def data_Convert_Saving_Protocol(objects, cmd):
        saving_Data = []
        for ele in objects:
            data = ele.combine_Data_Of_Object(cmd)
            saving_Data.append(data)

        return saving_Data

    # TAG : Motion load
    def data_Recombine_Loaded_Pose(data):
        ik_List = data[0]
        fk_List = data[1]
        cnt = 0
        length = len(fk_List)
        while (cnt < length):
            num = cnt + 1
            pose_Number = num
            curr_Data = fk_List[cnt]
            ik_Element = ik_List[cnt]
            fk_Element = curr_Data
            control_Speed = curr_Data[0]
            moving_State = curr_Data[1]
            ik_Data = [ik_Element[2], ik_Element[3], ik_Element[4], ik_Element[5], ik_Element[6], ik_Element[7]]
            fk_Data = [fk_Element[2], fk_Element[3], fk_Element[4], fk_Element[5], fk_Element[6], fk_Element[7]]
            velo = curr_Data[8]
            c_Velo = curr_Data[9]
            accel = curr_Data[10]
            radius = curr_Data[11]
            gripper = curr_Data[12]
            Bl_Op_Data.data_Ui_Motion_Elapsed_Time.append(velo)
            cnt += 1

            Bl_Op_Data.data_Set_Loaded_Object(pose_Number, control_Speed, moving_State, ik_Data, fk_Data, velo, c_Velo,
                                              accel, radius, gripper)

    # TAG : Motion load
    def date_Set_Curr_Motion_As_Map():
        Task = {}
        Task[Bl_Op_Data.data_Ui_Current_Loaded_Data] = Bl_Op_Data.data_Current_Loaded_Motion_List

        return Task

    ### Initiate pose object data # ================================================================================== #
    def data_Set_Mesh_Object(poseobj):
        curr_Pose = Bl_Def_Pose()
        curr_Pose.pose_Number = Bl_Op_Data.data_Get_Motion_List_Length()
        curr_Pose.robot_Operate_Data_Control_Speed = Bl_Op_Data.data_Op_Speed_Or_Time
        curr_Pose.robot_Operate_Data_Moving_State = Bl_Op_Data.data_Get_Way_To_Robot_Move()
        curr_Pose.mesh_Data = poseobj
        curr_Pose.ik_Pose_Data = Bl_Op_Data.data_Get_Ik_Data(poseobj)
        curr_Pose.fk_Pose_Data = Bl_Op_Data.data_Get_Joint_Angle_List()
        curr_Pose.robot_Operate_Data_Velocity = Bl_Op_Data.data_Op_Robot_Speed
        curr_Pose.robot_Operate_Data_Converted_Velocity = Bl_Op_Data.data_Op_Converted_Robot_Speed
        curr_Pose.robot_Operate_Data_Acceleration = Bl_Op_Data.data_Op_Robot_Accel
        curr_Pose.robot_Operate_Data_Radius = 0
        curr_Pose.robot_Operate_Data_Gripper = 0

        Bl_Op_Data.data_Motion_List.append(curr_Pose)
        Bl_Op_Data.data_Motion_Length = len(Bl_Op_Data.data_Motion_List)

    def data_Set_Loaded_Object(pose_Number, control_Speed, moving_State, ik_Data, fk_Data, velo, c_Velo,
                               accel, radius, gripper):
        curr_Pose = Bl_Def_Pose()
        curr_Pose.pose_Number = pose_Number
        curr_Pose.robot_Operate_Data_Control_Speed = control_Speed
        curr_Pose.robot_Operate_Data_Moving_State = moving_State
        curr_Pose.ik_Pose_Data = ik_Data
        curr_Pose.fk_Pose_Data = fk_Data
        curr_Pose.robot_Operate_Data_Velocity = velo
        curr_Pose.robot_Operate_Data_Converted_Velocity = c_Velo
        curr_Pose.robot_Operate_Data_Acceleration = accel
        curr_Pose.robot_Operate_Data_Radius = radius
        curr_Pose.robot_Operate_Data_Gripper = gripper

        Bl_Op_Data.data_Op_Speed_Or_Time = control_Speed
        if (pose_Number == 1):
            if (moving_State == 0):
                Bl_Op_Data.data_Op_Moving_State = 'J'
                bof.FLAG_SELECT_LMOVE = False
            else:
                Bl_Op_Data.data_Op_Moving_State = 'L'
                bof.FLAG_SELECT_LMOVE = True

        # TAG : Panel context update
        bof.FLAG_PANEL_CONTEXT_UPDATE = True

        Bl_Op_Data.data_Motion_List.append(curr_Pose)
        Bl_Op_Data.data_Current_Loaded_Motion_List.append(curr_Pose)
        Bl_Op_Data.data_Motion_Length = len(Bl_Op_Data.data_Motion_List)
        Bl_Op_Data.data_Current_Loaded_Motion_length = len(Bl_Op_Data.data_Current_Loaded_Motion_List)

    def data_Set_Edited_Mesh_Object(poseobj, pose, num):
        curr_Pose = pose
        curr_Pose.pose_Number = num
        curr_Pose.robot_Operate_Data_Control_Speed = Bl_Op_Data.data_Op_Speed_Or_Time
        curr_Pose.robot_Operate_Data_Moving_State = Bl_Op_Data.data_Get_Way_To_Robot_Move()
        curr_Pose.mesh_Data = poseobj
        curr_Pose.ik_Pose_Data = Bl_Op_Data.data_Get_Ik_Data(poseobj)
        curr_Pose.fk_Pose_Data = Bl_Op_Data.data_Get_Joint_Angle_List()
        curr_Pose.robot_Operate_Data_Velocity = Bl_Op_Data.data_Op_Robot_Speed
        curr_Pose.robot_Operate_Data_Converted_Velocity = Bl_Op_Data.data_Op_Converted_Robot_Speed
        curr_Pose.robot_Operate_Data_Acceleration = Bl_Op_Data.data_Op_Robot_Accel
        curr_Pose.robot_Operate_Data_Radius = 0
        curr_Pose.robot_Operate_Data_Gripper = 0

    def data_Set_Added_Mesh_Object(poseobj, num):
        curr_Pose = Bl_Def_Pose()
        curr_Pose.pose_Number = num
        curr_Pose.robot_Operate_Data_Control_Speed = Bl_Op_Data.data_Op_Speed_Or_Time
        curr_Pose.robot_Operate_Data_Moving_State = Bl_Op_Data.data_Get_Way_To_Robot_Move()
        curr_Pose.mesh_Data = poseobj
        curr_Pose.ik_Pose_Data = Bl_Op_Data.data_Get_Ik_Data(poseobj)
        curr_Pose.fk_Pose_Data = Bl_Op_Data.data_Get_Joint_Angle_List()
        curr_Pose.robot_Operate_Data_Velocity = Bl_Op_Data.data_Op_Robot_Speed
        curr_Pose.robot_Operate_Data_Converted_Velocity = Bl_Op_Data.data_Op_Converted_Robot_Speed
        curr_Pose.robot_Operate_Data_Acceleration = Bl_Op_Data.data_Op_Robot_Accel
        curr_Pose.robot_Operate_Data_Radius = 0
        curr_Pose.robot_Operate_Data_Gripper = 0

        Bl_Op_Data.data_Motion_List.insert(num, curr_Pose)
        Bl_Op_Data.data_Motion_Length = len(Bl_Op_Data.data_Motion_List)
    # ================================================================================================================ #

    ### Delete pose object data # ==================================================================================== #
    def data_Reset_Pose():
        Bl_Op_Data.delete_Instance()
        Bl_Op_Data.data_Motion_List = []
        Bl_Op_Data.data_Current_Loaded_Motion_List = []
        Bl_Op_Data.data_Draw_Pose_Count = 0
        Bl_Op_Data.data_Motion_Length = 0
        Bl_Op_Data.data_Current_Loaded_Motion_length = 0
        Bl_Op_Data.bl_def_task.scheduled_Task.queue.clear()
        Bl_Op_Data.bl_def_task.task_Length = Bl_Op_Data.bl_def_task.task_Queue_Size()

    def delete_Instance():
        cnt = 0
        length = Bl_Op_Data.data_Motion_Length
        while (cnt < length):
            del Bl_Op_Data.data_Motion_List[0]
            cnt += 1

        Bl_Op_Data.data_Motion_Length = 0
    # ================================================================================================================ #

    # =================================================== #
    # NOTE : Get objects that is composed of motion list.
    # =================================================== #
    def data_Get_Motion_List():
        data_Motion_List = Bl_Op_Data.data_Motion_List.copy()
        Bl_Op_Data.delete_Instance()
        Bl_Op_Data.data_Motion_List = []
        return data_Motion_List
    # =================================================== #

    def data_Get_Motion_List_Length():
        length = len(Bl_Op_Data.data_Motion_List) + 1
        return length

    # Replace existing pose # ======================================================================================== #
    # NOTE : 모션 자동생성 기능 이용 시 ik_Pose_Data 수정을 위한 함수
    # TAG : Auto create motion
    def data_Set_Replace_With_Automatically_Created_Pose(pose, cur_loc, cur_rot):
        pose.ik_Pose_Data = [cur_loc.x, cur_loc.y, cur_loc.z, cur_rot.x, cur_rot.y, cur_rot.z]
    # ================================================================================================================ #

### Data set # ======================================================================================================= #
    def data_Set_Ui_Slidebar_Motion_Rate(value):
        Bl_Op_Data.data_Ui_Slidebar_Motion_Rate = value

    def data_Set_Ikcontrol_Home_Location():
        object = bpy.data.objects['ik_control']
        loc = mathutils.Vector((-0.01177, 0.1, 0.81792))
        rot = mathutils.Euler((math.radians(-90), math.radians(0), math.radians(0)))
        object.location = loc
        object.rotation_euler = rot

        return list(object.location)

    def data_Set_Ikcontrol_Loc_Rot_Value(loc, rot):
        object = bpy.data.objects['ik_control']
        loc = mathutils.Vector((loc.x, loc.y, loc.z))
        rot = mathutils.Euler((rot.x, rot.y, rot.z))
        object.location = loc
        object.rotation_euler = rot

    def data_Set_Core_Product_Home_Position():
        loc = mathutils.Vector((15, -14, 1.43256))
        bpy.data.objects['{}'.format(Bl_Op_Data.data_Pc_Ply_Name)].location = loc

    def data_Set_Ikcontrol_Ghost_Vector_Euler_Value(loc, rot):
        object = bpy.data.objects['ik_control_Ghost']
        object.location = loc
        object.rotation_euler = rot

    def data_Set_Pc_Editing_Object_Location(obj, loc):
        obj.location.x += loc.x
        obj.location.y += loc.y
        obj.location.z += loc.z

    def data_Set_Pc_Editing_Object_Rotation(obj, rot):
        obj.rotation_euler.x += rot.x
        obj.rotation_euler.y += rot.y
        obj.rotation_euler.z += rot.z

    def data_Set_Pc_Editing_Object_Scale(obj, scale):
        obj.scale.x += scale.x
        obj.scale.y += scale.y
        obj.scale.z += scale.z

    # ================================================================================== #
    # NOTE : Change the position of the camera towards the position of the mouse cursor.
    # ================================================================================== #
    def data_Set_modify_Camera_Location_In_Cursor_Direction(loc, cmd):
        obj = bpy.data.objects['Camera']
        if (cmd == 0):
            obj.location.x += loc.x
            obj.location.y += loc.y
            obj.location.z += loc.z
        else:
            obj.location.x -= loc.x
            obj.location.y -= loc.y
            obj.location.z -= loc.z
    ######################################################################################

    # NOTE : The rotational value used as a parameter is "degrees".
    def data_Set_Text_Loc_Rot_Value(name, loc_x, loc_y, loc_z, rot_x, rot_y, rot_z):
        asrad = math.radians
        loc = mathutils.Vector((loc_x, loc_y, loc_z))
        eul = mathutils.Euler((asrad(rot_x), asrad(rot_y), asrad(rot_z)))
        object = bpy.data.objects['{}'.format(name)]
        object.location = loc
        object.rotation_euler = eul

    # NOTE : The rotational value used as a parameter is "degrees".
    def data_Set_Camera_Loc_Rot_Value(loc_x, loc_y, loc_z, rot_x, rot_y, rot_z):
        asrad = math.radians
        loc = mathutils.Vector((loc_x, loc_y, loc_z))
        eul = mathutils.Euler((asrad(rot_x), asrad(rot_y), asrad(rot_z)))
        object = bpy.data.objects['Camera']
        object.location = loc
        object.rotation_euler = eul

    # NOTE : cmd = 0 >> appear, cmd = 1 >> disappear
    def data_Set_Bbox_Appear_Or_Hide(cmd):
        vec = mathutils.Vector
        obj = bpy.data.objects['bbox']
        if (cmd):
            loc = (15.0, -14.0, 0.22)
        else:
            loc = (0, 0.7, 0.7)
        obj.location = vec(loc)

    def data_Set_New_Motion_Elapsed_Time_On_Panel():
        elapsed_Time = 0
        # ======================================================================== #
        # NOTE : deg/s나 mm/s인 경우엔 별도의 시간 계산식이 필요
        pose_Elapsed_Time = Bl_Op_Data.data_Op_Robot_Speed
        # ======================================================================== #
        Bl_Op_Data.data_Ui_Motion_Elapsed_Time.append(pose_Elapsed_Time)
        for time in Bl_Op_Data.data_Ui_Motion_Elapsed_Time:
            elapsed_Time += time
        Bl_Op_Data.widgets_panel.func_Set_Motion_Elapsed_Time_On_Panel(elapsed_Time)

    def data_Set_Revised_Motion_Elapsed_Time_On_Panel():
        elapsed_Time = 0
        for time in Bl_Op_Data.data_Ui_Motion_Elapsed_Time:
            elapsed_Time += time
        Bl_Op_Data.widgets_panel.func_Set_Motion_Elapsed_Time_On_Panel(elapsed_Time)

    ####################################################################################################################
    # Information # ================================================================================================== #
    ''' 설정된 카메라뷰의 방향에 따라 카메라의 위치를 변경
        NINE : 정면뷰
        EIGHT : 좌상단
        SEVEN : 좌측
        ZERO : 우상단
        MINUS : 우측
        SIX : 상단(약간 좌측으로 편향된)
    ┌────────────────────────────────────────────────┐
    │ Change the position of the camera according to │ 
    │ the orientation of the camera view set         │
    └───────────────────────────────────────────── '''
    # ================================================================================================================ #
    def data_Set_Camera_Location_With_Camera_Direction():
        if (Bl_Op_Data.data_Ui_Camera_Direction == "NINE"):
            if (Bl_Op_Data.data_Info_Curr_Pc_Ip_Adress == Bl_Op_Data.data_Info_Pc_One_Ip):
                Bl_Op_Data.data_Set_Camera_Loc_Rot_Value(0, -4, 0.73, 90, 0, 0)
            else:
                Bl_Op_Data.data_Set_Camera_Loc_Rot_Value(0, -4, 0.83, 90, 0, 0)

        if (Bl_Op_Data.data_Ui_Camera_Direction == "ZERO"):
            Bl_Op_Data.data_Set_Camera_Loc_Rot_Value(1.99, -2.56, 3.21, 54.8, 0, 31)

        if (Bl_Op_Data.data_Ui_Camera_Direction == "MINUS"):
            if (Bl_Op_Data.data_Info_Curr_Pc_Ip_Adress == Bl_Op_Data.data_Info_Pc_One_Ip):
                Bl_Op_Data.data_Set_Camera_Loc_Rot_Value(3.6, 0.583, 0.72, 90, 0, 90)
            else:
                Bl_Op_Data.data_Set_Camera_Loc_Rot_Value(3.6, 0.583, 0.82, 90, 0, 90)

        if (Bl_Op_Data.data_Ui_Camera_Direction == "EIGHT"):
            Bl_Op_Data.data_Set_Camera_Loc_Rot_Value(-1.928, -1.52, 2.61, 57.2, 0, -44)

        if (Bl_Op_Data.data_Ui_Camera_Direction == "SEVEN"):
            if (Bl_Op_Data.data_Info_Curr_Pc_Ip_Adress == Bl_Op_Data.data_Info_Pc_One_Ip):
                Bl_Op_Data.data_Set_Camera_Loc_Rot_Value(-3.37, 0.677, 0.713, 90, 0, -90)
            else:
                Bl_Op_Data.data_Set_Camera_Loc_Rot_Value(-3.37, 0.677, 0.813, 90, 0, -90)

        if (Bl_Op_Data.data_Ui_Camera_Direction == "SIX"):
            Bl_Op_Data.data_Set_Camera_Loc_Rot_Value(-0.01, -0.2, 1.27, 62, 0, -6)
    ####################################################################################################################

    # ================================================================================== #
    # NOTE : cmd = 0 >> appear, cmd = 1 >> disappear
    # ================================================================================== #
    def data_Set_Text_Appear_Or_Hide(text_Name, cmd):
        vec = mathutils.Vector
        if (cmd == 0):
            Bl_Op_Data.data_Set_Text_Information_According_To_Camera_Direction(text_Name)
            Bl_Op_Data.data_Ui_Current_Text_Name = text_Name
        else:
            Bl_Op_Data.data_Ui_Current_Text_Name = ""
            loc = (15.0, -14.0, 0.22)
            bpy.data.objects['{}'.format(text_Name)].location = vec(loc)
    ######################################################################################

    ### Information # ================================================================================================ #
    ''' ─────────────────────────────────────────────────────────────
    MavizHandler에서 Panel은 코딩한 순서대로 초기화된다. 이 때, 이 순서에
    따라 각 Panel은 data_Ui_Panel_Widget_List에 append된다. 다시 말해 
    초기화 순서에 따라 각 Panel에 고유번호가 0번부터 차례로 부여된다. 그리고 
    초기화 시 해당 Panel을 'Key', 해당 Panel의 고유번호를 'Value'로 하여 
    data_Ui_Panel_Namespace에 Map형태로 저장해두고 특정 Panel의 호출이 
    필요할 때 data_Ui_Panel_Namespace의 매개변수로 필요한 Panel의 이름을 
    넣어 return된 숫자를 data_Ui_Panel_Widget_List의 Index로 사용해 
    특정 Panel을 호출한다. 
    ───────────────────────────────────────────────────────────── '''

    def data_Set_Save_Panel_Name(panel_Name):
        length = len(Bl_Op_Data.data_Ui_Panel_Widget_List)
        Bl_Op_Data.data_Ui_Panel_Namespace[panel_Name] = length

    # ================================================================================================================ #

    # NOTE : data_Ui_Activated_Panel_Map 있는 Panel을 제거한다. (더이상 GUI에 현시되지 않음)
    def data_Set_Deactivate_Activated_Panel(panel_Name):
        try:
            if (panel_Name in Bl_Op_Data.data_Ui_Activated_Panel_Map):
                del Bl_Op_Data.data_Ui_Activated_Panel_Map[panel_Name]
        except Exception as e:
            print("error : ", e)

    # NOTE : GUI에 현시할 Panel은 다음 함수를 이용해 data_Ui_Activated_Panel_Map에 넣어준다.
    def data_Set_Activated_Panel_List_Map(panel_Name):
        number = Bl_Op_Data.data_Ui_Panel_Namespace[panel_Name]
        Bl_Op_Data.data_Ui_Activated_Panel_Map[panel_Name] = number

    ### Information # ================================================================================================ #
    ''' ────────────────────────────────────────────────────┐
    │ When initializing the information on the panel,       │
    │ return the y coordinates of the panel corresponding   │
    │ to the resolution of the currently connected display. │
    └──────────────────────────────────────────────────── '''

    def data_Set_Coords_Of_Panel(panel_Name, x, y):
        num = Bl_Op_Data.data_Ui_Panel_Namespace[panel_Name]
        Bl_Op_Data.data_Ui_Panel_Widget_List[num].loc_x = (Bl_Op_Data.data_Ui_Window_Width / 2) - (x * Bl_Op_Data.data_Ui_X_Ratio)
        Bl_Op_Data.data_Ui_Panel_Widget_List[num].loc_y = Bl_Op_Data.data_Ui_Window_Height - (y * Bl_Op_Data.data_Ui_X_Ratio)
        loc_x = Bl_Op_Data.data_Ui_Panel_Widget_List[num].loc_x
        loc_y = Bl_Op_Data.data_Ui_Panel_Widget_List[num].loc_y

        return loc_x, loc_y

    def data_Set_Coords_Of_Aux_Panel(panel_Name, x, y, w, h):
        num = Bl_Op_Data.data_Ui_Panel_Namespace[panel_Name]
        Bl_Op_Data.data_Ui_Panel_Widget_List[num].loc_x = x + w
        Bl_Op_Data.data_Ui_Panel_Widget_List[num].loc_y = y + h
        loc_x = Bl_Op_Data.data_Ui_Panel_Widget_List[num].loc_x
        loc_y = Bl_Op_Data.data_Ui_Panel_Widget_List[num].loc_y

        return loc_x, loc_y
    # ================================================================================================================ #

    # Information # ============================================================================================== #
    ''' 설정된 카메라뷰의 방향에 따라 현재 현시된 Text의 위치 및 회전 정보를 적용
    ┌──────────────────────────────────────────────────────────────────────┐
    │ Apply the position and rotation information of the currently present │
    │ text according to the orientation of the camera view.                │
    └─────────────────────────────────────────────────────────────────── '''
    # ============================================================================================================ #
    def data_Set_Text_Information_According_To_Camera_Direction(text_Name):
        if (len(text_Name) == 0):
            pass
        else:
            idx = Bl_Op_Data.data_Ui_Text_Properties[Bl_Op_Data.data_Ui_Camera_Direction]
            Bl_Op_Data.data_Set_Text_Loc_Rot_Value(text_Name, idx[0], idx[1], idx[2], idx[3], idx[4], idx[5])

    def data_Set_Modify_Region_Color(curr_Loc, Red, Green, Blue):
        material = bpy.data.materials["{}".format(curr_Loc)].node_tree.nodes["Principled BSDF"]
        material.inputs[0].default_value[0] = Red
        material.inputs[0].default_value[1] = Green
        material.inputs[0].default_value[2] = Blue
        if (Green == 1.0):
            # NOTE : transparency = 0.2
            material.inputs[18].default_value = 0.2
        else:
            # NOTE : transparency = 0.0 (invisible)
            material.inputs[18].default_value = 0.0

    # ======================================================================== #
    # NOTE : Changes the position of the text for the currently selected mode.
    # ======================================================================== #
    def data_Set_Selected_Menu_Text_Location(text_Name):
        for text in Bl_Op_Data.data_Ui_Blender_Text:
            if (text == text_Name):
                Bl_Op_Data.data_Set_Text_Appear_Or_Hide(text, 0)
            else:
                Bl_Op_Data.data_Set_Text_Appear_Or_Hide(text, 1)
    ############################################################################

    def data_Set_Slidabar_Motion_Rate_List(motion_List):
        Motion_Rate_List = []
        length = len(motion_List)
        for i in range(1, (length + 1)):
            Motion_Rate_List.append(i * 5)

        return Motion_Rate_List

    def data_Set_Camera_Zoom(event, camera, weight, zoom):
        x_Center = Bl_Op_Data.data_Ui_Window_Width / 2
        y_Center = Bl_Op_Data.data_Ui_Window_Height / 2
        x = float(event.mouse_x - x_Center) / 100000.0
        y = float(event.mouse_y - y_Center) / 100000.0
        camera.ortho_scale += weight
        lloc = Bl_Op_Data.data_Calculate_Location_Oriented_Local_For_Zoom(x, y)
        Bl_Op_Data.data_Set_modify_Camera_Location_In_Cursor_Direction(lloc, zoom)

    # TAG : Capture point cloud
    def data_Set_Save_Compressed_Point_Cloud(points):
        length = len(os.listdir(Bl_Op_Data.data_Ui_Image_Data_Path)) + 1
        current_Captured_Point_Cloud = "Captured_Point_Cloud_{}".format(length)
        directory = Bl_Op_Data.data_Ui_Image_Data_Path + current_Captured_Point_Cloud + "/"
        os.mkdir(directory)
        path = "{}{}.npy.gz".format(directory, current_Captured_Point_Cloud)
        compressed_File = gzip.GzipFile(path, "w")
        np.save(file=compressed_File, arr=points)
        compressed_File.close()

    # TAG : Save trimmed point cloud
    def data_Set_Save_Trimed_Compressed_Point_Cloud(points, name):
        current_Captured_Point_Cloud = name
        directory = Bl_Op_Data.data_Ui_Image_Data_Path + current_Captured_Point_Cloud + "/"
        os.mkdir(directory)
        path = "{}{}.npy.gz".format(directory, current_Captured_Point_Cloud)
        compressed_File = gzip.GzipFile(path, "w")
        np.save(file=compressed_File, arr=points)
        compressed_File.close()

    # TAG : Auto create motion
    def data_Set_Auto_Created_Motion():
        # Information # ====================================================================== #
        ''' ──────────────────────────────────────────────────────────────────────────────────┐
        │ Modifying the "mesh_Data" and "ik_Pose_Data" of all motions to the robot's expected │
        │ arrival point according to the speed of the conveyor belt and robot speed when you  │
        │ pressed motion create button.                                                       │
        └────────────────────────────────────────────────────────────────────────────────── '''
        # ==================================================================================== #
        cnt = 0
        piled_length = 0

        obj = Bl_Op_Data.data_Motion_List
        for pose in obj:
            pose.mesh_Data.location.x += Bl_Op_Data.data_Draw_Atmp_Length
            if (cnt == 0):
                Bl_Op_Data.data_Set_Replace_With_Automatically_Created_Pose(pose, pose.mesh_Data.location, pose.mesh_Data.rotation_euler)
            elif (cnt > 0):
                robot_Speed = pose.robot_Operate_Data_Velocity
                duration = robot_Speed
                moved_Length = (Bl_Op_Data.data_Op_Conveyor_Velocity / 60) * duration
                if (Bl_Op_Data.data_Info_Curr_Pc_Ip_Adress == Bl_Op_Data.data_Info_Pc_One_Ip):
                    piled_length += moved_Length
                    pose.mesh_Data.location.x -= piled_length
                else:
                    piled_length += moved_Length
                    pose.mesh_Data.location.x += piled_length
                Bl_Op_Data.data_Set_Replace_With_Automatically_Created_Pose(pose, pose.mesh_Data.location, pose.mesh_Data.rotation_euler)
            cnt += 1

        current_Pose_Number = Bl_Op_Data.data_Set_Revising_Data_Update()
        Bl_Op_Data.data_Get_First_Pos_Info_To_Draw_Point_Line(current_Pose_Number)

    def data_Set_Revising_Data_Update():
        Bl_Op_Data.data_Current_Loaded_Motion_List = Bl_Op_Data.data_Motion_List
        Bl_Op_Data.data_Current_Loaded_Motion_length = Bl_Op_Data.data_Motion_Length
        Bl_Op_Data.data_Draw_Current_Pose_Mesh_Number = 1
        Bl_Op_Data.data_Draw_Repeat_Count = Bl_Op_Data.data_Motion_Length

        return 0

    # TAG : Draw point path
    def data_Set_Check_Last_Point_Line_Spot():
        # Information # =============================================== #
        ''' ───────────────────────────────────────────────────────────
            모션을 생성(혹은 자동생성)하여 FLAG_DRAWING_POINT_PATH = True일 때,
            모션을 수정하여 FLAG_POSE_____ING_MODAL_OPEN = True일 때,
            Path point를 찍는 modal반복 중 현재 상태가 마지막 Pose인지 확인
            ───────────────────────────────────────────────────────────'''
        # ============================================================= #

        # NOTE : When you load motion from Data Base.
        if (bof.FLAG_POSE_ADDING_STATE == False and bof.FLAG_POSE_DELETING_STATE == False and bof.FLAG_POSE_EDITING_STATE == False):
            if (Bl_Op_Data.data_Draw_Repeat_Count > 0):
                bof.FLAG_SET_IKCONTROL_AT_NEXT_POSITION = True
            elif ((bof.FLAG_MAKE_MOTION_BUTTON_PRESSED == True or bof.FLAG_MODIFY_ALL_POSE_AUX == True)
                  and Bl_Op_Data.data_Draw_Repeat_Count == 0):
                # TAG : Modify all pose
                bof.FLAG_MODIFY_ALL_POSE_AUX = False
                bof.FLAG_MAKE_MOTION_BUTTON_PRESSED = False

            if (Bl_Op_Data.data_Draw_Repeat_Count == 0):
                Bl_Op_Data.data_Draw_Pose_Count += Bl_Op_Data.data_Current_Loaded_Motion_length

        # NOTE : When you revise some motions.
        else:
            # ======================================================================================================== #
            # TAG : Edit mode
            # ======================================================================================================== #
            if (bof.FLAG_EDIT_MODE == True):
                ''' ──────────────────────────────────────────────────────┐
                │ Start = data_Draw_Repeat_Count = bod.data_Motion_Length │
                │   >> data_Draw_Repeat_Count -= 1                        │
                │ End = data_Draw_Repeat_Count = 0                        │
                └────────────────────────────────────────────────────── '''
                if (Bl_Op_Data.data_Draw_Repeat_Count > 1):
                    bof.FLAG_SET_IKCONTROL_AT_NEXT_POSITION = True
                else:
                    if (bof.FLAG_POSE_EDITING_STATE == True):
                        bof.FLAG_POSE_EDITING_STATE = False
                        bof.FLAG_EDIT_ONE_POSE = False
                        bof.FLAG_EDIT_MODE = False
                        Bl_Op_Data.data_Draw_Repeat_Count = 0

                        if (bof.FLAG_PLYAXIS_ANCHOR_DROPPED == False):
                            Bl_Op_Data.data_Draw_Curr_Ply_Axis_Loc = Bl_Op_Data.data_Draw_Ply_Axis_First_Loc
                            Bl_Op_Data.data_Draw_plyAxis_Obj.location.x = Bl_Op_Data.data_Draw_Curr_Ply_Axis_Loc
                            Bl_Op_Data.data_Draw_Pre_Location = None
            ############################################################################################################

                    if (bof.FLAG_REST_POINT_EXIST == True):
                        bof.FLAG_REST_POINT_EXIST = False
                        bof.FLAG_AUTO_CHANGE_SPEED_OF_REST_POINT = True
            else:
                if (Bl_Op_Data.data_Draw_Repeat_Count > 1):
                    bof.FLAG_SET_IKCONTROL_AT_NEXT_POSITION = True
                else:
                    # ================================================================================================ #
                    # TAG : Add mode
                    # ================================================================================================ #
                    if (bof.FLAG_POSE_ADDING_STATE == True):
                        if (Bl_Op_Data.data_Draw_Repeat_Count > 1):
                            bof.FLAG_SET_IKCONTROL_AT_NEXT_POSITION = True
                        else:
                            bof.FLAG_ADD_ONE_POSE = False
                            bof.FLAG_POSE_ADDING_STATE = False
                            bof.FLAG_PLYAXIS_ANCHOR_DROPPED = False
                            Bl_Op_Data.data_Draw_Repeat_Count = 0

                        if (bof.FLAG_PLYAXIS_ANCHOR_DROPPED == False):
                            Bl_Op_Data.data_Draw_Curr_Ply_Axis_Loc = Bl_Op_Data.data_Draw_Ply_Axis_First_Loc
                            Bl_Op_Data.data_Draw_plyAxis_Obj.location.x = Bl_Op_Data.data_Draw_Curr_Ply_Axis_Loc
                            Bl_Op_Data.data_Draw_Pre_Location = None
                    ####################################################################################################

                    # ================================================================================================ #
                    # TAG : Delete mode
                    # ================================================================================================ #
                    else:
                        if (Bl_Op_Data.data_Draw_Repeat_Count > 1):
                            bof.FLAG_SET_IKCONTROL_AT_NEXT_POSITION = True
                        else:
                            bof.FLAG_DELETE_ONE_POSE = False
                            bof.FLAG_POSE_DELETING_STATE = False
                            bof.FLAG_RESTRICT_DELETING_COUNT = False
                            bof.FLAG_PLYAXIS_ANCHOR_DROPPED = False
                            Bl_Op_Data.data_Draw_Repeat_Count = 0

                        if (bof.FLAG_PLYAXIS_ANCHOR_DROPPED == False):
                            Bl_Op_Data.data_Draw_Curr_Ply_Axis_Loc = Bl_Op_Data.data_Draw_Ply_Axis_First_Loc
                            Bl_Op_Data.data_Draw_plyAxis_Obj.location.x = Bl_Op_Data.data_Draw_Curr_Ply_Axis_Loc
                            Bl_Op_Data.data_Draw_Pre_Location = None
                    ####################################################################################################

                    if (bof.FLAG_REST_POINT_EXIST == True):
                        bof.FLAG_REST_POINT_EXIST = False
                        bof.FLAG_AUTO_CHANGE_SPEED_OF_REST_POINT = True

    def data_Set_Revise_Product_Location_With_Teaching(curnum, befnum):
        ### Information # ============================================================================================ #
        ''' ──────────────────────────────────────────────────────────────────┐
        │ Predict next position of product using by code that is below here.  │
        │ Measure distance between previous pose of point and the ik_Tracker. │
        └────────────────────────────────────────────────────────────────── '''
        Bl_Op_Data.data_Draw_Pre_Location = Bl_Op_Data.data_Draw_plyAxis_Obj.location.x
        obj = Bl_Op_Data.data_Motion_List
        robot_V = (obj[curnum].robot_Operate_Data_Velocity / 1000)                    # v (m/s)
        try:
            befpos = bpy.data.objects['pos{}'.format(befnum)].location
            curpos = bpy.data.objects['pos{}'.format(curnum)].location
            length = Bl_Op_Data.data_Calculate_Duration(befpos, curpos)               # s (m)
            duration = length / robot_V                                               # t (= s <= m/ m/s)
            moved_Length = (Bl_Op_Data.data_Op_Conveyor_Velocity / 60) * duration     # 0.116 m/s (7 M/min)
            if (Bl_Op_Data.data_Info_Curr_Pc_Ip_Adress == Bl_Op_Data.data_Info_Pc_One_Ip):
                Bl_Op_Data.data_Draw_plyAxis_Obj.location.x += moved_Length
            else:
                Bl_Op_Data.data_Draw_plyAxis_Obj.location.x -= moved_Length
            bpy.context.view_layer.update()
            Bl_Op_Data.data_Draw_Curr_Ply_Axis_Loc = Bl_Op_Data.data_Draw_plyAxis_Obj.location.x
        except:
            pass
        # ============================================================================================================ #

    def data_Set_Revise_Product_Location_With_Teaching_Second(curnum):
        ### Information # ============================================================================================ #
        ''' ──────────────────────────────────────────────────────────────────┐
        │ Predict next position of product using by code that is below here.  │
        │ Measure distance between previous pose of point and the ik_Tracker. │
        └────────────────────────────────────────────────────────────────── '''
        try:
            Bl_Op_Data.data_Draw_Pre_Location = Bl_Op_Data.data_Draw_plyAxis_Obj.location.x
            obj = Bl_Op_Data.data_Motion_List
            robot_V = (obj[curnum].robot_Operate_Data_Velocity)               # v (s) >> 로봇속도제어를 Time으로 함
            duration = robot_V                                                # t = v (s)
            moved_Length = (Bl_Op_Data.data_Op_Conveyor_Velocity / 60) * duration     # 0.116 m/s (7 M/min)
            if (Bl_Op_Data.data_Info_Curr_Pc_Ip_Adress == Bl_Op_Data.data_Info_Pc_One_Ip):
                Bl_Op_Data.data_Draw_plyAxis_Obj.location.x += moved_Length
            else:
                Bl_Op_Data.data_Draw_plyAxis_Obj.location.x -= moved_Length
            bpy.context.view_layer.update()
            Bl_Op_Data.data_Draw_Curr_Ply_Axis_Loc = Bl_Op_Data.data_Draw_plyAxis_Obj.location.x
        except Exception as e:
            print("data_Set_Revise_Product_Location_With_Teaching_Second exception : ", e)
        # ============================================================================================================ #

    def data_Set_Return_To_Original_State():
        ### Information # ================================================================================ #
        ''' ───────────────────────────────────────────────┐
        │ When you cancel the teaching, It works as a tool │
        │ that moves product to origin location.           │
        └─────────────────────────────────────────────── '''
        if (Bl_Op_Data.data_Draw_Pre_Location != None):
            Bl_Op_Data.data_Draw_plyAxis_Obj.location.x = Bl_Op_Data.data_Draw_Pre_Location
            Bl_Op_Data.data_Draw_Curr_Ply_Axis_Loc = Bl_Op_Data.data_Draw_plyAxis_Obj.location.x
            Bl_Op_Data.data_Draw_Pre_Location = None
        # ================================================================================================ #

    def date_Set_Cancel_Teach_Mode():
        ### Information # ============================================================================================ #
        ''' ───────────────────────────────────────────────────────────────────────────────────────┐
        │  Initialize the corrected position value of the product when the other button is pressed │
        │  while using edit, add, and delete mode.                                                 │
        └─────────────────────────────────────────────────────────────────────────────────────── '''
        if (Bl_Op_Data.data_Draw_Pre_Location != None):
            Bl_Op_Data.data_Draw_plyAxis_Obj.location.x = Bl_Op_Data.data_Draw_Pre_Location
            Bl_Op_Data.data_Draw_Curr_Ply_Axis_Loc = Bl_Op_Data.data_Draw_plyAxis_Obj.location.x
            Bl_Op_Data.data_Draw_Pre_Location = None
        # ============================================================================================================ #

    def data_Set_Shifted_Location_Ik_Control_Tracking(obj, gun_Length):
        # Information # =============================================== #
        ''' ───────────────────────────────────────────────────────────
            ik_control의 위치가 로봇 end와 다를 때 아래 메소드를 이용한다.
            >> 로봇의 Ik는 ik_control에 따라 움직이지만 Pose는 로봇 end에
               찍어야한다. 그러므로 ik_control로 로봇을 움직인 후 그냥 Pose를
               찍게되면 ik_control과 로봇 end간의 거리 차만큼 Pose 위치가
               어긋나게 되므로, 해당 차 만큼 Local축 기준 위치를 보정해야한다.
            ───────────────────────────────────────────────────────────'''
        # ============================================================= #
        pos = obj
        vec = mathutils.Vector
        # NOTE : Local Z-axis reference shift.
        normal_Vector = vec((0.0, 0.0, gun_Length)) # ─┐
        # ─────────────────────────────────────────────┘
        pos_Matrix_Wolrd_Cache = pos.matrix_world.copy()
        pos_Matrix_Wolrd_Cache.invert()
        # NOTICE # =================================================================================================== #
        location_Local_Shift = normal_Vector @ pos_Matrix_Wolrd_Cache
        # FIXME : Matrix multiplication >> after version 2.8 = X @ Y, before version 2.8 = X * Y
        # ============================================================================================================ #
        converted_Loc = pos.location + location_Local_Shift

        return converted_Loc
    #################################################################

    # NOTE : It uses at bl_server
    ### Robot communication protocol # =============================================================================== #
    def data_Set_Angles_Float_To_String(angles_List_Deg_Float):
        angle_List_Deg_Str = []
        for angle_List_Deg_Float in angles_List_Deg_Float:          # Round off from third decimal places to discard the negligible
            angle_List_Deg_Float = round(angle_List_Deg_Float, 3)

            if (angle_List_Deg_Float == 0):                         # If rounded result is 0, It returns string as +000.000 that is fixed.
                angle_List_Deg_Float = "+000.000"

            elif angle_List_Deg_Float > 0:                          # If rounded result is positive number
                if angle_List_Deg_Float >= 100:
                    angle_List_Deg_Float = "+" + str(angle_List_Deg_Float)
                elif angle_List_Deg_Float >= 10:
                    angle_List_Deg_Float = "+0" + str(angle_List_Deg_Float)
                else:
                    angle_List_Deg_Float = "+00" + str(angle_List_Deg_Float)

            else:                                                   # If rounded result is negative number
                angle_List_Deg_Float = angle_List_Deg_Float * -1
                if angle_List_Deg_Float >= 100:
                    angle_List_Deg_Float = "-" + str(angle_List_Deg_Float)
                elif angle_List_Deg_Float >= 10:
                    angle_List_Deg_Float = "-0" + str(angle_List_Deg_Float)
                else:
                    angle_List_Deg_Float = "-00" + str(angle_List_Deg_Float)

            splited_Angle_Data_By_Point = angle_List_Deg_Float.split(".")[1] # If the number below zero is 0 or 00, add 0 after that.
            if len(splited_Angle_Data_By_Point) == 1:
                angle_List_Deg_Float = angle_List_Deg_Float + "00"
            elif len(splited_Angle_Data_By_Point) == 2:
                angle_List_Deg_Float = angle_List_Deg_Float + "0"
            angle_List_Deg_Str.append(angle_List_Deg_Float)

        return angle_List_Deg_Str

    def data_Set_Motion_Length_Protocol(length):
        if (len(length) == 1):
            Length = '0' + length
        else:
            Length = length
        return Length

    def data_Set_Combine_Angle_Data(length, angle_Datas, motion_Data):
        combined_Joint_Angle_Data = []
        number = 0
        for angle in angle_Datas:
            Angles = "RJ" # Moving cmd
            Angles += ''.join(angle)
            ### mm/s # =============================================================================================== #
            # converted_Robot_Speed = RCM_Data.data_Calculate_Robot_Speed(speed[number])
            # Angles += (str(gripper[number]) + converted_Robot_Speed + "000")
            # ======================================================================================================== #

            ### % # ================================================================================================== #
            converted_Robot_Speed = str(float(motion_Data[number].robot_Operate_Data_Velocity))
            converted_Robot_Accel = str(motion_Data[number].robot_Operate_Data_Acceleration)
            gripper = str(motion_Data[number].robot_Operate_Data_Gripper)
            mstate = str(motion_Data[number].robot_Operate_Data_Moving_State)
            Angles += (gripper + converted_Robot_Speed + "0000") # converted_Robot_Accel + mstate
            # ======================================================================================================== #
            combined_Joint_Angle_Data.append(Angles)
            number += 1

        return combined_Joint_Angle_Data

    def data_Set_Direct_Ordering(loc, rot): # Deer, For direct order
        data_Motion_List = []
        curr_Pose = Bl_Def_Pose()
        curr_Pose.pose_Number = Bl_Op_Data.data_Get_Motion_List_Length()
        curr_Pose.robot_Operate_Data_Control_Speed = Bl_Op_Data.data_Op_Speed_Or_Time
        curr_Pose.robot_Operate_Data_Moving_State = Bl_Op_Data.data_Get_Way_To_Robot_Move()
        curr_Pose.mesh_Data = None
        curr_Pose.ik_Pose_Data = [loc.x, loc.y, loc.z, rot.x, rot.y, rot.z]
        curr_Pose.fk_Pose_Data = Bl_Op_Data.data_Get_Joint_Angle_List()
        curr_Pose.robot_Operate_Data_Velocity = 1.0
        curr_Pose.robot_Operate_Data_Converted_Velocity = 1.0
        curr_Pose.robot_Operate_Data_Acceleration = Bl_Op_Data.data_Op_Robot_Accel
        curr_Pose.robot_Operate_Data_Radius = 0
        curr_Pose.robot_Operate_Data_Gripper = 0

        data_Motion_List.append(curr_Pose)

        return data_Motion_List
    # ================================================================================================================ #

# ==================================================================================================================== #

### Data get # ======================================================================================================= #
    def data_Get_Tracker_Local_Matrix():
        tracker_Local_Matrix = list(bpy.data.objects['Tracker'].matrix_local.translation)
        return tracker_Local_Matrix

    def data_Get_Tracker_Rotation():
        tracker_Rot_Angle_List = list(bpy.data.objects['Tracker'].rotation_euler)
        return tracker_Rot_Angle_List

    def data_Get_Tracker_Clone_Local_Matrix():
        tracker_Clone_Local_Matrix = list(bpy.data.objects['Tracker_Clone'].matrix_local.translation)
        return tracker_Clone_Local_Matrix

    def data_Get_Tracker_Clone_Rotation():
        tracker_Clone_Rot_Angle_List = list(bpy.data.objects['Tracker_Clone'].rotation_euler)
        return tracker_Clone_Rot_Angle_List

    def data_Get_Pose_Location(pos_Number):
        pos_Loc_Coords_List = list(bpy.data.objects[f'pos{pos_Number - 1}'].location)
        return pos_Loc_Coords_List

    def data_Get_Standard_Point_Location(point_Num):
        standard_Coord = list(bpy.data.objects['point{}'.format(point_Num)].location)
        return standard_Coord

    def data_Get_Aim_Point_Location(point_Num):
        aim_Coord = list(bpy.data.objects['point{}'.format(point_Num)].location)
        return aim_Coord

    def data_Get_Ik_Control_Vector():
        ik_Control_Vector = bpy.data.objects[Bl_Op_Data.data_Draw_IK_Control_Tracker].matrix_world.translation
        return ik_Control_Vector

    def data_Get_Ik_Control_Euler():
        ik_Control_Euler = bpy.data.objects[Bl_Op_Data.data_Draw_IK_Control_Tracker].matrix_world.to_euler()
        return ik_Control_Euler

    def data_Get_Fk_Joint_Angle():
        fk_Joint_Angle = Bl_Op_Data.bl_data_robot.data_Get_Ik_Robot_Joint_Angle(0, 1)
        return fk_Joint_Angle

    def data_Get_Load_Compressed_Point_Cloud(filepath):
        decompressing_File = gzip.GzipFile(filepath, "r")
        loaded_Points = np.load(decompressing_File)
        return loaded_Points

    # NOTE : Gets the joint angle data from the "Clone robot" to update the "fk_Pose_Data"
    #        >> when "Automatically creating motion.(모션 만들기)"
    def data_Get_Fk_Joint_From_Clone_Robot(num):
        obj = Bl_Op_Data.data_Motion_List
        joint_Angle = Bl_Op_Data.bl_data_robot.data_Get_Ik_Robot_Joint_Angle(1, 1)
        obj[num].fk_Pose_Data = joint_Angle

    def data_Get_Joint_Angle_List():
        joint_Angle_List = Bl_Op_Data.bl_data_robot.data_Get_Ik_Robot_Joint_Angle(0, 1)
        return joint_Angle_List

    def data_Get_Way_To_Robot_Move():
        if (Bl_Op_Data.data_Op_Moving_State == 'J'):
            mstate = 0
        else:
            mstate = 1
        return mstate

    def data_Get_Ik_Data(obj):
        ik_Data = [obj.location.x, obj.location.y, obj.location.z,
                   obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z]
        return ik_Data

    def data_Get_Current_Receiving_Joint_Angle():
        Curr_Ur_Angle_Return = Bl_Op_Data.data_Draw_Received_Joint_To_Modeled_Robot
        Bl_Op_Data.data_Draw_Received_Joint_To_Modeled_Robot = []
        return Curr_Ur_Angle_Return


    def data_Get_First_Pos_Info_To_Draw_Point_Line(Number):
        pose = bpy.data.objects['pos{}'.format(Number)]
        target_Object = bpy.data.objects['ik_control_Clone']
        target_Object.location = pose.location
        target_Object.rotation_euler = pose.rotation_euler
        bpy.context.view_layer.update()

        Bl_Op_Data.data_Draw_Select_Robot_Getting_Joint = 1
        Bl_Op_Data.data_Get_Fk_Joint_From_Clone_Robot(Number)
        Bl_Op_Data.bl_data_robot.data_Set_Pose_Armature_Fk(Bl_Op_Data.data_Draw_Select_Robot_Getting_Joint)
        Bl_Op_Data.data_Draw_Previous_Robot_Pose_list = Bl_Op_Data.bl_data_robot.data_Get_Ik_Robot_Joint_Angle(1, 0)
        if (Bl_Op_Data.data_Motion_Length != 1):
            bof.FLAG_SET_IKCONTROL_AT_NEXT_POSITION = True
# ==================================================================================================================== #

### Data calculate # ================================================================================================= #
    def data_Calculate_Location_Oriented_Local_For_Zoom(x, y):
        obj = bpy.data.objects['Camera']
        vec = mathutils.Vector
        normal_Vector = vec((x, y, 0.0))
        pos_Matrix_Wolrd_Cache = obj.matrix_world.copy()
        pos_Matrix_Wolrd_Cache.invert()
        location_Local_Shift = normal_Vector @ pos_Matrix_Wolrd_Cache
        return location_Local_Shift

    def data_Calculate_Length(current_Pose_Number):
        aim_X = bpy.data.objects['pos{}'.format(current_Pose_Number)].location.x
        aim_Y = bpy.data.objects['pos{}'.format(current_Pose_Number)].location.y
        aim_Z = bpy.data.objects['pos{}'.format(current_Pose_Number)].location.z
        std_X = bpy.data.objects['pos{}'.format(current_Pose_Number - 1)].location.x
        std_Y = bpy.data.objects['pos{}'.format(current_Pose_Number - 1)].location.y
        std_Z = bpy.data.objects['pos{}'.format(current_Pose_Number - 1)].location.z
        xyz = pow(pow((aim_X - std_X), 2) + pow((aim_Y - std_Y), 2) + pow((aim_Z - std_Z), 2), 0.5)
        return xyz

    def data_Calculate_Angle_To_Kawasaki_Protocol(angle_List):
        # print(angle_List) ### ===========================================================================> Get fk data(ghost robot)
        converted_Angle_To_Kawasaki_Protocol = []
        for angle in angle_List:
            converted_Angle_To_Kawasaki_Protocol.append(Bl_Op_Data.data_Set_Angles_Float_To_String(angle))
        return converted_Angle_To_Kawasaki_Protocol

    def data_Calculate_Length_Between_Revised_Motions(ict, number, cmd):
        ict_Loc = Bl_Op_Data.data_Motion_List[number].mesh_Data.location
        ict_Rot = Bl_Op_Data.data_Motion_List[number].mesh_Data.rotation_euler
        ict.location = ict_Loc
        ict.rotation_euler = ict_Rot

        # kawasaki # ======================================================= #
        gun_Length = Bl_Op_Data.data_Info_Gun_Length * -1
        ict.location = Bl_Op_Data.data_Set_Shifted_Location_Ik_Control_Tracking(ict, gun_Length)
        # ================================================================== #
        bpy.context.view_layer.update()

        loc = ict_Loc.copy()
        loc_ = Bl_Op_Data.data_Get_Ik_Control_Vector()
        l_1 = Bl_Op_Data.data_Calculate_Path_Length(loc_, loc) * 1000
        aux_Loc_ = bpy.data.objects['ik_control_Aux'].matrix_world.translation
        aux_Loc = bpy.data.objects['ik_control_Aux_Tracking'].matrix_world.translation
        l_2 = Bl_Op_Data.data_Calculate_Path_Length(aux_Loc_, aux_Loc) * 1000
        differential = abs(l_1) - abs(l_2)
        bpy.context.view_layer.update()

        # ============================================================================================================ #
        # NOTE : cmd = 0 >> The motion that is loaded.
        # NOTE : cmd = 1 >> The motion that is teaching.
        # ============================================================================================================ #
        if (cmd == 0):
            speed = Bl_Op_Data.data_Motion_List[number + 1].robot_Operate_Data_Velocity
            if (Bl_Op_Data.data_Op_Robot_Speed == speed):
                pass
            else:
                speed = Bl_Op_Data.data_Op_Robot_Speed
        else:
            speed = Bl_Op_Data.data_Op_Robot_Speed

        if (-2 < differential < 2):
            Bl_Op_Data.data_Op_Converted_Robot_Speed = speed
        else:
            try:
                if (Bl_Op_Data.data_Op_Speed_Or_Time == 0):
                    converted_Robot_Speed = Bl_Op_Data.data_Calculate_Convert_Robot_Speed(speed, l_1, l_2)
                    Bl_Op_Data.data_Op_Converted_Robot_Speed = converted_Robot_Speed
                else:
                    converted_Robot_Speed = Bl_Op_Data.data_Calculate_Convert_Elapsed_Time(speed, l_1, l_2)
                    Bl_Op_Data.data_Op_Converted_Robot_Speed = converted_Robot_Speed
            except:
                print("bod.data_Op_Converted_Robot_Speed has an error")

    def data_Calculate_Angle(std_X, std_Y, std_Z, aim_X, aim_Y, aim_Z, point_Num):
        ### Information # ============================================================================================ #
        ''' ──────────────────────────────────────────────────────────────────┐
        │  x/y/z => Length of x/y/z between std_X/Y/Z and aim_X/Y/Z           │
        │  xy/yz/zx => Length of diagonal between std_(X, Y) and aim_(X, Y)   │
        │  xyz => Length of diagonal between std_(X, Y, Z) and aim_(X, Y, Z)  │
        └────────────────────────────────────────────────────────────────── '''
        xy = pow(pow((aim_X - std_X), 2) + pow((aim_Y - std_Y), 2), 0.5)

        xyz = pow(pow((aim_X - std_X), 2) + pow((aim_Y - std_Y), 2) + pow((aim_Z - std_Z), 2), 0.5)

        x = aim_X - std_X
        y = aim_Y - std_Y
        z = aim_Z - std_Z

        if (xy == 0 or xyz == 0 or y == 0):
            print("You can not divide integers as zero")

        else:
            # NOTE : angle_X_Y => angle between x and y
            angle_X_Y = (pow(xy, 2) + pow(y, 2) - pow(x, 2)) / (2 * xy * y) # ─┐
            # ─────────────────────────────────────────────────────────────────┘
            if (x > 0):
                rotation_To_Z = math.acos(angle_X_Y)
            else:
                rotation_To_Z = -math.acos(angle_X_Y)

            # NOTE : angle_XYZ_XY => angle between xyz and xy
            angle_XYZ_XY = (pow(xyz, 2) + pow(xy, 2) - pow(z, 2)) / (2 * xyz * xy) # ─┐
            # ────────────────────────────────────────────────────────────────────────┘
            if (z > 0):
                rotation_To_X = math.acos(angle_XYZ_XY) - (math.pi / 2)
            else:
                rotation_To_X = -math.acos(angle_XYZ_XY) - (math.pi / 2)

            bpy.data.objects['point{}'.format(point_Num)].rotation_euler[0] = rotation_To_X
            bpy.data.objects['point{}'.format(point_Num)].rotation_euler[1] = 0
            bpy.data.objects['point{}'.format(point_Num)].rotation_euler[2] = -rotation_To_Z
            # ======================================================================================================== #

    def data_Calculate_Duration(pos_Loc, ik_Loc):
        dx = pos_Loc.x - ik_Loc.x
        dy = pos_Loc.y - ik_Loc.y
        dz = pos_Loc.z - ik_Loc.z
        length = pow(pow(dx, 2) + pow(dy, 2) + pow(dz, 2), 0.5)
        return length

    def data_Calculate_Path_Length(std, aim):
        dx = std.x - aim.x
        dy = std.y - aim.y
        dz = std.z - aim.z
        length = pow(pow(dx, 2) + pow(dy, 2) + pow(dz, 2), 0.5)
        return length

    def data_Calculate_Convert_Robot_Speed(speed, l_1, l_2):
        t = l_1 / speed
        v = l_2 / t
        v_2 = round(v, 1)
        return v_2

    def data_Calculate_Convert_Elapsed_Time(speed, l_1, l_2):
        t1 = speed
        t2 = (l_1 * t1) / l_2
        t_2 = round(t2, 1)
        return t_2

    def data_Calculate_Convert_List_To_Vector(x, y, z):
        vec = mathutils.Vector
        vector = vec((x, y, z))
        return vector

    def data_Calculate_Convert_List_To_Euler(x, y, z):
        eul = mathutils.Euler
        euler = eul((x, y, z))
        return euler
# ==================================================================================================================== #

### Data robot joint # =============================================================================================== #
    def data_Set_Fk_Joint_Angle_Keyframe():
        pose = bpy.data.objects['Armature_fk'].pose
        pose.bones['Base'].keyframe_insert(data_path='rotation_euler')
        pose.bones['Shoulder'].keyframe_insert(data_path='rotation_euler')
        pose.bones['Elbow'].keyframe_insert(data_path='rotation_euler')
        pose.bones['Wrist1'].keyframe_insert(data_path='rotation_euler')
        pose.bones['Wrist2'].keyframe_insert(data_path='rotation_euler')
        pose.bones['Wrist3'].keyframe_insert(data_path='rotation_euler')

    def data_Set_Fk_Objects_Viewport_Value(cmd):
        if (cmd == 0):
            bool = True # Hide
        else:
            bool = False # Reveal

        objects = bpy.data.collections['{}(fk)'.format(Bl_Op_Data.data_Info_Robot_Model)].objects.keys() # Deer
        for cnt in objects:
            if (cnt != 'Armature_fk' and cnt != 'Tracker'):
                bpy.data.objects['{}'.format(cnt)].hide_viewport = bool

    def data_Get_Pose_Differential(dividing_Value, cmd):
        div_Value = dividing_Value
        pose_Differential_List = []
        prev_Joint_Angle = Bl_Op_Data.data_Draw_Previous_Robot_Pose_list
        if (cmd == 0):
            curr_Joint_Angle = Bl_Op_Data.bl_data_robot.data_Get_Ik_Robot_Joint_Angle(0, 0)
        else:
            curr_Joint_Angle = Bl_Op_Data.bl_data_robot.data_Get_Ik_Robot_Joint_Angle(1, 0)

        for count in range(0, 6):
            pose_Differential_List.append((curr_Joint_Angle[count] - prev_Joint_Angle[count]) / div_Value)

        return pose_Differential_List
# ==================================================================================================================== #

'''
    def data_Calculate_Check_Current_Location_Of_Ik_Control():
        Loc_Y = Bl_Op_Data.data_Get_Ik_Control_Vector().y
        if (Loc_Y < 0.4):
            if (bof.FLAG_DOT_FOUR == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.4", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_FOUR = False
            if (bof.FLAG_DOT_FIVE == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.5", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_FIVE = False
            if (bof.FLAG_DOT_SIX == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.6", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_SIX = False
            if (bof.FLAG_DOT_SEVEN == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.7", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_SEVEN = False
            if (bof.FLAG_DOT_EIGHT == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.8", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_EIGHT = False
            if (bof.FLAG_DOT_NINE == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.9", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_NINE = False

        elif (0.4 <= Loc_Y < 0.5):
            if (bof.FLAG_DOT_FIVE == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.5", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_FIVE = False
            if (bof.FLAG_DOT_SIX == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.6", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_SIX = False
            if (bof.FLAG_DOT_SEVEN == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.7", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_SEVEN = False
            if (bof.FLAG_DOT_EIGHT == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.8", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_EIGHT = False
            if (bof.FLAG_DOT_NINE == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.9", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_NINE = False

            if (bof.FLAG_DOT_FOUR == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.4", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_FOUR = True

        elif (0.5 <= Loc_Y < 0.6):
            if (bof.FLAG_DOT_SIX == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.6", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_SIX = False
            if (bof.FLAG_DOT_SEVEN == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.7", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_SEVEN = False
            if (bof.FLAG_DOT_EIGHT == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.8", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_EIGHT = False
            if (bof.FLAG_DOT_NINE == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.9", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_NINE = False

            if (bof.FLAG_DOT_FOUR == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.4", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_FOUR = True
            if (bof.FLAG_DOT_FIVE == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.5", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_FIVE = True

        elif (0.6 <= Loc_Y < 0.7):
            if (bof.FLAG_DOT_SEVEN == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.7", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_SEVEN = False
            if (bof.FLAG_DOT_EIGHT == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.8", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_EIGHT = False
            if (bof.FLAG_DOT_NINE == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.9", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_NINE = False

            if (bof.FLAG_DOT_FOUR == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.4", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_FOUR = True
            if (bof.FLAG_DOT_FIVE == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.5", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_FIVE = True
            if (bof.FLAG_DOT_SIX == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.6", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_SIX = True

        elif (0.7 <= Loc_Y < 0.8):
            if (bof.FLAG_DOT_EIGHT == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.8", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_EIGHT = False
            if (bof.FLAG_DOT_NINE == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.9", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_NINE = False

            if (bof.FLAG_DOT_FOUR == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.4", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_FOUR = True
            if (bof.FLAG_DOT_FIVE == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.5", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_FIVE = True
            if (bof.FLAG_DOT_SIX == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.6", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_SIX = True
            if (bof.FLAG_DOT_SEVEN == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.7", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_SEVEN = True

        elif (0.8 <= Loc_Y < 0.9):
            if (bof.FLAG_DOT_NINE == True):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.9", 0.0, 1.0, 0.0)
                bof.FLAG_DOT_NINE = False

            if (bof.FLAG_DOT_FOUR == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.4", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_FOUR = True
            if (bof.FLAG_DOT_FIVE == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.5", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_FIVE = True
            if (bof.FLAG_DOT_SIX == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.6", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_SIX = True
            if (bof.FLAG_DOT_SEVEN == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.7", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_SEVEN = True
            if (bof.FLAG_DOT_EIGHT == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.8", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_EIGHT = True

        elif (0.9 <= Loc_Y):
            if (bof.FLAG_DOT_FOUR == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.4", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_FOUR = True
            if (bof.FLAG_DOT_FIVE == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.5", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_FIVE = True
            if (bof.FLAG_DOT_SIX == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.6", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_SIX = True
            if (bof.FLAG_DOT_SEVEN == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.7", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_SEVEN = True
            if (bof.FLAG_DOT_EIGHT == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.8", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_EIGHT = True
            if (bof.FLAG_DOT_NINE == False):
                Bl_Op_Data.data_Set_Modify_Region_Color("Region_0.9", 0.0, 0.0, 0.0)
                bof.FLAG_DOT_NINE = True
'''
