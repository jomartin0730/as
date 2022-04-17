import bpy
import math
import time
import datetime
import threading
from bl_op_data import Bl_Op_Data as bod
from bl_op_flag import Bl_Op_Flag as bof

class robot_Data():

    def __init__(self):
        self.camera_Props = {'SIX' : [-0.01, -0.2, 1.27, 62, 0, -6],
                             'SEVEN' : [-3.37, 0.677, 0.713, 90, 0, -90],
                             'EIGHT' : [-1.928, -1.52, 2.61, 57.2, 0, -44],
                             'NINE' : [0, -4, 0.73, 90, 0, 0],
                             'ZERO' : [1.99, -2.56, 3.21, 54.8, 0, 31],
                             'MINUS' : [3.6, 0.583, 0.72, 90, 0, 90]}

        self.text_Props = {'SIX' : [-1.02, 0.01, 0.52, 62, 0.0, -6],
                           'SEVEN' : [0.0, 1.7, 0.1, 90, 0.0, -90],
                           'EIGHT' : [-0.94, 0.975, 0.28, 57.2, 0.0, -44],
                           'NINE' : [-1.023, 0.0, 0.117, 90, 0.0, 0.0],
                           'ZERO' : [1.0325, 0.56, 0.22, 54.8, 0.0, 31],
                           'MINUS' : [0.0, 1.37, 0.1, 90, 0.0, 90]}

        # ====================================================== #
        # NOTE :    -x,  -z,  +x,  +y,  +z,  -y
        #            1    2    3    4    5    6
        #          num4 num5 num6 num7 num8 num9
        self.loc = ['1', '2', '3', '4', '5', '6']

        # ====================================================== #
        # NOTE :    +x,  -x,  +y,  -y,  -z,  +z
        #            1    2    3    4    5    6
        #            J    L    I    K    U    O
        self.rot = ['1', '2', '3', '4', '5', '6']

        bod.data_Ui_Pre_Process = True
        bod.data_Draw_IK_Control_Tracker = 'ik_Tracker' # 'ik_control'
        bod.data_Ui_Camera_Properties = self.camera_Props
        bod.data_Ui_Text_Properties = self.text_Props
        bod.data_Ui_Ik_Location_Control = self.loc
        bod.data_Ui_Ik_Rotation_Control = self.rot

    def data_Get_Ik_Robot_Joint_Angle(self, cmd, cmd2):
        if (cmd == 0):
            armature_Name = 'Armature_ik'
        elif(cmd == 2):
            armature_Name = 'Armature_Ghost_Robot'
        else:
            armature_Name = 'Armature_Clone_ik'

        obj = bpy.data.objects['{}'.format(armature_Name)]

        matrix_Channel_Base = obj.pose.bones['Base'].matrix_channel
        matrix_Channel_Shoulder = obj.pose.bones['Shoulder'].matrix_channel
        matrix_Channel_Elbow = obj.pose.bones['Elbow'].matrix_channel
        matrix_Channel_Wrist1 = obj.pose.bones['Wrist1'].matrix_channel
        matrix_Channel_Wrist2 = obj.pose.bones['Wrist2'].matrix_channel
        matrix_Channel_Wrist3 = obj.pose.bones['Wrist3'].matrix_channel

        Joint1 = -matrix_Channel_Base.to_euler().z
        Joint2 = -matrix_Channel_Shoulder.to_euler().x
        Joint3 = (matrix_Channel_Elbow.to_euler().x) - (matrix_Channel_Shoulder.to_euler().x)
        Joint4 = -((matrix_Channel_Wrist1.inverted() @ matrix_Channel_Elbow).to_euler().z)
        Joint5 = -((matrix_Channel_Wrist2.inverted() @ matrix_Channel_Wrist1).to_euler().x)
        Joint6 = -((matrix_Channel_Wrist3.inverted() @ matrix_Channel_Wrist2).to_euler().z)

        joint_Angle = [Joint1, Joint2, Joint3, Joint4, Joint5, Joint6]

        for cnt in range (0, len(joint_Angle)):
            ### NOTE : cmd2 == 0 >> Euler / cmd2 == 1 >> degrees
            if (cmd2 == 0):
                weight = 1
                if (cnt < 2):
                    weight = -1
                joint_Angle[cnt] = round(joint_Angle[cnt], 3) * weight
            elif (cmd2 == 1):
                joint_Angle[cnt] = round(math.degrees(joint_Angle[cnt]), 3)

        return joint_Angle

    def data_Set_Pose_Armature_Fk(self, cmd):
        pose = bpy.data.objects['Armature_fk_Clone'].pose
        if (cmd == 0):
            fk_Joint_Angle_List = self.data_Get_Ik_Robot_Joint_Angle(0, 0)
        elif (cmd == 2):
            pose = bpy.data.objects['Armature_fk'].pose
            fk_Joint_Angle_List = self.data_Get_Ik_Robot_Joint_Angle(2, 0)
        else:
            fk_Joint_Angle_List = self.data_Get_Ik_Robot_Joint_Angle(1, 0)

        pose.bones['Base'].rotation_euler.y = fk_Joint_Angle_List[0]
        pose.bones['Shoulder'].rotation_euler.x = fk_Joint_Angle_List[1]
        pose.bones['Elbow'].rotation_euler.x = fk_Joint_Angle_List[2]
        pose.bones['Wrist1'].rotation_euler.y = fk_Joint_Angle_List[3]
        pose.bones['Wrist2'].rotation_euler.x = fk_Joint_Angle_List[4]
        pose.bones['Wrist3'].rotation_euler.y = fk_Joint_Angle_List[5]

    def draw_Move_Pose_Armature_Fk(self, pose_Differential_List):
        pose = bpy.data.objects['Armature_fk_Clone'].pose
        pose.bones['Base'].rotation_euler.y += pose_Differential_List[0]
        pose.bones['Shoulder'].rotation_euler.x += pose_Differential_List[1]
        pose.bones['Elbow'].rotation_euler.x += pose_Differential_List[2]
        pose.bones['Wrist1'].rotation_euler.y += pose_Differential_List[3]
        pose.bones['Wrist2'].rotation_euler.x += pose_Differential_List[4]
        pose.bones['Wrist3'].rotation_euler.y += pose_Differential_List[5]

    # def data_Draw_Received_Joint_To_Armature(self):
    #     curr_Ur_Angle = bod.data_Get_Current_Receiving_Joint_Angle()
    #     if curr_Ur_Angle:
    #         Base = -math.radians(curr_Ur_Angle[0])
    #         Shoulder = -math.radians(curr_Ur_Angle[1])
    #         Elbow = math.radians(curr_Ur_Angle[2])
    #         Wrist1 = math.radians(curr_Ur_Angle[3])
    #         Wrist2 = math.radians(curr_Ur_Angle[4])
    #         Wrist3 = math.radians(curr_Ur_Angle[5])
    #
    #         pose = bpy.data.objects['Armature_fk_2R'].pose
    #         pose.bones['Base'].rotation_euler.y = Base
    #         pose.bones['Shoulder'].rotation_euler.y = Shoulder
    #         pose.bones['Elbow'].rotation_euler.y = Elbow
    #         pose.bones['Wrist1'].rotation_euler.y = Wrist1
    #         pose.bones['Wrist2'].rotation_euler.y = Wrist2
    #         pose.bones['Wrist3'].rotation_euler.y = Wrist3

class robot_Controller():

    def __init__(self):
        print("\n{} controller".format(bod.data_Info_Robot_Model))

        self.repetition = 1
        self.repeat_Count = 0
        self.product_Name = ""
        self.motion_Row_Number = 0
        self.sended_Data_Number = 0
        self.product_Static_Speed = '50'
        self.combined_Joint_Angle_Data = []
        self.order = robot_Function()

        send_Waiting_Order = threading.Thread(target=self.send_Waiting_Order_To_Robot)
        send_Waiting_Order.daemon = True
        send_Waiting_Order.start()

    def __del__(self):
        print("\n  > Deinit robot controller")

    def send_Waiting_Order_To_Robot(self):
        print(" > Sending standby command to Kawasaki is started.\n")
        while (bof.FLAG_SERVER_OPENED):
            try:
                if (bof.FLAG_THREAD_SENDING_STATE == False):
                    if (bof.FLAG_SEND_ANGLE_DATA_TO_ROBOT == False):
                        if 'ROBOT' in bod.data_Tcp_Clinet_List:
                            self.order.STANDBY()
                    time.sleep(0.2)
                else:
                    if (bof.FLAG_START_SENDING_JOINT_ANGLE_DATA == True):
                        while (self.repeat_Count <= self.repetition):
                            if (bof.FLAG_HOME_POSITIONING_ORDER == True):
                                bof.FLAG_HOME_POSITIONING_ORDER = False
                                break
                            elif (self.repeat_Count == self.repetition):
                                bof.FLAG_START_SENDING_JOINT_ANGLE_DATA = False
                                bof.FLAG_THREAD_SENDING_STATE = False
                                bof.FLAG_MOTION_EXECUTED = False
                                bof.FLAG_ROBOT_MOTION_TEST = False
                                self.repeat_Count = 0
                                break
                            elif (self.sended_Data_Number > (self.motion_Row_Number - 1) and bof.FLAG_ROBOT_MOTION_DONE == True):
                                bof.FLAG_ROBOT_MOTION_DONE = False
                                self.save_Log_Data_Of_Robot(bod.data_Ui_Current_Loaded_Data, self.product_Static_Speed, 'O')
                                self.sended_Data_Number = 0
                                self.repeat_Count += 1
                                bof.FLAG_ROBOT_MOTION_TEST = False
                            elif (self.sended_Data_Number > (self.motion_Row_Number - 1) and bof.FLAG_ROBOT_MOTION_DONE == False):
                                pass
                            else:
                                self.order.JMOVE(self.combined_Joint_Angle_Data[self.sended_Data_Number])
                                self.sended_Data_Number += 1
                            time.sleep(0.12) # Speed that send data to robot.
            except Exception as e:
                bof.FLAG_THREAD_SENDING_STATE = False
                bof.FLAG_SEND_ANGLE_DATA_TO_ROBOT = True
                bof.FLAG_START_SENDING_JOINT_ANGLE_DATA = False
                bof.FLAG_ROBOT_DISCONNECTED = True
                print("Disconnected", e)

    def save_Log_Data_Of_Robot(self, product_Name, product_Static_Speed, painting):
        datetime_ = str(datetime.datetime.now())
        splited_datetime = datetime_.split(' ')
        _date = splited_datetime[0]
        _time = splited_datetime[1]
        bod.bl_op_sql.save_Log_Data_To_DB(_date, _time, product_Name, product_Static_Speed, painting)

    def convert_Joint_Angles_To_Suitable_Protocol(self, motion_Data, received_Speed):
        fk_Pose_Data = []

        # ===================================================================================== #
        # NOTE : 퍼시스 안성공장 1호기 로봇 엔드 체결이 4˚가량 돌아가 있어 이를 보정해주기 위한 코드
        joint6_Revising = False
        if (bod.data_Info_Curr_Pc_Ip_Adress == bod.data_Info_Pc_One_Ip):
            joint6_Revising = True

        for pose in motion_Data:
            if (joint6_Revising):
                pose.fk_Pose_Data[5] = round(pose.fk_Pose_Data[5] - 4.0, 3)
        # ===================================================================================== #

            fk_Pose_Data.append(pose.fk_Pose_Data)
            pose.robot_Operate_Data_Velocity = float(pose.robot_Operate_Data_Velocity * (int(received_Speed) * 0.02))

        string_Converted_Joint_Angles = bod.data_Calculate_Angle_To_Kawasaki_Protocol(fk_Pose_Data)
        self.motion_Row_Number = len(string_Converted_Joint_Angles)
        self.combined_Joint_Angle_Data = bod.data_Set_Combine_Angle_Data(self.motion_Row_Number, string_Converted_Joint_Angles, motion_Data)

    def send_Returning_Home_Command(self):
        self.order.HOME()

    def send_Stop_Command(self):
        self.order.EMERGENCY()

class robot_Function():

    def __init__(self):
        print("{} Functions".format(bod.data_Info_Robot_Model))

    def __del__(self):
        print("  > Deinit robot function")

    def JMOVE(self, angle_Data):
        script = robot_Script()
        script.JMOVE(angle_Data)
        print("Data that MAVIZ sended : ", script.command_Line_Kawasaki)
        bod.bl_op_server.send_To_Robot(script.command_Line_Kawasaki)

    def START_SENDING(self):
        script = robot_Script()
        script.START_SENDING()
        print("Data that MAVIZ sended : ", script.command_Line_Kawasaki)
        bod.bl_op_server.send_To_Robot(script.command_Line_Kawasaki)

    def CLEAR(self):
        script = robot_Script()
        script.CLEAR()
        print("Data that MAVIZ sended : ", script.command_Line_Kawasaki)
        bod.bl_op_server.send_To_Robot(script.command_Line_Kawasaki)

    def STANDBY(self):
        script = robot_Script()
        script.STANDBY()
        # print("Data that MAVIZ sended : ", script.command_Line_Kawasaki)
        bod.bl_op_server.send_To_Robot(script.command_Line_Kawasaki)

    def EXECUTE(self):
        script = robot_Script()
        script.EXECUTE()
        print("Data that MAVIZ sended : ", script.command_Line_Kawasaki)
        bod.bl_op_server.send_To_Robot(script.command_Line_Kawasaki)

    def EMERGENCY(self):
        script = robot_Script()
        script.EMERGENCY()
        print("Data that MAVIZ sended : ", script.command_Line_Kawasaki)
        bod.bl_op_server.send_To_Robot(script.command_Line_Kawasaki)

    def HOME(self):
        script = robot_Script()
        script.HOME()
        print("Data that MAVIZ sended : ", script.command_Line_Kawasaki)
        bod.bl_op_server.send_To_Robot(script.command_Line_Kawasaki)

    def SENDING_FINISHED(self):
        script = robot_Script()
        script.SENDING_FINISHED()
        print("Data that MAVIZ sended : ", script.command_Line_Kawasaki)
        bod.bl_op_server.send_To_Robot(script.command_Line_Kawasaki)

    def SPEEDUP(self):
        script = robot_Script()
        script.SPEEDUP()
        print("Data that MAVIZ sended : ", script.command_Line_Kawasaki)
        bod.bl_op_server.send_To_Robot(script.command_Line_Kawasaki)

    def NORMALSPEED(self):
        script = robot_Script()
        script.NORMALSPEED()
        print("Data that MAVIZ sended : ", script.command_Line_Kawasaki)
        bod.bl_op_server.send_To_Robot(script.command_Line_Kawasaki)

    def SPEEDDOWN(self):
        script = robot_Script()
        script.SPEEDDOWN()
        print("Data that MAVIZ sended : ", script.command_Line_Kawasaki)
        bod.bl_op_server.send_To_Robot(script.command_Line_Kawasaki)

    def SHUTDOWN(self):
        try:
            print("ROBOT shut_Down")
            script = robot_Script()
            script.END_SIGNAL()
            bod.bl_op_server.send_To_Robot(script.command_Line_Kawasaki)
            print("Sended ROBOT shut_Down Signal")
        except Exception as e:
            print("shut_Down error", e)

class robot_Script():

    def __init__(self):
        # print(datetime.datetime.now())
        self.command_Line_Kawasaki = ''
        self.order_STANDBY = '0'
        self.order_JMOVE = 'J'
        self.order_EXECUTE = 'E'
        self.order_HOME = 'H'
        self.order_SENDING_FINISHED = 'F'
        self.order_EMERGENCY = 'B'
        self.order_CLEAR = 'C'
        self.order_SPEEDUP = 'U'
        self.order_NORMALSPEED = 'N'
        self.order_SPEEDDOWN = 'D'
        self.order_END_SIGNAL = 'T'

    def __del__(self):
        # print("MAVIZ sent data to kawasaki")
        pass

    def JMOVE(self, angle):
        self.command_Line_Kawasaki = angle

    def EXECUTE(self):
        self.command_Line_Kawasaki = self.order_EXECUTE

    def CLEAR(self):
        self.command_Line_Kawasaki = self.order_CLEAR

    def STANDBY(self):
        self.command_Line_Kawasaki = self.order_STANDBY

    def EMERGENCY(self):
        self.command_Line_Kawasaki = self.order_EMERGENCY

    def HOME(self):
        self.command_Line_Kawasaki = self.order_HOME

    def SENDING_FINISHED(self):
        self.command_Line_Kawasaki = self.order_SENDING_FINISHED

    def SPEEDUP(self):
        self.command_Line_Kawasaki = self.order_SPEEDUP

    def NORMALSPEED(self):
        self.command_Line_Kawasaki = self.order_NORMALSPEED

    def SPEEDDOWN(self):
        self.command_Line_Kawasaki = self.order_SPEEDDOWN

    def END_SIGNAL(self):
        self.command_Line_Kawasaki = self.order_END_SIGNAL