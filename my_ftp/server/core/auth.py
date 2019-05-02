import os
import hashlib
from conf.settings import userinfo,base_path

class Auth:
    @staticmethod
    def md5(usr,pwd):
        md5_obj = hashlib.md5(usr.encode())
        md5_obj.update(pwd.encode())
        return md5_obj.hexdigest()

    @classmethod
    def login(cls,opt_dic):
        with open(userinfo,encoding='utf-8') as f:
            for line in f:
                'username|MD5(password)'
                username,password = line.strip().split('|')
                if username == opt_dic['user'] and password == cls.md5(opt_dic['user'],opt_dic['passwd']):
                    home_path = os.path.join(base_path, 'home', (opt_dic['user']))
                    return {'result':True,'info':'登陆成功','home_path':home_path}
        return {'result':False,'info':'登陆失败'}

    @classmethod
    def register(cls,opt_dic):
        with open(userinfo,encoding='utf-8') as f:
            for line in f:
                'username|MD5(password)'
                username,_ = line.split('|')
                if username == opt_dic['user']:
                    return {'result':False,'info':'用户名已存在'}
        with open(userinfo,'a',encoding='utf-8') as f:
            f.write('%s|%s\n'%(opt_dic['user'],cls.md5(opt_dic['user'],opt_dic['passwd'])))
        home_path = os.path.join(base_path,'home',(opt_dic['user']))
        os.mkdir(home_path)
        return {'result':True,'info':'注册成功',
                'home_path':home_path   # 之所以返回这个家目录是为了后续处理目录相关的功能的时候要用
                }

    @classmethod
    def exit(cls):
        return {'result':'exit'}
