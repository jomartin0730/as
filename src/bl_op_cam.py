import os
import cv2
import time
import math
import gzip
import numpy as np
import pyrealsense2 as rs
from numpy.lib.recfunctions import unstructured_to_structured as uts
from bl_op_flag import Bl_Op_Flag as bof
from bl_op_data import Bl_Op_Data as bod

class AppState:

    def __init__(self, *args, **kwargs):
        self.WIN_NAME = 'RealSense'
        self.pitch, self.yaw = math.radians(-10), math.radians(-15)
        self.translation = np.array([0, 0, -1], dtype=np.float32)
        self.distance = 2
        self.prev_mouse = 0, 0
        self.mouse_btns = [False, False, False]
        self.paused = False
        self.decimate = 1
        self.scale = True
        self.color = True
        self.num = 0

    def reset(self):
        self.pitch, self.yaw, self.distance = 0, 0, 2
        self.translation[:] = 0, 0, -1

    @property
    def rotation(self):
        Rx, _ = cv2.Rodrigues((self.pitch, 0, 0))
        Ry, _ = cv2.Rodrigues((0, self.yaw, 0))
        return np.dot(Ry, Rx).astype(np.float32)

    @property
    def pivot(self):
        return self.translation + np.array((0, 0, self.distance), dtype=np.float32)

# TAG : Point cloud streaming
class Bl_Op_Cam():

    def __init__(self):
        print("Depth camera initialization is started...")
        self.pipeline = rs.pipeline()
        self.pc = rs.pointcloud()
        self.config = rs.config()
        self.state = AppState()
        self.align = None
        self.align_to = None
        self.get_Aligned_Frame = True

        # TAG : Intel L515
        self.depth_Width = 1024
        self.depth_Height = 768
        self.color_Width = 1280
        self.color_Height = 720
        self.fps = 30

        # TAG : Intel D435
        # self.depth_Width = 640
        # self.depth_Height = 480
        # self.color_Width = 640
        # self.color_Height = 480
        # self.fps = 6

        depth_Resolution = self.depth_Width * self.depth_Height
        color_Resolution = self.color_Width * self.color_Height
        if (depth_Resolution == color_Resolution):
            self.get_Aligned_Frame = False

        context = rs.context()
        connect_device = None
        try:
            if context.devices[0].get_info(rs.camera_info.name).lower() != 'platform camera':
                connect_device = context.devices[0].get_info(rs.camera_info.serial_number)

            self.config.enable_device(connect_device)

            self.config.enable_stream(rs.stream.depth, self.depth_Width, self.depth_Height, rs.format.z16, self.fps)
            self.config.enable_stream(rs.stream.color, self.color_Width, self.color_Height, rs.format.bgr8, self.fps)
            print("Depth camera is ready")
        except:
            bof.FLAG_KEEP_COLLECT_DEPTH_INFO = False
            print("┌─ * * * ────────────────────────────┐")
            print("│ Fail to connect with depth camera. │")
            print("│ Check connection status of it.     │")
            print("└──────────────────────────── * * * ─┘")

    def __del__(self):
        print("┌──────────────────────────────────────┐")
        print('│ Collecting of depth info is stopped. │')
        print("└──────────────────────────────────────┘")

    def view(self, v):
        """apply view transformation on vector array"""
        return np.dot(v - self.state.pivot, self.state.rotation) + self.state.pivot - self.state.translation

    def execute(self):
        print("┌─────────────────────────────────┐")
        print('│ Collecting depth information... │')
        print("└─────────────────────────────────┘")
        try:
            self.pipeline.start(self.config)
            bod.data_Pc_Camera_Type = "L515"
            # bod.data_Pc_Removing_Indexes = [num for num in range(0, 700000)]
            print("  > Camera type : Intel L515")
        except:
            self.depth_Width = 640
            self.depth_Height = 480
            self.color_Width = 640
            self.color_Height = 480
            self.fps = 6

            self.config.enable_stream(rs.stream.depth, self.depth_Width, self.depth_Height, rs.format.z16, self.fps)
            self.config.enable_stream(rs.stream.color, self.color_Width, self.color_Height, rs.format.bgr8, self.fps)
            bod.data_Pc_Camera_Type = "D435"
            # bod.data_Pc_Removing_Indexes = [num for num in range(0, 200000)]
            print("  > Camera type : Intel D435")
            try:
                self.pipeline.start(self.config)
            except:
                print("┌─ * * * ──────────────────────────────────────┐")
                print("│ There is no signal sended from depth camera. │")
                print("│ Check connection status of camera.           │")
                print("└────────────────────────────────────── * * * ─┘")
                bof.FLAG_KEEP_COLLECT_DEPTH_INFO = False
                del bod.bl_op_cam
                return
        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)

        while (bof.FLAG_KEEP_COLLECT_DEPTH_INFO == True):
            if (bof.FLAG_PLY_LOAD_FINISHED == True):
                bod.s_Time = time.time()
                frames = self.pipeline.wait_for_frames()

                if (self.get_Aligned_Frame):
                    # ============================================================================================ #
                    # NOTE : Use "aligned frames" when the resolution of Depth frame and color frame is different.
                    # ============================================================================================ #
                    aligned_frames = self.align.process(frames)
                    depth_frame = aligned_frames.get_depth_frame()
                    color_frame = aligned_frames.get_color_frame()
                    color_image = np.array(color_frame.get_data())
                    ################################################################################################

                else:
                    # ============================================================================================ #
                    # NOTE : Use "frame" when the resolution of Depth frame and color frame is same.
                    # ============================================================================================ #
                    depth_frame = frames.get_depth_frame()
                    color_frame = frames.get_color_frame()
                    color_image = np.array(color_frame.get_data())
                    ################################################################################################

                # self.pc.map_to(color_frame)
                points = self.pc.calculate(depth_frame)

                vertices = np.asanyarray(points.get_vertices()).view(np.float32).reshape(-1, 3)
                # vertices = self.view(verts)

                color = color_image.reshape(-1, 3)

                point_Cloud_Np_Data = np.append(vertices, color, axis=1)
                custom_type = np.dtype(
                    [('x', '<f4'), ('y', '<f4'), ('z', '<f4'), ('blue', 'u1'), ('green', 'u1'), ('red', 'u1')])
                points = uts(point_Cloud_Np_Data, dtype=custom_type)

                # TAG : Capture point cloud
                if (bof.FLAG_CAPTURE_CURRENT_POINT_CLOUD == True):
                    print(" ")
                    print("┌──────────────────────────────────┐")
                    print('│ Capture operation in progress... │')
                    print("└──────────────────────────────────┘")
                    bof.FLAG_CAPTURE_CURRENT_POINT_CLOUD = False
                    bod.data_Set_Save_Compressed_Point_Cloud(points)
                    print(" > Point cloud capture complete\n")

                bod.data_Pc_Point_Cloud_Data = points
                bof.FLAG_GET_CAMERA_DATA = True
                bof.FLAG_PLY_LOAD_FINISHED = False
            else:
                time.sleep(0.01)

        self.pipeline.stop()
        print("Pipeline terminated successfully.")
        bof.FLAG_DELETE_POINT_CLOUD = True
# ==================================================================================================================== #