# -*- coding: utf-8 -*-
import os
# import configparser
# from OpenExcelTestPlan import ExcelPlan


POS_nwlyzd_HEAD = 0
POS_nwlyzd_LEN = 2  # 1
POS_nwlyzd_HEAD2 = 10  # 1
POS_nwlyzd_CTRL = 12  # 1
POS_nwlyzd_ADDR = 14  # 7
POS_nwlyzd_DATA = 28  # 10
MIN_LEN_nwlyzdFRAME = 30  # 12


def reverse(data):
    string = ''
    for i in range(len(data)-1, -1, -2):
        string += data[i-1]
        string += data[i]
    return string

def calcCheckSum(fr):
    checkSum = 0
    for i in range(0, len(fr), 2):
        checkSum += int(fr[i:i + 2], 16)
    return str(hex(checkSum))


def point(data):
    strvalue = ''
    if data[0:4] == '0000':
        strvalue += str(int(data, 16))
        return strvalue
    else:
        data1 = transto2(data[0:2])
        data2 = data1[::-1]
        fa = ''
#        G = ''
        for j in range(0, 8):
            if data2[j] == '1':
                dd = j + 1
                ee = str(dd)
                fa += ''.join(ee)
        for xp in range(0, len(fa)):
            strvalue += str((int(data[2:4], 16)-1)*8 + int(fa[xp], 16)) + ','
        return strvalue


#  测量点和数据标识
def measpoint(data):
    strvalue = []
    if data[0:4] == '0000':
        strvalue.append(int(data[0:2], 16))
        strvalue.append(reverse(data[4:12]))
        return strvalue
    else:
        data1 = transto2(data[:2])
        data2 = data1[::-1]
        fa = ''
#        G =''
        for j in range(0, 8):
            if data2[j] == '1':
                dd = j + 1
                ee = str(dd)
                fa += ''.join(ee)
        for xp in range(0, len(fa)):
            strvalue.append((int(data[2:4], 16)-1)*8 + int(fa[xp], 16))
            strvalue.append(reverse(data[4:12]))
        return strvalue


def parsedata(afn, data, refere):
    strvalue = {}
    if len(data) < 12:
        return strvalue
    else:
        data1 = data[0:12]
        data2 = data[12:]
#        pos = 0
        aa = measpoint(data1)
        bb = judgeMarke(afn, aa[0], aa[1], data2, refere)
        da = {'DA': str(aa[0])}
        dt = {'DT': aa[1]}
        strvalue.update(da)
        strvalue.update(dt)
        strvalue.update({'DATA': bb[0]})
        strvalue.update(strvalue)
        if bb[1] == 0:
            return strvalue, 0
        else:
            return strvalue, data[12 + bb[1]:], bb[1]


def dealnwlyzdFrame(fram, refere):
    ll = [False]
    if len(fram) < MIN_LEN_nwlyzdFRAME:
        return ll
    aa = fram.find(']')
    time = fram[:aa]
    time = time.replace('-', '')
    time = time.replace(':', '')
    time = time.replace('[', '')
    time = time.replace(']', '')
    time = time[:14]
    ll[0] = True
    ll += [time]
    for i in range(aa+1, len(fram), 2):
        if  fram[i:i + 2] == '68' and fram[(i + POS_nwlyzd_HEAD2):(i + POS_nwlyzd_HEAD2 + 2)] == '68':
            datalen = (int(reverse(fram[(i + POS_nwlyzd_LEN ):(i + POS_nwlyzd_LEN + 4)]),16))*2
            checkSum = calcCheckSum(fram[(i + POS_nwlyzd_CTRL) :(i + POS_nwlyzd_CTRL + datalen)])
            checkSum = checkSum[-2:]
            checkSum = checkSum.upper()
            framending = fram[(i + POS_nwlyzd_CTRL + datalen + 2) :(i + POS_nwlyzd_CTRL + datalen +4 )]
            if  checkSum == fram[(i + POS_nwlyzd_CTRL + datalen ) :(i + POS_nwlyzd_CTRL + datalen + 2 )] and framending =='16':
                ctrl = fram[(i + POS_nwlyzd_CTRL):(i + POS_nwlyzd_CTRL + 2)]
                addr = fram[(i + POS_nwlyzd_ADDR):(i + POS_nwlyzd_ADDR + 14)]
                data = fram[(i + POS_nwlyzd_DATA):(i + POS_nwlyzd_DATA + datalen - 16)]
                ll += [ctrl,addr,data,refere]
                return ll
    return ll


def transto2(data):
    StrValue =''
    for i in range(len(data)):
        aa=bin(int(data[i],16))
        aa=aa.zfill(6)
        aa=aa.replace('0b','')
        StrValue +=''.join(aa)
    return  StrValue



def analyctrl(ctrl):
    StrValue = ''
    A = transto2(ctrl)
    StrValue += 'DIR=' + A[0] + " "
    StrValue += 'PRM=' + A[1] + " "
    StrValue += 'FCB/ACD=' + A[2] + " "
    StrValue += 'FCV=' + A[3] + " "
    StrValue += 'FUNCCODE=' + str(int(A[4:], 2))
    return  StrValue


def analyaddr(addr):
    StrValue1= ''
    StrValue1 += reverse(addr[:6]) + reverse(addr[6:12])
    StrValue2 ={'ADDR':StrValue1 }
    return  StrValue2



def analydata(flag,data,reference):
    #StrValue = []
    flag = transto2(flag)
    data1= data[0:2]
    StrValue ={'AFN': data1}
    data2 = data[4:]
    if flag[0] == '0':
       pass
       #elif data[:2]=='0A':
       #    return FieldParsingNWLYZD_AFN0Aa(data1,data2,reference)
    else:
        if data[:2]=='0C':
           view = FieldParsingNWLYZD_AFN0Cb(data1,data2,reference)
           StrValue.update({'DATA':view})
        elif data[:2] == '04':
            view = FieldParsingNWLYZD_AFN04b(data1, data2, reference)
            StrValue.update({'DATA': view})
        elif data[:2] == '0A':
            view = FieldParsingNWLYZD_AFN0Ab(data1, data2, reference)
            StrValue.update({'DATA': view})
        elif data[:2] == '0D':
            view = FieldParsingNWLYZD_AFN0Db(data1, data2, reference)
            StrValue.update({'DATA': view})
        elif data[:2] == '12':
            view = FieldParsingNWLYZD_AFN12b(data1, data2, reference)
            StrValue.update(view)
    return  StrValue

def analy(time,ctrl,addr,data,reference):
    #StrValue ={}
    StrValue =( {'TIME':time} )
    #StrValue.append(analyctrl(ctrl))
    StrValue.update(analyaddr(addr))
    StrValue.update(analydata(ctrl,data,reference))
    return  StrValue


def func(data1,data2,reference):
    StrValue = []
    if len(data2) <= 12:
        return StrValue, None
    else:
        aa = parsedata(data1, data2, reference)
        aa[0]['VALUE'] =aa[0].pop('DATA')
        StrValue.append(aa[0])
        return  StrValue, aa[1]



def fund(data1,data2,reference):
    StrValue = []
    if len(data2) <= 12:
        return StrValue, ''
    else:
        aa = parsedata(data1, data2, reference)
        aa[0]['VALUE'] = aa[0].pop('DATA')
        bb = aa[1][:12]
        cc = aa[1][12:]
        aa[0].update({'TIME': bb})
        StrValue.append(aa[0])
        if len(cc)%(12+aa[2]) != 0:
            StrValue, cc
        else:
            l = []
            ee = aa[0]
            for i in range(0,len(cc),12+aa[2]):
                ee={}
                dd = data2[0:12] + cc
                aa = parsedata(data1, dd, reference)
                aa[0]['VALUE'] = aa[0].pop('DATA')
                bb = aa[1][:12]
                cc = aa[1][12:]
                aa[0].update({'TIME': bb})
                StrValue.append(aa[0])
            return StrValue,''




def FieldParsingNWLYZD_AFN0Cb(data1,data2,reference):
    #StrValue = {'AFN': data1}
    StrValue = []
    aa, ret = func(data1,data2,reference)
    StrValue.extend(aa)
    while ret != '':
        aa, ret = func(data1, ret, reference)
        StrValue.extend(aa)
    rf = StrValue
    for i in range(0, len(rf)):
        rf[i].update({'TIME': ''})
    return rf

def FieldParsingNWLYZD_AFN04b(data1,data2,reference):
    #StrValue = {'AFN': data1}
    StrValue = []
    StrValue1 = {}
    aa = measpoint(data2[:4])
    StrValue1.update({'DA': str(aa[0])})
    StrValue1.update({'DT': reverse(data2[4:12])})
    StrValue1.update({'VALUE': reverse(data2[12:14])})
    StrValue1.update({'TIME': ''})
    StrValue.append( StrValue1)
    return  StrValue

def FieldParsingNWLYZD_AFN0Db(data1, data2, reference):
    StrValue = []
    aa, ret = fund(data1, data2, reference)
    StrValue.extend(aa)
    while ret != '':
        aa, ret = fund(data1, ret, reference)
        StrValue.extend(aa)
    rf = StrValue
    return rf

def FieldParsingNWLYZD_AFN0Ab(data1,data2,reference):
    StrValue = {}
    StrValue.update(parsedata(data1, data2, reference)[0])
    StrValue['VALUE'] = StrValue.pop('DATA')
    return StrValue



def FieldParsingNWLYZD_AFN12b(data1,data2,reference):
    StrValue = ({'AFN':data1})
    x,y = parsedata(data1,data2,reference)
    StrValue.update(x)
    StrValue.pop('DA')
    StrValue.pop('DT')
    return StrValue


def getpointdata(data,m,b):
    StrValue = ''
    data1 = reverse(data)
    for i in range(0,len(data1)):
        if i ==m:
            StrValue += '.'
        StrValue += data1[i]
    return (StrValue,b)

Marke0000FF00 = ['042', '0000FF00', '050601FF', '0001FF00']
Marke00000000 = ['008', 'NNNNNN.NN', '00000000', '00010000', '00010100', '00010200', '00010300',
                 '00010400', '00020000', '00020100', '00020200', '00020300', '00020400', '00030000',
                 '00040000', '00050000', '00060000', '00070000', '00080000', '00010001', '00010201',
                 '00010301', '00010401', '00020001', '00020101', '00020201', '00020301', '00020401',
                 '00030001', '00040001', '00000001', '00000101', '00000201', '00000301', '00000401',
                 '00010101', '00020001', '00020101', '00020201', '00020301', '00020401', '00030001',
                 '00030101', '00030201', '00030301', '00030401', '00040001', '00040101', '00040201',
                 '00040301', '00040401']
Marke02010100 = ['004', 'NNN.N', '02010100', '02010200', '02010300', '02070000', '02070100', '02070200',
                 '02070300', '02070400', '02070500', '02070600']
Marke02020100 = ['006', 'NNN.NNN', '02020100', '02020200', '02020300', '02800001']
Marke02030100 = ['006', 'NN.NNNN', '02030100', '02030200','02030000','02030300', '02030400', '02040000',
                 '02040100', '02040200', '02040300', '02050100', '02050200', '02050300']
Marke02060000 = ['004', 'N.NNN', '02060000', '02060100', '02060200', '02060300']
Marke02080001 = ['004', 'NN.NN', '02080001', '02080002', '02080002', '02080003', '02090001', '02090002',
                 '02090003','E000018A', 'E0800100', 'E0800101', 'E0800102', 'E0800103', 'E0800104',
                 'E0800105','E0800106', 'E0800107', 'E0800108', 'E0800109', 'E080010A', 'E080010B',
                 'E0800200', 'E0800201','E0800202', 'E0800203', 'E0800207', 'E0800208', 'E0800209',
                 'E080020A', 'E080020B', 'E080020C']
MarkeE000018B = ['006', 'NNNN.NN', 'E000018B']
Marke04000101 = ['008', 'YYMMDDWW', '04000101']
Marke04000102 = ['006', 'hhmmss', '04000102']
Marke01010000 = ['016', 'YYMMDDhhmm,NN.NNNN', '01010000', '01010100', '01010200', '01010300', '01010400',
                 '01020000', '01020100', '01020200', '01020300', '01020400', '01010001', '01010101',
                 '01010201', '01010301', '01010401', '01020001', '01020101', '01020201', '01020301',
                 '01020401']
MarkeE0000000 = ['002','NN','E0000000']
MarkeE0000100 = ['018','NN...NN,MM','E0000100', 'E0000101', 'E0000102']
MarkeE0000103 = ['016','NN...NN','E0000103']
MarkeE0000104 = ['032','NN...NN','E0000104']
MarkeE0000105 = ['064','NN...NN','E0000105', 'E0000106']
MarkeE0000107 = ['2', 'NN(BCD)','E0000107', 'E0000108', 'E0000109', 'E000010A', 'E0000122', 'E0000127',
                 'E0000140', 'E0000180', 'E0000181', 'E0000182', 'E0000183', 'E0000184', 'E0000185',
                 'E0000186', 'E0000187', 'E0000188', 'E0000189', 'E0000221', 'E0000300', 'E0800204',
                 'E1800015']
MarkeE000010F = ['238','E000010F']
MarkeE0000120 = ['4', 'NNNN(BCD)', 'E0000120']
MarkeE0000121 = ['004', 'NNNN(BIN)', 'E0000121', 'E0000123']
MarkeE000018C = ['006', 'NNNNNN(BCD)', 'E000018C', 'E1008030', 'E1008031', 'E100C030', 'E100C031',
                 'E1000020', 'E1000021']
MarkeE0000124 = ['NNNNNNNN(BIN)', 'E0000124', 'E0000125', 'E0000126']
MarkeE000012F = ['E000012F']
MarkeE0000130 = ['12', 'YYMMDDhhmmss', 'E0000130']
MarkeE0000131 = ['E0000130', ]
MarkeE000013F = ['E000013F']
MarkeE0000150 = ['E0000150', 'E0000151', 'E0000152', ]
MarkeE0000160 = ['E0000160', 'E0000161', 'E0000162', 'E0000163']
MarkeE000018F = ['036','E000018F']
MarkeE080001F = ['020','E080001F']
MarkeE080002F = ['036','E080002F']
MarkeE000000F = ['036','E000000F']
MarkeE0000200 = ['E0000200', 'E0000201', 'E0000202', 'E0000203', 'E0000204', 'E0000205', 'E0000206',
                 'E0000207', 'E0000208', 'E0000209', 'E000020A', 'E000020B', 'E000020C', 'E000020D',
                 'E000020E', 'E000020F', 'E0000210', 'E0000211', 'E0000212', 'E0000213', 'E0000214',
                 'E0000215', 'E0000216', 'E0000217', 'E0000218', 'E0000219', 'E000021A', 'E000021B',
                 'E000021C', 'E000021D', 'E000021E', 'E000021F', 'E0000220']
MarkeE0000301 = ['E0000301', 'E0000302', 'E0000303', 'E0000304', 'E0000305', 'E0000306', 'E0000307',
                 'E0000308', 'E0000309', 'E000030A', 'E000030B', 'E000030C', 'E000030D', 'E000030E',
                 'E000030F', 'E0000310', 'E0000311', 'E0000311', 'E0000312', 'E0000313', 'E0000314',
                 'E0000315', 'E0000316', 'E0000317', 'E0000318', 'E0000319', 'E000031A', 'E000031B',
                 'E000031C', 'E000031D', 'E000031E', 'E000031F', 'E0000320', 'E0000321', 'E0000322',
                 'E0000323', 'E0000324', 'E0000325', 'E0000326', 'E0000327', 'E0000328', 'E0000329',
                 'E000032A', 'E000032B', 'E000032C']
MarkeE080010C = ['006', 'NN,NN,NN', 'E080010C', 'E0800204','E0800206']
MarkeE1008010 = ['054', 'NN,NN,NN', 'E1008010', 'E1008011','E1008012','E1008013','E100C010', 'E100C011',
                 'E100C012', 'E100C013']
MarkeE1008015 = ['028', 'NN,NN,NN', 'E1008015', 'E1008016', 'E1008017']
MarkeE1008018 = ['028', 'NN,NN,NN', 'E1008018', 'E1008019']
MarkeE100801A = ['024', 'NN,NN,NN', 'E100801A']
MarkeE100801D = ['028', 'NNN.NNN,MMDDhhmm,NNN.NNN,MMDDhhmm,', 'E100801D']
Marke020A01FF = ['084', 'NN.NN*n', '020A01FF', '020A02FF', '020A03FF', '020B01FF', '020B02FF', '020B03FF']
MarkeE1008041 = ['080', 'NN,NN,NN', 'E1008041', 'E1008042']



def judgeMarke(afn,DA,marke,data,reference):
    marke = marke.upper()
    if marke in Marke0000FF00:
        StrValue = []
        b = int( Marke0000FF00[0])
        return FieldParsingNWLYZD_0000FF00(data[:b], b)
    elif marke in Marke00000000:
        aa = Marke00000000[0]
        b = int(aa)
        return FieldParsingNWLYZD_00000000(data[:b], b)
    elif marke in Marke02010100:
        aa = Marke02010100[0]
        b = int(aa)
        return FieldParsingNWLYZD_02010100(data[:b], b)
    elif marke in Marke02020100:
        aa = Marke02020100[0]
        b = int(aa)
        return FieldParsingNWLYZD_02020100(data[:b], b)
    elif marke in Marke02030100:
        aa = Marke02030100[0]
        b = int(aa)
        return FieldParsingNWLYZD_02030100(data[:b], b)
    elif marke in Marke02060000:
        aa = Marke02060000[0]
        b = int(aa)
        return FieldParsingNWLYZD_02060000(data[:b], b)
    elif marke in Marke02080001:
        aa = Marke02080001[0]
        b = int(aa)
        return FieldParsingNWLYZD_02080001(data[:b], b)
    elif marke in Marke04000101:
        aa = Marke04000101[0]
        b = int(aa)
        return FieldParsingNWLYZD_04000101(data[:b], b)
    elif marke in Marke04000102:
        aa = Marke04000102[0]
        b = int(aa)
        return FieldParsingNWLYZD_04000102(data[:b], b)
    elif marke in Marke01010000:
        aa = Marke01010000[0]
        b = int(aa)
        return FieldParsingNWLYZD_01010000(data[:b], b)
    elif  marke in MarkeE0000000:
        b = int(MarkeE0000000[0])
        return FieldParsingNWLYZD_E0000000(data[:b], b)
    elif  marke in MarkeE0000100:
        b = int(MarkeE0000100[0])
        return FieldParsingNWLYZD_E0000100(data[:b],b)
    elif marke in MarkeE0000103:
        b = int(MarkeE0000103[0])
        return FieldParsingNWLYZD_E0000103(data[:b],b)
    elif marke in MarkeE0000104:
        b = int(MarkeE0000104[0])
        return FieldParsingNWLYZD_E0000104(data[:b],b)
    elif marke in MarkeE0000105:
        b = int(MarkeE0000105[0])
        return FieldParsingNWLYZD_E0000105(data[:b],b)
    elif marke in MarkeE0000107:
        b = int(MarkeE0000107[0])
        return FieldParsingNWLYZD_E0000107(data[:b], b)
    elif marke in MarkeE000010F:
        b = int(MarkeE000010F[0])
        return FieldParsingNWLYZD_E000010F(data[:b],b)
    elif marke in MarkeE0000120:
        b = int(MarkeE0000120[0])
        return FieldParsingNWLYZD_E0000120(data[:b],b)
    elif marke in MarkeE0000121:
        b = int(MarkeE0000121[0])
        return FieldParsingNWLYZD_E0000121(data[:b],b)
    elif marke in MarkeE0000124:
        b = int(MarkeE0000124[0])
        return FieldParsingNWLYZD_E0000124(data[:b],b)
    elif marke in MarkeE000012F:
        b = int(MarkeE000012F[0])
        return FieldParsingNWLYZD_E000012F(data[:b],b)
    elif marke in MarkeE0000130:
        b = int(MarkeE0000130[0])
        return FieldParsingNWLYZD_E0000130(data[:b],b)
    elif marke in MarkeE0000131:
        b = int(MarkeE0000131[0])
        return FieldParsingNWLYZD_E0000131(data[:b],b)
    elif marke in MarkeE000013F:
        b = int(MarkeE000013F[0])
        return FieldParsingNWLYZD_E000013F(data[:b],b)
    elif marke in MarkeE0000150:
        b = int(MarkeE0000150[0])
        return FieldParsingNWLYZD_E0000150(data[:b],b)
    elif marke in MarkeE0000160:
        b = int(MarkeE0000160[0])
        return FieldParsingNWLYZD_E0000160(data[:b],b)
    elif marke in MarkeE000018B:
        b = int(MarkeE000018B[0])
        return FieldParsingNWLYZD_E000018B(data[:b],b)
    elif marke in MarkeE000018C:
        b = int(MarkeE000018C[0])
        return FieldParsingNWLYZD_E000018C(data[:b],b)
    elif marke in MarkeE000018F:
        b = int(MarkeE000018F[0])
        return FieldParsingNWLYZD_E000018F(data[:b],b)
    elif marke in MarkeE0000200:
        b = int(MarkeE0000200[0])
        return FieldParsingNWLYZD_E0000200(data[:b],b)
    elif marke in MarkeE080010C:
        b =int(MarkeE080010C[0])
        return FieldParsingNWLYZD_E080010C(data[:b], b)
    elif marke in MarkeE080010C:
        b =int(MarkeE080010C[0])
        return FieldParsingNWLYZD_E080010C(data[:b], b)
    elif marke in MarkeE1008010:
        b= int(MarkeE1008010[0])
        return FieldParsingNWLYZD_E1008010(data[:b], b)
    elif marke in MarkeE1008015:
        b= int(MarkeE1008015[0])
        return FieldParsingNWLYZD_E1008015(data[:b], b)
    elif marke in MarkeE1008018:
        b= int(MarkeE1008018[0])
        return FieldParsingNWLYZD_E1008018(data[:b], b)
    elif marke in MarkeE100801A:
        b= int(MarkeE100801A[0])
        return FieldParsingNWLYZD_E100801A(data[:b], b)
    elif marke in MarkeE100801D:
        b= int(MarkeE100801D[0])
        return FieldParsingNWLYZD_E100801D(data[:b], b)
    elif marke in MarkeE1008041:
        b= int(MarkeE1008041[0])
        return FieldParsingNWLYZD_E1008041(data[:b], b)
    elif marke in MarkeE080001F:
        b = int(MarkeE080001F[0])
        return FieldParsingNWLYZD_E080001F(data[:b], b)
    elif marke in Marke020A01FF:
        b = int(Marke020A01FF[0])
        return FieldParsingNWLYZD_020A01FF(data[:b], b)
    elif marke in MarkeE0000301:
        if afn=='0A':
            return FieldParsingNWLYZD_E0000301a(data,reference)
        elif afn=='12'and data[:2]== '01':
            strValue = []
            a0 = reference[2]['DATA']['Value'][10]
            a1 = reference[2]['DATA']['Value'][11]
            #c = findAna(a0, ',')
            d = findAna(a1, ',')
            #f = 2
            #for i in c:
            f = 6
            for j in range(0, len(d)):
                qwe = judgeMarke(afn, DA, d[j], data[f:], reference)
                f += qwe[1]
                strValue1 = {'DA': str(a0)}
                strValue1.update({'DT': d[j]})
                strValue1.update({'VALUE': qwe[0]})
                strValue.append(strValue1)
            strValue2 = {'TIME': data[f:f+12]}
            f += 12
            strValue3 =[]
            for x in range(0,len(strValue)):
                strValue[x].update(strValue2)
                strValue3.append(strValue[x])
            a = int(len(data)/f)
            if a > 1:
                strValue4 = []
                for xp in range(1,a):
                    strValue4 = []
                    strValue7 = []
                    f += 6
                    for j in range(0, len(d)):
                        qwe = judgeMarke(afn, DA, d[j], data[f:], reference)
                        f += qwe[1]
                        strValue5 = {'DA': str(a0)}
                        strValue5.update({'DT': d[j]})
                        strValue5.update({'VALUE': qwe[0]})
                        strValue4.append(strValue5)
                    strValue6 = {'TIME': data[f:f + 12]}
                    f += 12
                for x in range(0, len(strValue4)):
                    strValue4[x].update(strValue6)
                    strValue3.append(strValue4[x])
                return strValue3,0
            else: return strValue3,0
        elif afn=='12'and data[:2]== '00':
            StrValue = []
            x,y ,z= function12(afn,DA,marke,data,reference)
            StrValue.extend(x)
            if len(y) % z == 0 :
                a = int(len(y)/z)
                for i in range(0,a):
                    x, y, z = function12(afn, DA, marke, y, reference)
                    StrValue.extend(x)
            return  StrValue,0
    else:
        return "The Mark is not defined!", data

def function12(afn,DA,marke,data,reference):
    StrValue = []
    a = int(data[2:4],16)*int(data[4:6],16)
    f = 6
    for i in range(0,a):
        StrValue1 = {}
        ab = measpoint(data[f:f+4])
        f  += 4
        aa = reverse(data[f:f+8])
        f +=8
        b = judgeMarke(afn, ab, aa, data[f:], reference)
        StrValue1.update({'DA': str(ab[0])})
        StrValue1.update({'DT': aa})
        StrValue1.update({'Value':b[0]})
        f += b[1]
        StrValue1.update({'TIME':data[f:f+10]})
        f += 10
        StrValue.append(StrValue1)
    f += 12
    return StrValue,data[f:], f







def FieldParsingNWLYZD_00000000(data,b):
    if len(data) != 8:
        return 'Cannot Parse The data: ' + data
    strValue = ''
    data1=reverse(data)
    for i in range(0, len(data1), 1):
        if i == 6:
            strValue += '.'
        strValue += data1[i]
    return (strValue,b)

def FieldParsingNWLYZD_0000FF00(data,b):
    strValue = ''
    data1 = data[:2]
    data2 = data[2:]
    # aa = int( data1,16) +1
    for i in range (0,len(data2),8):
        strValue1 = ''
        for j in range(0,8):
            strValue1 += data2[i+j]
        strValue2 = FieldParsingNWLYZD_00000000(strValue1,b)
        strValue += strValue2[0] + ','
    return  strValue[:-1],b

def FieldParsingNWLYZD_01010000(data,b):
    if len(data) != 16:
        return 'Cannot Parse The data: ' + data
    strValue = ''
    data1 = reverse(data[:10])
    data2 = getpointdata(data[10:16],2,b)
    strValue += data2[0] + ','+ data1
    return (strValue,b)

def FieldParsingNWLYZD_02010100(data,b):
    if len(data) != 4:
        return 'Cannot Parse The data: ' + data
    strValue = ''
    data1=reverse(data)
    for i in range(0, len(data1), 1):
        if i == 3:
            strValue += '.'
        strValue += data1[i]
    return (strValue,b)

def FieldParsingNWLYZD_02020100(data,b):
    if len(data) != 6:
        return 'Cannot Parse The data: ' + data
    strValue = ''
    data1=reverse(data)
    for i in range(0, len(data1), 1):
        if i == 3:
            strValue += '.'
        strValue += data1[i]
    return (strValue,b)

def FieldParsingNWLYZD_02030100(data,b):
    if len(data) != 6:
        return 'Cannot Parse The data: ' + data
    strValue = ''
    data1=reverse(data)
    for i in range(0, len(data1), 1):
        if i == 2:
            strValue += '.'
        strValue += data1[i]
    return (strValue,b)


def FieldParsingNWLYZD_02060000(data,b):
    if len(data) != 4:
        return 'Cannot Parse The data: ' + data
    strValue = ''
    data1=reverse(data)
    for i in range(0, len(data1), 1):
        if i == 1:
            strValue += '.'
        strValue += data1[i]
    return (strValue,b)

def FieldParsingNWLYZD_02080001(data,b):
    if len(data) != 4:
        return 'Cannot Parse The data: ' + data
    strValue = ''
    data1=reverse(data)
    for i in range(0, len(data1), 1):
        if i == 2:
            strValue += '.'
        strValue += data1[i]
    return (strValue,b)

def FieldParsingNWLYZD_04000101(data,b):
    if len(data) != 6:
        return 'Cannot Parse The data: ' + data
    strValue = ''
    data1=reverse(data)
    strValue += data1
    return (strValue,b)


def FieldParsingNWLYZD_04000102(data,b):
    if len(data) != 6:
        return 'Cannot Parse The data: ' + data
    strValue = ''
    data1=reverse(data)
    strValue += data1
    return (strValue,b)

def FieldParsingNWLYZD_E0000000(data,reference):
    strValue = []
    if data[0:2] =='00':
        strValue.append('确认')
    strValue.append('否认')
    return  strValue

def FieldParsingNWLYZD_E0000100(data,b):
    strValue = []
    if data[16:18] =='02'or data[16:18] =='04':
        data1 = reverse(data[:16])
        data2 = ''
        for i in range(0,len(data1[2:10]),2):
            data2 += str(int(data1[i+2: i + 4],16)) + '.'
        data3 = data2[:-1]
        data4 =str(int(data1[12:16],16))
        strValue.append(data3 )
        strValue.append(data4)
        strValue.append(data[16:18])
        return strValue,b
    elif data[16:18] =='03'or data[16:18] =='07':
        data1 = reverse(data[:16])
        strValue.append( data1)
        strValue.append(data[16:18])
        return strValue,b
    elif data[16:18] =='05'or data[16:18] =='08':
        strValue.append( + data[16:18] )
        return  strValue,b
    else:
        strValue.append('无效')
        return  strValue,None

def FieldParsingNWLYZD_E0000103(data,reference):
    strValue = []
    data1 = reverse(data[:16])
    data2 = ''
    for i in range(0, len(data1[2:10]), 2):
        data2 += str(int(data1[i + 2: i + 4], 16)) + '.'
    data3 = data2[:-2]
    data4 = str(int(data1[12:16], 16))
    strValue.append( data3)
    strValue.append(data4)
    return strValue

def FieldParsingNWLYZD_E0000104(data,reference):
    strValue = []
    strValue1 = ''
    for i in range(0,len(data),2):
        strValue1 += chr(int(data[i:i+2],16))
    strValue.append(strValue1)
    return strValue


def FieldParsingNWLYZD_E0000105(data,reference):
    strValue = []
    strValue1 = ''
    for i in range(0,len(data),2):
        strValue1 += chr(int(data[i:i+2],16))
    strValue.append(strValue1)
    return strValue


def FieldParsingNWLYZD_E0000107(data,b):
    strValue = ''
    strValue += data
    return (strValue,b)

def FieldParsingNWLYZD_E000010F(data,b):
    strValue = []
    strValue.append(FieldParsingNWLYZD_E0000100(data[:18]))
    strValue.append(FieldParsingNWLYZD_E0000100(data[18:36]))
    strValue.append(FieldParsingNWLYZD_E0000100(data[36:54]))
    strValue.append(FieldParsingNWLYZD_E0000103(data[54:70]))
    strValue.append(FieldParsingNWLYZD_E0000104(data[70:102]))
    strValue.append(FieldParsingNWLYZD_E0000105(data[102:166]))
    strValue.append(FieldParsingNWLYZD_E0000105(data[166:230]))
    strValue.append(FieldParsingNWLYZD_E0000107(data[230:232]))
    strValue.append(FieldParsingNWLYZD_E0000107(data[232:234]))
    strValue.append(FieldParsingNWLYZD_E0000107(data[234:236]))
    strValue.append(FieldParsingNWLYZD_E0000107(data[236:238]))
    return strValue,b


def FieldParsingNWLYZD_E0000120(data,b):
    strValue = []
    strValue.append(reverse(data))
    return strValue,b


def FieldParsingNWLYZD_E0000121(data,b):
    strValue = []
    strValue.append(reverse(data) + str(int( reverse(data),16)))
    return strValue,b

def FieldParsingNWLYZD_E0000124(data,b):
    strValue = []
    data1 = reverse(data)
    data2 = ''
    for i in range(0, len(data), 2):
        data2 += str(int(data1[i + 2: i + 4], 16)) + '.'
    data3 = data2[:-2]
    strValue.append(data3)
    return strValue,b

def FieldParsingNWLYZD_E000012F(data,b):
    strValue = []
    strValue.append(FieldParsingNWLYZD_E0000120(data[:4]))
    strValue.append(FieldParsingNWLYZD_E0000121(data[4:8]))
    strValue.append(FieldParsingNWLYZD_E0000107(data[8:10]))
    strValue.append(FieldParsingNWLYZD_E0000121(data[10:14]))
    strValue.append(FieldParsingNWLYZD_E0000124(data[14:22]))
    strValue.append(FieldParsingNWLYZD_E0000124(data[22:30]))
    strValue.append(FieldParsingNWLYZD_E0000124(data[30:38]))
    strValue.append(FieldParsingNWLYZD_E0000107(data[38:40]))
    return strValue,b


def FieldParsingNWLYZD_E0000130(data,b):
    strValue = []
    strValue.append(data)
    return strValue,b

def FieldParsingNWLYZD_E0000131(data,b):
    strValue = []
    strValue.append(reverse(data[:4]))
    strValue.append(str(int(reverse(data[4:]),16)))
    return strValue,b

def FieldParsingNWLYZD_E000013F(data,b):
    strValue = []
    strValue.append(FieldParsingNWLYZD_E0000130(data[:12]))
    strValue.append(FieldParsingNWLYZD_E0000130(data[12:20]))
    return strValue,b


def FieldParsingNWLYZD_E0000150(data,b):
    strValue = []
    strValue.append(data)
    return strValue,b

def FieldParsingNWLYZD_E0000160(data,b):
    strValue = []
    strValue.append(data[:2])
    strValue.append(data[2:4])
    return strValue,b

def FieldParsingNWLYZD_E0000180(data,b):
    strValue = []
    strValue.append(data)
    return strValue,b

def FieldParsingNWLYZD_E000018A(data,b):
    strValue = []
    data1 = ''
    data1 = data[2:4] + '.' + data[0:2]
    strValue.append(data1)
    return strValue,b

def FieldParsingNWLYZD_E000018B(data,b):
    strValue = []
    data1 = ''
    data1 = data[4:6] + data[2:4] +'.' + data[0:2]
    strValue.append(data1)
    return strValue,b

def FieldParsingNWLYZD_E000018C(data,b):
    strValue = ''
    strValue += reverse(data)
    return (strValue,b)

def FieldParsingNWLYZD_E1008010(data,b):
    strValue = ''
    strValue += reverse(data[:6]) + ','
    strValue += getpointdata(data[6:12],4,b)[0]  + ','
    strValue += getpointdata(data[12:18], 4, b)[0] + ','
    strValue += reverse(data[18:24]) + ','
    strValue += reverse(data[24:30]) + ','
    strValue += getpointdata(data[30:34], 3, b)[0] + ','
    strValue += reverse(data[34:42]) + ','
    strValue += getpointdata(data[42:46], 3, b)[0] + ','
    strValue += reverse(data[46:54])
    return ( strValue,b)

def FieldParsingNWLYZD_E1008015(data,b):
    strValue = ''
    strValue += getpointdata(data[0:6],3,b)[0]  + ','
    strValue += reverse(data[6:14]) + ','
    strValue += getpointdata(data[14:20], 3, b)[0] + ','
    strValue += reverse(data[20:28])
    return ( strValue,b)

def FieldParsingNWLYZD_E1008018(data,b):
    strValue = ''
    strValue += getpointdata(data[0:6],2,b)[0]  + ','
    strValue += reverse(data[6:14]) + ','
    strValue += getpointdata(data[14:20], 2, b)[0] + ','
    strValue += reverse(data[20:28])
    return ( strValue,b)

def FieldParsingNWLYZD_E100801A(data,b):
    strValue = ''
    strValue += getpointdata(data[0:4],1,b)[0]  + ','
    strValue += reverse(data[4:12]) + ','
    strValue += getpointdata(data[12:16], 1, b)[0] + ','
    strValue += reverse(data[16:24])
    return ( strValue,b)

def FieldParsingNWLYZD_E100801D(data,b):
    strValue = ''
    strValue += getpointdata(data[0:6],3,b)[0]  + ','
    strValue += reverse(data[6:14]) + ','
    strValue += getpointdata(data[14:20], 3, b)[0] + ','
    strValue += reverse(data[20:28])
    return ( strValue,b)


def FieldParsingNWLYZD_020A01FF(data,b):
    strValue = ''
    for i in range(0,len(data),4):
        strValue += getpointdata(data[0:4], 2, b)[0] + ','
    strValue = strValue[:-1]
    return ( strValue,b)



def FieldParsingNWLYZD_E1008041(data,b):
    strValue = ''
    for i in range (0,48,6):
        strValue += reverse(data[i:6+i]) + ','
    strValue += getpointdata(data[48:56], 6, b)[0] + ','
    strValue += getpointdata(data[56:64], 6, b)[0] + ','
    strValue += getpointdata(data[64:72], 6, b)[0] + ','
    strValue += getpointdata(data[72:80], 6, b)[0]
    return (strValue,b)





def FieldParsingNWLYZD_E000018F(data,reference):
    strValue = []
    strValue.append(FieldParsingNWLYZD_E0000180(data)[:2])
    strValue.append(FieldParsingNWLYZD_E0000180(data)[2:4])
    strValue.append(FieldParsingNWLYZD_E0000180(data)[4:6])
    strValue.append(FieldParsingNWLYZD_E0000180(data)[6:8])
    strValue.append(FieldParsingNWLYZD_E0000180(data)[8:10])
    strValue.append(FieldParsingNWLYZD_E0000180(data)[10:12])
    strValue.append(FieldParsingNWLYZD_E0000180(data)[12:14])
    strValue.append(FieldParsingNWLYZD_E0000180(data)[14:16])
    strValue.append(FieldParsingNWLYZD_E0000180(data)[16:18])
    strValue.append(FieldParsingNWLYZD_E0000180(data)[18:20])
    strValue.append(FieldParsingNWLYZD_E000018A(data)[20:24])
    strValue.append(FieldParsingNWLYZD_E000018B(data)[24:30])
    strValue.append(FieldParsingNWLYZD_E000018C(data)[30:36])
    return strValue


def FieldParsingNWLYZD_E0000200(data,reference):
    strValue = []
    strValue.append(data[:10])
    strValue.append(str(int(data[10:12],16)))
    strValue.append(str(int(data[12:14],16)))
    return  strValue


def FieldParsingNWLYZD_E080010C(data,b):
    strValue = []
    for i in range (0,len(data),2):
        strValue.append(data[i:i+2])
    return (strValue,b)

def FieldParsingNWLYZD_E080002F(data, b):
    strValue = ''
    strValue += reverse(data[:16])
    strValue +=   chr(int(data[16:18],16)) + data[16:32]
    return strValue, b

def FieldParsingNWLYZD_E080001F(data, b):
    strValue = ''
    strValue += data[:2]
    strValue += getpointdata(data[2:6],3,b)[0]
    strValue += getpointdata(data[6:12],3,b)[0]
    strValue += getpointdata(data[12:16],2,b)[0]
    strValue += getpointdata(data[16:20], 2, b)[0]
    return strValue, b



def FieldParsingNWLYZD_E0000301a(data,reference):
    strValue = []
    strValue1 = ''
    strValue.append(str(int(data[:2],16)))
    strValue.append(  reverse(data[2:12]))
    strValue.append(str(int(data[12:14], 16)))
    #strValue.append(str(int(data[12:14], 16)) )
    strValue.append( str(int(data[14:16], 16)))
    strValue.append(  str(int(data[16:18], 16)))
    strValue.append( reverse(data[18:28]))
    strValue.append(str(int(data[28:30], 16)))
    strValue.append(  str(int(data[30:32], 16)))
    strValue.append( str(int(data[32:34], 16)))
    strValue.append(str(int(reverse(data[34:38]), 16)) )
    aa = int(reverse(data[38:40]), 16)
    aa= ''
    for i in range(0,aa):
        aaa = ''
        aaa += str(point(data[40 + 4 * i:44 + 4 * i])) + ','
        aa += aaa
    strValue.append(aa[:-1])
    b = aa*4
    #strValue.append('数据标识编码组数 =' + str(int(data[40+b:42+b], 16)))
    c = int(reverse(data[40+b:42+b]), 16)
    cc = ''
    for j in range(0,c):
       # strValue.append(reverse(data[42+b + 8*j:50+b+8*j]))
        ccc = ''
        ccc += reverse(data[42+b + 8*j:50+b+8*j]) + ','
        cc += ccc
    strValue.append(cc[:-1])
    return   strValue,1

def findAna(aa, s):
    start = 0
    end = 0
    flag = s
    la = []
    aa = aa + ','
    for i in range(aa.count(flag)):
        end = aa.find(flag, start)
        la += [aa[start:end]]
        start = end + 1
    return la

def FieldParsingNWLYZD_E0000301b(marke,data,reference):
    strValue = []
    strValue1 = {}
    strValue.append(data[:2])
    a0 = reference[2]['DATA']['Value'][10]
    a1 = reference[2]['DATA']['Value'][11]
    a1 =a1.replace(' ','')
    c = findAna(a0, ',')
    d = findAna(a1, ',')
    strValue.append(data[2:6])
    data1 =data[6:]
    for i in c:
        strValue1 = {'DA':str(i)}
        for j in range(0,len(d)) :
            qwe = judgeMarke(0,0,d[j], data1, reference)
            #data1 = data1[:]
            strValue1.update({'DT': d[j]})
            strValue1.update({'VALUE': qwe})
            strValue.append(strValue1)
    return  (strValue,0)



def makemeaspoit(data):
    if int(data) == 0:
        return '0000'
    da2 = int((int(data,16) / 8) +1)
    da1 = (int(data,16) - 1) % 8
    b =int( 1 << da1)
    return ("%02x%02x" % (b,da2))



# 组帧函数
def makeNWLYZDFrame(FRAME):
    aa = FRAME['ADDR']
    A = reverse(aa[:6]) + reverse(aa[6:]) + '04'
    AFN = FRAME['AFN']
    da = FRAME['DA']
    dt = FRAME['DT']
    data = FRAME['DATA']
    da1 = findAna(da, ',')
    dt1 = findAna(dt, ',')
    DATA = ''
    if AFN == '04':
        CTRL = '4A'
        DADT = makemeaspoit(da) + reverse(dt)
        dt = dt.upper()
        if  dt == 'E000010F':
            DATA = makeE000010F(data)
        elif dt in ['E0000130']:
            DATA = makeE0000130(data[0])
        elif dt in ['BS','E0000C63','E0000C64','E0000C65']:
            DATA = change16(data[0])
        elif dt == 'E000018F':
            DATA = makeE000018F(data)
        elif dt == 'E080000F':
            DATA =  makeE080000F(data)
        elif dt in ['NN','BCD','E0000107','E0000108','E0000109','E000010A','E000010B','E0000180','E0000181','E0000182','E0000183','E0000184','E0000185','E0000186','E0000187','E0000188','E0000189','E0000C60','E0000C61','E0000C62','E0000E10',]:
            DATA = data[0].zfill(2)
        elif  dt in ['NN','BIN','E0800000','E0800001','E0800003','E0800004','E0800005','E0800006','E0800007','E0800008','E0800000','E080000A','E0800010','E0000C60','E0000C61','E0000C62','E0000E10','E0000C63','E0000C64','E0000C65',]:
            DATA =  change16(data[0])
        elif dt in ['NNNNNNNNNNNN','E0800002','E0800009']:
            DATA = reverse(data[0].zfill(12))
        elif dt in ['N,N,N,N','E080000B']:
            aa = findAna(data[0], ',')
            DATA = ''
            for i in range(0, len(aa)):
                DATA += change16(aa[i])
        elif dt in ['NNNN','BIN','E080000C','E080000D']:
            DATA = change16_2(data[0])
        elif dt in ['NNNN', 'BCD', 'E000018C', ]:
            DATA = reverse(data[0].zfill(6))
        elif dt == 'E080001F':
            DATA = makeE080001F(data)
        elif dt in ['NNN.N', 'E0800011']:
            DATA =  reverse(muldata(data[0],10,4))
        elif dt in ['NNN.NNN', 'E0800012']:
            DATA =  reverse(muldata(data[0],1000,6))
        elif dt in ['NNNN.NN', 'E000018B']:
            DATA = reverse(muldata(data[0], 100, 6))
        elif dt in ['NN.NN', 'E0800013','E0800014','E000018A']:
            DATA = reverse(muldata(data[0], 100, 4))
        elif dt == 'E080002F':
            DATA = makeE080002F(data)
        elif dt in ['AAAAAAAA', 'E0800021','E0800022']:
            aa = reverse(changeASC(data[0]))
            DATA = reverse(aa.zfill(16))
        elif dt in ['taskID','E0000301','E0000302','E0000303','E0000304','E0000305','E0000306','E0000307','E0000308','E0000309','E000030A','E000030B','E000030C','E000030D','E000030E','E000030F','E0000310','E0000311','E0000311','E0000312','E0000313','E0000314','E0000315'
            , 'E0000316','E0000317','E0000318','E0000319','E000031A','E000031B','E000031C','E000031D','E000031E','E000031F','E0000320','E0000321','E0000322','E0000323','E0000324','E0000325','E0000326','E0000327','E0000328','E0000329','E000032A','E000032B','E000032C']:
            DATA = makeE0000301(data)
        elif dt in ('32,BIN','E0000150','E0000151','E0000152'):
            DATA = makeE0000150(data)
    elif AFN == '0A':
        if data == []:
            DATA = ''
        CTRL = '4B'
        DADT = ''
        for i in range(0, len(da1)):
            DADT += makemeaspoit(da1[i]) + reverse((dt))
    elif AFN == '0C':
        if data == []:
            DATA = ''
        CTRL = '4B'
        DADT = ''
        for i in range(0,len(da1)):
            DADT += makemeaspoit(da1[i]) + reverse((dt))
    elif AFN == '0D':
        if data == []:
            DATA = ''
        else:
            daa = data[0].split(u',')
            if len(daa) == 3:
                DATA += daa[0].zfill(12)
                DATA += daa[1].zfill(12)
                DATA += daa[2].zfill(2)
        CTRL = '4B'
        DADT = ''
        for i in range(0, len(da1)):
            DADT += makemeaspoit(da1[i]) + reverse((dt))
    if AFN == '04':
        changL = '00000000000000000000000000000000'
        L = CTRL + A + AFN + '70' + DADT + DATA +  changL
    else:
        L = CTRL + A + AFN + '70' + DADT + DATA
    L1 = str(hex(len(L) // 2))
    L2 = L1.zfill(6)
    L3 = L2.replace('0x', '')
    dataL = reverse(L3)
    frame = '68' + dataL + dataL + '68' + L
    checkSum = calcCheckSum(L)
    checkSum = checkSum[-2:]
    frame += (checkSum + '16')
    ll = ''
    for j in range (0,len(frame),2):
        ll +=frame[j:j+2 ] + ' '
    return ll


def change16(data):
    aa = hex(int((data),10))
    b = aa.zfill(4)
    c = b.replace('0x','')
    return c

def change16_2(data):
    aa =  hex(int((data),10))
    b = aa.zfill(6)
    c = b.replace('0x', '')
    d = reverse(c)
    return d

def muldata(data,s,t):
    aa = float(data)
    b = aa * s
    c = str(int (b))
    d = c.zfill(t)
    return d

def makeE000010F(data):
    pass

def makeE000018F(data):
    data0 = data[0].zfill(2)
    data1 = data[1].zfill(2)
    data2 = data[2].zfill(2)
    data3 = data[3].zfill(2)
    data4 = data[4].zfill(2)
    data5 = data[5].zfill(2)
    data6 = data[6].zfill(2)
    data7 = data[7].zfill(2)
    data8 = data[8].zfill(2)
    data9 = data[9].zfill(2)
    data10 = reverse(muldata(data[10], 100, 4))
    data11 = reverse(muldata(data[11], 100, 6))
    data12 = reverse(data[12].zfill(6))
    DATA = data0 + data1 + data2 + data3 +data4 +data5 +data6 +data7 +data8 +data9 +data10 +data11 +data12
    return   DATA


def makeE080000F(data):
    data0 = change16(data[0])
    data1 = change16(data[1])
    data2= reverse(data[2].zfill(12))
    #data2 = ss.zfill(12)
    data3 = change16(data[3])
    data4 = change16(data[4])
    data5 = change16(data[5])
    data6 = change16(data[6])
    data7 = change16(data[7])
    data8 = change16(data[8])
    data9 = reverse(data[9].zfill(12))
    data10 = change16(data[10])
    aa = findAna(data[11], ',')
    data11 = ''
    for i in range (0,len(aa)):
      data11 +=change16(aa[i])
    data12 = change16_2(data[12])
    data13 = change16_2(data[13])
    DATA = data0 + data1 + data2 + data3 +data4 +data5 +data6 +data7 +data8 +data9 +data10 +data11 +data12 +data13
    return   DATA

def  makeE080001F(data):
    data0 = change16(data[0])
    data1 = reverse(muldata(data[1],10,4))
    data2 = reverse(muldata(data[2], 1000, 6))
    data3 = reverse(muldata(data[3], 100, 4))
    data4 = reverse(muldata(data[4], 100, 4))
    DATA = data0 + data1 + data2 + data3 +data4
    return DATA

def changeASC(data):
    b = ''
    for i in range(len(data)):
        b += str(hex(ord(data[i])))
    c = b.replace('0x', '')
    return c


def  makeE080002F(data):
     aa = changeASC(data[0])
     b = reverse(aa)
     data0 = reverse(b.zfill(16))
     c =  changeASC(data[1])
     d =  reverse(c)
     data1 = reverse(d.zfill(16))
     DATA = data0 + data1
     return DATA



def makeE0000301(data):
    data0 = change16(data[0])
    data1 = reverse(data[1])
    data2 = change16(data[2])
    data3 = change16(data[3])
    data4 = change16(data[4])
    data5 = reverse(data[5])
    data6 = change16(data[6])
    data7 = change16(data[7])
    data8 = change16(data[8])
    data9 = change16_2(data[9])
    aa = findAna(data[10], ',')
    data10 = change16(str(len(aa)))
    data11 = ''
    for i in range(0,len(aa)):
        data11 += makemeaspoit(aa[i])
    b = findAna(data[11], ',')
    data12 = change16(str(len(b)))
    data13 = ''
    for j in range(0,len(b)):
        data13 += reverse(b[j])
    DATA = data0 + data1 + data2 + data3 +data4 +data5 +data6 +data7 +data8 +data9 +data10 +data11 +data12 +data13
    return DATA


def makeE0000150(data):
    DATA = reverse(data[0])
    return DATA

def makeE0000130(dat):
    data = ''
    dat = dat.zfill(12)
    ll = len(dat.zfill(12))
    for i in range(0, 6):
        #print dat[i:i+1]
        data += dat[ll - int(i*2) - 2: ll - int(i * 2)]
    return data


if __name__ == '__main__':
   # FRAME1 = {'ADDR': '000755000001', 'AFN': '04', 'DA': '0', 'DT': 'E0000c62', 'DATA': ['01']}
   # frame = makeNWLYZDFrame(FRAME1)
   # frame =frame.upper()
   #print(frame)
#FRAME1 = {'ADDR': '000755000001', 'AFN': '0C', 'DA': '0', 'DT': 'E0000303', 'DATA': ['1', '1705010121', '0', '1', '1', '1705010100', '0', '1', '1', '0', '0,1', '00010001,00010101,00010201,00010301,00010400,00030000,00020000
    print(makeE0000130('20180813131702'))
    print('jx')
    print(point('FF02'))
    #frame = '[2011-09-07 17:18:29:796] 68 88 00 88 00 68 88 55 07 00 01 00 00 FF 0D 69 00 00 00 00 01 00 20 77 00 00 20 18 07 03 01 00 26 77 00 00 20 18 07 03 01 05 31 77 00 00 20 18 07 03 01 10 37 77 00 00 20 18 07 03 01 15 42 77 00 00 20 18 07 03 01 20 48 77 00 00 20 18 07 03 01 25 53 77 00 00 20 18 07 03 01 30 59 77 00 00 20 18 07 03 01 35 64 77 00 00 20 18 07 03 01 40 70 77 00 00 20 18 07 03 01 45 75 77 00 00 20 18 07 03 01 50 81 77 00 00 20 18 07 03 01 55 BF 16     '
    #frame = '[2011-09-07 17:18:29:796] 68 2F 00 2F 00 68 88 55 07 00 E8 02 00 20 0A 62 00 00 07 03 00 E0 01 16 00 01 05 17 02 01 01 05 00 01 05 17 02 01 01 00 00 01 00 00 02 30 80 00 E1 31 80 00 E1 C8 16  '
# 任务1 多点
    # frame = '[2011-09-07 17:18:29:796] 68 09 01 09 01 68 C4 55 07 00 01 00 00 00 12 71 00 00 01 03 00 E0 01 00 00 40 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 15 14 00 20 17 08 25 14 15 01 00 00 43 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 15 15 00 20 17 08 25 15 15 01 00 00 44 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 30 15 31 20 17 08 25 15 30 4C 16   '
    # frame = '[2011-09-07 17:18:29:796] 68 A1 03 A1 03 68 C4 55 07 00 01 00 00 00 12 78 00 00 01 03 00 E0 01 00 00 76 22 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 30 11 00 20 17 08 25 11 30 01 00 00 73 22 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 45 11 00 20 17 08 25 11 45 01 00 00 70 22 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 00 12 00 20 17 08 25 12 00 01 00 00 11 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 15 12 00 20 17 08 25 12 15 01 00 00 22 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 30 12 00 20 17 08 25 12 30 01 00 00 25 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 45 12 00 20 17 08 25 12 45 01 00 00 30 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 00 13 00 20 17 08 25 13 00 01 00 00 35 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 15 13 00 20 17 08 25 13 15 01 00 00 38 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 30 13 00 20 17 08 25 13 30 01 00 00 32 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 45 13 00 20 17 08 25 13 45 01 00 00 35 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 00 14 00 20 17 08 25 14 00 23 16'
# 任务1单点
    #frame = '[2011-09-07 17:18:29:796] 68 63 00 63 00 68 C4 55 07 00 01 00 00 00 12 70 00 00 01 03 00 E0 01 00 00 55 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 10 00 10 00 10 00 00 00 24 00 12 00 00 00 24 00 12 00 00 00 00 00 00 00 00 00 00 00 00 45 15 31 20 17 08 25 15 45 F5 16  '
# 确认
    #frame = '[2011-09-07 17:18:29:796] 68 11 00 11 00 68 88 55 07 00 E8 02 00 20 04 6E 00 00 85 01 00 E0 00 C6 16   '
# 召测参数响应
    # frame = '[2011-09-07 17:18:29:796] 68 11 00 11 00 68 88 55 07 00 E8 02 00 20 0A 60 00 00 80 01 00 E0 15 CE 16   '
# 任务参数响应
    #frame = '[2011-09-07 17:18:29:796] 68 93 00 93 00 68 88 55 07 00 E8 02 00 20 0A 66 00 00 01 03 00 ' \
    #        'E0 01 10 00 01 05 17 00 0F 01 00 00 01 05 17 00 0F 01 00 00 01 00 00 1B 00 01 01 02 00 02 ' \
    #        '01 02 00 03 01 02 00 01 02 02 00 02 02 02 00 03 02 02 00 00 03 02 00 01 03 02 00 02 03 02 ' \
    #        '00 03 03 02 00 00 04 02 00 01 04 02 00 02 04 02 00 03 04 02 00 00 06 02 00 01 06 02 00 02 ' \
    #        '06 02 00 03 06 02 00 01 07 02 00 02 07 02 00 03 07 02 00 04 07 02 00 05 07 02 00 06 07 02 ' \
    #        '01 00 80 02 02 01 00 04 15 00 80 E1 93 16  '
# 召测测量点参数E080000F响应
   # frame = '[2011-09-07 17:18:29:796] 68 2D 00 2D 00 68 88 55 07 00 E8 02 00 20 0A 68 01 01 0F 00 80 E0 ' \
   #         '01 01 08 00 02 00 00 00 01 02 01 01 00 04 00 00 00 00 00 00 00 08 01 08 00 01 00 01 00 F9 ' \
   #         '16  '

    #reference = [{'ADDR': '000755000001'}, {'AFN': '12'}, {'DATA': {'DA': 0, 'DT': 'E0000301', 'Value': ['1', '1705010121', '1', '1', '1', '1705010100', '1', '1', '1', '0', '0', '02010100,02010200,02010300,02020100,02020200,02020300,02030000,02030100,02030200,02030300,02040000,02040100,02040200,02040300,02060000,02060100,02060200,02060300,02070100,02070200,02070300,02070400,02070500,02070600,01010000,02800001,04000102,E1800015']}}]
    # reference = [{'ADDR': '000755000001'}, {'AFN': '12'}, {'DATA':{'DT': u'E0000301','Value': ['1', u'1705010001', u'0', u'15', u'1', u'1705010000', u'0', u'15', u'1', u'0', u'0',u'02010100,02010200,02010300,02020100,02020200,02020300,02030000,02030100,02030200,02030300,02040000,02040100,02040200,02040300,02060000,02060100, 02060200, 02060300, 02070100, 02070200, 02070300, 02070400, 02070500, 02070600,01010000, 02800001, 04000102, E1800015\n'],'DA': 0}}]
    # frame = '681800180068885507000C0000040A600101210080E030303030303000000116'
    # frame = frame.replace(' ', '')
    # l = dealnwlyzdFrame(frame,reference)
    # aa=analy(l[1],l[2],l[3],l[4],l[5])
    #for i in aa:
    # print(aa)
    #print(aa)
    #68 16 00 16 00 68 4B 55 07 00 01 00 00 02 0C 70 00 00 00 01 01 02 01 01 00 01 01 02 30 16
    #68 1A 00 1A 00 68 88 55 07 00 01 00 00 02 0C 60 00 00 00 01 01 02 37 23 01 01 00 01 01 02 37 23 11 16
    #68 10 00 10 00 68 4B 88 77 66 01 00 00 02 0C 70 03 01 00 FF 00 00 32 16
        #6810001000684B550700070000020C71010100FF00002E16
        #680f000f00684B550700010000020C700101000101022c16


 #   reference =[{'ADDR': '000755000001'}, {'AFN': '0A'},
    # {'DATA': {'DA': 0, 'DT': 'E0000307', 'Value':
    # ['1', '1705010121', '1', '1', '1', '1705010100', '1', '1', '1', '0', '0,1',
    # '00010001,00010101,00010201,00010301,00010401,00030001,00020001,00020101,00020201,00020301,00020401,00040001,00000001,00000101,00000201,00000301,00000401,01010001,01020001']}}]

