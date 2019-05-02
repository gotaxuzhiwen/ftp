import socketserver
import json
import struct
import os
import hashlib
from core.auth import Auth

class FTPServer(socketserver.BaseRequestHandler):
    def handle(self):
        opt_dic = self.my_recv()
        # 先进行用户认证
        while True:
            if hasattr(Auth,opt_dic['operate']):  # 客户的请求应该是用户认证,进行Auth类的反射
                ret = getattr(Auth, opt_dic['operate'])(opt_dic)  # 用户的行为是注册,就反射getattr(Auth,'register')
                if ret['result'] == True:  # 登陆成功/注册成功
                    self.name = opt_dic['user']
                    self.homepath = ret['home_path']    # 我的用户最高只能回到自己的家目录
                    self.currentpath = ret['home_path'] # 我的用户当前所在的目录
                    self.prot_send(ret,False)
                    while True:
                        # 实现具体的用户操作
                        opt_dic = self.my_recv()
                        if opt_dic['operate'] == 'exit':return
                        elif hasattr(self,opt_dic['operate']):
                            getattr(self,opt_dic['operate'])(opt_dic)
                elif ret['result'] == 'exit': return
                else:
                    self.prot_send(ret,False)

    def my_recv(self):
        info = self.request.recv(1024)  # 接收客户端的请求
        opt_str = info.decode()
        opt_dic = json.loads(opt_str)  # 将客户端的请求变成字典
        return opt_dic

    def prot_send(self,send_info,use_pro=True):
        # 自定义协议 避免send的文件信息和文件的内容黏在一起
        file_str = json.dumps(send_info)
        send_info = file_str.encode()
        if use_pro:
            file_len = len(send_info)
            send_len = struct.pack('i', file_len)
            self.request.send(send_len)
        self.request.send(send_info)

    def download(self,opt_dic):
        filename = opt_dic['filename']
        file_abs = os.path.join(self.currentpath,filename)
        if os.path.exists(file_abs):
            filesize = os.path.getsize(file_abs)
            file_info = {'filename':filename,'filesize':filesize}
            self.prot_send(file_info)
            # 发送文件
            md5_obj = hashlib.md5()
            with open(file_abs,'rb') as f:
                while filesize:
                    content = f.read(20480)
                    md5_obj.update(content)
                    self.request.send(content)
                    filesize -= len(content)
            dic = {'filename':filename,'md5':md5_obj.hexdigest()}
            self.prot_send(dic)
    def upload(self,opt_dic):
        filename = opt_dic['filename']
        file_abs = os.path.join(self.currentpath, filename)
        total = opt_dic['filesize']
        md5_obj = hashlib.md5()
        with open(file_abs , 'wb') as f:
            while total:
                if total < 2048:
                    content = self.request.recv(total)
                else:
                    content = self.request.recv(2048)  # 接收文件
                md5_obj.update(content)
                f.write(content)
                total -= len(content)
                # self.processBar(total - opt_dic['filesize'], total)
        md5code = md5_obj.hexdigest()
        dic = {'filename': filename, 'md5': md5code}
        self.prot_send(dic)


    def list_dir(self):
        ret = os.listdir(self.currentpath)
        dic = {'dir': [], 'file': []}
        for name in ret:
            path = os.path.join(self.currentpath, name)
            if os.path.isfile(path):
                dic['file'].append(name)
            else:
                dic['dir'].append(name)
        return dic
    def ls(self,opt_dic):
        dic = self.list_dir()
        self.prot_send(dic)

    def mkdir(self,opt_dic):
        if opt_dic['dirname'] in os.listdir(self.currentpath):
            dic = {'flag': False, 'info': '您要创建的文件夹已存在'}
        else:
            path = os.path.join(self.currentpath,opt_dic['dirname'])
            os.mkdir(path)
            dic = {'flag':True,'info':'创建成功'}
        self.prot_send(dic)

    def cd(self,opt_dic):
        path = os.path.join(self.currentpath,opt_dic['dir'])
        if os.path.isdir(path):
            self.currentpath = path
            self.prot_send({'flag':True,'info':self.list_dir()})
        else:
            self.prot_send({'flag': False, 'info': '您要切换的目录不存在'})
