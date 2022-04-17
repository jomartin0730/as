class partClass():
    def __init__(self, name):
        self.cname = name
        self.w = 0
        self.h = 0
        self.sa = None  # start area 1
        self.tw = None  # tracking window 1

    def rectContains(self, rect, pt):
        logic = rect[0] < pt[0] < rect[2] and rect[1] < pt[1] < rect[3]
        return logic

    def isStartArea(self, pt):
        return self.rectContains(self.sa, pt)

    def getTW(self):
        return self.tw

    def setTW(self, rect):
        self.tw = rect

    def setSA(self, rect):
        self.sa = rect

    def getSA(self):
        return self.sa

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def toStr(self):
        return str(self.sa) + ' : ' + str(self.tw)


class partClassInfo():
    def __init__(self):

        p0242_1 = partClass('A011P0242#1') #데스크 측판 DSA200
        p0242_1['w'] = 80
        p0242_1['height'] = 120
        p0242_1.setSA([560, 10, 900, 520])
        p0242_1.setTW([560, 20, 860, 440])
        p0242_1['start'] = 18
        p0242_1['end'] = 25
        p0242_1['ready'] = 6

        b0084_1 = partClass('A011B0084#1') #수직 덕트 0101
        b0084_1['w'] = 40
        b0084_1['height'] = 70
        b0084_1.setSA([560, 10, 900, 520])
        b0084_1.setTW([560, 20, 860, 440])
        b0084_1['start'] = 20
        b0084_1['end'] = 26
        b0084_1['ready'] = 10

        b3834_1 = partClass('A011B3834#1') #하우징 1400
        b3834_1['w'] = 80
        b3834_1['height'] = 120
        b3834_1.setSA([560, 10, 900, 520])
        b3834_1.setTW([560, 20, 860, 440])
        b3834_1['start'] = 9
        b3834_1['end'] = 11
        b3834_1['ready'] = 7

        d2007_1 = partClass('A011D2007#1') #서포터 스크린
        d2007_1['w'] = 80
        d2007_1['height'] = 120
        d2007_1.setSA([560, 10, 900, 520])
        d2007_1.setTW([560, 20, 860, 440])
        d2007_1['start'] = 9
        d2007_1['end'] = 11
        d2007_1['ready'] = 7

        s0797_1 = partClass('STCGPG0000797#1') #서포터 스크린
        s0797_1['w'] = 80
        s0797_1['height'] = 120
        s0797_1.setSA([560, 10, 900, 520])
        s0797_1.setTW([560, 20, 860, 440])
        s0797_1['start'] = 9
        s0797_1['end'] = 11
        s0797_1['ready'] = 7

        d0055_1 = partClass('A011D0055#1') #서포터 스크린
        d0055_1['w'] = 80
        d0055_1['height'] = 120
        d0055_1.setSA([560, 10, 900, 520])
        d0055_1.setTW([560, 20, 860, 440])
        d0055_1['start'] = 12
        d0055_1['end'] = 14
        d0055_1['ready'] = 10

        d0048_1 = partClass('A011D0048#1') #힌지
        d0048_1['w'] = 80
        d0048_1['height'] = 120
        d0048_1.setSA([560, 10, 900, 520])
        d0048_1.setTW([560, 20, 860, 440])
        d0048_1['start'] = 9
        d0048_1['end'] = 11
        d0048_1['ready'] = 7

        b2541_1 = partClass('A011B2541#1') #가림판 1인용
        b2541_1['w'] = 80
        b2541_1['height'] = 100
        b2541_1.setSA([560, 10, 900, 520])
        b2541_1.setTW([560, 20, 860, 440])
        b2541_1['start'] = 9
        b2541_1['end'] = 11
        b2541_1['ready'] = 7

        p3240_1 = partClass('A011P3240#1') #가림판 1인용
        p3240_1['w'] = 80
        p3240_1['height'] = 120
        p3240_1.setSA([560, 10, 900, 520])
        p3240_1.setTW([560, 20, 860, 440])
        p3240_1['start'] = 9
        p3240_1['end'] = 11
        p3240_1['ready'] = 7

        p0223_1 = partClass('A011P0223#1') 
        p0223_1['w'] = 100
        p0223_1['height'] = 140
        p0223_1.setSA([560, 10, 900, 520])
        p0223_1.setTW([560, 20, 860, 440])
        p0223_1['start'] = 9
        p0223_1['end'] = 11
        p0223_1['ready'] = 7

        d2006_1 = partClass('A011D2006#1') 
        d2006_1['w'] = 100
        d2006_1['height'] = 140
        d2006_1.setSA([560, 10, 900, 520])
        d2006_1.setTW([560, 20, 860, 440])
        d2006_1['start'] = 9
        d2006_1['end'] = 11
        d2006_1['ready'] = 7

####################################################################################
################2호기###############################################################
####################################################################################

        p0242_2 = partClass('A011P0242#2') #데스크 측판 DSA200
        p0242_2['w'] = 80
        p0242_2['height'] = 120
        p0242_2.setSA([80, 0, 360, 400])
        p0242_2.setTW([80, 0, 360, 400])
#        p0242_2['start'] = 6
        p0242_2['start'] = 16
        p0242_2['end'] = 22
        p0242_2['ready'] = 4

        b0084_2 = partClass('A011B0084#2') #수직 덕트 0101
        b0084_2['w'] = 40
        b0084_2['height'] = 70
        b0084_2.setSA([25, 0, 420, 440])
        b0084_2.setTW([40, 0, 480, 440])
        #b0084_2.setSA([40, 0, 300, 260])
        #b0084_2.setTW([40, 0, 300, 250])
        b0084_2['start'] = 20
        b0084_2['end'] = 30
        b0084_2['ready'] = 10

        b3834_2 = partClass('A011B3834#2') #하우징 1400
        b3834_2['w'] = 80
        b3834_2['height'] = 120
        b3834_2.setSA([25, 0, 420, 440])
        b3834_2.setTW([40, 0, 480, 440])
        b3834_2['start'] = 9
        b3834_2['end'] = 11
        b3834_2['ready'] = 5

        b3835_2 = partClass('A011B3835#2') #하우징 1600
        b3835_2['w'] = 80
        b3835_2['height'] = 120
        b3835_2.setSA([25, 0, 420, 440])
        b3835_2.setTW([40, 0, 480, 440])
        b3835_2['start'] = 9
        b3835_2['end'] = 11
        b3835_2['ready'] = 5

        d2007_2 = partClass('A011D2007#2') #서포터 스크린
        d2007_2['w'] = 80
        d2007_2['height'] = 120
        d2007_2.setSA([25, 0, 420, 300])
        d2007_2.setTW([40, 0, 480, 300])
        d2007_2['start'] = 9
        d2007_2['end'] = 11
        d2007_2['ready'] = 7

        s0797_2 = partClass('STCGPG0000797#2') #서포터 스크린
        s0797_2['w'] = 80
        s0797_2['height'] = 120
        s0797_2.setSA([25, 0, 420, 520])
        s0797_2.setTW([40, 0, 480, 400])
        s0797_2['start'] = 9
        s0797_2['end'] = 11
        s0797_2['ready'] = 7

        d0055_2 = partClass('A011D0055#2') #서포터 스크린
        d0055_2['w'] = 80
        d0055_2['height'] = 120
        d0055_2.setSA([25, 0, 420, 520])
        d0055_2.setTW([40, 0, 480, 400])
        d0055_2['start'] = 9
        d0055_2['end'] = 11
        d0055_2['ready'] = 7

        d0048_2 = partClass('A011D0048#2') #힌지
        d0048_2['w'] = 80
        d0048_2['height'] = 120
        d0048_2.setSA([25, 0, 420, 520])
        d0048_2.setTW([40, 0, 480, 400])
        d0048_2['start'] = 8
        d0048_2['end'] = 10
        d0048_2['ready'] = 6

        b2541_2 = partClass('A011B2541#2') #가림판 1인용
        b2541_2['w'] = 80
        b2541_2['height'] = 100
        b2541_2.setSA([25, 0, 420, 520])
        b2541_2.setTW([40, 0, 480, 400])
        b2541_2['start'] = 9
        b2541_2['end'] = 11
        b2541_2['ready'] = 5

        p3240_2 = partClass('A011P3240#2') 
        p3240_2['w'] = 100
        p3240_2['height'] = 140
        p3240_2.setSA([25, 0, 420, 440])
        p3240_2.setTW([40, 0, 480, 440])
        p3240_2['start'] = 9
        p3240_2['end'] = 11
        p3240_2['ready'] = 7

        p0223_2 = partClass('A011P0223#2') 
        p0223_2['w'] = 100
        p0223_2['height'] = 140
        p0223_2.setSA([25, 0, 420, 440])
        p0223_2.setTW([40, 0, 480, 440])
        p0223_2['start'] = 9
        p0223_2['end'] = 11
        p0223_2['ready'] = 7

        d0046_2 = partClass('A011D0046#2') 
        d0046_2['w'] = 100
        d0046_2['height'] = 140
        d0046_2.setSA([25, 0, 420, 520])
        d0046_2.setTW([40, 0, 480, 400])
        d0046_2['start'] = 9
        d0046_2['end'] = 11
        d0046_2['ready'] = 7

        d0047_2 = partClass('A011D0047#2') 
        d0047_2['w'] = 100
        d0047_2['height'] = 140
        d0047_2.setSA([25, 0, 420, 520])
        d0047_2.setTW([40, 0, 480, 400])
        d0047_2['start'] = 9
        d0047_2['end'] = 11
        d0047_2['ready'] = 7

        d0041_2 = partClass('A011D0041#2') 
        d0041_2['w'] = 100
        d0041_2['height'] = 140
        d0041_2.setSA([25, 0, 420, 520])
        d0041_2.setTW([40, 0, 480, 400])
        d0041_2['start'] = 9
        d0041_2['end'] = 11
        d0041_2['ready'] = 7

        b3817_2 = partClass('A011B3817#2') 
        b3817_2['w'] = 100
        b3817_2['height'] = 140
        b3817_2.setSA([25, 0, 420, 520])
        b3817_2.setTW([40, 0, 480, 400])
        b3817_2['start'] = 9
        b3817_2['end'] = 11
        b3817_2['ready'] = 7

        p0225_2 = partClass('A011P0225#2') 
        p0225_2['w'] = 100
        p0225_2['height'] = 140
        p0225_2.setSA([25, 0, 210, 260])
        p0225_2.setTW([40, 0, 240, 200])
        p0225_2['start'] = 9
        p0225_2['end'] = 11
        p0225_2['ready'] = 7

        p0228_2 = partClass('A011P0228#2') 
        p0228_2['w'] = 100
        p0228_2['height'] = 140
        p0228_2.setSA([25, 0, 210, 260])
        p0228_2.setTW([40, 0, 240, 200])
        p0228_2['start'] = 9
        p0228_2['end'] = 11
        p0228_2['ready'] = 7

        p3245_2 = partClass('A011P3245#2') 
        p3245_2['w'] = 100
        p3245_2['height'] = 140
        p3245_2.setSA([25, 0, 210, 260])
        p3245_2.setTW([40, 0, 240, 200])
        p3245_2['start'] = 9
        p3245_2['end'] = 11
        p3245_2['ready'] = 7

        d2006_2 = partClass('A011D2006#2') 
        d2006_2['w'] = 100
        d2006_2['height'] = 140
        # d2006_2.setSA([25, 0, 210, 260])
        # d2006_2.setTW([40, 0, 240, 200])
        d2006_2.setSA([25, 0, 420, 520])
        d2006_2.setTW([40, 0, 480, 400])
        d2006_2['start'] = 9
        d2006_2['end'] = 11
        d2006_2['ready'] = 7

        b3841_2 = partClass('A011B3841#2') #수직 덕트 0101
        b3841_2['w'] = 40
        b3841_2['height'] = 70
        b3841_2.setSA([25, 0, 200, 260])
        b3841_2.setTW([25, 0, 200, 250])
        b3841_2['start'] = 9
        b3841_2['end'] = 11
        b3841_2['ready'] = 7




        self.db = {'A011P0242#1': p0242_1, 'A011B0084#1': b0084_1, 'A011B3834#1': b3834_1, 'A011D2007#1' : d2007_1, 'STCGPG0000797#1' : s0797_1, 'A011D0055#1': d0055_1, 'A011D0048#1' : d0048_1, 'A011B2541#1' : b2541_1, 'A011P3240#1' : p3240_1, 'A011P0223#1' : p0223_1,'A011D2006#1' : d2006_1,
                   'A011P0242#2': p0242_2, 'A011B0084#2': b0084_2, 'A011B3834#2': b3834_2, 'A011D2007#2' : d2007_2, 'STCGPG0000797#2' : s0797_2, 'A011D0055#2': d0055_2, 'A011D0048#2' : d0048_2, 'A011B2541#2' : b2541_2, 'A011P3240#2' : p3240_2, 'A011P0223#1' : p0223_2, 'A011D0046#2': d0046_2, 'A011D0047#2': d0047_2, 'A011D0041#2':d0041_2,'A011B3817#2':b3817_2,'A011P0223#2':p0223_2,'A011P0225#2':p0225_2,'A011P0228#2':p0228_2,'A011P3245#2':p3245_2,'A011D2006#2':d2006_2,'A011B3841#2':b3841_2,'A011B3835#2':b3835_2}
        matching1 = [s for s in self.db if "#1" in s] 
        print("1호기 : "+str(len(matching1))+"개")     
        matching2 = [s for s in self.db if "#2" in s] 
        print("2호기 : "+str(len(matching2))+"개")  
        print('part class info initialized.')



    def getClass(self, cname):
        #print(cname)
        return self.db.get(cname)

    def getPartInfo(self, cname):
        # 기본레이아웃정보 , x,y,w,h
        # 시작인식영역
        clstemp = self.db.get(cname)
        return clstemp
