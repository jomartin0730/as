import pymysql
from gcm_data import GCM_Data as gd
from gcm_flag import GCM_Flag as gf

class GCM_Sql():
    def __init__(self):
        self.host = '192.168.0.103'
        self.passwd = 'aA!12345'
        self.user = 'mgt'
        self.db = 'maviz'
        self.gun_Table = 'fixgun_motion'

        # self.host = '127.0.0.1'
        # self.passwd = 'aA!12345'
        # self.user = 'mgt'
        # self.db = 'maviz'
        # #self.table = 'motion_data'
        # #self.log_Table = 'Robot_log'
        # self.gun_Table = 'fixgun_motion'

        self.charset = 'utf8'

    def connect_To_DB(self):
        conn = pymysql.connect(host=self.host, user=self.user, password=self.passwd, db=self.db, charset=self.charset)
        return conn

    def check_Db_On(self):
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = 'select product_Name from {}.{}'.format(self.db, self.gun_Table)
        cursor.execute(sql)
        conn.close()
        gf.FLAG_DATABASE_IS_ON = True

    def load_Fixgun_Motion_Names(self):# 딕셔너리 형태로 제품이름과 모션 내용이 저장되어있음
        list_Value = []
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = 'select product_Name from {}.{}'.format(self.db, self.gun_Table)
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            list_Value.append(list(row)[0])
        conn.close()
        return list_Value

    def load_Fixgun_Names(self, columnName):# load only motion name
        try:
            conn = self.connect_To_DB()
            cursor = conn.cursor()
            sql = 'select product_Name, motion_Data from {}.{} where product_Name="'"{}"'";'.format(self.db, self.gun_Table, columnName)
            cursor.execute(sql)
            rows = cursor.fetchall()
            name_value = rows[0][0]
            conn.close()
            return name_value
        except Exception as e:
            print("DB loading has an error1 : ", e)

    def load_Fixgun_Motion(self, columnName):# load only motion
        try:
            conn = self.connect_To_DB()
            cursor = conn.cursor()
            sql = 'select product_Name, motion_Data from {}.{} where product_Name="'"{}"'";'.format(self.db, self.gun_Table, columnName)
            cursor.execute(sql)
            rows = cursor.fetchall()
            angle_value = rows[0][1]
            conn.close()
            return angle_value
        except Exception as e:
            print("DB loading has an error2 : ", e)

    def save_Pose_Data_To_DB(self,name,pose_data):
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = 'insert into {}.{}(product_Name, motion_Data)VALUES("'"{}"'","'"{}"'")'.format(self.db, self.gun_Table, name, pose_data)
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def send_Product_Name(self):
        # productData = []
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = 'select * from maviz.sg_log order by idx desc limit 1'
        cursor.execute(sql)
        rows = cursor.fetchall()
        # startTime = rows[0][1]
        # endTime = rows[0][2]
        pcode = rows[0][3]
        # paint = rows[0][6]
        # loading = rows[0][7]
        # painting = rows[0][9]
        # for row in rows:
        #     productData.append(list(row)[0])
        conn.commit()
        conn.close()
        return pcode