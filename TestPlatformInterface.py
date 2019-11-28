
import sys
import time
import datetime
import logging
import os
import xlrd
import xlwt
#from pyExcelerator import *
from Protocol.jsonly import *
from sshsjr import MySshClient
import datetime
from paramiko import AuthenticationException
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import NoValidConnectionsError


__EXCELTYPE__ = 'param'
rootdir = u'E:\\2019work\designMeter20190725\designMeter'
TestTemplatePath =rootdir + "\config"


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
   # wb = Workbook()
    wb = xlwt.Workbook()
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


# 处理数据
def procexcel(sshClient:MySshClient,excellist):
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
        print(excellist[itm]['op'].find(CMD_READ645))

        if excellist[itm]['op'].find(CMD_READ645) >= 0:
            print('下发命令')
            SendCommandSSH(sshClient, excellist[itm])
            # time.sleep(JGTIME)

    return True

def SendCommandSSH(sshClient:MySshClient,ldata):
    strCommand = ldata['命令内容']
    return True

if __name__ == '__main__':
    snow = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%y/%m/%d %H:%M:%S',
                        filename=os.path.curdir + '\log\\' + snow + 'SSH.log', level=logging.DEBUG)
    # 远程主机IP
    Host_ip = '192.168.127.98'
    # 远程主机用户名
    Username = 'root'
    # 远程主机密码
    Password = 'sjr'
    # 要执行的shell命令；换成自己想要执行的命令
    # 自己使用ssh时，命令怎么敲的command参数就怎么写
    Command = ''
    # 实例化
    ssh_client = MySshClient()
    # 登录，如果返回结果为1000，那么执行命令，然后退出

    loginResult = ssh_client.ssh_login(Host_ip, Username, Password)
    if loginResult != 1000:
        print("SSH登录失败")
        logging.warning(f"{Host_ip}-SSH 登录失败")
        exec()
    print("SSH登录成功")
    logging.warning(f"{Host_ip}-SSH 登录成功")

    dllist = readexcel(TestTemplatePath + '/平台测试模板.xlsx', u'平台测试')
    if dllist is not None:
        print('测试模板读取完毕')

    procexcel(ssh_client,dllist)
    # ssh_client.execute_some_command(Command)

    ssh_client.ssh_logout()
    # print(my_ssh_client.ssh_logout.__doc__)
    input()
