#VERSION=0
#
#Claset\Base\Configs\Configs.py
#

from . import User

class Configs():
    def __init__(self):
        self.user = User.user()
