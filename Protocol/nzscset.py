# coding=utf-8

import time
import serial



TXOUTTIME = 1.0
RXOUTTIME = 2.0
RXBUFFSIZE = 1024
COMLIST = []

# 三相四线220，1三相四线57.7, 2 三相三线100
nzsc_Y220mode = 0
nzsc_Y57mode = 1
nzsc_Vmode = 2
jxmode = nzsc_Y220mode
# 'F'频率,'Y'三相四线, 'O'相序, 'UB'额定电压, 'U?'Ub%,'UA?'绝对相角，'IB'额定电流,'I?'Ib%'，IA?绝对相角
nzscY220Dict = {'F': '50', 'Y': '0', 'o': '0', 'UB': '220.0', 'IB': '5', 'W': '0', 'L': '0'}
# 'F'频率,'Y'三相四线, 'O'相序, 'UB'额定电压, 'U?'Ub%,'UA?'绝对相角，'IB'额定电流,'I?'Ib%'，IA?绝对相角
nzscY57Dict = {'F': '50', 'Y': '0', 'o': '0', 'UB': '57.7', 'IB': '1', 'W': '0', 'L': '0'}
# 'F'频率,'Y'三相三线, 'O'相序, 'UB'额定电压, 'U?'Ub%,'UA?'绝对相角，'IB'额定电流,'I?'Ib%'，IA?绝对相角
nzscVDict = {'F': '50', 'V': '0', 'o': '0', 'UB': '100.0', 'IB': '1', 'W': '0', 'L': '0'}

nzscCosDict = {'0.5L': '60.0', '0.8L': '36.87', '0.8C': '143.13'}

def hexShow(argv):
    result = ''
    hLen = len(argv)
    for i in xrange(hLen):
        hvol = ord(argv[i])
        hhex = '%02x' % hvol
        result += hhex.upper()
    print('hexShow:', result)
    return result


# 初始化(打开)台体系统串口com2
def initsyscom(imode):
    nCt = 0
    if len(COMLIST) == 0:
        try:
            pcom = serial.Serial('COM2')
            pcom.baudrate = 9600
            pcom.parity = 'N'
            pcom.bytesize = 8
            pcom.stopbits = 1
            pcom.timeout = 3
            pcom.xonxoff = False
            pcom.rtscts = False
            pcom.dsrdtr = False
            pcom.writeTimeout = TXOUTTIME
            COMLIST.append(pcom)
        except:
            return False
    rvalue = ReadSource()
    fUa = 0.0
    fUb = 0.0
    fUc = 0.0
    if len(rvalue) >= 3:
        fUa = float(rvalue['Ua'])
        fUb = float(rvalue['Ub'])
        fUc = float(rvalue['Uc'])
# 台体有电压不进行初始化
    if fUa > 60.0 and fUb > 60.0 and fUc > 60.0:
        return True
    if setmode(imode):
        print('set-jx-xiangxu:OK')
        nCt += 1
    if setUIBbymode(imode):
        print('set-Ub-Ib:OK')
        nCt += 1
    if setUb('100'):
        print('up U:OK')
        nCt += 1
    if setFb(imode):
        print('set-F:OK')
        nCt += 1
    if setIb('100'):
        print('up I:OK')
        nCt += 1
    if nCt == 5:
        return True
    else:
        return False


# 设置制式
def setmode(imode):
    stx = '!'
    if imode == nzsc_Y57mode:
        # stx += 'F=' + nzscY57Dict['F'] + ';'
        stx += 'YP=' + nzscY57Dict['Y'] + ';'
        stx += 'o=' + nzscY57Dict['o']
        # stx += 'UB=' + nzscY57Dict['UB'] + ';'
    elif imode == nzsc_Vmode:
        # stx += 'F=' + nzscVDict['F'] + ';'
        stx += 'VP=' + nzscVDict['V'] + ';'
        stx += 'o=' + nzscVDict['o']
        # stx += 'UB=' + nzscVDict['UB'] + ';'
    else:
        # stx += 'F=' + nzscY220Dict['F'] + ';'
        stx += 'YP=' + nzscY220Dict['Y'] + ';'
        stx += 'o=' + nzscY220Dict['o']
        # stx += 'UB=' + nzscY220Dict['UB'] + ';'
    # stx += 'W=' + nzscY220Dict['W'] + ';'
    # stx += 'L=' + nzscY220Dict['L']
    stx += chr(0x0D)
    stx += chr(0x0A)
    bren = nzscTxRx(stx)[0]
    time.sleep(2.0)
    if bren is False:
        bren = nzscTxRx(stx)[0]
    return bren

# 设置额定电压电流
def setUIBbymode(imode):
    stx = '!'
    if imode == nzsc_Y57mode:
        stx += 'UB=' + nzscY57Dict['UB'] + ';'
        stx += 'IB=' + nzscY57Dict['IB']
    elif imode == nzsc_Vmode:
        stx += 'UB=' + nzscVDict['UB'] + ';'
        stx += 'IB=' + nzscVDict['IB']
    else:
        stx += 'UB=' + nzscY220Dict['UB'] + ';'
        stx += 'IB=' + nzscY220Dict['IB']
    stx += chr(0x0D)
    stx += chr(0x0A)
    bren = nzscTxRx(stx)[0]
    time.sleep(2.0)
    return bren

# 设置电压 fUvalue=100
def setUb(fUvalue):
    stx = '!'
    stx += 'UC=' + fUvalue
    stx += chr(0x0D)
    stx += chr(0x0A)
    bren = nzscTxRx(stx)[0]
    time.sleep(5.0)
    return bren

# 设置频率
def setFb(imode):
    stx = '!'
    if imode == nzsc_Y57mode:
        stx += 'FF=' + nzscY57Dict['F']
    elif imode == nzsc_Vmode:
        stx += 'FF=' + nzscVDict['F']
    else:
        stx += 'FF=' + nzscY220Dict['F']
    stx += chr(0x0D)
    stx += chr(0x0A)
    bren = nzscTxRx(stx)[0]
    time.sleep(5.0)
    return bren

# 设置电流 fuvalue=100
def setIb(fIvalue):
    stx = '!IC=' + fIvalue + ';'
    stx += chr(0x0D)
    stx += chr(0x0A)
    bren = nzscTxRx(stx)[0]
    time.sleep(6.0)
    return bren

# 设置相角 fuvalue=100
def setIbymode(fPvalue):
    # stx = '!UP=0;'
    # stx += chr(0x0D)
    # stx += chr(0x0A)
    stx1 = '!IP=' + fPvalue
    stx1 += chr(0x0D)
    stx1 += chr(0x0A)
    bren = nzscTxRx(stx1)[0]
    time.sleep(6.0)
    return bren


nzscCDict = {'U1': 0.0, 'U2': 0.0, 'U3': 0.0, 'UA1': 0.0, 'UA2': 0.0, 'UA3': 0.0,
             'I1': 0.0, 'I2': 0.0, 'I3': 0.0, 'IA1': 0.0, 'IA2': 0.0, 'IA3': 0.0}


# 生成命令帧 整定下行帧  Ua=Un;Ub=Un;Uc=Un;Ia=0In;Ib=0In;Ic=0In;fltF=30;Un=220;In=1.0
def makeframe(sset):
    stx = ''
    # print(isinstance(sset, str))
    if isinstance(sset, str) is False:
        return stx
    sUp = sset.strip().upper()
    if sUp.find(';') >= 0:
        tset = sUp.split(';')
    elif sUp.find(',') >= 0:
        tset = sUp.split(',')
    for item in tset:
        if item.find('UA=') >= 0:
            svalue1 = item.replace('UA=', '')
            svalue = svalue1.replace('UN', '')
            if len(svalue) == 0:
                nzscCDict['U1'] = 100.0
            elif svalue.find('%') >= 0:
                sb = svalue.replace('%', '')
                if len(sb) > 0:
                    try:
                        fsb = float(sb)
                        nzscCDict['U1'] = fsb
                    except ValueError:
                        pass
        elif item.find('UB=') >= 0:
            svalue1 = item.replace('UB=', '')
            svalue = svalue1.replace('UN', '')
            if len(svalue) == 0:
                nzscCDict['U2'] = 100.0
            elif svalue.find('%') >= 0:
                sb = svalue.replace('%', '')
                if len(sb) > 0:
                    try:
                        fsb = float(sb)
                        nzscCDict['U2'] = fsb
                    except ValueError:
                        pass
        elif item.find('UC=') >= 0:
            svalue1 = item.replace('UC=', '')
            svalue = svalue1.replace('UN', '')
            if len(svalue) == 0:
                nzscCDict['U3'] = 100.0
            elif svalue.find('%') >= 0:
                sb = svalue.replace('%', '')
                if len(sb) > 0:
                    try:
                        fsb = float(sb)
                        nzscCDict['U3'] = fsb
                    except ValueError:
                        pass
        elif item.find('IA=') >= 0:
            svalue1 = item.replace('IA=', '')
            svalue = svalue1.replace('IN', '')
            if len(svalue) == 0:
                nzscCDict['I1'] = 100.0
            elif svalue.find('%') >= 0:
                sb = svalue.replace('%', '')
                if len(sb) > 0:
                    try:
                        fsb = float(sb)
                        nzscCDict['I1'] = fsb
                    except ValueError:
                        pass
        elif item.find('IB=') >= 0:
            svalue1 = item.replace('IB=', '')
            svalue = svalue1.replace('IN', '')
            if len(svalue) == 0:
                nzscCDict['I2'] = 100.0
            elif svalue.find('%') >= 0:
                sb = svalue.replace('%', '')
                if len(sb) > 0:
                    try:
                        fsb = float(sb)
                        nzscCDict['I2'] = fsb
                    except ValueError:
                        pass
        elif item.find('IC=') >= 0:
            svalue1 = item.replace('IC=', '')
            svalue = svalue1.replace('IN', '')
            if len(svalue) == 0:
                nzscCDict['I3'] = 100.0
            elif svalue.find('%') >= 0:
                sb = svalue.replace('%', '')
                if len(sb) > 0:
                    try:
                        fsb = float(sb)
                        nzscCDict['I3'] = fsb
                    except ValueError:
                        pass
        elif item.find('FLTF=') >= 0:
            svalue = item.replace('FLTF=', '')
            if len(svalue) > 0:
                try:
                    fsb = float(svalue)
                    nzscCDict['IA1'] = fsb
                except ValueError:
                    pass
        elif item.find('UN=') >= 0:
            pass
        elif item.find('IN=') >= 0:
            pass
    stx = '!'
    stx += 'U1=%.0f;' % nzscCDict['U1']
    stx += 'U2=%.0f;' % nzscCDict['U2']
    stx += 'U3=%.0f;' % nzscCDict['U3']
    stx += 'IF1=%.0f;' % nzscCDict['I1']
    stx += 'IF2=%.0f;' % nzscCDict['I2']
    stx += 'IF3=%.0f;' % nzscCDict['I3']
    stx += 'IP=%.0f;' % nzscCDict['IA1']
    stx += chr(0x0D) + chr(0x0A)
    return stx


# 响应帧分析[True,{}]
def annzscframe(stxdata, srxdata):
    tret = [False]
    stxdata = stxdata.replace('\r\n', '')
    # print(stxdata)
    # print(srxdata)
    if srxdata.find(stxdata) >= 0:
        if srxdata.find('?') >= 0:
            dValue = {}
            srx = srxdata.splitlines()
            for item in srx:
                if item.find('U:') >= 0:
                    sv1 = item.split(':')
                    if len(sv1) >= 2:
                        sv2 = sv1[1].split(',')
                    if len(sv2) == 4:
                        dValue['Ua'] = sv2[0].replace(' ', '')
                        dValue['Ub'] = sv2[1].replace(' ', '')
                        dValue['Uc'] = sv2[2].replace(' ', '')
                        dValue['Uo'] = sv2[3].replace(' ', '')
                elif item.find('I:') >= 0:
                    sv1 = item.split(':')
                    if len(sv1) >= 2:
                        sv2 = sv1[1].split(',')
                    if len(sv2) == 4:
                        dValue['Ia'] = sv2[0].replace(' ', '')
                        dValue['Ib'] = sv2[1].replace(' ', '')
                        dValue['Ic'] = sv2[2].replace(' ', '')
                        dValue['Io'] = sv2[3].replace(' ', '')
                elif item.find('A:') >= 0:
                    sv1 = item.split(':')
                    if len(sv1) >= 2:
                        sv2 = sv1[1].split(',')
                    if len(sv2) == 4:
                        dValue['Aa'] = sv2[0].replace(' ', '')
                        dValue['Ab'] = sv2[1].replace(' ', '')
                        dValue['Ac'] = sv2[2].replace(' ', '')
                        dValue['Ao'] = sv2[3].replace(' ', '')
                elif item.find('F:') >= 0:
                    sv1 = item.split(':')
                    if len(sv1) >= 2:
                        sv2 = sv1[1].split(',')
                    if len(sv2) == 1:
                        dValue['F'] = sv2[0].replace(' ', '')
                elif item.find('B:') >= 0:
                    sv1 = item.split(':')
                    if len(sv1) >= 2:
                        sv2 = sv1[1].split(',')
                    if len(sv2) >= 1:
                        dValue['B'] = sv2[0].replace(' ', '')
                elif item.find('P:') >= 0:
                    sv1 = item.split(':')
                    if len(sv1) >= 2:
                        sv2 = sv1[1].split(',')
                    if len(sv2) == 4:
                        dValue['Pa'] = sv2[0].replace(' ', '')
                        dValue['Pb'] = sv2[1].replace(' ', '')
                        dValue['Pc'] = sv2[2].replace(' ', '')
                        dValue['Pz'] = sv2[3].replace(' ', '')
                elif item.find('R:') >= 0:
                    sv1 = item.split(':')
                    if len(sv1) >= 2:
                        sv2 = sv1[1].split(',')
                    if len(sv2) == 4:
                        dValue['Ra'] = sv2[0].replace(' ', '')
                        dValue['Rb'] = sv2[1].replace(' ', '')
                        dValue['Rc'] = sv2[2].replace(' ', '')
                        dValue['Rz'] = sv2[3].replace(' ', '')
                elif item.find('M:') >= 0:
                    sv1 = item.split(':')
                    if len(sv1) >= 2:
                        sv2 = sv1[1].split(',')
                    if len(sv2) == 4:
                        dValue['Cosa'] = sv2[0].replace(' ', '')
                        dValue['Cosb'] = sv2[1].replace(' ', '')
                        dValue['Cosc'] = sv2[2].replace(' ', '')
                        dValue['Coso'] = sv2[3].replace(' ', '')
                elif item.find('N:') >= 0:
                    sv1 = item.split(':')
                    if len(sv1) >= 2:
                        sv2 = sv1[1].split(',')
                    if len(sv2) == 4:
                        dValue['Sina'] = sv2[0].replace(' ', '')
                        dValue['Sinb'] = sv2[1].replace(' ', '')
                        dValue['Sinc'] = sv2[2].replace(' ', '')
                        dValue['Sino'] = sv2[3].replace(' ', '')
            tret[0] = True
            tret.append(dValue)
        elif srxdata.find('!') >= 0:
            tret[0] = True
            tret.append({})
        else:
            tret[0] = False
            tret.append({})
    return tret


# return [True, {'Pz': '6553.76', 'Rz': '-14.6111',}]
def nzscTxRx(sTx):
    if len(COMLIST) == 0:
        return [False]
    if COMLIST[0].isOpen() is False:
        return [False]
    print('TxtoSet:'+sTx)
    COMLIST[0].write(sTx)
    time.sleep(RXOUTTIME)
    sRx = COMLIST[0].read(RXBUFFSIZE)
    print('RxfromSet:' + sRx)
    retn = annzscframe(sTx, sRx)
    return retn

# sset Ua=Un;Ub=Un;Uc=Un;Ia=0In;Ib=0In;Ic=0In;fltF=0 Un=220,In=1.0
def StartSource(sset):
    bret = False
    stx = makeframe(sset)
    print(stx)
    bret = nzscTxRx(stx)[0]
    return bret


# return [True, {'Pz': '6553.76', 'Rz': '-14.6111',}]
def ReadSource():
    stx = '?U;I;A;F;B;P;R;M;N' + chr(0x0D) + chr(0x0A)
    value = nzscTxRx(stx)
    if len(value) >= 2:
        return value[1]
    else:
        return {}


# !U=0;I=0
def StopSource():
    bret = False
    stx = '!U=0;I=0' + chr(0x0D) + chr(0x0A)
    bret = nzscTxRx(stx)[0]
    return bret


# 初始化误差串口com3
def initwccom():
    pass


if __name__ == '__main__':
    initsyscom(0)
    ss = 'Ua=Un;Ub=Un;Uc=Un;Ia=In;Ib=In;Ic=In;fltF=45'
    StartSource(ss)
    vv = ReadSource()
    print(vv)
    # StopSource()
    time.sleep(3.0)
    vv1 = ReadSource()
    print(vv1)
    # stx = '!YP=0;o=0\r\n'
    # srx = '!YP=0;o=0\r\n'
    # srx = '?U;I;A;F;B;P;R;M;N\r\nU: 219.794, 219.576, 216.383, 0.00000\r\nI: 9.99388, 9.99755, 9.99482, 0.00000\r\n' \
    #       'A: 359.790, 359.694, 0.20692, 359.872\r\nF: 49.9989\r\nB:--\r\n' \
    #       'P: 2196.30, 2194.98, 2162.48, 6553.76\r\nR:-10.8320,-2.33634,-1.44278,-14.6111\r\n' \
    #       'M: 0.99986, 0.99988, 0.99989, 0.99988\r\nN:-0.00493,-0.00106,-0.00066,-0.00222'
    # ss = annzscframe(stx,srx)
    # print ss
    # print '串口测试'
    # t = serial.Serial('COM1')
    # t.baudrate = 2400
    # t.parity = 'E'
    # t.bytesize = 8
    # t.stopbits = 1
    # t.timeout = 3
    # t.xonxoff = False
    # t.rtscts = False
    # t.dsrdtr = False
    # t.writeTimeout = 2
    # print t.BAUDRATES
    # print t.PARITIES
    # print t.STOPBITS
    # print u'串口打开状态:'
    # print t.portstr
    # print t.baudrate
    # print str(t.bytesize) + t.parity + str(t.stopbits)
    # print t.name
    # print t.isOpen()
    # t.close()
    # print t.isOpen()
    # t.open()
    # print t.isOpen()
    # print t._timeout
    # print t._writeTimeout
    # data = [0xFE, 0xFE,0xFE,0x68,0x08,0x00,0x00,0x00,0x00,0x00,0x68,0x11,0x04,0x33,0x032, 0x34, 0x35, 0xBB, 0x16]
    # data = 'FE FE FE 68 08 00 00 00 00 00 68 11 04 33 32 34 35 BB 16 '
    # out = ''
    # frame = data.replace(' ', '')
    # print len(frame)/2
    # for i in range(0, len(frame), 2):
    #     tt = frame[i:i+2]
    #     out += chr(int(tt, 16))
    # for i in data:
    #    out += chr(i)
    # hexShow(out)
    # n = t.write(out)
    # print n
    # time.sleep(1)
    # str = t.read(1024)
    # rdhex = hexShow(str)
    # str = t.read(n)
    # print hexShow(str)
    # print rdhex
    # ll = isReturn(rdhex, '000000000008', CMD_READ, '0201FF00')                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               

