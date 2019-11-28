from ftplib import FTP


def ftpconnect(host, username, password):
    ftp = FTP()
    ftp.set_debuglevel(2)
    ftp.connect(host, 21)
    ftp.login(username, password)
    return ftp

def downloadfile(ftp, remotepath, localpath):
    # 从ftp下载文件
    bufsize = 1024
    fp = open(localpath, 'wb')
    ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize)
    ftp.set_debuglevel(0)
    fp.close()

def uploadfile(ftp, localpath, remotepath):
    # 从本地上传文件到ftp
    bufsize = 1024
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR ' + remotepath, fp, bufsize)
    ftp.set_debuglevel(0)
    fp.close()

if __name__ == "__main__":
    ftp = ftpconnect("10.1.2.254", "download", "download")
    uploadfile(ftp, "/home/rxf/other/PlatServerTest/2.jpg", "D:/download/Ranxiangfei/2.jpg")
    downloadfile(ftp, "D:/download/Ranxiangfei/svn/V2.0.xxx.171030_Alpha/xzrs.tar.gz",
              "/home/rxf/svn/V2.0.xxx.171030_Alpha/xzrs.tar.gz")

    ftp.quit()