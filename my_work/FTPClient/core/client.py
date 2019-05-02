import socket
import json
import struct
import hashlib
from core import pg_info

class FTPClient(object):

    def __init__(self):
        self.ip="127.0.0.1"
        self.server_port=9999
        self.hook = False
        self.run()

    def get_socket(self):
        sock = socket.socket()
        return sock

    def run(self):
        self.sock = self.get_socket()
        self.sock.connect((self.ip,self.server_port))
        self.login()
        print('''
            上传文件    put file_name
            下载文件    get file_name
            切换目录    cd  directory_name 
            查看文件目录 ls+空格  
        ''')
        while 1:
           choose = input("请输入命令>>>")
           action, params = choose.split(" ")
           action_dict = ('put','download','cd','ls')
           if action not in action_dict:
               continue
           if hasattr(self, action):
               if self.hook:
                    getattr(self, action)(params)
               else:
                   self.login()
           else:
               pass


    def login(self):
        print("欢迎来到FTP_Sever！")
        flag = True
        while flag:
            user = input("用户名：").strip()
            password = input("密码：").strip()
            if user == '' or password == '':
                print("用户名或密码不能为空")
                continue
            else:
                md5 = hashlib.md5()
                md5.update(password.encode())
                password = md5.hexdigest()
                info = {"action":"login","name": user, "passwd": password}
                info_bites = (json.dumps(info)).encode()
                length_pack = struct.pack("i", len(info_bites))
                new_info = length_pack + info_bites
                self.sock.send(new_info)
                login_flag = int(self.sock.recv(1024).decode())
                if login_flag:
                    self.hook = True
                    break
                else:
                    print('failed')
                    continue

    def put(self,filename):
        print("欢迎上传文件！")
        # 上传的基本信息
        filesize=0
        with open(filename, "rb") as f:
            for line in f:
                filesize+=len(line)
        info={"action":"put","filename":filename,"filesize":filesize}
        #打包格式： xxx xxx xxx xxx{"action":"put","filename":params,"filesize":filesize}
        info_bites=(json.dumps(info)).encode()
        length_pack=struct.pack("i",len(info_bites))
        new_info=length_pack+info_bites
        self.sock.send(new_info)
        # 上传数据
        send_data_len = 0
        md5 = hashlib.md5()
        md5.update(filename.encode())
        check_file = md5.hexdigest()
        with open(filename,"rb") as f:
            for line in f:
                self.sock.send(line)
                md5.update(line)
                send_data_len += len(line)
                percent = send_data_len / filesize
                pg_info.progress(percent, width=70)
        server_check = self.sock.recv(1024).decode()
        # print(server_check,check_file)
        if server_check == check_file:
            print("上传完毕")

    def download(self,filename):
        '''
        下载文件
        :return:
        '''
        print("欢迎下载文件！")

        # 上传的基本信息
        filesize=0
        info={"action":"download","filename":filename,"filesize":filesize}
        info_bites=(json.dumps(info)).encode()
        length_pack=struct.pack("i",len(info_bites))
        new_info=length_pack+info_bites
        self.sock.send(new_info)
        # 下载数据
        length_pack02 = self.sock.recv(4)
        data_len = struct.unpack("i",length_pack02)[0]
        with open(filename, "wb") as f:
            recv_data_len = 0
            while recv_data_len < data_len:
                line = self.sock.recv(1024)
                f.write(line)
                recv_data_len += len(line)
                percent = recv_data_len / data_len
                pg_info.progress(percent, width=70)
        print("下载完毕")



    def ls(self,filename):

        print("欢迎查看文件目录！")
        info={"action":"ls","filename":filename,"op_action":'dir'}
        info_bites=(json.dumps(info)).encode()
        length_pack=struct.pack("i",len(info_bites))
        new_info=length_pack+info_bites
        self.sock.send(new_info)

        length_pack02 = self.sock.recv(4)
        data_len = struct.unpack("i",length_pack02)[0]
        recv_data_len = 0
        recv_data = b""
        while recv_data_len < data_len:
            temp_data = self.sock.recv(1024)
            recv_data += temp_data
            recv_data_len += len(temp_data)
        print("命令响应:", recv_data.decode("gbk"))



    def cd(self,filename):
        print("欢迎切换文件目录！")
        info={"action":"cd","filename":filename,"op_action":'cd'}
        info_bites=(json.dumps(info)).encode()
        length_pack=struct.pack("i",len(info_bites))
        new_info=length_pack+info_bites
        self.sock.send(new_info)



