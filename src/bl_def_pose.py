class Bl_Def_Pose():

    def __init__(self):
        self.pose_Number = 0
        ### NOTE >> 0 : velo/accel, 1 : time # =============== #
        self.robot_Operate_Data_Control_Speed = 0
        # ==================================================== #
        ### NOTE >> 0 : Jmove, 1 : Lmove
        self.robot_Operate_Data_Moving_State = 0
        # ==================================================== #
        self.mesh_Data = None
        self.ik_Pose_Data = []
        self.fk_Pose_Data = []
        self.robot_Operate_Data_Velocity = 0
        self.robot_Operate_Data_Converted_Velocity = 0
        self.robot_Operate_Data_Acceleration = 0
        self.robot_Operate_Data_Radius = 0
        self.robot_Operate_Data_Gripper = 0

    def __del__(self):
        self.pose_Number = 0
        self.robot_Operate_Data_Control_Speed = 0
        self.robot_Operate_Data_Moving_State = 0
        self.mesh_Data = None
        self.ik_Pose_Data = []
        self.fk_Pose_Data = []
        self.robot_Operate_Data_Velocity = 0
        self.robot_Operate_Data_Converted_Velocity = 0
        self.robot_Operate_Data_Acceleration = 0
        self.robot_Operate_Data_Radius = 0
        self.robot_Operate_Data_Gripper = 0

    def combine_Data_Of_Object(self, cmd):
        # ============================================== #
        # NOTE : cmd = 0 >> Ik motion
        # NOTE : cmd = 1 >> Fk motion
        # ============================================== #
        motion_Data_Pack = []
        motion_Data_Pack.append(self.robot_Operate_Data_Control_Speed)
        motion_Data_Pack.append(self.robot_Operate_Data_Moving_State)
        if (cmd == 0):
            for ele in self.ik_Pose_Data:
                motion_Data_Pack.append(ele)
        else:
            for ele in self.fk_Pose_Data:
                motion_Data_Pack.append(ele)
        motion_Data_Pack.append(self.robot_Operate_Data_Velocity)
        motion_Data_Pack.append(self.robot_Operate_Data_Converted_Velocity)
        motion_Data_Pack.append(self.robot_Operate_Data_Acceleration)
        motion_Data_Pack.append(self.robot_Operate_Data_Radius)
        motion_Data_Pack.append(self.robot_Operate_Data_Gripper)

        return motion_Data_Pack


    def print_Info(self):
        print("pose_Number : ", self.pose_Number)
        print("robot_Operate_Data_Control_Speed : ", self.robot_Operate_Data_Control_Speed)
        print("robot_Operate_Data_Moving_State : ", self.robot_Operate_Data_Moving_State)
        print("mesh_Data : ", self.mesh_Data)
        print("ik_Pose_Data : ", self.ik_Pose_Data)
        print("fk_Pose_Data : ", self.fk_Pose_Data)
        print("robot_Operate_Data_Velocity : ", self.robot_Operate_Data_Velocity)
        print("robot_Operate_Data_Converted_Velocity : ", self.robot_Operate_Data_Converted_Velocity)
        print("robot_Operate_Data_Acceleration : ", self.robot_Operate_Data_Acceleration)
        print("robot_Operate_Data_Radius : ", self.robot_Operate_Data_Radius)
        print("robot_Operate_Data_Gripper : ", self.robot_Operate_Data_Gripper)
        print(" ")