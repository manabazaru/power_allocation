import numpy as np

class BaseStation():
    def __init__(self, height, com_radius, bs_xy, usr_xy_arr):
        self.hight = height
        self.com_r = com_radius
        self.xy = bs_xy
        self.usr_xy_arr = usr_xy_arr

