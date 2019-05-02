import struct
import json
import subprocess
import os
import hashlib
import socketserver
from core.auth import login
from conf.settings import *

class FTPServer(socketserver.BaseRequestHandler):
    count = 0
    def handle(self):
        self.hook = 0
        self.name = ''
        self.count += 1
        self.run()

    def run(self):

        print("server open %s connect ...."%self.count)
        while True:
            length_pack = self.request.recv(4)
            length = struct.unpack("i", length_pack)[0]
            info_bites = self.request.recv(length)
            info = json.loads(info_bites)
            print("info", info)
            cmd = info.get("action")
            if self.hook:
                if hasattr(self, cmd):
                    getattr(self, cmd)(info)
            else:
                ret = login(info['name'], info['passwd'])
                self.name = info['name']
                self.hook = ret
                self.request.send(str(ret).encode())

    def put(self, info):

        filename = info.get("filename")
        filesize = info.get("filesize")
        with open(filename, "wb") as f:
            recv_data_len = 0
            while recv_data_len < int(filesize):
                line = self.request.recv(1024)
                f.write(line)
                recv_data_len += len(line)
        md5 = hashlib.md5()
        md5.update(filename.encode())
        check_file = md5.hexdigest()
        self.request.send(check_file.encode())
        print("uploaded...")

    def download(self, info):

        filename = info.get("filename")
        filesize_temp = 0
        with open(filename, "rb") as f:
            for line in f:
                filesize_temp += len(line)
        length_file = struct.pack("i", filesize_temp)
        self.request.send(length_file)
        with open(filename, "rb") as f:
            for line in f:
                self.request.send(line)
        print("下载完毕")

    def ls(self, info):
        # 执行远程查看目录文件命令,得到结果返回
        res = subprocess.Popen('dir', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        data = res.stdout.read()
        pack_length = struct.pack("i", len(data))
        final_data = pack_length + data
        self.request.send(final_data)

    def cd(self, info):
        #切换目录功能
        filename = info.get('filename')
        print(filename)
        temp_path = os.getcwd()
        print(temp_path)
        home_path = os.path.join(base_path, 'home', self.name)
        print(home_path)
        son_list = os.listdir(temp_path)
        print('\home' + self.name)
        print(temp_path.endswith('\home\\' + self.name))
        if filename in son_list and os.path.isdir(filename):
            os.chdir(filename)
        elif filename == '..' and temp_path.endswith('\home\\' + self.name) != True:
            print('yes')
            print(temp_path.endswith('\home\\' + self.name) != True)
            os.chdir(filename)


















# server = socketserver.ThreadingTCPServer(("127.0.0.1", 8899), FTPServer)
# server.serve_forever()




# class FTPServer(object):
#     def __init__(self):
#         self.hook = 0
#         self.name = ''
#         self.run()
#         # self.login()
#
#
#     def get_socket(self):
#         # 1  创建一个套接字对象(socket)  AF_INET: ipv4协议   SOCK_STREAM： TCP协议
#         sock = socket.socket()
#         # 2 绑定IP与端口
#         sock.bind(("127.0.0.1", 9999))
#         # 3 创建监听数
#         sock.listen(5)
#         return sock
#
#     def run(self):
#         self.sock=self.get_socket()
#         print("server is waiting....")
#         self.conn,self.addr=self.sock.accept()
#         while 1:
#             length_pack=self.conn.recv(4)
#             length=struct.unpack("i",length_pack)[0]
#             info_bites=self.conn.recv(length)
#             info=json.loads(info_bites)
#             print("info",info)
#             cmd=info.get("action")
#             if self.hook and cmd != 'login':
#                 if hasattr(self,cmd):
#                     getattr(self,cmd)(info)
#             else:
#                 ret = login(info['name'],info['passwd'])
#                 self.name = info['name']
#                 self.hook = ret
#                 self.conn.send(str(ret).encode())
#
#
#     def put(self,info):
#         '''
#         上传文件
#         :return:
#         '''
#         filename = info.get("filename")
#         filesize = info.get("filesize")
#         # 循环接受文件
#         with open(filename,"wb") as f:
#             recv_data_len=0
#             while recv_data_len<int(filesize):
#                 line=self.conn.recv(1024)
#                 f.write(line)
#                 recv_data_len+=len(line)
#         md5 = hashlib.md5()
#         md5.update(filename.encode())
#         check_file= md5.hexdigest()
#         self.conn.send(check_file.encode())
#
#         print("上传完毕")
#
#
#     def download(self,info):
#         '''
#         下载文件
#         :return:
#         '''
#         filename = info.get("filename")
#         # filesize = info.get("filesize")
#         filesize_temp = 0
#         with open(filename, "rb") as f:
#             for line in f:
#                 filesize_temp += len(line)
#         # info = {"action": "put", "filename": filename, "filesize": filesize_temp}
#         # 打包格式： xxx xxx xxx xxx{"action":"put","filename":params,"filesize":filesize}
#         # info_bites = (json.dumps(info)).encode()
#         length_file = struct.pack("i", filesize_temp)
#         # new_info = length_pack + info_bites
#         self.conn.send(length_file)
#         # 下载数据
#         with open(filename, "rb") as f:
#             for line in f:
#                 self.conn.send(line)
#         print("下载完毕")
#
#     def ls(self,info):
#     # 执行远程命令,得到结果返回
#         res=subprocess.Popen('dir',shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
#         data=res.stdout.read()
#         # print("data",data.decode("gbk"))
#         # print("length",len(data))
#
#         #  获取长度的打包结果
#         # import  struct
#         pack_length=struct.pack("i",len(data))
#         final_data=pack_length+data
#         self.conn.send(final_data)
#
#     def cd(self,info):
#         # op_action = info.get('op_action')
#         filename = info.get('filename')
#         temp_path = os.getcwd()
#         print(temp_path)
#         home_path = os.path.join(base_path,'home',self.name)
#         print(home_path)
#         son_list = os.listdir(temp_path)
#         print('\home'+ self.name)
#         print(temp_path.endswith('\home\\'+ self.name) )
#         if filename in son_list and os.path.isdir(filename):
#             os.chdir(filename)
#         elif filename == '..' and temp_path.endswith('\home'+ self.name):
#             print('yes')
#             print(temp_path.endswith('\home'+ self.name) != True)
#             os.chdir(filename)


