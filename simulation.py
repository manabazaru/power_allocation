import load
import save
import utils
import rand_uni as ru
import grouping
import fig
from haps import CyrindricalHAPS as chaps
from haps import PlanarHAPS as phaps
import haps
from beamforming import BeamForming, ZeroForcing
from eval import SystemEvaluator as eval
from us_equipment import AUSEquipment
from properties import Property as prop
from parameters import Parameter as param
import numpy as np
import rand_uni

class Dataset():
    def __init__(self, typ, nu, r, shp, DSidx):
        # basic parameters
        self.typ = typ
        self.nu = nu
        self.nt = haps.get_Nt(shp)
        self.r = r
        self.z = param.z
        self.shp = shp
        self.dsi = DSidx  # index of dataset

        # tag for loading
        self.xy_tag = ''
        self.ang_tag = ''
        self.ua_tag = ''
        
        # dataset
        self.xy_arr = None
        self.ang_arr = None
        self.eqpt = None
        self.ua_angr_arr = None
        self.setup_tag()
    
    # set tag for loading (execute 1st)
    def setup_tag(self):
        self.xy_tag = f'typ={self.typ}_r={self.r}_DSidx={self.dsi}'
        self.ang_tag = f'typ={self.typ}_r={self.r}_z={self.z}_DSidx={self.dsi}'
        self.ua_tag = f'typ={self.typ}_Nu={self.nu}_Nt={self.nt}_' + \
                      f'r={self.r}_z={self.z}_shp={self.shp}_DSidx={self.dsi}'

    # load or generate xy_arr
    def setup_xy(self):
        try:
            # load
            self.xy_arr = load.load_xy(self.xy_tag)
        except FileNotFoundError:
            # generate
            if self.typ in prop.cities:
                city = self.typ + '_' + {self.r}  # ex. tokyo_20
                self.xy_arr = load.load_mat(city)
            elif 'random' in self.typ:
                nuk = int(self.typ[6:])  # get number of users from typ like 'random2400'
                self.xy_arr = rand_uni.generate_random_uniform_usr_xy(nuk, self.r)
            else:
                raise Exception('[INFO ERROR] There is an error in setup_xy(): '+\
                                'Invalid type to create xy array is entered.')
            save.save_xy_arr(self.xy_arr, self.xy_tag)
    
    # load or generate ang_arr
    def setup_ang(self):
        try:
            # load
            self.ang_arr = load.load_angle(self.ang_tag)
        except FileNotFoundError:
            # generate
            self.setup_xy()
            self.ang_arr = utils.xy2ang(self.xy_arr, -self.z)
            # save
            save.save_angle_arr(self.ang_arr, self.ang_tag)
    
    # generate AUSEquipment
    def setup_eqpt(self):
        if self.ang_arr is None:
            self.setup_ang()
        self.eqpt = AUSEquipment(self.ang_arr, self.nu)
    
    # load or generate user and antenna angle & distance (azimuth, elevation, distance)
    def setup_ua_angr_arr(self):
        try:
            # load
            self.ua_angr_arr = load.load_usr_haps_angle(self.ua_tag)
        except FileNotFoundError:
            # generate
            self.setup_eqpt()
            self.ua_angr_arr = haps.get_user_antenna_angle_r_arr(self.shp, self.eqpt)
            # save
            save.save_user_HAPS_angle(self.ua_angr_arr, self.ua_tag)
    
    def get_xy(self):
        return self.xy_arr
    
    def get_ang(self):
        return self.ang_arr
    
    def get_eqpt(self):
        return self.eqpt
    
    def get_ua_angr_arr(self):
        return self.ua_angr_arr


class Simulation():
    def __init__(self, ds: Dataset, alg, SIMidx, **addl_param):
        # basic parameters
        self.ds: Dataset = ds
        self.typ = ds.typ
        self.nu = ds.nu
        self.nt = ds.nt
        self.r = ds.r
        self.z = ds.z
        self.shp = ds.shp
        self.alg = alg
        self.dsi = ds.dsi
        self.simi = SIMidx  # index of simulation

        # additional parameter
        # M: cluster size of MRUS(ACUS)
        self.addl_param: dict = addl_param

        # tag for loading
        self.grp_tag = ''
        self.grp_mAD_tag = ''
        self.usr_mAD_tag = ''
        self.flop_tag = ''
        self.sig_tag = ''
        self.intf_tag = ''
        self.noise_tag = ''
        self.cap_tag = ''
        self.setup_tag()

        # simulation result
        self.group_table = None
        self.grp_mAD_arr = None
        self.usr_mAD_arr = None
        self.flop_arr = None
        self.sig_arr = None
        self.intf_arr = None
        self.noise_arr = None
        self.cap_arr = None  # capacity list
    
    # set tags for loading (execute 1st)
    def setup_tag(self):
        tag1 = f'typ={self.typ}_Nu={self.nu}_' + \
               f'r={self.r}_z={self.z}_alg={self.alg}_' + \
               f'DSidx={self.dsi}_SIMidx={self.simi}'
        tag2 = f'typ={self.typ}_Nu={self.nu}_' + \
               f'Nt={self.nt}_r={self.r}_z={self.z}_shp={self.shp}_'+\
               f'alg={self.alg}_DSidx={self.dsi}_SIMidx={self.simi}'
        tag3 = f'typ={self.typ}_Nu={self.nu}_' + \
               f'Nt={self.nt}_r={self.r}_z={self.z}_'+\
               f'alg={self.alg}_DSidx={self.dsi}_SIMidx={self.simi}'
        self.grp_tag = self.grp_mAD_tag = self.usr_mAD_tag = tag1
        self.cap_tag = self.sig_tag = self.intf_tag = self.noise_tag = tag2
        self.flop_tag = tag3
    
    # load or generate (self.group_table, self.grp_mAD_arr, self.usr_mAD_arr)
    def execute_grouping(self):
        try:
            # load
            self.group_table = load.load_group_table(self.grp_tag)
            self.grp_mAD_arr = load.load_group_minAD_arr(self.grp_mAD_tag)
            self.usr_mAD_arr = load.load_user_minAD_arr(self.usr_mAD_tag)
            self.flop_arr = load.load_flop(self.flop_arr)
        except FileNotFoundError:
            # generate
            self.ds.setup_eqpt()
            eqpt :AUSEquipment = self.ds.get_eqpt()
            if self.alg == 'RUS':
                grp = grouping.RUS(eqpt)
            elif self.alg == 'AUS':
                grp = grouping.AUS(eqpt)
            elif self.alg in ['MRUS', 'ACUS']:
                # set 'M' (cluster size)
                if 'M' in self.addl_param.keys():
                    m = self.addl_param['M']
                else:
                    m = int(input('[INPUT] Input M (cluster size) for executing' +\
                                  'MRUS(ACUS) algorithm.'))
                grp = grouping.MRangeAUS(eqpt, m)
            else:
                raise Exception("[ERROR] Invalid algorithm is entered.")
            grp.execute()
            self.group_table = grp.get_group_table()
            self.grp_mAD_arr = grp.get_min_ad_arr()
            self.usr_mAD_arr = grp.get_user_mAD_arr()
            self.flop_arr = grp.get_flop_list()

            # save
            save.save_group_table(self.group_table, self.grp_tag)
            save.save_group_minAD_arr(self.grp_mAD_arr, self.grp_mAD_tag)
            save.save_user_minAD_arr(self.usr_mAD_arr, self.usr_mAD_tag)
            save.save_flop_arr(self.flop_arr, self.flop_tag)
            
    
    # load or generate (self.sig_arr, self.intf_arr, self.noise_arr, self.cap_arr)
    def execute_all(self):
        try:
            # load
            self.sig_arr = load.load_sig(self.sig_tag)
            self.intf_arr = load.load_interference(self.intf_tag)
            self.noise_arr = load.load_noise(self.noise_tag)
            self.cap_arr = load.load_eval(self.cap_tag)
        except FileNotFoundError:
            # generate
            self.execute_grouping()
            self.ds.setup_ua_angr_arr()  # calculate ua_angr_arr in Dataset obj
            ua_angr_arr = self.ds.get_ua_angr_arr()
            ev = eval(self.group_table, ua_angr_arr)
            self.sig_arr = ev.get_signal_pwr()
            self.intf_arr = ev.get_interference()
            self.noise_arr = ev.get_noise_pwr()
            self.cap_arr = ev.get_sum_cap_arr()

            # save
            save.save_sig_arr(self.sig_arr, self.sig_tag)
            save.save_interference_arr(self.intf_arr, self.intf_tag)
            save.save_noise_arr(self.noise_arr, self.noise_tag)
            save.save_eval_arr(self.cap_arr, self.cap_tag)
            
        

        

    



def save_city_csv(city):
    xy_arr = load.load_mat(city)
    xyz_arr = utils.xy2xyz(xy_arr, 0-param.z)
    angr_arr = utils.xyz2angr(xyz_arr)
    ang_arr = utils.angr2ang(angr_arr)
    save.save_angle_arr(ang_arr, city)
    save.save_xy_arr(xy_arr, city)

def generate_random_user_angle(user_n, set_n):
    for set_idx in range(1, set_n+1):
        xy_arr = rand_uni.generate_random_uniform_usr_xy(user_n, 20)
        angr_arr = utils.xyz2angr(utils.xy2xyz(xy_arr, -param.z))
        ang_arr = utils.angr2ang(angr_arr)
        save.save_angle_arr(ang_arr, f"random_user={user_n}_r={20}_{set_idx}")

def save_AUS_flops(cnt_per_data, usrs_per_group, user_n_list, set_list, radius):
    for user_n in user_n_list:
        aus_flop_arr = []
        aus_flop_filename = f"random_user={user_n}_alg=AUS_r={radius}_users_per_group={usrs_per_group}"
        for set_idx in set_list:
            filename = f"random_user={user_n}_r={radius}_{set_idx}"
            ang_arr = load.load_angle(filename)
            eqpt = AUSEquipment(ang_arr, usrs_per_group)
            for loop_idx in range(cnt_per_data):
                aus = grouping.AUS(eqpt)
                aus.execute()
                aus_flop_arr.append(aus.get_flop_list())
        save_flop = np.array(aus_flop_arr)
        save.save_flop_arrs(save_flop, aus_flop_filename)

def save_MRUS_flops(cnt_per_data, usrs_per_group, user_n_list, set_list, radius, m_list):
    for m in m_list:
        for user_n in user_n_list:
            mrus_flop_filename = f"random_user={user_n}_alg=MRUS_m={m}_r={radius}_users_per_group={usrs_per_group}"
            mrus_flop_arr = []
            for set_idx in set_list:
                filename = f"random_user={user_n}_r={radius}_{set_idx}"
                ang_arr = load.load_angle(filename)
                eqpt = AUSEquipment(ang_arr, usrs_per_group)
                for loop_idx in range(cnt_per_data):
                    mrus = grouping.MRangeAUS(eqpt, m)
                    mrus.execute()
                    mrus_flop_arr.append(mrus.get_flop_list())
            save_flop = np.array(mrus_flop_arr)
            save.save_flop_arrs(save_flop, mrus_flop_filename)

def save_cities_csv():
    for city in prop.cities:
        save_city_csv(city)

def execute_simulation(m_list, usrs_per_group):
    cities = prop.main_cities
    for city in cities:
        cap_title = 'Capacity_' + city
        sinr_title = 'SINR_' + city
        ang_arr = load.load_angle(city)
        eqpt = AUSEquipment(ang_arr, usrs_per_group)
        haps = phaps()
        usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
        alg_list = []
        alg_obj_list = []
        group_list = []
        sorted_minAD_list = []
        eval_list = []
        sinr_list = []
        cap_list = []
        flop_list = []
        # AUS
        aus = grouping.AUS(eqpt)
        alg_list.append('conventional')
        alg_obj_list.append(aus)
        for m in m_list:
            alg_name = f'proposed_m={m}'
            mrus = grouping.MRangeAUS(eqpt, m)
            alg_list.append(alg_name)
            alg_obj_list.append(mrus)
        for alg_idx in range(len(alg_list)):
            alg_name = alg_list[alg_idx]
            alg_obj_list[alg_idx].execute()
            table = alg_obj_list[alg_idx].get_group_table()
            sorted_minAD = alg_obj_list[alg_idx].get_sorted_min_ad_list()
            flop = alg_obj_list[alg_idx].get_flop_list()
            group_list.append(table)
            sorted_minAD_list.append(sorted_minAD)
            flop_list.append(flop)
            ev = eval(table, usr_ant_angr)
            eval_list.append(ev)
            sinr = ev.get_SINR()
            sinr_list.append(sinr)
            cap = ev.get_sum_cap_arr()
            cap_list.append(cap)
            save.save_sinr_arr(sinr, alg_name)
            save.save_eval_arr(cap, alg_name)
            save.save_flop_arr(flop, alg_name)
        figure = fig.make_cumulative_SINR(sinr_list, alg_list, sinr_title, True)
        figure2 = fig.make_cumulative_figures(cap_list, alg_list, cap_title, True)





        
    