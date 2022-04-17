class Bl_Op_Flag():
    FLAG_OP_SHUTDOWN =  False
    FLAG_DATA_FROM_SERVER = False
        ### NOTE : "서버시작" 버튼을 누르면 True로 바뀌고 "서버종료" 버튼을 누르면 False로 바뀐다.
    FLAG_SERVER_OPENED = False
    FLAG_CUT_DATA_RECEIVED_FROM_DB = False
        ### NOTE : Motion teach시(or load 후) Path를 그리는 상태
    FLAG_DRAWING_POINT_PATH = False
        ### NOTE : Motion path를 자동으로 그릴 때 현재 Pose가 마지막이 아니면 다음 Pose로 자동으로 넘기기 위한 Flag
    FLAG_SET_IKCONTROL_AT_NEXT_POSITION = False
        ### NOTE : 'T'를 누르면 True로 바뀌어 Sliderbar number를 바꿀 수 있음
    FLAG_CHANGE_SLIDEBAR_NUMBER = False
    FLAG_HIDE_INFROMATION_PANEL = True

        ### NOTE : 파일로부터 포인트 클라우드를 호출
    FLAG_GET_POINT_CLOUD = False
        ### NOTE : Point cloud를 불러왔을 때만 수행돼야 하는 함수에 대한 FLAG
    FLAG_POINT_CLOUD_IS_LOADED = False
        ### NOTE : 현재 현시되고 있는 Point cloud를 캡처(파일로 저장)
    FLAG_CAPTURE_CURRENT_POINT_CLOUD = False
        ### NOTE : Cache memory에서 Point cloud 삭제
    FLAG_DELETE_POINT_CLOUD = False
        ### NOTE : Point cloud를 삭제할 때 cache memory에 데이터가 올라가는 것을 제한.
    FLAG_RESTRICT_MAKE_POINT_CLOUD = False
        ### NOTE : FLAG_POINT_CLOUD_IS_LOADED가 초기화 버튼을 눌렀을 때에만 False로 바뀌도록 제한.
    FLAG_CONFIRM_TO_DELETE_UUID = False
        ### NOTE : FLAG_GET_CORE_PRODUCT_PLY가 초기화 버튼을 눌렀을 때에만 False로 바뀌도록 제한.
    FLAG_CONFIRM_TO_RESET_CORE_PRODUCT = False
        ### NOTE : DB(혹은 파일)에서 Motion이 로드됨을 표시
    FLAG_MOTION_LOADED = False
        ### NOTE : Point cloud를 bbox에 맞게 나머지 부분을 잘라내는 기능을 실행
    FLAG_TRIM_POINT_CLOUD_BY_BBOX = False
        ### NOTE : 편집한 Point cloud를 save 모듈의 dialog box로 저장하기 위한 Flag
    FLAG_SAVE_TRIMMED_POINT_CLOUD = False

        ### NOTE : 실시간 Point cloud 현시 on/off
    FLAG_GET_CAMERA_DATA = False
        ### NOTE : 카메라에서 받은 frame을 numpy화하여 cache 올리면 True로 바뀌어 다음 frame을 받을 수 있게 함
    FLAG_PLY_LOAD_FINISHED = False

        ### NOTE : 카메라로부터 frame을 받기 시작함 on/off
    FLAG_KEEP_COLLECT_DEPTH_INFO = False
        ### NOTE : '시뮬레이션'버튼을 누르면 0.05초마다 True로 바뀜 (FLAG_PRODUCT_SIMULATION_AUX가 True일 때 False로 바뀜)
    FLAG_PRODUCT_SIMULATION = False
        ### NOTE : FLAG_PRODUCT_SIMULATION가 True일 때 True로 바뀌어 0.05초마다 'length'만큼 product의 위치를 이동
    FLAG_PRODUCT_SIMULATION_AUX = False

    FLAG_PLYAXIS_ANCHOR_DROPPED = False

        ### NOTE : 생성한 Motion data를 Robot으로 송신할 때 True로 바뀜
    FLAG_SEND_ANGLE_DATA_TO_ROBOT = False
        ### NOTE : When you move the slide bar, It changes to True.
    FLAG_MOVE_IK_CONTROL = False

    # TAG : Edit mode
        ### NOTE : Motion revising 중 'NUMPAD_0'을 눌렀을 때 Edit mode로 가기 위한 Flag
    FLAG_EDIT_ONE_POSE = False
        ### NOTE : Motion을 자동으로 그리기 모드가 끝났을 때(현재 Pose가 마지막 pose) Edit mode에 의해 변화된 조건들을 초기화하기 위한 Flag
    FLAG_EDIT_MODE = False
        ### NOTE : Pose edit시 Edit된 Pose mesh를 생성하기 위해 modal을 열어주기 위한 Flag
    FLAG_POSE_EDITING_MODAL_OPEN = False
        ### NOTE : Pose edit시 Edit된 Pose mesh를 모두 생성 후 Path를 그릴 때 Edit에 맞는 동작을 > 할 수 있도록 현재 상태는 Edit mode라는 것을 알려주는 Flag
    FLAG_POSE_EDITING_STATE = False

    # TAG : Add mode
    FLAG_ADD_ONE_POSE = False
    FLAG_POSE_ADDING_MODAL_OPEN = False
    FLAG_POSE_ADDING_STATE = False
    # ========================================= #
    # NOTE : Undeveloped
    FLAG_ADDING_STATE_MOVE_PLYAXIS = False
    FLAG_ADDING_STATE_MOVE_PLYAXIS_AUX = False
    # ========================================= #

    # TAG : Delete mode
    FLAG_DELETE_ONE_POSE = False
    FLAG_POSE_DELETING_MODAL_OPEN = False
    FLAG_POSE_DELETING_STATE = False
    # Information # ================================================================================================== #
    # NOTE : ex) 5개 모션 중 1개를 지우면 반복문이 5회 반복하면서 data_Draw_Curr_Revising_Point_Number일 때의 Pose object를
    #            삭제한다. 이 때, 3번 모션이 지워지게 되면 4번이 3번 자리에 오게 되고 self.count_Pose_Number -= 1로 인해 4번이었던
    #            모션이 다시 Delete object 조건문에 들어가기 때문에 이를 방지하기 위해 아래의 Flag를 이용
    # 참고 : MavizHandler - draw_Pose_With_Deleting()
    FLAG_RESTRICT_DELETING_COUNT = False
    # ================================================================================================================ #

    FLAG_RESET_SLIDE_BAR = False

        ### NOTE : 모션만 초기화(Point cloud는 그대로 유지)
    FLAG_DELETE_MOTION_ONLY = False
    FLAG_RESTRICT_EVENT = False
        ### NOTE : Armature fk에 key frame삽입 명령
    FLAG_SIMULATION_WITH_ANIMATION = False
        ### NOTE : Simulation이 시작되고 목표 frame이 정해졌을 때 True가 되어 목표 frame이 감지되면 False로 바뀌며 Simulation 종료
    FLAG_WAIT_SIMULATION_END = False
    FLAG_SELECT_LMOVE = False
    FLAG_HIDE_IK_ROBOT_MESHES = False
    FLAG_GET_CORE_PRODUCT_PLY = False
    FLAG_MAKE_MOTION_BUTTON_PRESSED = False
        ### NOTE : 전체 Pose를 일정량만큼 동시에 이동시키기 위한 Flag
    FLAG_MODIFY_ALL_POSE = False
        ### NOTE : 이동된 포즈를 GUI에 그리는 동안 다음 pose에 대한 그리기 작업을 제한하기 위한 Flag
    FLAG_MODIFY_ALL_POSE_AUX = False

        ### NOTE : True >> 미세한 움직임, False >> 큰 움직임
    FLAG_CHANGE_MOVEMENT_RATIO = False
    FLAG_ZOOM_CAMERA = False
    FLAG_AUTO_CHANGE_SPEED_OF_REST_POINT = False
        ### NOTE : 로봇 제어 속도(시간제어/속도제어)를 변경하기 위한 Flag
    FLAG_MODIFY_SPEED = False

    # Information # ================================================================================================== #
    # NOTE : 1개 이상의 Pose가 존재할 때 S를 누르면 True.
    #        >> Slidebar를 움직이기 전까진 무한루프로 돌면서 plyAxis의 다음 위치를 예상
    FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT = False
    # ================================================================================================================ #

    # Information # ================================================================================================== #
    ''' ──────────────────────────────────────────────────────────────────────────
        Tracking mode는 Slidebar를 움직이면 종료된다. 
        (Slidebar를 수동으로 조작 or NUMPAD_0 : 새로운 Pose 생성)
        새로운 Pose 생성 시엔 FLAG_RESTRICT_TRACKING_OFF를 True로 바꾸어
        Tracking mode 종료 조건을 타지 않게 하여 Tracking teach를 지속할 수 있게 해준다.
    ────────────────────────────────────────────────────────────────────────── '''
    FLAG_RESTRICT_TRACKING_OFF = False
    FLAG_REST_POINT_EXIST = False
    FLAG_PANEL_CONTEXT_UPDATE = False

    FLAG_SQL_CONNECTION_ERROR = False
    FLAG_REVEAL_PANEL = False

        ### NOTE : 주기적으로 panel image를 새로고침.(새로고침 안하면 image가 cache에서 사라짐)
    FLAG_PANEL_REFRESH = False

    # TAG : Depth wall
    FLAG_DOT_FOUR = False
    FLAG_DOT_FIVE = False
    FLAG_DOT_SIX = False
    FLAG_DOT_SEVEN = False
    FLAG_DOT_EIGHT = False
    FLAG_DOT_NINE = False
    # ==================== #

    FLAG_MODIFY_BBOX_INFORMATION = False
    FLAG_MODIFY_PLYAXIS_INFORMATION = False

    # ================================================================================================================ #
    # NOTE : RCM code
    FLAG_ROBOT_MOTION_TEST = False # " RCM에서 시뮬레이션일 때는 로봇으로 모션 전송 안하도록 하기 위한 Flag 210823 삭제예정
    FLAG_ROBOT_DISCONNECTED = False
    FLAG_HOME_POSITIONING_ORDER = False
    FLAG_THREAD_SENDING_STATE = False
    FLAG_ROBOT_MOTION_DONE = False
    FLAG_MOTION_EXECUTED = False
    FLAG_FIRST_MOTION = False
    FLAG_START_SENDING_JOINT_ANGLE_DATA = False

    FLAG_RECV_OK = False
    FLAG_EMERGENCY = False
    FLAG_MOTION_FINISHED = False
    FLAG_GRIPPER = False
    # ================================================================================================================ #



'''
class Bl_Op_Flag():
    FLAG_OP_SHUTDOWN =  False
    FLAG_DATA_FROM_SERVER = False
    FLAG_CUT_DATA_RECEIVED_FROM_DB = False
    FLAG_DATA_RECEIVED_FROM_CAMERA = False
    FLAG_DRAWING_POINT_PATH = False
    FLAG_SET_IKCONTROL_AT_NEXT_POSITION = False
    FLAG_APPEARANCE_RATE = False
    FLAG_HIDE_INFROMATION_PANEL = True

    FLAG_GET_POINT_CLOUD = False # 파일에서 포인트 클라우드 호출
    FLAG_POINT_CLOUD_IS_LOADED = False # Point cloud를 불러왔을 때만 수행돼야 하는 함수에 대한 FLAG
    FLAG_CAPTURE_CURRENT_POINT_CLOUD = False
    FLAG_DELETE_POINT_CLOUD = False
    FLAG_RESTRICT_MAKE_POINT_CLOUD = False

    FLAG_GET_CAMERA_DATA = False # 실시간 Point cloud 현시 on/off
    FLAG_PLY_LOAD_FINISHED = False # 카메라에서 받은 frame을 numpy화하여 cache 올리면 True로 바뀌어 다음 frame을 받을 수 있게 함
    FLAG_KEEP_COLLECT_DEPTH_INFO = False # 카메라로부터 frame을 받기 시작함 on/off
    FLAG_SETDEFAULT_UUID = False
    FLAG_PRODUCT_SIMULATION = False
    FLAG_PRODUCT_SIMULATION_AUX = False

    FLAG_SEND_ANGLE_DATA_TO_ROBOT = False
    FLAG_MOVE_IK_CONTROL = False
    FLAG_ADD_OVER_LENGTH_ERROR = False

    FLAG_EDIT_ONE_POSE = False
    FLAG_EDIT_MODE = False
    FLAG_POSE_EDITING_MODAL_OPEN = False  # Pose add시 Add된 Pose mesh를 생성하기 위해 modal을 열어주기 위한 FLAG
    FLAG_POSE_EDITING_STATE = False       # Pose add시 Add된 Pose mesh를 모두 생성 후 Path를 그릴 때 Add에 맞는 동작을
                                          # > 할 수 있도록 현재 상태는 Add라는 것을 알려주는 FLAG

    FLAG_ADD_ONE_POSE = False
    FLAG_POSE_ADDING_MODAL_OPEN = False
    FLAG_POSE_ADDING_STATE = False
    FLAG_ADDING_STATE_MOVE_PLYAXIS = False

    FLAG_DELETE_ONE_POSE = False
    FLAG_POSE_DELETING_MODAL_OPEN = False
    FLAG_POSE_DELETING_STATE = False
    FLAG_RESTRICT_DELETING_COUNT = False

    FLAG_MOTION_LOADED = False
    FLAG_RESET_SLIDE_BAR = False
    FLAG_RESTRICT_EVENT = False
    FLAG_SIMULATION_WITH_ANIMATION = False
    FLAG_CHANGE_MOVEMENT_RATIO = False
    FLAG_WAIT_SIMULATION_END = False
    FLAG_HIDE_IK_ROBOT_MESHES = False
    FLAG_AUTO_CHANGE_SPEED_OF_REST_POINT = False
    FLAG_SELECT_JMOVE = False
    FLAG_GET_CORE_PRODUCT_PLY = False
    FLAG_PLYAXIS_ANCHOR_DROPPED = False
    FLAG_MAKE_MOTION_BUTTON_PRESSED = False
    FLAG_SELECT_LMOVE = False
    FLAG_CLEAR = False

    FLAG_ROBOT_MOTION_TEST = False
    FLAG_DELETE_MOTION_ONLY = False
    FLAG_TEACHING_STATE = False
    FLAG_ROBOT_DISCONNECTED = False
    FLAG_MOTION_DELETE_TO_LOADED_DATA = False
    FLAG_MOTION_ADD_TO_LOADED_DATA = False
    FLAG_RECV_OK = False
    FLAG_EMERGENCY = False

    FLAG_THREAD_SENDING_STATE = False
    FLAG_START_SENDING_JOINT_ANGLE_DATA = False

    FLAG_MOVE_IKCONTROL_GHOST_BY_POSE_LIST = False
    FLAG_GET_JOINT_ANGLE_OF_GHOST_ROBOT = False
    FLAG_SET_APPEARANCE_RATE_MOTION_LOADED = False
    FLAG_UPDATE_LOADED_MOTION_NAME = False
    FLAG_PREDICTING_CONVEYOR_BELT_MOVEMENT = False
    FLAG_REST_POINT_EXIST = False
    FLAG_PANEL_CONTEXT_UPDATE = False

    FLAG_MOTION_FINISHED = False
    FLAG_GRIPPER = False
    FLAG_TEMP_DATA = False
    FLAG_CONFIRM_SAVE = True
    FLAG_SQL_CONNECTION_ERROR = False

    FLAG_DOT_FOUR = False
    FLAG_DOT_FIVE = False
    FLAG_DOT_SIX = False
    FLAG_DOT_SEVEN = False
    FLAG_DOT_EIGHT = False
    FLAG_DOT_NINE = False

    FLAG_ZOOM_CAMERA = False
    FLAG_MODIFY_BBOX_INFORMATION = False
    FLAG_MODIFY_PLYAXIS_INFORMATION = False
'''