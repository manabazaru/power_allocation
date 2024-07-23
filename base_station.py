import numpy as np
import utils

def get_closest_angle_index(ang_list, ang):
    ans_idx = -1
    ang_min = 360
    for idx in range(len(ang_list)):
        abs_ang = abs(ang-ang_list[idx])
        if abs_ang > 180:
            abs_ang = 360 - abs_ang
        if ang_min > abs_ang:
            ang_min = abs_ang
            ans_idx = idx
    return ans_idx

class BaseStations():
    def __init__(self, bs_size, height_arr, com_radius_arr, bs_xy_arr, max_gain_arr,
                 azimuth_3db_arr, elevation_3db_arr, elevation_tilt_arr,
                 side_attenuation_arr, max_attenuation_arr, sec_size, **usr_setting_type):
        self.bs_list = []
        self.usr_n = 0
        self.sec_size = sec_size
        self.bs_n = bs_size
        usr_per_sec_flg = True
        usr_xy_arr_flg = True
        try:
            usrs_per_sector_arr = usr_setting_type['users_per_sector_arr']
        except KeyError:
            usr_per_sec_flg = False
        try:
            usr_xy_arrs = usr_setting_type['user_xy_arrs']
        except KeyError:
            usr_xy_arr_flg = False
        if not usr_per_sec_flg^usr_xy_arr_flg:
            raise ValueError('[ERROR] Invalid values are input on BaseStation object. Check usrsPerSector_usrxyArr_kwargs.')
        if usr_per_sec_flg:                 
            for i in range(bs_size):
                bs = BaseStation(height_arr[i],com_radius_arr[i], bs_xy_arr[i],
                                max_gain_arr[i], azimuth_3db_arr[i], 
                                elevation_3db_arr[i], elevation_tilt_arr[i],
                                side_attenuation_arr[i], max_attenuation_arr[i], 
                                sec_size, users_per_sector=usrs_per_sector_arr[i])
                self.bs_list.append(bs)
                self.usr_n = int(sum(usrs_per_sector_arr)*3)
        else:
            for i in range(bs_size):
                bs = BaseStation(height_arr[i],com_radius_arr[i], bs_xy_arr[i],
                                max_gain_arr[i], azimuth_3db_arr[i], 
                                elevation_3db_arr[i], elevation_tilt_arr[i],
                                side_attenuation_arr[i], max_attenuation_arr[i], 
                                sec_size, user_xy_arr=usr_xy_arrs[i])
                self.bs_list.append(bs)
                self.usr_n += len(usr_xy_arrs[i])

    def get_users_xy_arr(self):
        usr_xy_arr = np.zeros([self.usr_n, 2], dtype=float)
        head = 0
        for bs in self.bs_list:
            bs_usr_xy_arr = bs.get_users_xy_arr()
            tail = head + len(bs_usr_xy_arr)
            usr_xy_arr[head:tail] = bs_usr_xy_arr
            head = tail
        return usr_xy_arr
    
    def get_users_xy_arr_with_bs_sector_idx_arr(self):
        usr_xy_arr = np.zeros([self.usr_n, 2], dtype=float)
        usr_bs_sector_idx_arr = np.zeros([self.usr_n, 2], dtype=int)-1
        head = 0
        for idx, bs in enumerate(self.bs_list):
            bs_usr_xy_arr, usr_sector_idx_arr = bs.get_users_xy_arr_with_sector_idx()
            tail = head + len(bs_usr_xy_arr)
            usr_xy_arr[head:tail] = bs_usr_xy_arr
            usr_bs_sector_idx_arr[head:tail, 0] = idx
            usr_bs_sector_idx_arr[head:tail, 1] = usr_sector_idx_arr
            head = tail
        if -1 in usr_bs_sector_idx_arr:
            raise ValueError("Something wrong!!")
        return usr_xy_arr, usr_bs_sector_idx_arr
    
    def calc_user_bs_sector_angr(self, usr_xy_arr, usr_height):
        usr_n = len(usr_xy_arr)
        bs_n = len(self.bs_list)
        usr_bs_sector_angr = np.zeros([usr_n, bs_n, self.sec_size, 3],dtype=float)
        for bs_idx in range(bs_n):
            usr_bs_sector_angr[:,bs_idx] = self.bs_list[bs_idx].calc_user_bs_angr(usr_xy_arr, usr_height)
        return usr_bs_sector_angr
        
            

class BaseStation():
    def __init__(self, height, com_radius, bs_xy, max_gain, azimuth_3db, 
                 elevation_3db, elevation_tilt, side_attenuation, max_attenuation,
                 sector_size, **usrsPerSector_usrxyArr_kwargs):
        self.height = height
        self.com_r = com_radius
        self.xy = bs_xy
        self.max_gain = max_gain
        self.azi_3db = azimuth_3db
        self.elev_3db = elevation_3db
        self.elev_tilt = elevation_tilt
        self.side_attenuation = side_attenuation
        self.max_attenuation = max_attenuation
        self.sec_size = sector_size
        self.usrs_per_sector = -1
        self.usr_xy_arr = -1
        self.sector_list = []
        self.usr_assign_list = [[] for i in range(self.sec_size)]
        self.set_users(usrsPerSector_usrxyArr_kwargs)
    
    # sector は -180°方向にアンテナが向いている
    def set_sectors(self):
        dir_unit = 360 / self.sec_size
        for sec_idx in range(self.sec_size):
            dir_deg = -180+dir_unit*sec_idx
            sector = Sector(dir_deg, dir_unit)
            self.sector_list.append(sector)

    def set_users(self, kwargs):
        # self.usrs_per_sector, self.usr_xy_arrのどちらかをセット
        # どちらかが入っている想定, どちらも入っている状況はエラーを吐く
        usrs_per_sec_flg = True
        usr_xy_arr_flg = True
        try:
            self.usrs_per_sector = kwargs['users_per_sector']
        except KeyError:
            usrs_per_sec_flg = False
        try:
            self.usr_xy_arr = kwargs['user_xy_arr']
        except KeyError:
            usr_xy_arr_flg = False
        if not usrs_per_sec_flg^usr_xy_arr_flg:
            raise ValueError('[ERROR] Invalid values are input on BaseStation object. Check usrsPerSector_usrxyArr_kwargs.')
        # sector設定
        self.set_sectors()
        if usrs_per_sec_flg:
            usr_n = int(self.usrs_per_sector * self.sec_size)
            self.usr_xy_arr = np.zeros([usr_n, 2], dtype=float)
            for sector_idx in range(self.sec_size):
                self.sector_list[sector_idx].set_rand_users_location(self.xy, self.usrs_per_sector, self.com_r)
                xy_arr = self.sector_list[sector_idx].get_user_xy_arr()
                head = sector_idx*self.usrs_per_sector
                tail = head + self.usrs_per_sector
                self.usr_xy_arr[head:tail] = xy_arr
                self.usr_assign_list[sector_idx] = [i for i in range(head, tail)]
        else:
            sec_dir_list = [self.sector_list[i].azi_dir for i in range(self.sec_size)]
            usr_assign_list = [[] for i in range(self.sec_size)]
            for usr in range(len(self.usr_xy_arr)):
                usr_xy = self.usr_xy_arr[usr]
                ang_deg = np.arctan2(usr_xy[1], usr_xy[0]) / np.pi*180
                idx = get_closest_angle_index(sec_dir_list, ang_deg)
                usr_assign_list[idx].append(usr)
            for sec_idx in range(self.sec_size):
                usr_arr = self.usr_xy_arr[usr_assign_list[sec_idx]]
                self.sector_list[sec_idx].set_users_xy_arr(usr_arr, self.xy, self.com_r)
            self.usr_assign_list = usr_assign_list
        
    def get_users_xy_arr(self):
        return self.usr_xy_arr
    
    def get_users_xy_arr_with_sector_idx(self):
        usrs_sector_idx_arr = np.zeros(len(self.usr_xy_arr), dtype=int)-1
        for sector_idx in range(self.sec_size):
            assined_usr_list = self.usr_assign_list[sector_idx]
            for usr_idx in assined_usr_list:
                usrs_sector_idx_arr[usr_idx] = sector_idx
        if -1 in usrs_sector_idx_arr:
            raise ValueError("Something wrong!!")
        return self.usr_xy_arr, usrs_sector_idx_arr
    
    def calc_user_bs_angr(self, usr_xy_arr, usr_height):
        usr_n = len(usr_xy_arr)
        usr_bs_sector_angr = np.zeros([usr_n, self.sec_size, 3], dtype=float)
        new_usr_xy_arr = np.zeros(usr_xy_arr.shape, dtype=float)
        new_usr_xy_arr[:,0] = usr_xy_arr[:,0] - self.xy[0]
        new_usr_xy_arr[:,1] = usr_xy_arr[:,1] - self.xy[1]
        for sec_idx in range(self.sec_size):
            ang_rad = self.sector_list[sec_idx].azi_dir / 180 * np.pi
            xyz_arr = np.zeros([usr_n, 3], dtype=float)
            xyz_arr[:,0] = new_usr_xy_arr[:,0]*np.cos(-ang_rad) - new_usr_xy_arr[:,1]*np.sin(-ang_rad)
            xyz_arr[:,1] = new_usr_xy_arr[:,0]*np.sin(-ang_rad) + new_usr_xy_arr[:,1]*np.cos(-ang_rad)
            xyz_arr[:,2] = -self.height - usr_height
            usr_bs_sector_angr[:,sec_idx] = utils.xyz2angr(xyz_arr)
        return usr_bs_sector_angr
        

class Sector():
    def __init__(self, azimuth_direction_deg, azimuth_range):
        self.usrs_per_sec = -1
        self.usr_xy_arr = -1
        self.azi_dir = azimuth_direction_deg
        self.azi_range = azimuth_range
    
    def set_rand_users_location(self, bs_xy, usrs_per_sec, com_r):
        self.usrs_per_sec = usrs_per_sec
        com_r_arr = np.sqrt(np.random.random_sample(usrs_per_sec)) * com_r
        az_rad = np.pi/180 * self.azi_range * \
                (np.random.random_sample(usrs_per_sec)-0.5*np.ones(usrs_per_sec))
        az_from_ant_arr = az_rad + self.azi_dir*(np.pi/180)
        bs_x = com_r_arr * np.cos(az_from_ant_arr)
        bs_y = com_r_arr * np.sin(az_from_ant_arr)
        x = bs_x + bs_xy[0]
        y = bs_y + bs_xy[1]
        self.usr_xy_arr = np.zeros([self.usrs_per_sec, 2], dtype=float)
        self.usr_xy_arr[:,0] = x
        self.usr_xy_arr[:,1] = y
        
    def set_users_xy_arr(self, usr_xy_arr, bs_xy, com_r):
        usr_xy_arr_from_bs = usr_xy_arr
        usr_xy_arr_from_bs[:,0] -= bs_xy[0]
        usr_xy_arr_from_bs[:,1] -= bs_xy[1]
        usr_r_arr_from_bs = np.sqrt(usr_xy_arr_from_bs[:,0]**2 + usr_xy_arr_from_bs[:,1]**2)
        usr_az_arr = np.arctan2(usr_xy_arr_from_bs[:,1], usr_xy_arr_from_bs[:,0])
        azi_dir_rad = self.azi_dir * np.pi / 180
        usr_az_from_bs_arr = usr_az_arr - azi_dir_rad
        usr_n = len(usr_r_arr_from_bs)
        for usr in range(usr_n):
            if usr_r_arr_from_bs[usr] > com_r:
                raise ValueError("[ERROR] Invalid user location value is input in the sector: problem on radius.")
            abs_az = abs(usr_az_from_bs_arr[usr])
            if abs_az > np.pi:
                abs_az = 2*np.pi - abs_az
            if abs_az > self.azi_range/2:
                raise ValueError("[ERROR] Invalid user location value is input in the sector: problem on angle.")
        self.usr_xy_arr = np.zeros([usr_n, 2], dtype=float)
        self.usr_xy_arr[:,0] = usr_xy_arr[:,0]
        self.usr_xy_arr[:,1] = usr_xy_arr[:,1]
        self.usrs_per_sec = usr_n

    def get_user_xy_arr(self):
        return self.usr_xy_arr