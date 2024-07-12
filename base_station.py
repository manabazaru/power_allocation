import numpy as np
import utils

class BaseStation():
    def __init__(self, height, com_radius, bs_xy):
        self.height = height
        self.com_r = com_radius
        self.xy = bs_xy
        self.max_gain = 14
        self.azi_3db = 70
        self.elev_3db = 10
        self.elev_tilt = 1.15
        self.side_attenuation = 25
        self.max_attenuation = 20
        

    def get_user_antenna_angle_r_arr(self, usr_xy_arr):
        usr_n = len(usr_xy_arr)
        usr_ant_xyz_arr = np.zeros([usr_n, 3])
        usr_ant_xyz_arr[:,2] = -self.height
        usr_ant_xyz_arr[:,:2] = usr_xy_arr
        usr_ant_xyz_arr[:, 0] -= self.xy[0]
        usr_ant_xyz_arr[:, 1] -= self.xy[1]
        usr_ant_angr = utils.xyz2angr(usr_ant_xyz_arr)
