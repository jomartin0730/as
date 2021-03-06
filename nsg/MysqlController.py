import pymysql
import sys
import cv2
import numpy as np
import base64
import JsonLoader

class MysqlController:
    def __init__(self):
        self.sql_json = JsonLoader.JsonLoader()
        json_data = self.sql_json.load_data("Mysql")
        self.host = json_data['db']['ip']
        self.id = json_data['db']['id']
        self.pw = json_data['db']['passwd']
        self.db_name = json_data['db']['dbname']
        self.conn = None
        self.curs = None
        self.bConnect = False
        self.bMode = False
        self.rno = 0
    # def __init__(self, host, id, pw, db_name):
    #     '''
    #     self.conn = pymysql.connect(host=host, user= id, port=333, password=pw, db=db_name,charset='utf8')
    #     #self.conn = pymysql.connect(host=host, user= id,  password=pw, db=db_name,charset='utf8')
    #     self.curs = self.conn.cursor()
    #     self.bConnect = True
    #     self.bMode = False
    #     '''
    #     self.host = host
    #     self.id = id
    #     self.pw = pw
    #     self.db_name = db_name
    #     self.conn = None
    #     self.curs = None
    #     self.bConnect = False
    #     self.bMode = False
    
    def setRno(self, rno):
        self.rno = rno

    def db_connect(self):
        try:
            #self.conn = pymysql.connect(host=self.host, user=self.id, port=333, password=self.pw, db=self.db_name, charset='utf8')
            self.conn = pymysql.connect(host=self.host, user=self.id, password=self.pw, db=self.db_name, charset='utf8')
            self.curs = self.conn.cursor()
            self.bConnect = True
            self.bMode = False
        except Exception as e:
            print('Connect Error : ', e)

    def db_disconnect(self):
        if self.conn is not None:
            self.bConnect = False
            self.bMode = False
            self.conn.close()

    def check_data(self, pcode):
        if self.bConnect :
            try:
                check_result = True
                sql = """SELECT count(*) FROM partname WHERE pcode = %s"""
                args = (pcode)
                self.curs.execute(sql,args)
                rows = self.curs.fetchall()
                result = rows[0][0]
                if result > 0 :
                    check_result = False
                else :
                    check_result = True
                return check_result
            finally:
                #self.conn.close()
                pass
        else :
            # send message to parent
            print('DB is Not connected!!!!')


    def insert_partname(self, pname, ccode, pcode):    

        if self.bConnect :
            try:
                sql = """INSERT INTO partname (name,ccode,pcode) VALUES (%s,%s,%s)"""
                args = (pname,ccode,pcode)
                self.curs.execute(sql,args)
                self.conn.commit()
            finally:
                pass
                #self.conn.close()
        else :
            # send message to parent 
            print('DB is Not connected!!!!')

    def insert_partimage(self, pcode, frame):
        # ????????? ???????????? ????????? ?????? ????????? String?????? ????????? ????????? ???.
        if self.bConnect :
            try:
                result, e_img = cv2.imencode('.jpg', frame)
                e_img = np.array(e_img)
                e_img_array_data = e_img.tostring()
                e_img_stringData = base64.b64encode(e_img_array_data)
                e_img_stringData = e_img_stringData.decode()
                h, w, sz = frame.shape

                #sql = """SELECT pid FROM partname WHERE name = %s"""
                sql = """SELECT pid FROM partname WHERE pcode = %s"""
                args = (pcode)
                self.curs.execute(sql, args)
                rows = self.curs.fetchall()
                pid = rows[0][0]
                print(pid)
                sql = """INSERT INTO partimage (pid,image,size) VALUES (%s,%s,%s)"""
                args = (pid,e_img_stringData,sz)
                self.curs.execute(sql,args)
                self.conn.commit()
            finally:
                #self.conn.close()
                pass
        else : 
            # send message to parent 
            print('DB is Not connected!!!!')

    def modify_partimage(self, pcode, frame):
        # ????????? ???????????? ????????? ?????? ????????? String?????? ????????? ????????? ???.
        if self.bConnect :
            try:
                result, e_img = cv2.imencode('.jpg', frame)
                e_img = np.array(e_img)
                e_img_array_data = e_img.tostring()
                e_img_stringData = base64.b64encode(e_img_array_data)
                e_img_stringData = e_img_stringData.decode()
                h, w, sz = frame.shape

                sql = """SELECT pid FROM partname WHERE pcode = %s"""
                args = (pcode)
                self.curs.execute(sql, args)
                rows = self.curs.fetchall()
                pid = rows[0][0]
                print(pid)
                sql = """UPDATE partimage SET image=%s,size=%s WHERE pid = %s"""
                args = (pid,e_img_stringData,sz)
                self.curs.execute(sql,args)
                self.conn.commit()
            finally:
                #self.conn.close()
                pass
        else :
            # send message to parent
            print('DB is Not connected!!!!')

    #???????????? ???????????? ??????
    def select_partimage(self, pcode):
        # ????????? ???????????? ????????? ?????? ????????? String?????? ????????? ????????? ???.

        if self.bConnect :
            try:
                #sql = """SELECT image FROM partimage WHERE pid = (SELECT pid FROM partname where name = %s)"""
                #sql = """SELECT image FROM partimage WHERE pid = (SELECT pid FROM partname where pcode = %s)"""
                sql = """SELECT A.image, B.name, B.ccode FROM partimage as A, partname as B WHERE A.pid = B.pid AND A.pid = (SELECT pid FROM partname where pcode = %s)"""
                args = (pcode)
                self.curs.execute(sql,args)
                rows = self.curs.fetchall()
                img = rows[0][0]
                name = rows[0][1]
                color = rows[0][2]
                d_img = base64.decodebytes(img)
                d_img = np.fromstring(d_img,np.uint8)
                decode_img = cv2.imdecode(d_img, 1)

                return decode_img,name,color
            finally:
                #self.conn.close()
                pass
        else :
            # send message to parent
            print('DB is Not connected!!!!')

    #detect ??? ???????????? ????????? ??????
    def load_image(self, pcode) :

        if len(pcode) < 12 :
            sql_pcode = pcode[:3] + '-' + pcode[3:5] + "-" + pcode[5:]
        else :
            sql_pcode = pcode

        if self.bConnect:
            try:
                #print(sql_pcode)
                #sql = """SELECT A.image, B.name, B.state FROM partimage as A, partname as B WHERE A.pid = B.pid AND A.pid = (SELECT pid FROM partname where pcode = %s)"""
                sql = """SELECT name, state, speed FROM partname WHERE pcode = %s"""
                #sql = """SELECT name, state FROM partname WHERE pcode = %s"""
                args = (sql_pcode)
                self.curs.execute(sql, args)
                rows = self.curs.fetchall()
                #print("rows ?????? :", rows)
                #print("rows ?????? : " , len(rows))
                name, state, speed = None, None, None
                if len(rows) > 0:
                    name = rows[0][0]
                    state = rows[0][1]
                    speed = rows[0][2]
                    return name, state, speed
                    #return name, state
                else :
                    #print("db ????????? ??????")
                    pass
                return name, state, speed
                #return name, state
            finally:
                # self.conn.close()
                pass
        else:
            # send message to parent
            print('DB is Not connected!!!!')

    def change_image(self, pcode, frame) :
        if self.bConnect:
            try:
                sql = """SELECT pid FROM partname WHERE pcode = %s"""
                args = (pcode)
                self.curs.execute(sql, args)
                rows = self.curs.fetchall()
                pid = rows[0][0]
                print(pid)
                sql = """UPDATE partimages SET images = %s WHERE pid = %s"""
                args = (frame, pid)
                self.curs.execute(sql, args)
                rows = self.curs.fetchall()
                print(rows)
            finally:
                # self.conn.close()
                pass
        else:
            # send message to parent
            print('DB is Not connected!!!!')
    
    def load_product_data(self, pcode):
        result = None
        if self.bConnect:
            try:
                if self.rno == 1:
                    sql = """SELECT * FROM product_data1 WHERE name = %s"""
                else :
                    sql = """SELECT * FROM product_data2 WHERE name = %s"""
                args = (pcode)
                self.curs.execute(sql, args)
                rows = self.curs.fetchall()
                #print(rows)
                result = rows
            finally:
                # self.conn.close()
                pass
            
            return result
        else:
            # send message to parent
            print('DB is Not connected!!!!')