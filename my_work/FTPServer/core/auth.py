import os
from conf.settings import *

def login(user,password):

    with open(user_info) as f:
        for line in f:
            usrname,passwd= line.strip().split('|')
            if usrname == user and passwd == password:
                os.chdir(os.path.join(base_path,'home',user))
                return 1
        else:
            return 0