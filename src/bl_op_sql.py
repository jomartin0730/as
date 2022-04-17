import pymysql
from bl_op_data import Bl_Op_Data as bod
from bl_op_flag import Bl_Op_Flag as bof

class Bl_Op_Sql():
    def __init__(self):
        self.host = '192.168.0.103'
        self.passwd = 'aA!12345'
        self.user = 'mgt'
        self.db = 'maviz'
        if (bod.data_Info_Curr_Pc_Ip_Adress == bod.data_Info_Pc_One_Ip):
            self.table = 'motion_data'
            self.log_Table = "Robot_log"
        else:
            self.table = 'motion_data2'
            self.log_Table = "Robot_log2"
        self.charset = 'utf8'

    def connect_To_DB(self):
        conn = pymysql.connect(host=self.host, user=self.user, password=self.passwd, db=self.db, charset=self.charset)
        return conn

    # TAG : Motion save
    def save_Motion_Data_To_DB(self,name,pose_data):
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = 'insert into {}.{}(product_Name, motion_Data)VALUES("'"{}"'","'"{}"'")'.format(self.db, self.table, name, pose_data)
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def update_Pose_Data_To_DB(self, name, pose_data):
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = "UPDATE {}.{} SET motion_Data = "'"{}"'" WHERE product_Name = "'"{}"'"".format(self.db, self.table, pose_data, name)
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def load_Pose_Data_From_DB(self, columnName):
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = 'select product_Name, motion_Data from {}.{} where product_Name="'"{}"'";'.format(self.db, self.table, columnName)
        cursor.execute(sql)
        rows = cursor.fetchall()
        angle_value = rows[0][1]
        conn.close()
        return angle_value

    def pose_Delete(self, columnName):
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = 'delete from {}.{} where product_Name="'"{}"'";'.format(self.db, self.table, columnName)
        cursor.execute(sql)
        conn.commit()

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

    def save_Log_Data_To_DB(self, date, time, product_Name, velocity, painting):
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = 'insert into {}.{}(date, time, product_Name, velocity, painting)VALUES("'"{}"'", "'"{}"'", "'"{}"'", "'"{}"'", "'"{}"'")'.format(self.db, self.log_Table, date, time, product_Name, velocity, painting)
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def load_Pose_Data_Names(self):
        list_Value = []
        try:
            conn = self.connect_To_DB()
            cursor = conn.cursor()
            sql = 'select product_Name from {}.{}'.format(self.db, self.table)
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                list_Value.append(list(row)[0])
            conn.close()
        except:
            bof.FLAG_SQL_CONNECTION_ERROR = True
            print("├─────────────────────────────────────┤")
            print("│ Sql has an error. Check connection  │")
            print("│ > Data will be saved to a file.     │")
            print("├─────────────────────────────────────┤")
        return list_Value

    def print_Motion_List(self):
        list_Value = []
        conn = self.connect_To_DB()
        cursor = conn.cursor()
        sql = 'select product_Name from {}.{}'.format(self.db, self.table)
        cursor.execute(sql)
        rows = cursor.fetchall()
        for i in rows:
            val1 = "{}".format(i[0])
            val2 = "{}".format(i[0])
            val3 = " "
            list_pack = (val1, val2, val3)
            list_Value.append(list_pack)
        conn.close()
        return list_Value
