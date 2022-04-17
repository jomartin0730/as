class RCM_Data():
    data_Draw_Ur_Pose_List = []
    data_Draw_Ur_Time_List = []
    data_Draw_Robot_Speed_List = []
    data_Draw_Ur_Radius_List = []
    data_Draw_Ur_Gripper_Motion_List = []
    data_Tcp_Clinet_List = {}
    #pc_Name = " "
    loaded_Motion_Data_By_Appearance_Rate = None
    ghost_Robot_Angle_List = []
    combined_Joint_Angle_Data = []
    motion_Row_Number = 0
    client_Connection_Check = 2
    way_To_Robot_Move = 'J'
    sql_Datas = []
    old_Process_Value = 0
    old_Product_Name = ""
    old_Product_Velocity = 0
    received_Data = "20210115_173618645459.ply:1:P:A01-1P-0226:12:50"
    pc_One_Ip = "192.168.0.101"
    curr_Pc_Ip_Adress = ""
    scheduler = []
    rcm_server = None
    rcm_client = None
    thread_rcm = None
    robot_Motions = {}
    fixgun_Motions = {}
    old_sql_List = None
    
    def data_Reset_Pose():
        RCM_Data.data_Draw_Ur_Pose_List = []
        RCM_Data.data_Draw_Ur_Time_List = []
        RCM_Data.data_Draw_Ur_Radius_List = []
        RCM_Data.save_Data_Joint_Angle_List = []
        RCM_Data.data_Draw_Ur_Appearance_Rate_List = []
        RCM_Data.data_Draw_Ur_Gripper_Motion_List = []

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
            if (moving_Cmd_ == 'L'):
                if (number == 0 or number == length_ - 1):
                    moving_Cmd = 'J'
                else:
                    moving_Cmd = 'L'
            elif (moving_Cmd_ == 'J'):
                moving_Cmd = 'J'
            Angles = "R" + moving_Cmd
            Angles += ''.join(angle)
            ### mm/s # =============================================================================================== #
            converted_Robot_Speed = RCM_Data.data_Calculate_Robot_Speed(speed[number])
            Angles += (str(gripper[number]) + converted_Robot_Speed + "0000")
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

    def data_Set_Fixgun_Motion_Integer_To_String(fixgun_Motion):
        converted_Data = ""
        cnt = 0
        for pos in fixgun_Motion: # pos = pick one side
            for motor in pos:
                cnt += 1
                converted_Data += str(cnt)
                for one in motor:
                    ione = int(one)
                    if (ione == 0):  # If rounded result is 0, It returns string as +000.000 that is fixed.
                        converted_Data += "+000"

                    elif ione > 0:  # If rounded result is positive number
                        if ione >= 100:
                            converted_Data += "+" + str(ione)
                        elif ione >= 10:
                            converted_Data += "+0" + str(ione)
                        else:
                            converted_Data += "+00" + str(ione)

                    else:  # If rounded result is negative number
                        inone = ione * -1
                        if inone >= 100:
                            converted_Data += "-" + str(inone)
                        elif inone >= 10:
                            converted_Data += "-0" + str(inone)
                        else:
                            converted_Data += "-00" + str(inone)

        return converted_Data

    def convert_Fixgun_Motion_From_Panel_PC(fixGunMotion):
        gunLength1 = fixGunMotion[1:5]
        gunDegree1 = fixGunMotion[5:9]
        gunLength2 = fixGunMotion[10:14]
        gunDegree2 = fixGunMotion[14:18]
        gunLength3 = fixGunMotion[19:23]
        gunDegree3 = fixGunMotion[23:27]
        gunLength4 = fixGunMotion[28:32]
        gunDegree4 = fixGunMotion[32:36]
        gunLength5 = fixGunMotion[37:41]
        gunDegree5 = fixGunMotion[41:45]
        gunLength6 = fixGunMotion[46:50]
        gunDegree6 = fixGunMotion[50:54]
        gunLength7 = fixGunMotion[55:59]
        gunDegree7 = fixGunMotion[59:63]
        gunLength8 = fixGunMotion[64:68]
        gunDegree8 = fixGunMotion[68:72]

        if gunLength1[0] == "+":
            gunLength1 = gunLength1.replace("+","")
        if gunLength2[0] == "+":
            gunLength2 = gunLength2.replace("+","")
        if gunLength3[0] == "+":
            gunLength3 = gunLength3.replace("+","")
        if gunLength4[0] == "+":
            gunLength4 = gunLength4.replace("+","")
        if gunLength5[0] == "+":
            gunLength5 = gunLength5.replace("+","")
        if gunLength6[0] == "+":
            gunLength6 = gunLength6.replace("+","")
        if gunLength7[0] == "+":
            gunLength7 = gunLength7.replace("+","")
        if gunLength8[0] == "+":
            gunLength8 = gunLength8.replace("+","")

        if gunDegree1[0] == "+":
            gunDegree1 = gunDegree1.replace("+","")
        if gunDegree2[0] == "+":
            gunDegree2 = gunDegree2.replace("+","")
        if gunDegree3[0] == "+":
            gunDegree3 = gunDegree3.replace("+","")
        if gunDegree4[0] == "+":
            gunDegree4 = gunDegree4.replace("+","")
        if gunDegree5[0] == "+":
            gunDegree5 = gunDegree5.replace("+","")
        if gunDegree6[0] == "+":
            gunDegree6 = gunDegree6.replace("+","")
        if gunDegree7[0] == "+":
            gunDegree7 = gunDegree7.replace("+","")
        if gunDegree8[0] == "+":
            gunDegree8 = gunDegree8.replace("+","")

        left_Fixed_Guns = []
        right_Fixed_Guns = []
        whole_Fixed_Guns = []

        gun_Num1 = [int(gunLength1), int(gunDegree1)]
        gun_Num2 = [int(gunLength2), int(gunDegree2)]
        gun_Num3 = [int(gunLength3), int(gunDegree3)]
        gun_Num4 = [int(gunLength4), int(gunDegree4)]
        gun_Num5 = [int(gunLength5), int(gunDegree5)]
        gun_Num6 = [int(gunLength6), int(gunDegree6)]
        gun_Num7 = [int(gunLength7), int(gunDegree7)]
        gun_Num8 = [int(gunLength8), int(gunDegree8)]

        left_Fixed_Guns.append(gun_Num1)
        left_Fixed_Guns.append(gun_Num2)
        left_Fixed_Guns.append(gun_Num3)
        left_Fixed_Guns.append(gun_Num4)
        right_Fixed_Guns.append(gun_Num5)
        right_Fixed_Guns.append(gun_Num6)
        right_Fixed_Guns.append(gun_Num7)
        right_Fixed_Guns.append(gun_Num8)

        whole_Fixed_Guns.append(left_Fixed_Guns)
        whole_Fixed_Guns.append(right_Fixed_Guns)
        return whole_Fixed_Guns
# ==================================================================================================================== #