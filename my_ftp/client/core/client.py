import json
import struct
import socket
import hashlib
import os

class SocketClient:
    addr = ('127.0.0.1',9000)
    sk = socket.socket()
    sk.connect(addr)

    @classmethod
    def recv(cls,use_pro = True, info_len=1024):
        if use_pro:
            info_len = cls.sk.recv(4)
            info_len = struct.unpack('i', info_len)[0]
        res = cls.sk.recv(info_len).decode()
        res_d = json.loads(res)
        return res_d

    @classmethod
    def send(cls,dic):
        str_dic = json.dumps(dic)
        cls.sk.send(str_dic.encode())

    @classmethod
    def myexit(cls):
        operate_dict = {
            'operate': 'exit'}
        cls.send(operate_dict)
        exit()

class Auth(SocketClient):
    operate_lst = [('登陆', 'login'), ('注册', 'register'), ('退出','myexit')]
    @classmethod
    def auth(cls,opt):
        usr = input('username :').strip()
        pwd = input('password :').strip()
        dic = {'user': usr, 'passwd': pwd, 'operate': opt}
        cls.send(dic)
        res_d = cls.recv(use_pro=False)
        return res_d
    @classmethod
    def register(cls):
        return cls.auth('register')

    @classmethod
    def login(cls):
        return cls.auth('login')

class FTPClient(SocketClient):
    operate_lst = [('下载', 'download'),('上传','upload'), ('查看当前目录', 'ls'),
                   ('进入下一集目录', 'cd'),('新建文件夹', 'mkdir')
                   ,('退出', 'myexit')]
    @staticmethod
    def processBar(num, total):
        rate = num / total
        rate_num = int(rate * 100)
        if rate_num == 100:
            r = '\r%s>%d%%' % ('=' * rate_num, rate_num,)
        else:
            r = '\r%s>%d%%' % ('=' * rate_num, rate_num,)
        print(r,end = '')

    @classmethod
    def download(cls):
        '''download
            给server端发送需求
            操作 : 下载
            file : filename
        '''
        operate_dict = {
            'operate' : 'download',
            'filename': 'sql_test.mp4'
        }
        cls.send(operate_dict)
        file_dic = cls.recv()      # 接收要下载的文件信息
        total = file_dic['filesize']
        md5_obj = hashlib.md5()
        with open(file_dic['filename']+'.download','wb') as f:
            while file_dic['filesize']:
                if file_dic['filesize']< 2048:
                    content = cls.sk.recv(file_dic['filesize'])
                else:
                    content = cls.sk.recv(2048)  # 接收文件
                md5_obj.update(content)
                f.write(content)
                file_dic['filesize'] -= len(content)
                cls.processBar(total - file_dic['filesize'], total)
        md5code = md5_obj.hexdigest()
        ret = cls.recv()
        if ret['md5'] == md5code:
            print('下载成功')
        else:
            print('下载失败')

    @classmethod
    def upload(cls):
        filesize = os.path.getsize('cn_win_srv_2003_r2_enterprise_with_sp2_vl_cd1_X13-46432.iso')
        print(filesize,type(filesize))
        operate_dict = {
            'operate': 'upload',
            'filename': 'cn_win_srv_2003_r2_enterprise_with_sp2_vl_cd1_X13-46432.iso',
            'filesize':filesize
        }
        cls.send(operate_dict)
        md5_obj = hashlib.md5()
        with open(operate_dict['filename'], 'rb') as f:
            send_len = 0
            total = filesize
            while filesize:
                content = f.read(20480)
                md5_obj.update(content)
                cls.sk.send(content)
                filesize -= len(content)
                send_len += len(content)
                cls.processBar(send_len, total)
        md5code = md5_obj.hexdigest()
        ret = cls.recv()
        if ret['md5'] == md5code:
            print('上传成功')
        else:
            print('上传失败')

    @classmethod
    def ls(cls):
        operate_dict = {'operate': 'ls'}
        cls.send(operate_dict)
        dic = cls.recv()
        print('文件夹 : ')
        for index,name in enumerate(dic['dir'],1):
            print(index,name)
        print('文件 : ')
        for index, name in enumerate(dic['file'], 1):
            print(index, name)
        print()

    @classmethod
    def mkdir(cls):
        dirname = input('请输入新的文件夹名 >>>')
        operate_dict = {'operate': 'mkdir','dirname':dirname}
        cls.send(operate_dict)
        dic = cls.recv()
        print(dic['info'])

    @classmethod
    def cd(cls):
        cls.ls()
        name = input('请输入文件夹的名字')
        operate_dict = {'operate': 'cd','dir':name}
        cls.send(operate_dict)
        dic = cls.recv()
        if dic['flag']:
            print('文件夹 : ')
            for index, name in enumerate(dic['info']['dir'], 1):
                print(index, name)
            print('文件 : ')
            for index, name in enumerate(dic['info']['file'], 1):
                print(index, name)
        else:
            print(dic['info'])

def main(clas):
    for index,opt_tup in enumerate(clas.operate_lst,1):
        print(index,opt_tup[0])
    num = int(input('选择序号 >>>').strip())
    if hasattr(clas,clas.operate_lst[num-1][1]):
        ret = getattr(clas,clas.operate_lst[num-1][1])()
        return ret


while True:
    ret = main(Auth)
    print(ret['info'])
    if ret['result']:
        while True:
            print('请选择您要做的操作 :')
            main(FTPClient)






