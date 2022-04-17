import time
import threading
from bl_op_cam import *
from bl_op_data import Bl_Op_Data as bod
from bl_op_flag import Bl_Op_Flag as bof

class Bl_Op_Multiple_Thread:

    def __init__(self):
        ps_Thread = threading.Thread(target=self.product_Simulation)
        ps_Thread.daemon = True
        ps_Thread.start()

        edc_Thread = threading.Thread(target=self.execute_Depth_Camera)
        edc_Thread.daemon = True
        edc_Thread.start()

        # rpi_Thread = threading.Thread(target=self.refresh_Panel_Image)
        # rpi_Thread.daemon = True
        # rpi_Thread.start()

    # TAG : Motion simulation
    def product_Simulation(self):
        while (True):
            if (bof.FLAG_PRODUCT_SIMULATION == True):
                bof.FLAG_PRODUCT_SIMULATION_AUX = True
                time.sleep(0.05)
            else:
                time.sleep(0.1)

    # TAG : Point cloud streaming
    def execute_Depth_Camera(self):
        while(True):
            if (bof.FLAG_KEEP_COLLECT_DEPTH_INFO == True):
                bod.bl_op_cam = Bl_Op_Cam()
                bod.bl_op_cam.execute()
            else:
                pass
            time.sleep(1)

    # def refresh_Panel_Image(self):
    #     panel_Image_Refresh_Count = 0
    #     while(True):
    #         panel_Image_Refresh_Count += 1
    #         if (panel_Image_Refresh_Count == 30):
    #             bof.FLAG_PANEL_REFRESH = True
    #             panel_Image_Refresh_Count = 0
    #         time.sleep(1)