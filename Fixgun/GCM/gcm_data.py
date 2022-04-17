from gcm_flag import GCM_Flag as gf

class GCM_Data():
    data_Tcp_Clinet_List = {}
    client_Connection_Check = 2
    sql_Datas = []
    gcm_server = None
    gcm_client = None
    thread_gcm = None
    fixgun_Motions = {}
    #old_sql_List = None

    def data_Set_Motion_Length_Protocol(length):
        if (len(length) == 1):
            Length = '0' + length
        else:
            Length = length
        return Length

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