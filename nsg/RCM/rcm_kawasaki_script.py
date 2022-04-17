from RCM.rcm_flag import RCM_Flag as rf

class kawasaki_Script(object):
    def __init__(self):
        self.command_Line_Kawasaki = ''
        self.order_STANDBY = '0'
        self.order_JMOVE = 'J'
        self.order_HOME = 'H'
        self.order_EMERGENCY = 'B'
        self.order_PAINTING_GUN_ON = '1'
        self.order_PAINTING_GUN_OFF = '2'

        # self.order_EXECUTE = 'E'
        # self.order_SENDING_FINISHED = 'F'
        #self.order_CLEAR = 'C'
        # self.order_SPEEDUP = 'U'
        # self.order_NORMALSPEED = 'N'
        # self.order_SPEEDDOWN = 'D'

    def STANDBY(self):
        self.command_Line_Kawasaki = self.order_STANDBY

    def JMOVE(self, angle):
        self.command_Line_Kawasaki = angle

    def HOME(self):
        self.command_Line_Kawasaki = self.order_HOME

    def EMERGENCY(self):
        self.command_Line_Kawasaki = self.order_EMERGENCY

    def PAINTING_GUN(self):
        if (rf.FLAG_GUN_SPRAYING_ON == True):
            self.command_Line_Kawasaki = self.order_PAINTING_GUN_ON
        else:
            self.command_Line_Kawasaki = self.order_PAINTING_GUN_OFF


    # def EXECUTE(self):
    #     self.command_Line_Kawasaki = self.order_EXECUTE

    # def CLEAR(self):
    #     self.command_Line_Kawasaki = self.order_CLEAR

    # def SENDING_FINISHED(self):
    #     self.command_Line_Kawasaki = self.order_SENDING_FINISHED

    # def SPEEDUP(self):
    #     self.command_Line_Kawasaki = self.order_SPEEDUP

    # def NORMALSPEED(self):
    #     self.command_Line_Kawasaki = self.order_NORMALSPEED

    # def SPEEDDOWN(self):
    #     self.command_Line_Kawasaki = self.order_SPEEDDOWN

