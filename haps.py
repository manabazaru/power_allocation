import numpy as np
import tqdm
import utils
from parameters import Parameter as param
from us_equipment import AUSEquipment
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
class HAPS():
    def __init__(self):
        self.wv_len = param.c/param.carrier_freq
        self.altitude = param.z
    
    def rot_usr_xyz(self, xyz, yaw, pitch):
        xyz2 = utils.rotate_with_yaw(xyz, yaw)
        xyz3 = utils.rotate_with_pitch(xyz2, pitch)
        return xyz3

class PlanarHAPS(HAPS):
    def __init__(self):
        super().__init__()
        self.sd_n = param.planar_antenna_size_of_side
        self.ant_n = self.sd_n ** 2
        self.xyz_arr = np.zeros([self.sd_n, self.sd_n, 3])
        # parameter
        self.ant_dis = self.wv_len * param.distance_ratio_between_planar_antenna
        self.set_antenna_xyz()
    
    def set_antenna_xyz(self):
        coordinate_val = -(self.sd_n-1)/2 * self.ant_dis
        for xy in range(self.sd_n):
            self.xyz_arr[xy,:,0] = coordinate_val
            self.xyz_arr[:,xy,1] = coordinate_val
            coordinate_val += self.ant_dis
        self.xyz_arr[:,:,2] = 0
    
    def get_user_antenna_angle_r_arr(self, eqpt: AUSEquipment):
        print("[INFO HAPS] Calculation of user angle from each antenna "+
              "element has been started.")
        ang_arr = eqpt.get_ang_all()
        usr_n = eqpt.get_usr_n()
        usr_ant_angr = np.zeros([usr_n, self.ant_n, 3])
        usr_angr_arr = utils.ang2angr_with_z(ang_arr, -self.altitude)
        usr_xyz_arr = utils.angr2xyz(usr_angr_arr)
        flt_ant_xyz_arr = self.xyz_arr.reshape(self.sd_n**2,3)
        for usr in tqdm.tqdm(range(usr_n)):
            usr_xyz = usr_xyz_arr[usr]
            for ant in range(self.ant_n):
                xyz = flt_ant_xyz_arr[ant]
                shift_usr_xyz = usr_xyz - xyz
                rot_xyz = self.rot_usr_xyz(shift_usr_xyz, 0, -90)
                rot_angr = utils.xyz2angr(rot_xyz)
                usr_ant_angr[usr, ant] = rot_angr
        return usr_ant_angr
    
    def get_user_antenna_angle_r_arr_from_user_xy_arr(self, xy_arr, usr_height=0.001):
        print("[INFO HAPS] Calculation of user angle from each antenna "+
              "element has been started.")
        ang_arr = utils.xy2ang(xy_arr, -self.altitude+usr_height)
        usr_n = len(ang_arr)
        usr_ant_angr = np.zeros([usr_n, self.ant_n, 3])
        usr_angr_arr = utils.ang2angr_with_z(ang_arr, -self.altitude+usr_height)
        usr_xyz_arr = utils.angr2xyz(usr_angr_arr)
        flt_ant_xyz_arr = self.xyz_arr.reshape(self.sd_n**2,3)
        for usr in tqdm.tqdm(range(usr_n)):
            usr_xyz = usr_xyz_arr[usr]
            for ant in range(self.ant_n):
                xyz = flt_ant_xyz_arr[ant]
                shift_usr_xyz = usr_xyz - xyz
                rot_xyz = self.rot_usr_xyz(shift_usr_xyz, 0, -90)
                rot_angr = utils.xyz2angr(rot_xyz)
                usr_ant_angr[usr, ant] = rot_angr
        return usr_ant_angr
    
    def get_user_ang_arr_from_user_xy_arr(self, xy_arr, usr_height=0.001):
        ang_arr = utils.xy2ang(xy_arr, -self.altitude+usr_height)
        return ang_arr

class VariableAntennaPlanarHAPS(PlanarHAPS):
    def __init__(self, side_antenna_n):
        super().__init__()
        self.sd_n = side_antenna_n
        self.ant_n = self.sd_n ** 2
        self.xyz_arr = np.zeros([self.sd_n, self.sd_n, 3])
        # parameter
        self.set_antenna_xyz()
        

class CyrindricalHAPS(HAPS):
    def __init__(self):
        super().__init__()
        # number of each antenna element
        self.sd_h_n = param.side_horizonal_antenna
        self.sd_v_n = param.side_vertical_antenna
        self.sd_n = self.sd_h_n * self.sd_v_n
        self.btm_n = param.bottom_antenna
        self.ant_n = self.sd_n + self.btm_n
        # side antenna element
        self.sd_xyz_arr = np.zeros([self.sd_v_n, self.sd_h_n, 3])
        self.sd_vec_dir = np.zeros([self.sd_v_n, self.sd_h_n])
        # bottom antenna element
        self.btm_xyz_arr = np.zeros([self.btm_n, 3])
        self.btm_rot_yaw = np.zeros([self.btm_n])
        # length
        self.h_r = 0.6 * self.wv_len * (self.sd_h_n / (2*np.pi))
        self.b_r = 0.5 * self.h_r
        self.dv = 0.6 * self.wv_len 
        self.ant_height = param.antenna_height
        self.set_all()

    def set_side_antenna_vector_direction(self):
        vec_ang_dif = 360/self.sd_h_n
        dir_arr = np.arange(self.sd_h_n)*vec_ang_dif - 180
        for v in range(self.sd_v_n):
            self.sd_vec_dir[v,:] = dir_arr[:]

    def set_bottom_rot_yaw(self):
        rot_ang_dif = 360/self.btm_n
        rot_ang_arr = np.arange(self.btm_n)*rot_ang_dif - 180
        self.btm_rot_yaw = rot_ang_arr

    def set_antenna_xyz_arr(self):
        z = (self.sd_v_n-1) * self.dv / 2
        # set side antenna
        for v in range(self.sd_v_n):
            dir_rad = np.deg2rad(self.sd_vec_dir[v])
            x = self.h_r * np.cos(dir_rad)
            y = self.h_r * np.sin(dir_rad)
            self.sd_xyz_arr[v,:,0] = x
            self.sd_xyz_arr[v,:,1] = y
            self.sd_xyz_arr[v,:,2] = z
            z -= self.dv
        # set bottom antenna
        dir_rad = np.deg2rad(self.btm_rot_yaw)
        x = self.b_r * np.cos(dir_rad)
        y = self.b_r * np.sin(dir_rad)
        self.btm_xyz_arr[:,0] = x
        self.btm_xyz_arr[:,1] = y
        self.btm_xyz_arr[:,2] = -1*self.ant_height/2
    
    def set_all(self):
        print("[INFO HAPS] Initialization of HAPS has been started.")
        self.set_side_antenna_vector_direction()
        self.set_bottom_rot_yaw()
        self.set_antenna_xyz_arr()
 
    def get_user_antenna_angle_r_arr(self, eqpt: AUSEquipment):
        print("[INFO HAPS] Calculation of user angle from each antenna "+
              "element has been started.")
        ang_arr = eqpt.get_ang_all()
        usr_n = eqpt.get_usr_n()
        usr_angr_arr = utils.ang2angr_with_z(ang_arr, -self.altitude)
        usr_xyz_arr = utils.angr2xyz(usr_angr_arr)
        usr_sd_angr = np.zeros([usr_n, self.sd_n, 3])
        usr_btm_angr = np.zeros([usr_n, self.btm_n, 3])
        usr_ant_angr = np.zeros([usr_n, self.ant_n, 3])
        flt_sd_xyz_arr = self.sd_xyz_arr.reshape(self.sd_n,3)
        flt_sd_vec_dir = self.sd_vec_dir.reshape(self.sd_n)
        for usr in tqdm.tqdm(range(usr_n)):
            usr_xyz = usr_xyz_arr[usr]
            for sd_ant in range(self.sd_n):
                sd_xyz = flt_sd_xyz_arr[sd_ant]
                shift_usr_xyz = usr_xyz - sd_xyz
                shift_usr_angr = utils.xyz2angr(shift_usr_xyz)
                shift_usr_angr[0] = utils.calc_az_dif(shift_usr_angr[0],
                                                      flt_sd_vec_dir[sd_ant])
                usr_sd_angr[usr, sd_ant] = shift_usr_angr
            for btm_ant in range(self.btm_n):
                btm_xyz = self.btm_xyz_arr[btm_ant]
                shift_usr_xyz = usr_xyz - btm_xyz
                yaw = -1*self.btm_rot_yaw[btm_ant]
                rot_xyz = self.rot_usr_xyz(shift_usr_xyz, yaw, -90)
                rot_angr = utils.xyz2angr(rot_xyz)
                usr_btm_angr[usr, btm_ant] = rot_angr
        usr_ant_angr = np.concatenate([usr_sd_angr, usr_btm_angr],1)
        return usr_ant_angr

    def get_user_antenna_angle_r_arr_from_user_xy_arr(self, xy_arr, usr_height=0.001):
        print("[INFO HAPS] Calculation of user angle from each antenna "+
              "element has been started.")
        usr_n = len(xy_arr)
        usr_xyz_arr = utils.xy2xyz(xy_arr, -self.altitude+usr_height)
        usr_sd_angr = np.zeros([usr_n, self.sd_n, 3])
        usr_btm_angr = np.zeros([usr_n, self.btm_n, 3])
        usr_ant_angr = np.zeros([usr_n, self.ant_n, 3])
        flt_sd_xyz_arr = self.sd_xyz_arr.reshape(self.sd_n,3)
        flt_sd_vec_dir = self.sd_vec_dir.reshape(self.sd_n)
        for usr in tqdm.tqdm(range(usr_n)):
            usr_xyz = usr_xyz_arr[usr]
            for sd_ant in range(self.sd_n):
                sd_xyz = flt_sd_xyz_arr[sd_ant]
                shift_usr_xyz = usr_xyz - sd_xyz
                shift_usr_angr = utils.xyz2angr(shift_usr_xyz)
                shift_usr_angr[0] = utils.calc_az_dif(shift_usr_angr[0],
                                                      flt_sd_vec_dir[sd_ant])
                usr_sd_angr[usr, sd_ant] = shift_usr_angr
            for btm_ant in range(self.btm_n):
                btm_xyz = self.btm_xyz_arr[btm_ant]
                shift_usr_xyz = usr_xyz - btm_xyz
                yaw = -1*self.btm_rot_yaw[btm_ant]
                rot_xyz = self.rot_usr_xyz(shift_usr_xyz, yaw, -90)
                rot_angr = utils.xyz2angr(rot_xyz)
                usr_btm_angr[usr, btm_ant] = rot_angr
        usr_ant_angr = np.concatenate([usr_sd_angr, usr_btm_angr],1)
        return usr_ant_angr
    
    def get_user_ang_arr_from_user_xy_arr(self, xy_arr, usr_height=0.001):
        ang_arr = utils.xy2ang(xy_arr, -self.altitude+usr_height)
        return ang_arr


class CyrindricalSideHAPS(HAPS):
    def __init__(self):
        super().__init__()
        # number of each antenna element
        self.sd_h_n = param.side_horizonal_antenna
        self.sd_v_n = param.side_vertical_antenna
        self.sd_n = self.sd_h_n * self.sd_v_n
        self.ant_n = self.sd_n
        # side antenna element
        self.sd_xyz_arr = np.zeros([self.sd_v_n, self.sd_h_n, 3])
        self.sd_vec_dir = np.zeros([self.sd_v_n, self.sd_h_n])
        # length
        self.h_r = 0.6 * self.wv_len * (self.sd_h_n / (2*np.pi))
        self.dv = 0.6 * self.wv_len
        self.ant_height = param.antenna_height
        self.set_all()

    def set_side_antenna_vector_direction(self):
        vec_ang_dif = 360/self.sd_h_n
        dir_arr = np.arange(self.sd_h_n)*vec_ang_dif - 180
        for v in range(self.sd_v_n):
            self.sd_vec_dir[v,:] = dir_arr[:]

    def set_antenna_xyz_arr(self):
        z = (self.sd_v_n-1) * self.dv / 2
        # set side antenna
        for v in range(self.sd_v_n):
            dir_rad = np.deg2rad(self.sd_vec_dir[v])
            x = self.h_r * np.cos(dir_rad)
            y = self.h_r * np.sin(dir_rad)
            self.sd_xyz_arr[v,:,0] = x
            self.sd_xyz_arr[v,:,1] = y
            self.sd_xyz_arr[v,:,2] = z
            z -= self.dv

    def set_all(self):
        print("[INFO HAPS] Initialization of HAPS has been started.")
        self.set_side_antenna_vector_direction()
        self.set_antenna_xyz_arr()
 
    def get_user_antenna_angle_r_arr(self, eqpt: AUSEquipment):
        print("[INFO HAPS] Calculation of user angle from each antenna "+
              "element has been started.")
        ang_arr = eqpt.get_ang_all()
        usr_n = eqpt.get_usr_n()
        usr_angr_arr = utils.ang2angr_with_z(ang_arr, -self.altitude)
        usr_xyz_arr = utils.angr2xyz(usr_angr_arr)
        usr_sd_angr = np.zeros([usr_n, self.sd_n, 3])
        usr_ant_angr = np.zeros([usr_n, self.ant_n, 3])
        flt_sd_xyz_arr = self.sd_xyz_arr.reshape(self.sd_n,3)
        flt_sd_vec_dir = self.sd_vec_dir.reshape(self.sd_n)
        for usr in tqdm.tqdm(range(usr_n)):
            usr_xyz = usr_xyz_arr[usr]
            for sd_ant in range(self.sd_n):
                sd_xyz = flt_sd_xyz_arr[sd_ant]
                shift_usr_xyz = usr_xyz - sd_xyz
                shift_usr_angr = utils.xyz2angr(shift_usr_xyz)
                shift_usr_angr[0] = utils.calc_az_dif(shift_usr_angr[0],
                                                      flt_sd_vec_dir[sd_ant])
                usr_sd_angr[usr, sd_ant] = shift_usr_angr
        usr_ant_angr = usr_sd_angr
        return usr_ant_angr


class PrevCyrindricalHAPS(HAPS):
    def __init__(self):
        super().__init__()
        # number of each antenna element
        self.sd_h_n = param.side_horizonal_antenna
        self.sd_v_n = param.side_vertical_antenna
        self.sd_n = self.sd_h_n * self.sd_v_n
        self.btm_n = param.bottom_antenna
        self.ant_n = self.sd_n + self.btm_n
        # side antenna element
        self.sd_xyz_arr = np.zeros([self.sd_v_n, self.sd_h_n, 3])
        self.sd_vec_dir = np.zeros([self.sd_v_n, self.sd_h_n])
        # bottom antenna element
        self.btm_xyz_arr = np.zeros([self.btm_n, 3])
        self.btm_rot_yaw = np.zeros([self.btm_n])
        # length
        d_h = d_b = d_v = 0.5 * self.wv_len

        self.h_r = 0.5 * d_h / np.sin(np.pi/self.sd_h_n)
        self.b_r = 0.5 * d_b / np.sin(np.pi/self.btm_n)
        self.dv = d_v
        self.ant_height = param.antenna_height
        self.set_all()

    def set_side_antenna_vector_direction(self):
        vec_ang_dif = 360/self.sd_h_n
        dir_arr = np.arange(self.sd_h_n)*vec_ang_dif - 180
        for v in range(self.sd_v_n):
            self.sd_vec_dir[v,:] = dir_arr[:]

    def set_bottom_rot_yaw(self):
        rot_ang_dif = 360/self.btm_n
        rot_ang_arr = np.arange(self.btm_n)*rot_ang_dif - 180
        self.btm_rot_yaw = rot_ang_arr

    def set_antenna_xyz_arr(self):
        z = (self.sd_v_n-1) * self.dv / 2
        # set side antenna
        for v in range(self.sd_v_n):
            dir_rad = np.deg2rad(self.sd_vec_dir[v])
            x = self.h_r * np.cos(dir_rad)
            y = self.h_r * np.sin(dir_rad)
            self.sd_xyz_arr[v,:,0] = x
            self.sd_xyz_arr[v,:,1] = y
            self.sd_xyz_arr[v,:,2] = z
            z -= self.dv
        # set bottom antenna
        dir_rad = np.deg2rad(self.btm_rot_yaw)
        x = self.b_r * np.cos(dir_rad)
        y = self.b_r * np.sin(dir_rad)
        self.btm_xyz_arr[:,0] = x
        self.btm_xyz_arr[:,1] = y
        self.btm_xyz_arr[:,2] = -1*self.ant_height/2

    def set_all(self):
        print("[INFO HAPS] Initialization of HAPS has been started.")
        self.set_side_antenna_vector_direction()
        self.set_bottom_rot_yaw()
        self.set_antenna_xyz_arr()
 
    def get_user_antenna_angle_r_arr(self, eqpt: AUSEquipment):
        print("[INFO HAPS] Calculation of user angle from each antenna "+
              "element has been started.")
        ang_arr = eqpt.get_ang_all()
        usr_n = eqpt.get_usr_n()
        usr_angr_arr = utils.ang2angr_with_z(ang_arr, -self.altitude)
        usr_xyz_arr = utils.angr2xyz(usr_angr_arr)
        usr_sd_angr = np.zeros([usr_n, self.sd_n, 3])
        usr_btm_angr = np.zeros([usr_n, self.btm_n, 3])
        usr_ant_angr = np.zeros([usr_n, self.ant_n, 3])
        flt_sd_xyz_arr = self.sd_xyz_arr.reshape(self.sd_n,3)
        flt_sd_vec_dir = self.sd_vec_dir.reshape(self.sd_n)
        for usr in tqdm.tqdm(range(usr_n)):
            usr_xyz = usr_xyz_arr[usr]
            for sd_ant in range(self.sd_n):
                sd_xyz = flt_sd_xyz_arr[sd_ant]
                shift_usr_xyz = usr_xyz - sd_xyz
                shift_usr_angr = utils.xyz2angr(shift_usr_xyz)
                shift_usr_angr[0] = utils.calc_az_dif(shift_usr_angr[0],
                                                      flt_sd_vec_dir[sd_ant])
                usr_sd_angr[usr, sd_ant] = shift_usr_angr
            for btm_ant in range(self.btm_n):
                btm_xyz = self.btm_xyz_arr[btm_ant]
                shift_usr_xyz = usr_xyz - btm_xyz
                yaw = -1*self.btm_rot_yaw[btm_ant]
                rot_xyz = self.rot_usr_xyz(shift_usr_xyz, yaw, -90)
                rot_angr = utils.xyz2angr(rot_xyz)
                usr_btm_angr[usr, btm_ant] = rot_angr
        usr_ant_angr = np.concatenate([usr_sd_angr, usr_btm_angr],1)
        return usr_ant_angr

def get_user_antenna_angle_r_arr(shp, eqpt: AUSEquipment):
    if shp == 'p':
        haps = PlanarHAPS()
    elif shp == 'c':
        haps = CyrindricalHAPS()
    elif shp == 'cs':
        haps = CyrindricalSideHAPS()
    elif shp == 'pc':
        haps = PrevCyrindricalHAPS()
    ua_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    return ua_angr

def get_Nt(shp):
    nt = 0
    if shp == 'p':
        nt = param.planar_antenna_size_of_side ** 2
    elif shp == 'c':
        sd_n = param.side_horizonal_antenna * param.side_vertical_antenna
        nt = param.bottom_antenna + sd_n
    elif shp == 'cs':
        nt = param.side_horizonal_antenna * param.side_vertical_antenna
    elif shp == 'pc':
        sd_n = param.side_horizonal_antenna * param.side_vertical_antenna
        nt = param.bottom_antenna + sd_n
    return nt

def test():
    cy_2021 = PrevCyrindricalHAPS()
    cy_2022 = CyrindricalHAPS()
    v, h, size = cy_2021.sd_xyz_arr.shape
    sd_xyz_2021 = cy_2021.sd_xyz_arr.reshape([v*h, size])
    v, h, size = cy_2022.sd_xyz_arr.shape
    sd_xyz_2022 = cy_2022.sd_xyz_arr.reshape([v*h, size])
    xyz_arr_2021 = np.concatenate([sd_xyz_2021, cy_2021.btm_xyz_arr], 0) * 10**5
    xyz_arr_2022 = np.concatenate([sd_xyz_2022, cy_2022.btm_xyz_arr], 0) * 10**5
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    
    ax.set_title("Shapes of two Cylindrical Array Antenna (2021, 2022)")
    ax.set_xlabel("x (cm)",size=15,color="black")
    ax.set_ylabel("y (cm)",size=15,color="black")
    ax.set_zlabel("z (cm)",size=15,color="black")
    
    ax.scatter(xyz_arr_2021[:,0], xyz_arr_2021[:,1], xyz_arr_2021[:,2], s=1, c='red', label='2021')
    ax.scatter(xyz_arr_2022[:,0], xyz_arr_2022[:,1], xyz_arr_2022[:,2], s=1, c='blue', label='2022')
    ax.legend()
    plt.show()
    fig.savefig("C:/Users/manab/Pictures/3D_cylindrical.png")