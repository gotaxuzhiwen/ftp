import os
import sys

base_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(base_path)

from core.client import FTPClient

if __name__ == '__main__':
    FTPClient()