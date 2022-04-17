import pymysql
from RCM.rcm_data import RCM_Data as rd
from RCM.rcm_flag import RCM_Flag as rf

class RCM_Sql():
    def __init__(self):
        self.host = '192.168.0.103'
        self.passwd = 'aA!12345'
        self.user = 'mgt'
        self.db = 'maviz'
        #if (rd.curr_Pc_Ip_Adress == rd.pc_One_Ip):
        self.table = 'motion_data'
        self.log_Table = 'Robot_log'
        # else:
        #     self.table = 'motion_data2'
        #     self.log_Table = 'Robot_log2'


        # self.host = '127.0.0.1'
        # self.passwd = 'qwop1290'
        # self.user = 'maviz_main'
        # self.db = 'db_motion_datas'
        # self.table = 'motion_data'
        # self.log_Table = 'Robot_log'

        self.charset = 'utf8'

    def connect_To_DB(self):
        conn = pymysql.connect(host=self.host, user=self.user, password=self.passwd, db=self.db, charset=self.charset)
        return conn

    def check_Db_On(self):
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = 'select product_Name from {}.{}'.format(self.db, self.table)
        cursor.execute(sql)
        conn.close()
        rf.FLAG_DATABASE_IS_ON = True

    def load_Pose_Data_With_Product_Name_From_DB(self, columnName):
        try:
            conn = self.connect_To_DB()
            cursor = conn.cursor()
            sql = 'select product_Name, motion_Data from {}.{} where product_Name="'"{}"'";'.format(self.db, self.table, columnName)
            cursor.execute(sql)
            rows = cursor.fetchall()
            name_value = rows[0][0]
            conn.close()
            return name_value
        except Exception as e:
            print("DB loading has an error : ", e)

    def load_Pose_Data_With_Appearance_Rate_From_DB(self, columnName):
        try:
            conn = self.connect_To_DB()
            cursor = conn.cursor()
            sql = 'select product_Name, motion_Data from {}.{} where product_Name="'"{}"'";'.format(self.db, self.table, columnName)
            cursor.execute(sql)
            rows = cursor.fetchall()
            angle_value = rows[0][1]
            conn.close()
            return angle_value
        except Exception as e:
            print("DB loading has an error : ", e)

    def load_Pose_Data_Names(self):
        list_Value = []
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = 'select product_Name from {}.{}'.format(self.db, self.table)
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            list_Value.append(list(row)[0])
        conn.close()
        return list_Value

    def save_Log_Data_To_DB(self, date, time, product_Name, velocity, painting):
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = 'insert into {}.{}(date, time, product_Name, velocity, painting)VALUES("'"{}"'", "'"{}"'", "'"{}"'", "'"{}"'", "'"{}"'")'.format(self.db, self.log_Table, date, time, product_Name, velocity, painting)
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def load_Robot_Motion_Names(self):
        list_Value = []
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = 'select product_Name from {}.{}'.format(self.db, self.table)
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            list_Value.append(list(row)[0])
        conn.close()
        return list_Value