import bpy
import math
import mathutils
from bl_op_data import Bl_Op_Data as bod
from bl_op_flag import Bl_Op_Flag as bof

def Bl_Ui_Draw_Pose_Operator(code):
    if (code == 0):
        Bl_Ui_Draw_Pose.draw_Del_Pose()
    elif (code == 1):
        Bl_Ui_Draw_Pose.draw_Del_Path()
    elif (code == 2):
        Bl_Ui_Draw_Pose.draw_Modified_Poses_As_Motion()

class Bl_Ui_Draw_Pose():
    draw_Pose_List_Count = 0
    draw_Point_List_Count = 0
    dividing_Number_Count = 0
    temp_Count = 0
    pose_Location = []

    verts = [(0, 0, 3.0), (1.0, 0, 0), (0, 1.0, 0), (-1.0, 0, 0), (0, -1.0, 0)]
    faces = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (1, 2, 3, 4)]

    mat_Magenta = bpy.data.materials.new("Magenta")
    mat_Magenta.diffuse_color = (1.0, 0.1, 1.0, 0.1)
                               #  R    G    B
    mat_Magenta.specular_color = (2.0, 1.0, 1.0)

    mat_Black = bpy.data.materials.new("Black")
    mat_Black.diffuse_color = (0.0, 0.0, 0.0, 0.0)
    mat_Black.specular_color = (2.0, 0.0, 1.0)

    mat_Yellow = bpy.data.materials.new("Yellow")
    mat_Yellow.diffuse_color = (1.0, 1.0, 0.0, 0.1)
    mat_Yellow.specular_color = (2.0, 0.0, 1.0)

    mat_Green = bpy.data.materials.new("Green")
    mat_Green.diffuse_color = (0.0, 1.0, 0.0, 0.1)
    mat_Green.specular_color = (2.0, 0.0, 1.0)

    mat_Dark_Blue = bpy.data.materials.new("Dark_blue")
    mat_Dark_Blue.diffuse_color = (0.0, 0.0, 0.8, 0.1)
    mat_Dark_Blue.specular_color = (2.0, 0.0, 1.0)

    mat_Blue = bpy.data.materials.new("Blue")
    mat_Blue.diffuse_color = (0.0, 0.0, 1.0, 0.1)
    mat_Blue.specular_color = (2.0, 0.0, 1.0)

    mat_Sky_blue = bpy.data.materials.new("Sky_blue")
    mat_Sky_blue.diffuse_color = (0.5, 1.0, 1.0, 0.1)
    mat_Sky_blue.specular_color = (2.0, 0.0, 1.0)

### Draw meshes # ==================================================================================================== #

    # ================================================================================================================ #
    # TAG : Create new mesh
    def draw_Pose(cur_loc, cur_rot):
        try:
            poseMesh = bpy.data.meshes.new('Cube')
            poseMesh.from_pydata(Bl_Ui_Draw_Pose.verts, [], Bl_Ui_Draw_Pose.faces)
            poseObj = bpy.data.objects.new(f'pos{Bl_Ui_Draw_Pose.draw_Pose_List_Count}', poseMesh)
            poseObj.location = cur_loc
            poseObj.rotation_euler = cur_rot
            poseObj.scale = (0.01, 0.01, 0.01)
            # set color
            if (Bl_Ui_Draw_Pose.draw_Pose_List_Count == 0):
                poseObj.active_material = Bl_Ui_Draw_Pose.mat_Dark_Blue
            else:
                poseObj.active_material = Bl_Ui_Draw_Pose.mat_Magenta
            # link poseObject to blender
            bpy.context.collection.objects.link(poseObj)
            Bl_Ui_Draw_Pose.draw_Pose_List_Count += 1
            #print('add pose : ', Bl_Ui_Draw_Pose.draw_Pose_List_Count)
            #print("Product collection keys : ", bpy.data.collections['product'].objects.keys())
        except Exception as e:
            print("draw_Pose : ",e)
            poseObj = -1

        return poseObj

    # TAG : Create new mesh
    def draw_Ui_Ur_Add_Pose(cur_loc, cur_rot, budpm):
        try:
            draw_Done_Pose_Obj = Bl_Ui_Draw_Pose.draw_Pose(cur_loc, cur_rot)  # Create "poseObj" using by "draw_Pose" function
            bod.data_Set_Mesh_Object(draw_Done_Pose_Obj)  # "poseObj" is parameter that is put into "date_Set_Pose"
            if (Bl_Ui_Draw_Pose.draw_Pose_List_Count == 1):
                bod.data_Draw_Previous_Robot_Pose_list = []
                bod.bl_data_robot.data_Set_Pose_Armature_Fk(0)
                bod.data_Draw_Previous_Robot_Pose_list = bod.bl_data_robot.data_Get_Ik_Robot_Joint_Angle(0, 0)
            else:
                # TAG : Draw point path
                bof.FLAG_DRAWING_POINT_PATH = True
            if (bod.data_Ui_Slidebar_Motion_Rate != 150):
                bod.data_Ui_Slidebar_Motion_Rate += 5
                budpm.slider_Bar.set_value((bod.data_Ui_Slidebar_Motion_Rate / 5))
            else:
                bod.data_Ui_Slidebar_Motion_Rate += 5
                budpm.slider_Bar.set_value((bod.data_Ui_Slidebar_Motion_Rate / 5))
        except Exception as e:
            print("draw_Ui_Ur_Add_Pose", e)
    # ================================================================================================================ #

    # ================================================================================================================ #
    # TAG : Draw point path
    def draw_Point(tracker_Loc_Coords, tracker_Rot_Coords):  # Draw blue mesh on each divided point
        try:
            point_Mesh = bpy.data.meshes.new('Cube')
            point_Mesh.from_pydata(Bl_Ui_Draw_Pose.verts, [], Bl_Ui_Draw_Pose.faces)
            point_Obj = bpy.data.objects.new(f'point{Bl_Ui_Draw_Pose.draw_Point_List_Count}', point_Mesh)
            point_Obj.location = (tracker_Loc_Coords[0], tracker_Loc_Coords[1], tracker_Loc_Coords[2])
            point_Obj.rotation_euler = (math.radians((tracker_Rot_Coords[0])), math.radians(tracker_Rot_Coords[1]), math.radians(tracker_Rot_Coords[2]))
            point_Obj.scale = (0.007, 0.007, 0.007)
            # set color
            point_Obj.active_material = Bl_Ui_Draw_Pose.mat_Yellow
            # link poseObject to blender
            bpy.context.collection.objects.link(point_Obj)
            Bl_Ui_Draw_Pose.draw_Point_List_Count += 1
        except Exception as e:
            print("draw_Pose", e)
            point_Obj = -1

        return point_Obj

    # TAG : Draw point path
    def draw_Point_Path(): # Draw path to connect each point mesh
        try:
            point_List = bod.data_Draw_Path_Point_List
            point_Loc_List = []
            point_Count = len(point_List)
            for i in range(point_Count):
                loc = point_List[i].location
                point_Loc_List.append(loc)
            curve_Point_Line = Bl_Ui_Draw_Pose.draw_Curve_From_Points('cur_Point_Path', point_Loc_List)
            curve_Point_Line.active_material = Bl_Ui_Draw_Pose.mat_Sky_blue
            scn = bpy.context.scene
            scn.collection.objects.link(curve_Point_Line)
            # curve_Point_Line.select_set(True)
            bpy.data.curves['{}'.format(curve_Point_Line.name)].bevel_depth = 0.001
        except Exception as e:
            print("draw_Pose_Path has an error !!! : ", e)
            point_List = []
            point_Loc_List = []
            point_Count = 0

        return {"FINISHED"}

    # TAG : Draw point path
    def draw_Curve_From_Points(name, points): # Draw lines connect each point.
        try:
            # Adapted from https://blender.stackexchange.com/a/6751
            curve_data = bpy.data.curves.new(name, type='CURVE')
            curve_data.dimensions = '3D'
            curve_data.resolution_u = 1
            curve_data.use_path_follow = True
            polyline = curve_data.splines.new(type='POLY')
            # polyline = curve_data.splines.new(type='NURBS')

            # Add the points to the curve
            polyline.points.add(len(points)-1)
            for i, point in enumerate(points):
                x, y, z = point
                polyline.points[i].co = (x, y, z, 1)
            # Create a curve object with the toolpath where the original object is
            curve_object = bpy.data.objects.new(name, curve_data)
        except Exception as e:
            print("draw_Curve_From_Points",e)
            curve_object = -1
        return curve_object
    # ================================================================================================================ #


    ### Motion Revise # ============================================================================================== #
    # TAG : Edit mode
    def draw_Ui_Edit_Pose(cur_loc, cur_rot, current_Editing_Point_Number):
        obj = bod.data_Motion_List
        pose = obj[current_Editing_Point_Number]
        poseObj = Bl_Ui_Draw_Pose.draw_Pose(cur_loc, cur_rot)
        bod.data_Set_Edited_Mesh_Object(poseObj, pose, current_Editing_Point_Number)

    # TAG : Add mode
    def draw_Ui_Add_Pose(cur_loc, cur_rot, current_Adding_Point_Number):
        poseObj = Bl_Ui_Draw_Pose.draw_Pose(cur_loc, cur_rot)
        bod.data_Set_Added_Mesh_Object(poseObj, current_Adding_Point_Number)

    # TAG : Delete mode
    def draw_Ui_Delete_Pose(current_Deleting_Point_Number):
        obj = bod.data_Motion_List
        del obj[current_Deleting_Point_Number]
        bod.data_Motion_Length = len(bod.data_Motion_List)
    # ================================================================================================================ #

# ==================================================================================================================== #

### Load poses # ===================================================================================================== #
    # Load pose data ### ============================================================================================= #
    # TAG : Motion load
    def draw_Loaded_Poses_As_Motion():
        try:
            task_Number = bod.bl_def_task.task_Length - 1
            current_Task = bod.bl_def_task.scheduled_Task.queue[task_Number]
            for obj in current_Task[bod.data_Ui_Current_Loaded_Data]:
                ik_Data = obj.ik_Pose_Data
                load_Ur_Loc = bod.data_Calculate_Convert_List_To_Vector(ik_Data[0], ik_Data[1], ik_Data[2])
                load_Ur_Rot = bod.data_Calculate_Convert_List_To_Vector(ik_Data[3], ik_Data[4], ik_Data[5])
                draw_Done_Pose_Obj = Bl_Ui_Draw_Pose.draw_Pose(load_Ur_Loc, load_Ur_Rot)
                obj.mesh_Data = draw_Done_Pose_Obj

            current_Pose_Number = bod.data_Motion_Length - bod.data_Current_Loaded_Motion_length
            bod.data_Draw_Repeat_Count = bod.data_Current_Loaded_Motion_length - 1
            bod.data_Draw_Current_Pose_Mesh_Number = 1
            bod.data_Get_First_Pos_Info_To_Draw_Point_Line(current_Pose_Number)
            bod.data_Current_Loaded_Motion_List = []

        except Exception as e:
            print("draw_Load_Sql_Ur_Add_Pose : ", e)

    # TAG : Motion load
    def draw_Load_Sql_Data_Add_Pose(Data):
        try:
            bod.data_Recombine_Loaded_Pose(Data)
            bod.data_Set_Revised_Motion_Elapsed_Time_On_Panel()
            task = bod.date_Set_Curr_Motion_As_Map()
            bod.bl_def_task.scheduled_Task.put(task)
            bod.bl_def_task.task_Length = bod.bl_def_task.task_Queue_Size()
            Bl_Ui_Draw_Pose.draw_Loaded_Poses_As_Motion()

        except Exception as e:
            print("draw_Load_Sql_Data_Add_Pose : ", e)
    # ================================================================================================================ #

# ==================================================================================================================== #
    # TAG : Draw point path
    def draw_Point_Line(dividing_Number, state_Draw_Point): # This function is operated to draw blue meshes on divided point When you press "Add" button.
        if (bod.data_Draw_Path_Point_Mesh_Number == dividing_Number):
            standard_Coords = bod.data_Get_Standard_Point_Location(Bl_Ui_Draw_Pose.draw_Point_List_Count - 1)
            aim_Coords = bod.data_Get_Pose_Location(bod.data_Draw_Repeat_Count + 1)
            bod.data_Calculate_Angle(standard_Coords[0], standard_Coords[1], standard_Coords[2], aim_Coords[0], aim_Coords[1], aim_Coords[2], (Bl_Ui_Draw_Pose.draw_Point_List_Count - 1))

            bof.FLAG_DRAWING_POINT_PATH = False
            bod.data_Draw_Path_Point_Mesh_Number = 0
            if (state_Draw_Point == 0):
                bod.data_Draw_Previous_Robot_Pose_list = bod.bl_data_robot.data_Get_Ik_Robot_Joint_Angle(0, 0)
            else:
                bod.data_Draw_Previous_Robot_Pose_list = bod.bl_data_robot.data_Get_Ik_Robot_Joint_Angle(1, 0)

            bod.data_Set_Check_Last_Point_Line_Spot()

        elif (bof.FLAG_DRAWING_POINT_PATH == True):
            pose_Differential_List = bod.data_Get_Pose_Differential(dividing_Number, state_Draw_Point)
            bod.bl_data_robot.draw_Move_Pose_Armature_Fk(pose_Differential_List) # => Move fk robot to the next point before get tracker's loc, rot(at fk's tip)
                                                                   #    After above procedure is done, draw point mesh
            tracker_Local_Matrix = bod.data_Get_Tracker_Clone_Local_Matrix() # => Get tracker's location as matrix_local.
            tracker_Rotation = bod.data_Get_Tracker_Clone_Rotation() # => Get tracker's rotation as euler.
            point_Obj = Bl_Ui_Draw_Pose.draw_Point(tracker_Local_Matrix, tracker_Rotation)  # Draw point_mesh at location that is got from upper function.
            bod.data_Draw_Path_Point_List.append(point_Obj) # => This is necessary to draw a path that pass on points.
            Bl_Ui_Draw_Pose.draw_Point_Path()

            if (state_Draw_Point == 0):
                detect_First_Point = ((Bl_Ui_Draw_Pose.draw_Pose_List_Count - 2) * dividing_Number)
            else:
                detect_First_Point = ((bod.data_Draw_Current_Pose_Mesh_Number - 2) * dividing_Number)
            if (bod.data_Draw_Path_Point_Mesh_Number == detect_First_Point):
                pass
            else:
                standard_Coords = bod.data_Get_Standard_Point_Location(Bl_Ui_Draw_Pose.draw_Point_List_Count - 2)
                aim_Coords = bod.data_Get_Aim_Point_Location(Bl_Ui_Draw_Pose.draw_Point_List_Count - 1)
                bod.data_Calculate_Angle(standard_Coords[0], standard_Coords[1], standard_Coords[2], aim_Coords[0], aim_Coords[1], aim_Coords[2], (Bl_Ui_Draw_Pose.draw_Point_List_Count - 2))

            bod.data_Draw_Path_Point_Mesh_Number += 1

    # TAG : Modify all pose
    def draw_Modified_Poses_As_Motion():
        try:

            motion_Name = bod.data_Ui_Current_Loaded_Data
            Bl_Ui_Draw_Pose.draw_Del_Pose()
            bod.data_Ui_Current_Loaded_Data = motion_Name

            cnt = 0
            task_Number = bod.bl_def_task.task_Length - 1
            current_Task = bod.bl_def_task.scheduled_Task.queue[task_Number]
            for obj in current_Task[motion_Name]:
                ik_Data = obj.ik_Pose_Data
                lx = bod.data_Draw_Modified_Pose_Data[cnt][0]
                ly = bod.data_Draw_Modified_Pose_Data[cnt][1]
                lz = bod.data_Draw_Modified_Pose_Data[cnt][2]

                modified_Loc = bod.data_Calculate_Convert_List_To_Vector(lx, ly, lz)
                rot = bod.data_Calculate_Convert_List_To_Vector(ik_Data[3], ik_Data[4], ik_Data[5])
                draw_Done_Pose_Obj = Bl_Ui_Draw_Pose.draw_Pose(modified_Loc, rot)
                obj.mesh_Data = draw_Done_Pose_Obj
                obj.ik_Pose_Data = [lx, ly, lz, ik_Data[3], ik_Data[4], ik_Data[5]]
                cnt += 1

            current_Pose_Number = bod.data_Motion_Length - bod.data_Current_Loaded_Motion_length
            bod.data_Draw_Repeat_Count = bod.data_Current_Loaded_Motion_length - 1
            bod.data_Draw_Current_Pose_Mesh_Number = 1
            bod.data_Get_First_Pos_Info_To_Draw_Point_Line(current_Pose_Number)
            bod.data_Current_Loaded_Motion_List = []

        except Exception as e:
            print("draw_Modified_Poses_As_Motion : ", e)


########################################################################################################################
### Refresh all data # =============================================================================================== #
########################################################################################################################
    # NOTE : Delete all meshes
    def draw_Del_Pose():
        try:
            Bl_Ui_Draw_Pose.draw_Reset()
            bpy.ops.object.select_pattern(pattern="pos*", extend=False)
            bpy.ops.object.delete()
            bpy.ops.object.select_pattern(pattern="point*", extend=False)
            bpy.ops.object.delete()
            bpy.ops.object.select_pattern(pattern="cur_motion_path*", extend=False)
            bpy.ops.object.delete()
            bpy.ops.object.select_pattern(pattern="cur_Point_Path*", extend=False)
            bpy.ops.object.delete()
            Bl_Ui_Draw_Pose.draw_Del_Path()

            bod.data_Ui_Slidebar_Motion_Rate = 5
            bof.FLAG_DELETE_MOTION_ONLY = False
            bof.FLAG_CONFIRM_TO_DELETE_UUID = False
        except Exception as e:
            print("draw_Del_Pose",e)

    # NOTE : Delete all path of nurbs curve
    def draw_Del_Path():
        Length = Bl_Ui_Draw_Pose.draw_Point_List_Count
        for cnt in range (0, Length):
            if (cnt == 0):
                bpy.data.curves.remove(bpy.data.curves['cur_Point_Path'])
            else:
                if (cnt < 10):
                    str_Cnt = '00' + str(cnt)
                else:
                    str_Cnt = '0' + str(cnt)
                bpy.data.curves.remove(bpy.data.curves['cur_Point_Path.{}'.format(str_Cnt)])
        Bl_Ui_Draw_Pose.draw_Point_List_Count = 0

    # NOTE : Reset all variables and flags
    def draw_Reset():
        try:
            Bl_Ui_Draw_Pose.draw_Pose_List_Count = 0
            bod.data_Draw_Path_Point_List = []
            bod.data_Ui_Motion_Elapsed_Time = []
            bod.data_Ui_Pre_Point_Number = 5
            bod.data_Ui_Current_Loaded_Data = ""
            bod.data_Pc_Point_Cloud_Data = None
            bod.data_Pc_Point_Cloud_Color_Int_Data = None
            bof.FLAG_SELECT_LMOVE = False
            bof.FLAG_PANEL_CONTEXT_UPDATE = True
            text_Name = "None"
            bod.data_Set_Selected_Menu_Text_Location(text_Name)
            text_Name = "plytracking_text"
            bod.data_Set_Text_Appear_Or_Hide(text_Name, 1)

            if (bof.FLAG_ADD_ONE_POSE == False and bof.FLAG_DELETE_ONE_POSE == False and bof.FLAG_EDIT_ONE_POSE == False):
                bod.data_Draw_Current_Deleting_Point_Number = 0
                bod.data_Draw_Repeat_Count = 0
                bod.data_Draw_Pre_Loc_For_Cancel_Tracking = None

                bof.FLAG_EDIT_ONE_POSE = False
                bof.FLAG_ADD_ONE_POSE = False
                bof.FLAG_DELETE_ONE_POSE = False
                bof.FLAG_POSE_EDITING_MODAL_OPEN = False
                bof.FLAG_POSE_ADDING_MODAL_OPEN = False
                bof.FLAG_POSE_DELETING_MODAL_OPEN = False
                bof.FLAG_POSE_EDITING_STATE = False
                bof.FLAG_POSE_ADDING_STATE = False
                bof.FLAG_POSE_DELETING_STATE = False
                bof.FLAG_RESTRICT_DELETING_COUNT = False
                bof.FLAG_ADDING_STATE_MOVE_PLYAXIS_AUX = False
                bod.widgets_panel.loadedProduct.text = '불러 온 모션 : '

            if (bof.FLAG_ADD_ONE_POSE == True or bof.FLAG_DELETE_ONE_POSE == True or bof.FLAG_EDIT_ONE_POSE == True):
                bof.FLAG_EDIT_ONE_POSE = False
                bof.FLAG_ADD_ONE_POSE = False
                bof.FLAG_DELETE_ONE_POSE = False

            if (bof.FLAG_GET_CORE_PRODUCT_PLY == True and bof.FLAG_CONFIRM_TO_RESET_CORE_PRODUCT == True):
                bod.data_Set_Core_Product_Home_Position()
                bof.FLAG_GET_CORE_PRODUCT_PLY = False
                bof.FLAG_CONFIRM_TO_RESET_CORE_PRODUCT = False
            bof.FLAG_PLYAXIS_ANCHOR_DROPPED = False
            bof.FLAG_MOTION_LOADED = False
            bof.FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT = False
            if (bof.FLAG_DELETE_MOTION_ONLY == False and bof.FLAG_CONFIRM_TO_DELETE_UUID == True):
                # TAG : Slidebar
                bof.FLAG_RESET_SLIDE_BAR = True
                bof.FLAG_CONFIRM_TO_DELETE_UUID = False
                bof.FLAG_POINT_CLOUD_IS_LOADED = False
                bof.FLAG_DELETE_POINT_CLOUD = True
        except Exception as e:
            print("draw_Reset",e)
########################################################################################################################