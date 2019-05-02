import os
import sys

base_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(base_path)
user_object = os.path.join(base_path,'db','user_object')
user_info = os.path.join(base_path,'db','user_info')