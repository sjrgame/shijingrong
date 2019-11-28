
import sys
import os
import logging
# import time
import datetime
from paramiko import AuthenticationException
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import NoValidConnectionsError
import asn1PERser

# from ftplib import FTP  modularTerminal

class MySshClient:
    def __init__(self):
        self.ssh_client = SSHClient()

    # 此函数用于输入用户名密码登录主机
    # noinspection PyBroadException
    def ssh_login(self, host_ip: str, username: str, password: str) -> int:
        try:
            # 设置允许连接known_hosts文件中的主机（默认连接不在known_hosts文件中的主机会拒绝连接抛出SSHException）
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            self.ssh_client.connect(host_ip, port=22, username=username, password=password)
        except AuthenticationException:
            logging.warning('username or password error')
            return 1001
        except NoValidConnectionsError:
            logging.warning('connect time out')
            return 1002
        except Exception:
            logging.warning('unknown error')
            print("Unexpected error:", sys.exc_info()[0])
            return 1003
        return 1000

    # 此函数用于执行command参数中的命令并打印命令执行结果
    def execute_some_command(self, command):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        strRet = stdout.read().decode()
        print(strRet)
        logging.debug(strRet)
        return strRet

    # 此函数用于退出登录
    def ssh_logout(self):
        """此函数用于退出登录"""
        logging.warning('will exit host')
        self.ssh_client.close()


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
    Command = 'kubectl get nodes'
    # 实例化
    my_ssh_client = MySshClient()
    # 登录，如果返回结果为1000，那么执行命令，然后退出
    if my_ssh_client.ssh_login(Host_ip, Username, Password) == 1000:
        logging.warning(f"{Host_ip}-login success, will execute command：'{Command}'")
        Command = input("请输入命令：").strip()

        my_ssh_client.execute_some_command(Command)
        my_ssh_client.ssh_logout()
        # print(my_ssh_client.ssh_logout.__doc__)
        input()
    else:
        print("SSH登录失败")
