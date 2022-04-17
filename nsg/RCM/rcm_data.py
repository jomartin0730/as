class RCM_Data():
    drawRobotPoseList = []
    drawRobotSpeedList = []
    drawGripperList = []
    ghost_Robot_Angle_List = []
    combined_Joint_Angle_Data = []
    clientList = {}

    sql_Datas = []
    pc_One_Ip = "192.168.0.101"
    curr_Pc_Ip_Adress = ""

    def data_Set_Motion_Length_Protocol(length):
        if (len(length) == 1):
            Length = '0' + length
        else:
            Length = length
        return Length

    def data_Set_Combine_Angle_Data(length, moving_Cmd_, angle_Datas, gripper, speed):
        RCM_Data.combined_Joint_Angle_Data = []
        number = 0
        length_ = len(angle_Datas)
        for angle in angle_Datas:
            if (moving_Cmd_ == 1):
                if (number == 0 or number == length_ - 1):
                    moving_Cmd = 'J'
                else:
                    moving_Cmd = 'L'
            elif (moving_Cmd_ == 0):
                moving_Cmd = 'J'
            Angles = "R" + moving_Cmd
            Angles += ''.join(angle)
            ### mm/s # =============================================================================================== #
            converted_Robot_Speed = RCM_Data.data_Calculate_Robot_Speed(speed[number])
            if (number == length_ - 1):
                gripper = '0'
            else:
                gripper = '1'
            Angles += (gripper + converted_Robot_Speed + "0000") # str(gripper[number])
            # ======================================================================================================== #

            ### % # ================================================================================================== #
            # converted_Robot_Speed = str(speed[number])
            # Angles += (str(gripper[number]) + converted_Robot_Speed + "00000")
            # ======================================================================================================== #
            RCM_Data.combined_Joint_Angle_Data.append(Angles)
            number += 1

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

    def data_Calculate_Robot_Speed(robot_Speed):
        speed = str(robot_Speed)
        # if (robot_Speed < 10):
        #     speed = "000" + str(robot_Speed)
        # elif (robot_Speed < 100):
        #     speed = "00" + str(robot_Speed)
        # elif (robot_Speed < 1000):
        #     speed = "0" + str(robot_Speed)
        # else:
        #     speed = str(robot_Speed)
        #     pass
        return speed

    def data_Calculate_Angle_To_Kawasaki_Protocol(angle_List):
        converted_Angle_To_Kawasaki_Protocol = []
        for angle in angle_List:
            converted_Angle_To_Kawasaki_Protocol.append(RCM_Data.data_Set_Angles_Float_To_String(angle))
        return converted_Angle_To_Kawasaki_Protocol
# ==================================================================================================================== #