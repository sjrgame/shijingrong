# coding=utf-8

import time
import logging
import os
import xlrd
from pyExcelerator import *
from Protocol.jsonly import *
from Protocol.AESlyEX import *
from Protocol.dl645 import *
import socket
import threading
import socketserver


__EXCELTYPE__ = 'param'
# __EXCELTYPE__ = 'task'
DSOCKTTIMEOUT = 300
BUFFSIZE = 512
# 接收超时
RXOUTTIME = 60.0
# 发送
TXOUTTIME = 1.0
# 间隔
JGTIME = 1.0


client_addr = []
client_socket = []
public_sRxBuff = []


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    ip = ''
    port = ''
    timeout = DSOCKTTIMEOUT

    def setup(self):
        self.ip = self.client_address[0].strip()
        self.port = self.client_address[1]
        self.request.settimeout(self.timeout)
        print(self.ip + ':' + str(self.port) + 'connected server!')
        logging.info(self.ip + ':' + str(self.port) + 'connected server!')
        client_addr.append(self.client_address)
        client_socket.append(self.request)

    def handle(self):
        while True:
            time.sleep(0.1)
            try:
                if self.request:
                    data = self.request.recv(BUFFSIZE)
                else:
                    data = ''
            except socket.timeout:
                print(self.ip + ':' + str(self.port) + 'Rx timeout!break connect!')
                logging.info(self.ip + ':' + str(self.port) + 'Rx timeout!break connect!')
                # break
            if data:
                cur_thread = threading.current_thread()
                response = bytes("{}: {}".format(cur_thread.name, data))
                # self.request.sendall(response)
                print(response)
                logging.info('current thread:' + response)
                bb = isReturn(data, CMD_JSON_LOGIN, ['04A20209'])
                hh = isReturn(data, CMD_JSON_HEART, ['04A20208'])
                if bb[0]:
                    logging.info('login!')
                    time.sleep(1.0)
                    self.request.sendall(updatecrcffff(data))
                    time.sleep(2.0)
                    logging.info(('login-tx:' + updatecrcffff(data)))
                    print(updatecrcffff(data))
                elif hh[0]:
                    logging.info('Heart!')
                    time.sleep(1.0)
                    self.request.sendall(updatecrcffff(data))
                    time.sleep(1.5)
                    logging.info(('Heart-tx:' + updatecrcffff(data)))
                    print(updatecrcffff(data))
                else:
                    public_sRxBuff.append(data)

    def finish(self):
        print('client is disconnect!')
        client_addr.remove(self.client_address)
        client_socket.remove(self.request)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.sendall(bytes(message))
    response = str(sock.recv(1024))
    print("Received: {}".format(response))


# 检查配置文件
def readexcel(lfile, sname):
    # print lfile
    workbook = xlrd.open_workbook(lfile)
    rTem = {}
    for ns in workbook.sheet_names():
        # print (ns)
        sheet2 = workbook.sheet_by_name(ns)
        # print sheet2.nrows
        if ns == sname:
            for ir in range(0, sheet2.nrows):
                rowvalue = {}
                if __EXCELTYPE__ == "param":
                    rowvalue['op'] = sheet2.cell(ir, 0).value
                    rowvalue['id'] = sheet2.cell(ir, 1).value
                    rowvalue['format'] = sheet2.cell(ir, 2).value
                    rowvalue['len'] = sheet2.cell(ir, 3).value
                    rowvalue['unit'] = sheet2.cell(ir, 4).value
                    rowvalue['name'] = sheet2.cell(ir, 5).value
                    rowvalue['data'] = sheet2.cell(ir, 6).value
                    rowvalue['expect'] = sheet2.cell(ir, 7).value
                    rowvalue['real'] = sheet2.cell(ir, 8).value
                    rowvalue['result'] = sheet2.cell(ir, 9).value
                    rTem[ir] = rowvalue
                    # print rTem[ir]['op']
    return rTem


def SaveAsExcel(temfile, tlist):
    # print temfile
    wb = Workbook()
    ws0 = wb.add_sheet('sheet')
    # print tlist[0]['name']
    for key in tlist:
        # print tlist[key]
        if tlist[key]['op'] == u'操作':
            ws0.write(0, 0, tlist[key]['op'])
            ws0.write(0, 1, tlist[key]['id'])
            ws0.write(0, 2, tlist[key]['format'])
            ws0.write(0, 3, tlist[key]['len'])
            ws0.write(0, 4, tlist[key]['unit'])
            ws0.write(0, 5, tlist[key]['name'])
            ws0.write(0, 6, tlist[key]['data'])
            ws0.write(0, 7, tlist[key]['expect'])
            ws0.write(0, 8, tlist[key]['real'])
            ws0.write(0, 9, tlist[key]['result'])
        else:
            ws0.write(key, 0, tlist[key]['op'])
            ws0.write(key, 1, tlist[key]['id'])
            ws0.write(key, 2, tlist[key]['format'])
            ws0.write(key, 3, tlist[key]['len'])
            ws0.write(key, 4, tlist[key]['unit'])
            ws0.write(key, 5, tlist[key]['name'])
            ws0.write(key, 6, tlist[key]['data'])
            ws0.write(key, 7, tlist[key]['expect'])
            ws0.write(key, 8, tlist[key]['real'])
            ws0.write(key, 9, tlist[key]['result'])
    wb.save(temfile)


def checkfile(pfiles):
    path = "D:/python/designMeter/config"
    files = os.listdir(path)
    c = 0
    for temf in pfiles:
        for fil in files:
            if fil.decode('gbk') == pfiles[temf]:
                c += 1
    if c == len(pfiles):
        return True
    return False


# 检查本用例所需的设备
def checkset():
    return True


# 检查在线
def checkRtuline():
    if len(client_socket) > 0:
        return True
    else:
        return False


# 处理数据
def procexcel(excellist):
    for itm in excellist:
        temstr = u'步骤:' + str(itm)
        if isinstance(excellist[itm]['op'], float):
            temstr += str(excellist[itm]['op']) + '|'
        else:
            temstr += excellist[itm]['op'] + '|'
        if isinstance(excellist[itm]['id'], float):
            temstr += str(int(excellist[itm]['id'])) + '|'
        else:
            temstr += excellist[itm]['id'].strip() + '|'
        if isinstance(excellist[itm]['format'], float):
            temstr += str(excellist[itm]['format']) + '|'
        else:
            temstr += excellist[itm]['format'].strip() + '|'
        if isinstance(excellist[itm]['len'], float):
            temstr += str(excellist[itm]['len']) + '|'
        else:
            temstr += excellist[itm]['len'].strip() + '|'
        if isinstance(excellist[itm]['unit'], float):
            temstr += str(excellist[itm]['unit']) + '|'
        else:
            temstr += excellist[itm]['unit'].strip() + '|'
        if isinstance(excellist[itm]['name'], float):
            temstr += str(excellist[itm]['name']) + '|'
        else:
            temstr += excellist[itm]['name'].strip() + '|'
        if isinstance(excellist[itm]['data'], float):
            temstr += str(int(excellist[itm]['data'])) + '|'
        else:
            temstr += excellist[itm]['data'] + '|'
        if isinstance(excellist[itm]['expect'], float):
            temstr += str(int(excellist[itm]['expect'])) + '|'
        else:
            temstr += excellist[itm]['expect'] + '|'
        if isinstance(excellist[itm]['real'], float):
            temstr += str(excellist[itm]['real']) + '|'
        else:
            temstr += excellist[itm]['real'] + '|'
        logging.info(temstr)
        if excellist[itm]['op'].find(CMD_JSON_SET) >= 0:
            writertudata(excellist[itm], itm, excellist)
            time.sleep(JGTIME)
        elif excellist[itm]['op'].find(CMD_JSON_READ) >= 0:
            readrtudata(excellist[itm], itm, excellist)
            time.sleep(JGTIME)
        elif excellist[itm]['op'].find(CMD_WAIT) >= 0:
            logging.info('outtimewait:' + excellist[itm]['data'])
            print('outtimewait:' + excellist[itm]['data'])
            time.sleep(int(excellist[itm]['data']))
        elif excellist[itm]['op'].find(CMD_JSON_TRANS) >= 0:
            transmeterdata(excellist[itm], itm, excellist)
            time.sleep(JGTIME)
    return True


def totalresult():
    return True


# 设置电源
def setsource(ldata):
    slist = ldata['data'].split(';')
    # logging.info(slist)
    stemlist = {}
    for i in slist:
        ite = i.split('=')
        stemlist[ite[0]] = ite[1]
    logging.info(stemlist)
    # 写入电源接口add
    return True


# 读电源数据
# def readsource(ldata):pass


# 写数据
def writertudata(ldata, index, lists):
    if isinstance(ldata['op'], str) and ldata['op'] == '':
        return False
    if ldata['op'].replace(' ', '') != 'Set':
        return False
    if isinstance(ldata['id'], str) and len(ldata['id'].relace(' ', '')) < 8:
        return False
    sdata = ''
    sid = ldata['id'].replace(' ', '')[0:8]
    if sid.find('04A10101') >= 0:
        # 向下读取7条记录存储
        for i in range(0, 7):
            if i == 0:
                if isinstance(lists[index+i]['data'], float):
                    sdata = str(int(lists[index+i]['data']))
                else:
                    sdata = lists[index + i]['data']
            else:
                if isinstance(lists[index + i]['data'], float):
                    sdata += '#' + str(int(lists[index + i]['data']))
                else:
                    sdata += '#' + lists[index + i]['data']
    elif sid.find('04A30100') >= 0 or sid.find('04A30101') >= 0 or sid.find('04A30200') >= 0 \
            or sid.find('04A30201') >= 0:
        key = '1234567890123456'
        cryptor = ly_aes(key)
        if isinstance(ldata['data'], float):
            msg = str(int(ldata['data']))
        else:
            msg = ldata['data']
        cipher = cryptor.encrypt(msg, len(msg))
        sdata = cipher
    else:
        if isinstance(ldata['data'], float):
            sdata = str(int(ldata['data']))
        else:
            sdata = ldata['data']
    dcts = {sid: sdata}
    scm = ldata['op'].replace(' ', '')
    sTx = makepjson(scm, index, dcts)
    logging.info('Tx:' + sTx)
    if len(client_socket) > 0:
        ints = len(client_socket) - 1
        client_socket[ints].sendall(sTx)
    time.sleep(TXOUTTIME)
    itime = 0.0
    istart = time.time()
    slst = []
    while itime < RXOUTTIME:
        time.sleep(0.2)
        if len(public_sRxBuff) > 0:
            slst = isReturn(public_sRxBuff[0], CMD_JSON_SET, [sid])
            logging.info('Rx:' + public_sRxBuff[0])
            del(public_sRxBuff[0])
        if len(slst) > 0 and slst[0]:
            logging.info('wait:' + str(itime))
            print('wait:' + str(itime))
            break
        itime = time.time() - istart
    datalist = []
    print(slst)
    if len(slst) == 3:
        datalist.append(slst[2][sid])
        ldata['real'] = datalist[0]
# 判断结论
    if ldata['expect'].find(ldata['real']) >= 0 and ldata['real'] != '':
        ldata['result'] = u'合格'
    else:
        ldata['result'] = u'不合格'
    return True


# 读数据
def readrtudata(ldata, index, lists):
    if isinstance(ldata['op'], str) and ldata['op'] == '':
        return False
    if ldata['op'].replace(' ', '') != 'Read':
        return False
    if isinstance(ldata['id'], str) and len(ldata['id'].relace(' ', '')) < 8:
        return False
    sid = ldata['id'].replace(' ', '')[0:8]
    sdata = ''
    if isinstance(ldata['data'], float):
        sdata = str(int(ldata['data']))
    else:
        sdata = ldata['data']
    tdcts = {sid: sdata}
    scm = ldata['op'].replace(' ', '')
    sTx = makepjson(scm, index, tdcts)
    if sTx == False:
        return False
    logging.info('Tx:' + sTx)
    # if len(client_socket) > 0:
    #    ints = len(client_socket) - 1
    #    client_socket[ints].sendall(sTx)
    for i in client_socket:
        i.sendall(sTx)
    time.sleep(TXOUTTIME)
    itime = 0.0
    istart = time.time()
    slst = []
    while itime < RXOUTTIME:
        time.sleep(0.2)
        if len(public_sRxBuff) > 0:
            slst = isReturn(public_sRxBuff[0], CMD_JSON_READ, [sid])
            logging.info('Rx:' + public_sRxBuff[0])
            del(public_sRxBuff[0])
        if len(slst) > 0 and slst[0]:
            logging.info('wait:' + str(itime))
            print('wait:' + str(itime))
            break
        itime = time.time() - istart
    datalist = []
    print(slst)
    if len(slst) == 3 and sid != '04A10101':
        datalist.append(slst[2][sid])
        ldata['real'] = datalist[0]
    elif len(slst) == 3 and sid == '04A10101':
        datalist = slst[2][sid].split('#')
        if len(datalist) > 7:
            tem = datalist[6:]
            del(datalist[6:])
            shh = ''
            for i in range(0, len(tem), 1):
                if i == 0:
                    shh = tem[i]
                else:
                    shh += '#' + tem[i]
            datalist.append(shh)
        for i in range(0, len(datalist), 1):
            lists[index + i]['real'] = datalist[i]
# 判断结论
    if sid.find('04A10101') >= 0:
        bres = False
        for i in range(0, len(datalist), 1):
            if lists[index + i]['expect'].find(datalist[i]) >= 0:
                bres = True
            else:
                bres = False
                break
        if not bres:
            ldata['result'] = u'不合格'
        else:
            ldata['result'] = u'合格'
    else:
        if ldata['expect'].find(ldata['real']) >= 0 and ldata['real'] != '':
            ldata['result'] = u'合格'
        else:
            ldata['result'] = u'不合格'
    return True


# 透传电表数据
def transmeterdata(ldata, index, lists):
    if isinstance(ldata['op'], str) and ldata['op'] == '':
        return False
    if ldata['op'].replace(' ', '') != 'Read':
        return False
    if isinstance(ldata['id'], str) and len(ldata['id'].relace(' ', '')) < 8:
        return False
    sid = ldata['id'].replace(' ', '')[0:8]
    sdata = ''
    if isinstance(ldata['data'], float):
        sdata = str(int(ldata['data']))
    else:
        sdata = ldata['data']
    sdd = make645Frame('', 'AAAAAAAAAAAA', '11', sid, sdata, 1)
    tdcts = {'F0000010': sdd}
    scm = ldata['op'].replace(' ', '')
    sTx = makepjson(scm, index, tdcts)
    if sTx == False:
        return False
    logging.info('Tx:' + sTx)
    # if len(client_socket) > 0:
    #    ints = len(client_socket) - 1
    #    client_socket[ints].sendall(sTx)
    for i in client_socket:
        i.sendall(sTx)
    time.sleep(TXOUTTIME)
    itime = 0.0
    istart = time.time()
    slst = []
    while itime < RXOUTTIME:
        time.sleep(0.2)
        if len(public_sRxBuff) > 0:
            slst = isReturn(public_sRxBuff[0], CMD_JSON_READ, [sid])
            logging.info('Rx:' + public_sRxBuff[0])
            del(public_sRxBuff[0])
        if len(slst) > 0 and slst[0]:
            logging.info('wait:' + str(itime))
            print('wait:' + str(itime))
            break
        itime = time.time() - istart
    datalist = []
    print(slst)
    if len(slst) == 3 and sid != '04A10101':
        datalist.append(slst[2][sid])
        ldata['real'] = datalist[0]
    elif len(slst) == 3 and sid == '04A10101':
        datalist = slst[2][sid].split('#')
        if len(datalist) > 7:
            tem = datalist[6:]
            del(datalist[6:])
            shh = ''
            for i in range(0, len(tem), 1):
                if i == 0:
                    shh = tem[i]
                else:
                    shh += '#' + tem[i]
            datalist.append(shh)
        for i in range(0, len(datalist), 1):
            lists[index + i]['real'] = datalist[i]
# 判断结论
    if sid.find('04A10101') >= 0:
        bres = False
        for i in range(0, len(datalist), 1):
            if lists[index + i]['expect'].find(datalist[i]) >= 0:
                bres = True
            else:
                bres = False
                break
        if not bres:
            ldata['result'] = u'不合格'
        else:
            ldata['result'] = u'合格'
    else:
        if ldata['expect'].find(ldata['real']) >= 0 and ldata['real'] != '':
            ldata['result'] = u'合格'
        else:
            ldata['result'] = u'不合格'
    return True


def initModel():
    # print(sys.version)
    snow = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%y/%m/%d %H:%M:%S',
                        filename='D:\python\designMeter\log\\'+snow+'TLY1502.log', level=logging.DEBUG)


# 定义常量
paramfiles = {'parameter': u'产品需求确认模版.xlsx'}


def main():
    # 检查指定目录下文件是否齐,读当参数设置流程模版存内存字典
    initModel()
    # 启动服务
    logging.info(u'开始启动服务器!')
    HOST, PORT = "192.168.124.2", 11039
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    # ip, port = server.server_address
    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    logging.info(u'启动服务器成功!')
    # 检查终端是否在线
    logging.info(u'开始检查终端在线!')
    time.sleep(60)
    if checkRtuline():
        logging.info(u'终端在线!')
    else:
        logging.warning(u'终端不在线!')
        # server.shutdown()
        # server.server_close()
        # exit()
    paramlist = {}
    qtcslist = {}
    tasklist = {}
    sjlist = {}
    ydjlist = {}
    rdjlist = {}
    qxlist = {}
    xsllist = {}
    dllist = {}
    logging.info(u'开始检查配置文件!')
    if checkfile(paramfiles):
        path = "D:\python\designMeter\config"
        # daidlist =  readexcel(path+'/'+ paramfiles['relationship'])
        dllist = readexcel(path+'/' + paramfiles['parameter'], u'电量')
        print(len(dllist))
        xsllist = readexcel(path+'/' + paramfiles['parameter'], u'瞬时量')
        print(len(xsllist))
        qxlist = readexcel(path+'/' + paramfiles['parameter'], u'曲线')
        print(len(qxlist))
        ydjlist = readexcel(path+'/' + paramfiles['parameter'], u'月冻结')
        print(len(ydjlist))
        rdjlist = readexcel(path+'/' + paramfiles['parameter'], u'日冻结')
        print(len(rdjlist))
        sjlist = readexcel(path+'/' + paramfiles['parameter'], u'事件')
        print(len(sjlist))
        tasklist = readexcel(path+'/' + paramfiles['parameter'], u'任务参数')
        print(len(tasklist))
        qtcslist = readexcel(path+'/' + paramfiles['parameter'], u'其他参数')
        print(len(qtcslist))
        paramlist = readexcel(path+'/' + paramfiles['parameter'], u'参变量')
        print(len(paramlist))
        logging.info(u'配置文件齐备!')
    else:
        logging.warning(u'配置文件不齐备!')
        exit()
    # if procexcel(dllist):
    #     logging.info(u'电量,合格!')
    # if procexcel(xsllist):
    #     logging.info(u'瞬时量,合格!')
    # now = datetime.datetime.now()
    # path = "D:\python\designMeter\\report\dl"+now.strftime('%Y%m%d%H%M%S')+'.xls'
    # SaveAsExcel(path, dllist)
    # path = "D:\python\designMeter\\report\\xsl"+now.strftime('%Y%m%d%H%M%S')+'.xls'
    # SaveAsExcel(path, xsllist)

    # if procexcel(paramlist):
    #     logging.info(u'参变量,合格!')
    # now = datetime.datetime.now()
    # path = "D:\python\designMeter\\report\param"+now.strftime('%Y%m%d%H%M%S')+'.xls'
    # SaveAsExcel(path, paramlist)
    if procexcel(qtcslist):
        logging.info(u'其他参数,合格!')
    now = datetime.datetime.now()
    path = "D:\python\designMeter\\report\qtcs"+now.strftime('%Y%m%d%H%M%S')+'.xls'
    SaveAsExcel(path, qtcslist)

    # if procexcel(tasklist):
    #    logging.info(u'任务参数,合格!')
    # if procexcel(qxlist):
    #     logging.info(u'曲线,合格!')
    # now = datetime.datetime.now()
    # path = "D:\python\designMeter\\report\\task"+now.strftime('%Y%m%d%H%M%S')+'.xls'
    # SaveAsExcel(path, tasklist)
    # path = "D:\python\designMeter\\report\qx"+now.strftime('%Y%m%d%H%M%S')+'.xls'
    # SaveAsExcel(path, qxlist)

    # if procexcel(rdjlist):
    #     logging.info(u'日冻结,合格!')
    # now = datetime.datetime.now()
    # path = "D:\python\designMeter\\report\\rdj"+now.strftime('%Y%m%d%H%M%S')+'.xls'
    # SaveAsExcel(path, rdjlist)

    # if procexcel(ydjlist):
    #     logging.info(u'月冻结,合格!')
    # now = datetime.datetime.now()
    # path = "D:\python\designMeter\\report\ydj"+now.strftime('%Y%m%d%H%M%S')+'.xls'
    # SaveAsExcel(path, ydjlist)

    # if procexcel(sjlist):
    #     logging.info(u'事件,合格!')
    # now = datetime.datetime.now()
    # path = "D:\python\designMeter\\report\sj"+now.strftime('%Y%m%d%H%M%S')+'.xls'
    # SaveAsExcel(path, sjlist)

    server.shutdown()
    server.server_close()



if __name__ == '__main__':
    main()
