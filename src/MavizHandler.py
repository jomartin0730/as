import bpy
import os
import sys
import time

def pre_Processing_Operation():
    try:
        sys.path = []
        home = os.path.expanduser('~')
        _local = home + "/.local/lib/"
        _config = home + "/.config/blender/"
        blender = home + "/blender/"
        blf = os.listdir(blender)
        for version in blf:
            if (len(version) < 5 and len(version) != 3):
                blv = version
        scripts = blender + blv + "/scripts/"
        lib = blender + blv + "/python/lib/"
        pyv = os.listdir(lib)[0]
        python = lib + pyv
        route_Scripts = ["startup", "modules", "freestyle/modules", "addons/modules", "addons"]
        route_Python = ["", "/lib-dynload", "/site-packages"]
        route_Local = ["/site-packages", "/scripts/addons/modules", "/scripts/addons"]
        for pick in route_Scripts:
            sys.path.append(scripts + pick)
        for pick in route_Python:
            sys.path.append(python + pick)
        for cnt in range(0, 3):
            if cnt == 0:
                sys.path.append(_local + pyv + route_Local[cnt])
            else:
                sys.path.append(_config + blv + route_Local[cnt])
        cwd = home + "/MAVIZ"
        src = cwd + "/src"
        img = cwd + "/imgload/"
        pc = cwd + "/pointcloud/"
        motion = cwd + "/motion/"
        panel = cwd + "/panel/"
        font = cwd + "/font/"

        sys.path.append(src)
        print("┌─────────────────────────────────────┐")
        print("│ OS : Ubuntu linux                   │")

        return img, pc, motion, panel, font
    except:
        sys.path = []
        default_Path = "C:/Program Files/Blender Foundation/"
        dir = os.listdir(default_Path)[0]
        blender = default_Path + dir
        sys.path.append(blender)
        bl = blender + '/'
        ver = os.listdir(bl)
        for ele in ver:
            if (3 < len(ele) < 5):
                ver_ = ele
        blender = bl + ver_
        scripts = blender + '/scripts/'
        py = blender + '/python'
        sys.path.append(py)
        python = blender + '/python/'
        sclist = ['addons', 'addons/modules', 'addons_contrib', 'freestyle/modules', 'modules', 'startup']
        pylist = ['DLLs', 'lib', 'lib/site-packages']
        for ele in sclist:
            dir = scripts + ele
            sys.path.append(dir)
        for ele in pylist:
            dir = python + ele
            sys.path.append(dir)
        home_path = os.path.expanduser('~')
        dir = "/AppData/Roaming/Blender Foundation/Blender/"
        verpath = home_path + dir
        ver = os.listdir(verpath)[0]
        dir = "/scripts/addons/modules"
        modules = verpath + ver + dir
        sys.path.append(modules)
        cwd = home_path + "/MAVIZ"
        src = cwd + "/src"
        img = cwd + "/imgload/"
        pc = cwd + "/pointcloud/"
        motion = cwd + "/motion/"
        panel = cwd + "/panel/"
        font = cwd + "/font/"

        sys.path.append(src)
        print("┌─────────────────────────────────────┐")
        print("│ OS : Windows                        │")

        return img, pc, motion, panel, font

img, pc, motion, panel, font = pre_Processing_Operation()

from bpy.types import Operator
from maviz import *
from bl_ui_load import *
from bl_ui_delete import *
from bl_ui_save import *
from bl_ui_Velo_Change import *
from bl_ui_get_image import *
from bl_def_task import *
from bl_ui_draw_pose import Bl_Ui_Draw_Pose as budp, Bl_Ui_Draw_Pose_Operator
from bl_ui_draw_panel_menu import Bl_Ui_Draw_Panel_Menu as budpm, widget_Container
from bpy.types import PropertyGroup, Panel, Operator, AddonPreferences, UIList
from bl_op_pcm import *
from bl_op_server import *
from bl_op_flag import Bl_Op_Flag as bof
from bl_op_data import Bl_Op_Data as bod
bod.data_Ui_Image_Data_Path = img
bod.data_Ui_Point_Cloud_Data_Path = pc
bod.data_Ui_Motion_Data_Path = motion
bod.data_Ui_Panel_Image_Path = panel
bod.data_Ui_Font_Path = font

# Program Hanlder ==================================================================================================== #
class MavizHandler(bpy.types.Operator):
    bl_idname = "wm.maviz_handler"
    bl_label = "Maviz Handler"
    bod.data_Ui_Update_rate = 1 / 30
    _waiting_timer = 1
    _modal_action = None
    _timer = None
    instance = None
    bod.bl_def_task = Bl_Def_Task()

    # NOTE : Hide armature named "Armature fk"
    bpy.data.objects['Armature_fk'].hide_viewport = True

    # NOTE : Hide the meshes belonging to "Armature fk".
    bod.data_Set_Fk_Objects_Viewport_Value(0)

    def __init__(self):
        pose = bpy.data.objects['Armature_ik'].pose
        self.length_Current_Motion = 0
        self.matrix_Channel_Wrist1_Parent_Wrist2 = pose.bones['Wrist1'].matrix_channel
        self.matrix_Channel_Wrist2_Child_Wrist1 = pose.bones['Wrist2'].matrix_channel
        self.pcml = PCM_OT_load()
        self.pcvfib = PCV_OT_filter_boolean_intersect()
        self.check_Last_Pose_Number = 0
        self.count_Pose_Number = 0
        self.last_Frame = 0
        self.pop_Up_Latency = 0
        self.UHD_X = 3840
        self.UHD_Y = 2160
        self.main_Panel_X = 0
        self.main_Panel_Y = 0
        self.cnt = 0
        self.num = 0
        if (bod.data_Op_Speed_Or_Time == 0):
            if (bof.FLAG_SELECT_LMOVE == False):
                bod.data_Op_Robot_Speed = 80
            else:
                bod.data_Op_Robot_Speed = 200
        else:
            bod.data_Op_Robot_Speed = 0.4

    def init_widgets(self, context, widgets, state):
        initiated_Widget = []
        container = widget_Container()
        for widget in widgets:
            widget.init(context)
            initiated_Widget.append(widget)
        container.widget = initiated_Widget
        bod.data_Ui_Panel_Widget_List.append(container)
        ### NOTE : state = 1 : admit to get event / state = 0 : forbid to get event
        bod.data_Ui_Panel_button_Event_Distributor.append(state)

    def draw_callback_px(self, op, context):
        if (bof.FLAG_REVEAL_PANEL == True):
            if (len(bod.data_Ui_Activated_Panel_Map) > 1):
                # Information # ====================================================================================== #
                ''' ─────────────────────────────────────────────────────────────────── 
                Panel은 리스트의 index가 낮은 것부터 draw하기 때문에 가장 늦게 draw된 panel이 
                가장 위에 보이게 된다. 이를 이용해 그려지는 순서가 기타(Run, Teach) 패널 > 
                스크린 패널 > 메인 패널이 되도록 정렬해주는 역할(Activated Panel map에 panel이 
                들어가는 순서는 사용자가 누르는 때에 따라 계속 달라지지만 draw순서는 일정해야 하기 
                때문에 정렬이 필요함)
                ─────────────────────────────────────────────────────────────────── '''
                bod.data_Ui_Activated_Panel_Map = dict(sorted(bod.data_Ui_Activated_Panel_Map.items(), key=lambda x: x[1]))
                # ==================================================================================================== #
            for panel_Name in bod.data_Ui_Activated_Panel_Map:
                number = bod.data_Ui_Activated_Panel_Map[panel_Name]
                for widget in bod.data_Ui_Panel_Widget_List[number].widget:
                    widget.draw()

    def execute(self, context):
        self.draw_handle = None
        self.draw_event = None

        bod.data_Ui_Window_Width = context.area.width
        bod.data_Ui_Window_Height = context.area.height
        bod.data_Ui_X_Ratio = round(bod.data_Ui_Window_Width / self.UHD_X, 1)
        bod.data_Ui_Y_Ratio = round(bod.data_Ui_Window_Height / self.UHD_Y, 1)
        wm = context.window_manager
        args = (self, context)
        self.register_handlers(args, context)
        self._timer = wm.event_timer_add(bod.data_Ui_Update_rate, window=context.window)
        wm.modal_handler_add(self)
        self._modal_action = self._update_waiting

        ### Main panel menu # ======================================================================================== #
        self.panel1 = BL_UI_Drag_Panel(0, 0, 320, 620)
        self.panel1.bg_color = (0.2, 0.2, 0.2, 0.9)
        panel_Name = "main_Panel"
        bod.data_Set_Save_Panel_Name(panel_Name)
        bod.data_Set_Activated_Panel_List_Map(panel_Name)
        self.panel1.name = "panel"

        # TAG : Add panel image
        # self.panel.set_image(bod.data_Ui_Panel_Image_Path, "panel1.jpg")
        # self.panel.set_image_size((320, 620))
        # self.panel.set_image_position((0, 0))
        # ============================================================== #

        panel1 = [self.panel1]
        bod.widgets_panel = budpm()
        main_Panel = bod.widgets_panel.draw_Main_Panel_Menu()
        panel1 += main_Panel

        self.init_widgets(context, panel1, 1)
        self.panel1.add_widgets(main_Panel)
        self.main_Panel_X = (bod.data_Ui_Window_Width / 2) - (1749 * bod.data_Ui_X_Ratio)
        self.main_Panel_y = bod.data_Ui_Window_Height - (1749 * bod.data_Ui_X_Ratio)
        loc_x, loc_y = bod.data_Set_Coords_Of_Panel(panel_Name, 1749, 1749)
        # NOTE : + 1 했다가 instance에 저장해서 원래대로 돌리는 이유 : script를 regist해서 실행시키면 panel의 위치가 이상해지는데 이렇게 하면 원래대로 돌아온다.
        self.panel1.set_location(loc_x + 1, loc_y + 1)
        bod.data_Ui_Instance_Panel.append([self.panel1, loc_x, loc_y])
        # ============================================================================================================ #

        ### Point cloud editing panel menu # ========================================================================= #
        self.panel2 = BL_UI_Drag_Panel(0, 0, 300, 300)
        self.panel2.bg_color = (0.2, 0.2, 0.2, 0.9)
        panel_Name = "pc_Editing_Panel"
        bod.data_Set_Save_Panel_Name(panel_Name)
        self.panel2.name = "panel"

        # TAG : Add panel image
        # self.panel2.set_image(bod.data_Ui_Panel_Image_Path, "panel2.jpg")
        # self.panel2.set_image_size((300, 300))
        # self.panel2.set_image_position((0, 0))
        # ============================================================== #

        panel2 = [self.panel2]
        widgets_panel = budpm()
        point_Cloud_Editing_Panel = widgets_panel.draw_Point_Cloud_Editing_Panel_Menu()
        panel2 += point_Cloud_Editing_Panel

        self.init_widgets(context, panel2, 0)
        self.panel2.add_widgets(point_Cloud_Editing_Panel)
        loc_x, loc_y = bod.data_Set_Coords_Of_Panel(panel_Name, 1449, 1649)
        self.panel2.set_location(loc_x + 1, loc_y + 1)
        bod.data_Ui_Instance_Panel.append([self.panel2, loc_x, loc_y])
        # ============================================================================================================ #

        ### Point cloud streaming panel menu # ========================================================================= #
        self.panel3 = BL_UI_Drag_Panel(0, 0, 300, 150)
        self.panel3.bg_color = (0.2, 0.2, 0.2, 0.9)
        panel_Name = "pc_Streaming_Panel"
        bod.data_Set_Save_Panel_Name(panel_Name)
        self.panel3.name = "panel"

        # TAG : Add panel image
        # self.panel3.set_image(bod.data_Ui_Panel_Image_Path, "panel3.jpg")
        # self.panel3.set_image_size((300, 300))
        # self.panel3.set_image_position((0, 0))
        # ============================================================== #

        panel3 = [self.panel3]
        widgets_panel = budpm()
        point_Cloud_Streaming_Panel = widgets_panel.draw_Point_Cloud_Streaming_Panel_Menu()
        panel3 += point_Cloud_Streaming_Panel

        self.init_widgets(context, panel3, 0)
        self.panel3.add_widgets(point_Cloud_Streaming_Panel)
        loc_x, loc_y = bod.data_Set_Coords_Of_Panel(panel_Name, 1449, 1649)
        self.panel3.set_location(loc_x + 1, loc_y + 1)
        bod.data_Ui_Instance_Panel.append([self.panel3, loc_x, loc_y])
        # ============================================================================================================ #

        ### Robot control panel menu # =============================================================================== #
        self.panel4 = BL_UI_Drag_Panel(0, 0, 300, 310)
        self.panel4.bg_color = (0.2, 0.2, 0.2, 0.9)
        panel_Name = "robot_Control_Panel"
        bod.data_Set_Save_Panel_Name(panel_Name)
        self.panel4.name = "panel"

        # TAG : Add panel image
        # self.panel4.set_image(bod.data_Ui_Panel_Image_Path, "panel3.jpg")
        # self.panel4.set_image_size((300, 300))
        # self.panel4.set_image_position((0, 0))
        # ============================================================== #

        panel4 = [self.panel4]
        widgets_panel = budpm()
        draw_Robot_Control_Panel_Menu = widgets_panel.draw_Robot_Control_Panel_Menu()
        panel4 += draw_Robot_Control_Panel_Menu

        self.init_widgets(context, panel4, 0)
        self.panel4.add_widgets(draw_Robot_Control_Panel_Menu)
        loc_x, loc_y = bod.data_Set_Coords_Of_Panel(panel_Name, 1449, 1549)
        self.panel4.set_location(loc_x + 1, loc_y + 1)
        bod.data_Ui_Instance_Panel.append([self.panel4, loc_x, loc_y])
        # ============================================================================================================ #

        ### Modify all pose panel menu # =============================================================================== #
        self.panel5 = BL_UI_Drag_Panel(0, 0, 165, 180)
        self.panel5.bg_color = (0.2, 0.2, 0.2, 0.9)
        panel_Name = "modify_Pose_Panel"
        bod.data_Set_Save_Panel_Name(panel_Name)
        self.panel5.name = "panel"

        # TAG : Add panel image
        # self.panel4.set_image(bod.data_Ui_Panel_Image_Path, "panel3.jpg")
        # self.panel4.set_image_size((300, 300))
        # self.panel4.set_image_position((0, 0))
        # ============================================================== #

        panel5 = [self.panel5]
        widgets_panel = budpm()
        draw_Robot_Control_Panel_Menu = widgets_panel.draw_Modify_All_Pose_Panel_Menu()
        panel5 += draw_Robot_Control_Panel_Menu

        self.init_widgets(context, panel5, 0)
        self.panel5.add_widgets(draw_Robot_Control_Panel_Menu)

        # ============================================================================================================ #
        # NOTE : An auxiliary panel whose position is determined according to the position of a specific panel.
        x = self.panel1.x - 1
        y = self.panel1.y
        w = self.panel1.width
        h = bod.widgets_panel.modify_All_Pose.y
        loc_x, loc_y = bod.data_Set_Coords_Of_Aux_Panel(panel_Name, x, y, w, h)
        # ============================================================================================================ #

        self.panel5.set_location(loc_x + 1, loc_y + 1)
        bod.data_Ui_Instance_Panel.append([self.panel5, loc_x, loc_y])
        # ============================================================================================================ #

        ### Saving panel menu # =============================================================================== #
        self.panel6 = BL_UI_Drag_Panel(0, 0, 165, 230)
        self.panel6.bg_color = (0.2, 0.2, 0.2, 0.9)
        panel_Name = "saving_Panel"
        bod.data_Set_Save_Panel_Name(panel_Name)
        self.panel6.name = "panel"

        # TAG : Add panel image
        # self.panel4.set_image(bod.data_Ui_Panel_Image_Path, "panel3.jpg")
        # self.panel4.set_image_size((300, 300))
        # self.panel4.set_image_position((0, 0))
        # ============================================================== #

        panel6 = [self.panel6]
        widgets_panel = budpm()
        draw_Robot_Control_Panel_Menu = widgets_panel.draw_Saving_Panel_Menu()
        panel6 += draw_Robot_Control_Panel_Menu

        self.init_widgets(context, panel6, 0)
        self.panel6.add_widgets(draw_Robot_Control_Panel_Menu)
        x = self.panel1.x - 1
        y = self.panel1.y
        w = self.panel1.width
        h = bod.widgets_panel.PoseSaveA.y
        loc_x, loc_y = bod.data_Set_Coords_Of_Aux_Panel(panel_Name, x, y, w, h)
        self.panel6.set_location(loc_x + 1, loc_y + 1)
        bod.data_Ui_Instance_Panel.append([self.panel6, loc_x, loc_y])
        # ============================================================================================================ #

        return {'RUNNING_MODAL'}

    def register_handlers(self, args, context):
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)

    def unregister_handlers(self, context):
        context.window_manager.event_timer_remove(self.draw_event)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")
        self.draw_handle = None
        self.draw_event = None

### Modal # ========================================================================================================== #
    def modal(self, context, event):
        if event.type == 'ESC':
            Bl_Ui_Draw_Pose_Operator(0)
            bof.FLAG_OP_SHUTDOWN = True

        elif event.type == 'TIMER':
            self._modal_action()

        if (bof.FLAG_OP_SHUTDOWN == True):
            self._cancel(context)
            self.unregister_handlers(context)
            cleanup_and_quit()
            return {'CANCELLED'}

        self.send_Event_To_Selected_Widget(event)

        self.restrict_Robot_Joint_Angle(self.matrix_Channel_Wrist2_Child_Wrist1, self.matrix_Channel_Wrist1_Parent_Wrist2)

        # ik_control의 현재 위치를 GUI에 현시하기 위함
        bod.widgets_panel.func_Set_Ik_Control_Location()
        bod.widgets_panel.func_Set_Fk_Joint_Angle()

        # ik_control의 깊이 정보를 가지고 GUI에 깊이를 나타내는 벽을 현시 및 제거
        # self.check_Depth_Of_Ik_Control()

        # 로봇에서 보낸 joint angle data를 Armature에 적용
        # bod.bl_data_robot.data_Draw_Received_Joint_To_Armature()

        try:
            # TAG : Motion simulation
            if (bof.FLAG_SIMULATION_WITH_ANIMATION == True):
                self.simulation_With_Animation()

            # TAG : Motion simulation
            if (bof.FLAG_WAIT_SIMULATION_END == True):
                self.end_Simulation()

            # TAG : Motion simulation
            if (bof.FLAG_PRODUCT_SIMULATION_AUX == True):
                self.move_Product_In_Simulation(bod.data_Draw_Simul_Product_Convey_Length)

            if (bof.FLAG_MOVE_IK_CONTROL == True):
                self.move_Ik_Control()

            if (bof.FLAG_MODIFY_ALL_POSE == True):
                self.modify_All_Pose()

            # TAG : Draw point path
            if (bof.FLAG_SET_IKCONTROL_AT_NEXT_POSITION == True):
                self.set_Ik_Control_At_Next_Position()

            # TAG : Draw point path
            if (bof.FLAG_DRAWING_POINT_PATH == True): # This function is used to draw each path's divided point
                budp.draw_Point_Line(bod.data_Draw_Path_Dividing_Number, bod.data_Draw_Select_Robot_Getting_Joint)

            # TAG : Edit mode
            if (bof.FLAG_POSE_EDITING_MODAL_OPEN == True):
                self.draw_Pose_With_Editing()

            # TAG : Add mode
            if (bof.FLAG_POSE_ADDING_MODAL_OPEN == True):
                self.draw_Pose_With_Adding()

            # TAG : Delete mode
            if (bof.FLAG_POSE_DELETING_MODAL_OPEN == True):
                self.draw_Pose_With_Deleting()

            # TAG : Call point cloud
            if (bof.FLAG_GET_POINT_CLOUD == True):
                self.get_Ply()

            # TAG : Point cloud streaming
            if (bof.FLAG_GET_CAMERA_DATA == True):
                self.get_Pc_Data(context)

            # TAG : Trim point cloud
            if (bof.FLAG_TRIM_POINT_CLOUD_BY_BBOX == True):
                if (self.pop_Up_Latency == 1):
                    text_Name = "Waiting_text"
                    bod.data_Set_Text_Appear_Or_Hide(text_Name, 0)
                elif (self.pop_Up_Latency == 10):
                    self.trim_Point_Cloud_By_Bbox(context)
                    self.pop_Up_Latency = 0
                self.pop_Up_Latency += 1

            # TAG : Delete point cloud
            if (bof.FLAG_DELETE_POINT_CLOUD == True):
                self.delete_Point_Cloud(context)

            # TAG : Product Tracking
            if (bof.FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT == True and bof.FLAG_PLYAXIS_ANCHOR_DROPPED == False):
                self.predicting_Conveyor_Belt_Movement(budp.draw_Pose_List_Count)

            # TAG : Call core product
            if (bof.FLAG_GET_CORE_PRODUCT_PLY == True):
                self.sync_X_Location_Core_Product_With_Axis()

            # TAG : Convert speed
            if (bof.FLAG_AUTO_CHANGE_SPEED_OF_REST_POINT == True):
                self.auto_Change_Speed_Of_Rest_Point()

            # TAG : Panel context update
            if (bof.FLAG_PANEL_CONTEXT_UPDATE == True):
                self.panel_Context_Update(bod.widgets_panel)

            if (bof.FLAG_RESET_SLIDE_BAR == True):
                self.reset_Slide_Bar()

        except Exception as error:
            self.modal_Try_Except_Function()
            print("Modal has an error : ", error)

        if self.instance is not None:
           self.instance.set_event(event, context, bod.widgets_panel)

        bpy.context.view_layer.update()

        return {'RUNNING_MODAL'}
# ==================================================================================================================== #

### Functions # ====================================================================================================== #
    # TAG : Convert speed
    def auto_Change_Speed_Of_Rest_Point(self):
        bof.FLAG_AUTO_CHANGE_SPEED_OF_REST_POINT = False

        ### Information # ==================================================================================== #
        ''' ───────────────────────────────────────────────────────────────────────────────────────┐
        │ If you revise point3, ict moves to point4 and icta moves to point3. The reason for using │  
        │ this function is that you modified point3 and the pose of point3 changed accordingly.    │
        │ So the speed from point3 to point4 should also changes.                                  │
        └─────────────────────────────────────────────────────────────────────────────────────── '''
        try:
            obj = bod.data_Motion_List

            # NOTE : Move ict to next point of revised point.
            ict = bpy.data.objects['ik_control_Tracking']
            icta = bpy.data.objects['ik_control_Tracking_Aux']
            loc = obj[bod.data_Draw_Revised_Point_Number].mesh_Data.location
            rot = obj[bod.data_Draw_Revised_Point_Number].mesh_Data.rotation_euler
            ict.location = loc
            ict.rotation_euler = rot
            bpy.context.view_layer.update()
            gun_Length = bod.data_Info_Gun_Length * -1
            ict.location = bod.data_Set_Shifted_Location_Ik_Control_Tracking(ict, gun_Length)
            bpy.context.view_layer.update()

            # NOTE : Move icta to revised point.
            loc = obj[bod.data_Draw_Revised_Point_Number - 1].mesh_Data.location
            rot = obj[bod.data_Draw_Revised_Point_Number - 1].mesh_Data.rotation_euler
            icta.location = loc
            icta.rotation_euler = rot
            bpy.context.view_layer.update()

            loc = bpy.data.objects['ik_Tracker_Tracking'].matrix_world.translation
            loc_ = bpy.data.objects['ik_Tracker_Tracking_Aux'].matrix_world.translation
            bpy.context.view_layer.update()
            l_1 = bod.data_Calculate_Path_Length(loc_, loc) * 1000

            aux_Loc_ = bpy.data.objects['ik_control_Aux_Tracking'].matrix_world.translation
            aux_Loc = bpy.data.objects['ik_control_Aux_Tracking_Aux'].matrix_world.translation
            l_2 = bod.data_Calculate_Path_Length(aux_Loc_, aux_Loc) * 1000

            speed = obj[bod.data_Draw_Revised_Point_Number - 1].robot_Operate_Data_Velocity
            if (bod.data_Op_Speed_Or_Time == 0):
                converted_Robot_Speed = bod.data_Calculate_Convert_Robot_Speed(speed, l_1, l_2)
            else:
                converted_Robot_Speed = bod.data_Calculate_Convert_Elapsed_Time(speed, l_1, l_2)
            obj[bod.data_Draw_Revised_Point_Number - 1].robot_Operate_Data_Converted_Velocity = converted_Robot_Speed
            bod.data_Draw_Revised_Point_Number = 0
        except Exception as e:
            print("auto_Change_Speed_Of_Rest_Point has an error : ", e)

    # TAG : Panel context update
    def panel_Context_Update(self, pm_Instance):
        bof.FLAG_PANEL_CONTEXT_UPDATE = False
        pm_Instance.func_Panel_Context_Update()

    # TAG : Call core product
    def sync_X_Location_Core_Product_With_Axis(self):
        bpy.data.objects['{}'.format(bod.data_Pc_Ply_Name)].location.x = bod.data_Draw_plyAxis_Obj.location.x

    # TAG : Call point cloud
    def get_Ply(self):
        bof.FLAG_GET_POINT_CLOUD = False
        plyName = bod.data_Pc_Ply_Path + bod.data_Pc_Ply_Name
        if os.path.exists(plyName):
            self.pcml.loadply(plyName, bpy.context, 1)
        if (bod.data_Info_Curr_Pc_Ip_Adress == bod.data_Info_Pc_One_Ip):
            bod.data_Draw_plyAxis_Obj.location.x = 0.44878
        else:
            bod.data_Draw_plyAxis_Obj.location.x = -0.50094

    # TAG : Point cloud streaming
    def get_Pc_Data(self, context):
        bof.FLAG_GET_CAMERA_DATA = False
        self.pcml.loadply('None', context, 0)

    # TAG : Trim point cloud
    def trim_Point_Cloud_By_Bbox(self, context):
        bof.FLAG_TRIM_POINT_CLOUD_BY_BBOX = False
        self.pcvfib.execute(context)

    # TAG : Delete point cloud
    def delete_Point_Cloud(self, context):
        bof.FLAG_DELETE_POINT_CLOUD = False
        bof.FLAG_RESTRICT_MAKE_POINT_CLOUD = True
        self.pcml.loadply('None', context, 1)

    def check_Depth_Of_Ik_Control(self):
        bod.data_Calculate_Check_Current_Location_Of_Ik_Control()

    # TAG : Motion simulation
    def move_Product_In_Simulation(self, length):
        bof.FLAG_PRODUCT_SIMULATION_AUX = False
        if (bod.data_Info_Curr_Pc_Ip_Adress == bod.data_Info_Pc_One_Ip):
            bpy.data.objects['plyAxis'].location.x -= length
        else:
            bpy.data.objects['plyAxis'].location.x += length

    # Information # =============================================== #
    ''' ───────────────────────────────────────────────────────────
        ik_control_Ghost가 현재 현시 된 모든 Pose를 거쳐갈 때 해당 위치에 
        Armature_fk를 일치시킨다. 이 때, 각 Joint angle에 key frame을 
        삽입하여 Animation을 표현함 
        ───────────────────────────────────────────────────────────'''
    # ============================================================= #
    # TAG : Motion simulation
    def simulation_With_Animation(self):
        bof.FLAG_SIMULATION_WITH_ANIMATION = False

        if (bod.data_Draw_Simul_Count_Set_Anim_Keyframe < bod.data_Motion_Length):
            num = bod.data_Draw_Simul_Count_Set_Anim_Keyframe
            pose_List = bod.data_Motion_List
            if (pose_List[num].robot_Operate_Data_Control_Speed):
                operation = 1
            else:
                operation = 0
            # NOTE : Match the position of "ik_control_Ghost" to the 'num'th position.
            bod.data_Set_Ikcontrol_Ghost_Vector_Euler_Value(pose_List[num].mesh_Data.location, pose_List[num].mesh_Data.rotation_euler)
            bpy.context.view_layer.update()
            # NOTE : Match "Armature_fk" to "Armature_Ghost_Robot" that has moved.
            bod.bl_data_robot.data_Set_Pose_Armature_Fk(2)
            # NOTE : Insert key_frames in Joint angle of "Armature_fk"
            bod.data_Set_Fk_Joint_Angle_Keyframe()
            bod.data_Draw_Simul_Count_Set_Anim_Keyframe += 1

            cnt = bod.data_Draw_Simul_Count_Set_Anim_Keyframe
            length = bod.data_Motion_Length
            if (cnt < length):
                if (operation):
                    duration = int(30 * pose_List[cnt].robot_Operate_Data_Velocity)
                    self.last_Frame += duration
                    bpy.data.scenes['Scene'].frame_current += duration
                else:
                    object = bod.data_Motion_List[cnt]
                    mstate = object.robot_Operate_Data_Moving_State
                    if (mstate == 0): # J
                        duration = int(0.3 * (230 - object.robot_Operate_Data_Velocity))
                        self.last_Frame += duration
                        bpy.data.scenes['Scene'].frame_current += duration
                    else: # L
                        duration = int(0.2 * (1010 - object.robot_Operate_Data_Velocity))
                        self.last_Frame += duration
                        bpy.data.scenes['Scene'].frame_current += duration

            bod.data_Draw_Simul_Product_Convey_Length = bod.data_Op_Conveyor_Velocity / 1000
            bof.FLAG_SIMULATION_WITH_ANIMATION = True
            bof.FLAG_PRODUCT_SIMULATION = True

        else:
            bod.data_Draw_Simul_Last_Frame_Number = self.last_Frame
            bpy.data.scenes['Scene'].frame_current = 0
            bod.data_Set_Fk_Objects_Viewport_Value(1)
            bpy.ops.screen.animation_play()
            bof.FLAG_WAIT_SIMULATION_END = True

    # TAG : Motion simulation
    def end_Simulation(self):
        if (bpy.data.scenes['Scene'].frame_current == bod.data_Draw_Simul_Last_Frame_Number):
            bof.FLAG_WAIT_SIMULATION_END = False
            object = bpy.data.objects['Armature_fk']
            bpy.data.objects['plyAxis'].location.x = bod.data_Draw_Simul_Ply_Axis_First_Loc
            bod.data_Draw_Simul_Ply_Axis_First_Loc = None
            bof.FLAG_PRODUCT_SIMULATION = False

            object.hide_viewport = False
            bpy.context.view_layer.update()
            object.select_set(state=True)
            bpy.ops.anim.keyframe_clear_v3d()
            object.select_set(state=False)
            object.hide_viewport = True

            bod.data_Set_Fk_Objects_Viewport_Value(0)
            bpy.data.scenes['Scene'].frame_start = 120
            bpy.data.scenes['Scene'].frame_current = 120
            bpy.data.scenes['Scene'].frame_end = 240
            bod.data_Draw_Simul_Count_Set_Anim_Keyframe = 0
            bod.data_Draw_Simul_Last_Frame_Number = 0
            self.last_Frame = 0

    def modify_All_Pose(self):
        if (self.cnt <= len(bod.data_Draw_Modified_Pose_Data) - 1): # Deer 일단 여기까지 만듦 (모션 불러오기 > 포즈 수정 > ik_control이동 > 포즈 수정 하면 포즈가 하나씩 이동함. 근데 path는 이동 안 함. 이거 수정해야됨!!!)
            vec = mathutils.Vector
            eul = mathutils.Euler
            loc = vec(bod.data_Draw_Modified_Pose_Data[self.cnt][0])
            rot = eul(bod.data_Draw_Modified_Pose_Data[self.cnt][1])

            budp.draw_Ui_Ur_Add_Pose(loc, rot, bod.widgets_panel)

            self.cnt += 1
        else:
            self.cnt = 0
            bof.FLAG_MODIFY_ALL_POSE = False

    # TAG : Slidebar
    def move_Ik_Control(self):
        # Information # ============================================================================================== #
        ''' 슬라이드바를 움직일 때, "ik_control"을 슬라이드바가 현재 가리키는
            숫자에 해당하는 포즈 위치로 이동합니다.
        ┌────────────────────────────────────────────────────────────────┐
        │ When you move the slidebar, move "ik_control" to               │
        │ the position of the pose that corresponds to the number        │
        │ the slidebar currently points to.                              │
        └───────────────────────────────────────────────────────────── '''
        # ============================================================================================================ #
        bof.FLAG_MOVE_IK_CONTROL = False
        bod.data_Set_Ikcontrol_Loc_Rot_Value(bod.data_Draw_Curr_Ikcontrol_Loc, bod.data_Draw_Curr_Ikcontrol_Rot)
        bpy.context.view_layer.update()
        self.instance.mover.position = bod.data_Draw_Curr_Ikcontrol_Loc
        self.instance.mover.rotation = bod.data_Draw_Curr_Ikcontrol_Rot
        bpy.context.view_layer.update()
        bod.data_Draw_Curr_Ikcontrol_Loc = []
        bod.current_Ikcontrol_Rocation = None
        bod.widgets_panel.button_Set_Ik_Control_Current_Location()

    def set_Ik_Control_At_Next_Position(self):
        # Information # ============================================================================================== #
        ''' 경로를 자동으로 그리기 위해 나머지 Pose를 카운트하고 현재
            Pose가 마지막 Pose가 아닌 경우 "ik_control_Clone"을
            다음 Pose의 위치로 이동시킵니다.
        ┌─────────────────────────────────────────────────────────┐
        │ Count the remaining poses for automatically drawing     │
        │ the path and move "ik_control_Clone" to the next pose   │
        │ if it is not the last pose.                             │
        └───────────────────────────────────────────────────────'''
        # ============================================================================================================ #
        bod.data_Draw_Repeat_Count -= 1
        bod.data_Draw_Current_Pose_Mesh_Number += 1
        current_Pose_Number = ((bod.data_Current_Loaded_Motion_length - 1) - bod.data_Draw_Repeat_Count) + bod.data_Draw_Pose_Count

        # NOTE : motion is loaded
        if (bof.FLAG_POSE_EDITING_STATE == False and bof.FLAG_POSE_ADDING_STATE == False and bof.FLAG_POSE_DELETING_STATE == False):
            bpy.data.objects['ik_control_Clone'].location = bpy.data.objects['pos{}'.format(current_Pose_Number)].location
            bpy.data.objects['ik_control_Clone'].rotation_euler = bpy.data.objects['pos{}'.format(current_Pose_Number)].rotation_euler

        # NOTE : Revising mode
        else:
            pos_List_Length = (bod.data_Motion_Length - bod.data_Draw_Repeat_Count)
            bpy.data.objects['ik_control_Clone'].location = bpy.data.objects['pos{}'.format(pos_List_Length)].location
            bpy.data.objects['ik_control_Clone'].rotation_euler = bpy.data.objects['pos{}'.format(pos_List_Length)].rotation_euler
        bpy.context.view_layer.update()
        # TAG : Modify all pose
        if (bof.FLAG_MAKE_MOTION_BUTTON_PRESSED == True or bof.FLAG_MODIFY_ALL_POSE_AUX == True):
            bod.data_Get_Fk_Joint_From_Clone_Robot(current_Pose_Number)
        bof.FLAG_SET_IKCONTROL_AT_NEXT_POSITION = False
        bof.FLAG_DRAWING_POINT_PATH = True

    # TAG : Edit mode
    def draw_Pose_With_Editing(self):
        if (self.count_Pose_Number < bod.data_Motion_Length):
            if (self.count_Pose_Number == bod.data_Draw_Curr_Revising_Point_Number):
                loc = bod.data_Get_Ik_Control_Vector()
                rot = bod.data_Get_Ik_Control_Euler()
                budp.draw_Ui_Edit_Pose(loc, rot, self.count_Pose_Number)
                bod.data_Ui_Motion_Elapsed_Time[self.count_Pose_Number] = bod.data_Op_Robot_Speed
                bod.data_Set_Revised_Motion_Elapsed_Time_On_Panel()
            else:
                obj = bod.data_Motion_List
                pose = obj[self.count_Pose_Number]
                ik_List = pose.ik_Pose_Data
                loc = bod.data_Calculate_Convert_List_To_Vector(ik_List[0], ik_List[1], ik_List[2])
                rot = bod.data_Calculate_Convert_List_To_Euler(ik_List[3], ik_List[4], ik_List[5])
                poseObj = budp.draw_Pose(loc, rot)
                pose.mesh_Data = poseObj
            self.count_Pose_Number += 1
        else:
            bof.FLAG_POSE_EDITING_MODAL_OPEN = False
            bof.FLAG_POSE_EDITING_STATE = True

            self.count_Pose_Number = 0

            current_Pose_Number = bod.data_Set_Revising_Data_Update()
            bod.data_Get_First_Pos_Info_To_Draw_Point_Line(current_Pose_Number)

    # TAG : Add mode
    def draw_Pose_With_Adding(self):
        if (self.count_Pose_Number < bod.data_Motion_Length):
            if (self.count_Pose_Number == bod.data_Draw_Curr_Revising_Point_Number):
                loc = bod.data_Get_Ik_Control_Vector()
                rot = bod.data_Get_Ik_Control_Euler()
                budp.draw_Ui_Add_Pose(loc, rot, self.count_Pose_Number)
                bod.data_Ui_Motion_Elapsed_Time.insert(self.count_Pose_Number, bod.data_Op_Robot_Speed)
                bod.data_Set_Revised_Motion_Elapsed_Time_On_Panel()
            else:
                obj = bod.data_Motion_List
                pose = obj[self.count_Pose_Number]
                ik_List = pose.ik_Pose_Data
                loc = bod.data_Calculate_Convert_List_To_Vector(ik_List[0], ik_List[1], ik_List[2])
                rot = bod.data_Calculate_Convert_List_To_Euler(ik_List[3], ik_List[4], ik_List[5])
                poseObj = budp.draw_Pose(loc, rot)
                pose.mesh_Data = poseObj
                if (self.count_Pose_Number > bod.data_Draw_Curr_Revising_Point_Number):
                    pose.pose_Number += 1
            self.count_Pose_Number += 1
        else:
            bof.FLAG_POSE_ADDING_MODAL_OPEN = False
            bof.FLAG_POSE_ADDING_STATE = True

            self.count_Pose_Number = 0

            current_Pose_Number = bod.data_Set_Revising_Data_Update()
            bod.data_Get_First_Pos_Info_To_Draw_Point_Line(current_Pose_Number)

    # TAG : Delete mode
    def draw_Pose_With_Deleting(self):
        if (self.count_Pose_Number < bod.data_Motion_Length):
            if (self.count_Pose_Number == bod.data_Draw_Curr_Revising_Point_Number and bof.FLAG_RESTRICT_DELETING_COUNT == False):
                bof.FLAG_RESTRICT_DELETING_COUNT = True
                budp.draw_Ui_Delete_Pose(self.count_Pose_Number)
                del bod.data_Ui_Motion_Elapsed_Time[self.count_Pose_Number]
                bod.data_Set_Revised_Motion_Elapsed_Time_On_Panel()
                self.count_Pose_Number -= 1
            else:
                obj = bod.data_Motion_List
                pose = obj[self.count_Pose_Number]
                ik_List = pose.ik_Pose_Data
                loc = bod.data_Calculate_Convert_List_To_Vector(ik_List[0], ik_List[1], ik_List[2])
                rot = bod.data_Calculate_Convert_List_To_Euler(ik_List[3], ik_List[4], ik_List[5])
                poseObj = budp.draw_Pose(loc, rot)
                pose.mesh_Data = poseObj
                if (self.count_Pose_Number > bod.data_Draw_Curr_Revising_Point_Number):
                    pose.pose_Number -= 1
            self.count_Pose_Number += 1
        else:
            bof.FLAG_POSE_DELETING_MODAL_OPEN = False
            bof.FLAG_POSE_DELETING_STATE = True

            self.count_Pose_Number = 0

            current_Pose_Number = bod.data_Set_Revising_Data_Update()
            bod.data_Draw_Revised_Point_Number -= 1
            bod.data_Get_First_Pos_Info_To_Draw_Point_Line(current_Pose_Number)

    # TAG : Product Tracking
    def predicting_Conveyor_Belt_Movement(self, pose_Count):
        if (pose_Count > 0):
            point_Number = int(bod.data_Ui_Slidebar_Motion_Rate / 5)
            if (bof.FLAG_EDIT_ONE_POSE == False and bof.FLAG_ADD_ONE_POSE == False and bof.FLAG_DELETE_ONE_POSE == False and bof.FLAG_MOTION_LOADED == False):
                # State
                # Teach : OFF
                # Motion loaded : OFF
                # Move slider : OFF
                value = point_Number - 2
            else:
                # State
                # Teach : ON or Motion loaded : ON
                # Move slider : OFF
                if (pose_Count >= point_Number):
                    # State
                    # Number of pose is higher than the point number.
                    value = point_Number - 1
                else:
                    # State
                    # Number of pose is less than the point number.
                    value = point_Number - 2
            if (value >= 0):
                if (bof.FLAG_EDIT_ONE_POSE == False and bof.FLAG_ADD_ONE_POSE == False and bof.FLAG_DELETE_ONE_POSE == False):
                    pass
                else:
                    if (bof.FLAG_ADDING_STATE_MOVE_PLYAXIS_AUX == True):
                        bof.FLAG_ADDING_STATE_MOVE_PLYAXIS_AUX = False
                        if (point_Number == 1):
                            bof.FLAG_ADDING_STATE_MOVE_PLYAXIS = True
                            obj = bod.data_Motion_List
                            robot_V = (obj[0].robot_Operate_Data_Velocity / 1000)
                        else:
                            value = value - 1
                    else:
                        value = value - 1
                if (bod.data_Op_Speed_Or_Time == 0):
                    ### Information # ==================================================================================== #
                    ''' ─────────────────────────────────────────────────────────────────┐
                    │ Predict next position of product using by code that is below here. │
                    │ Measure distance between last pointed pose and the ik_Tracker.     │
                    └───────────────────────────────────────────────────────────────── '''
                    if (bof.FLAG_ADDING_STATE_MOVE_PLYAXIS == False):
                        robot_V = (bod.data_Op_Robot_Speed / 1000)                      # v (m/s)
                    pos_Loc = bpy.data.objects['pos{}'.format(value)].location
                    ik_Loc = bod.data_Get_Ik_Control_Vector()
                    length = bod.data_Calculate_Duration(pos_Loc, ik_Loc)               # s (m)
                    duration = length / robot_V                                         # t (= s <= m/ m/s)
                    moved_Length = (bod.data_Op_Conveyor_Velocity / 60) * duration      # 0.116 m/s (7 M/min)
                    bod.data_Draw_plyAxis_Obj.location.x = bod.data_Draw_Curr_Ply_Axis_Loc
                else:
                    duration = bod.data_Op_Robot_Speed                                  # t (= s <= m/ m/s)
                    moved_Length = (bod.data_Op_Conveyor_Velocity / 60) * duration      # 0.116 m/s (7 M/min)
                    bod.data_Draw_plyAxis_Obj.location.x = bod.data_Draw_Curr_Ply_Axis_Loc

                if (bod.data_Info_Curr_Pc_Ip_Adress == bod.data_Info_Pc_One_Ip):
                    if (bof.FLAG_ADDING_STATE_MOVE_PLYAXIS == False):
                        bod.data_Draw_plyAxis_Obj.location.x -= moved_Length
                    else:
                        bod.data_Draw_plyAxis_Obj.location.x += moved_Length
                else:
                    if (bof.FLAG_ADDING_STATE_MOVE_PLYAXIS == False):
                        bod.data_Draw_plyAxis_Obj.location.x += moved_Length
                    else:
                        bod.data_Draw_plyAxis_Obj.location.x -= moved_Length
                bof.FLAG_ADDING_STATE_MOVE_PLYAXIS = False


    def reset_Slide_Bar(self):
        bof.FLAG_RESET_SLIDE_BAR = False
        bod.widgets_panel.reset_Slider_Bar_()

    def modal_Try_Except_Function(self):
        bof.FLAG_SIMULATION_WITH_ANIMATION = False
        bof.FLAG_WAIT_SIMULATION_END = False
        bof.FLAG_PRODUCT_SIMULATION_AUX = False
        bof.FLAG_MOVE_IK_CONTROL = False
        bof.FLAG_SET_IKCONTROL_AT_NEXT_POSITION = False
        bof.FLAG_DRAWING_POINT_PATH = False
        bof.FLAG_POSE_EDITING_MODAL_OPEN = False
        bof.FLAG_POSE_ADDING_MODAL_OPEN = False
        bof.FLAG_POSE_DELETING_MODAL_OPEN = False
        bof.FLAG_GET_POINT_CLOUD = False
        bof.FLAG_GET_CAMERA_DATA = False
        bof.FLAG_DELETE_POINT_CLOUD = False
        bof.FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT = False
        bof.FLAG_GET_CORE_PRODUCT_PLY = False
        bof.FLAG_AUTO_CHANGE_SPEED_OF_REST_POINT = False
        bof.FLAG_PANEL_CONTEXT_UPDATE = False
        bof.FLAG_RESET_SLIDE_BAR = False
        bof.FLAG_TRIM_POINT_CLOUD_BY_BBOX = False
        bof.FLAG_MODIFY_ALL_POSE = False


    def _initialize(self):
        print('│ init                                │')
        instance = Maviz(
            item = Maviz.setup_item("Area1"),
            mover = Maviz.setup_ik_mover("Area2", "ik_control")
        )
        self.instance = instance

    def _cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def _update_waiting(self):
        self._waiting_timer -= bod.data_Ui_Update_rate
        if self._waiting_timer <= 0:
            self._initialize()
            bpy.ops.screen.animation_play()
            self._modal_action = self._update_running

    # Information # =============================================== #
    ''' ───────────────────────────────────────────────────────────
        실제 로봇의 5축은 ±180˚이상 돌 수 있지만 로봇 엔드가 추가되면서 로봇의
        스펙만큼 회전하게 되면 로봇엔드가 부러지기 때문에 Blender상에서 미리
        해당 각도만큼 제한을 걸어둠.
        ───────────────────────────────────────────────────────────'''
    # ============================================================= #
    def restrict_Robot_Joint_Angle(self, child_Angle, parent_Angle):
        Wrist2 = -((child_Angle.inverted() @ parent_Angle).to_euler().x)
        if ((Wrist2 - 2.0) > 0):
            revised_Angle = Wrist2 - 2.0
            self.instance.mover._decrease_x(revised_Angle)

    def send_Event_To_Selected_Widget(self, event):
        rtn = False
        try:
            for panel_Name in bod.data_Ui_Activated_Panel_Map:
                number = bod.data_Ui_Activated_Panel_Map[panel_Name]
                for widget in bod.data_Ui_Panel_Widget_List[number].widget:
                    if (widget.name != "panel"):
                        rtn = widget.handle_event(event)
        except:
            pass
        if rtn:
            print('redraw')

    def _realsenseInit(self):
        print('realsense start')

    def _update_running(self):
        self.instance.update(bod.data_Ui_Update_rate)
# ==================================================================================================================== #

### Initiation & Deletion # ========================================================================================== #
def cleanup_and_quit():
    unregister()
    bpy.ops.wm.quit_blender()

def register():
    bpy.utils.register_class(ImageGetOperator)
    bpy.utils.register_class(LoadEnumOperator)
    bpy.utils.register_class(DeleteEnumOperator)
    bpy.utils.register_class(DialogOperator)
    bpy.utils.register_class(PCV_properties)
    bpy.utils.register_class(DialogOperatorvelochanger)
    bpy.utils.register_class(MavizHandler)

def unregister():
    bpy.utils.unregister_class(ImageGetOperator)
    bpy.utils.unregister_class(LoadEnumOperator)
    bpy.utils.unregister_class(DeleteEnumOperator)
    bpy.utils.unregister_class(DialogOperator)
    bpy.utils.unregister_class(PCV_properties)
    bpy.utils.unregister_class(DialogOperatorvelochanger)
    bpy.utils.unregister_class(MavizHandler)

def setup_workspace():
    print('│ setup workspace                     │')
    window = bpy.context.window_manager.windows[0]
    screen = window.screen
    for area in screen.areas:
         if area.type == 'VIEW_3D':
             space = area.spaces[0]
             space.shading.type = 'RENDERED'
             override = {'window': window, 'screen': screen, 'area': area}
             bpy.ops.screen.screen_full_area(override, use_hide_panels = True)
             break

def main():
    setup_workspace()
    register()
    bpy.ops.wm.maviz_handler()

if __name__ == "__main__":
    main()

# ==================================================================================================================== #