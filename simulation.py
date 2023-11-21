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
    def __init__(self, typ, nuk, nu, nt, r, z, shp, DSidx):
        self.typ = typ
        self.nuk = nuk
        self.nu = nu
        self.nt = nt
        self.r = r
        self.z = z
        self.shp = shp
        self.dsi = DSidx
        self.xy_tag = ''
        self.ang_tag = ''
        self.ua_tag = ''
        self.setup_tag()
        self.y_arr = None
        self.ang_arr = None
        self.eqpt = None
        self.ua_angr_arr = None
        self.setup_usr_ang_arr()
    
    def setup_tag(self):
        self.xy_tag = f'typ={self.typ}_NuK={self.nuk}_' + \
                      f'r={self.r}_DSidx={self.dsi}'
        self.ang_tag = f'typ={self.typ}_NuK={self.nuk}_r={self.r}_' + \
                       f'z={self.z}_DSidx={self.dsi}'
        self.ua_tag = f'typ={self.typ}_NuK={self.nuk}_Nu={self.nu}_Nt={self.nt}_' + \
                      f'r={self.r}_z={self.z}_shp={self.shp}_DSidx={self.dsi}'

    def setup_xy(self):
        try:
            self.xy_arr = load.load_xy(self.xy_tag)
        except FileNotFoundError:
            if self.typ in prop.cities:
                city = self.typ + '_' + {self.r}
                self.xy_arr = load.load_mat(city)
            elif self.typ is 'random':
                self.xy_arr = rand_uni.generate_random_uniform_usr_xy(self.nuk, self.r)
            else:
                raise Exception('[INFO ERROR] There is an error in setup_xy(): '+\
                                'Invalid type to create xy array is entered.')
            save.save_xy_arr(self.xy_arr, self.xy_tag)
    
    def setup_ang(self):
        try:
            self.ang_arr = load.load_angle(self.ang_tag)
        except FileNotFoundError:
            self.setup_xy()
            self.ang_arr = utils.xy2ang(self.xy_arr, -self.z)
            save.save_angle_arr(self.ang_arr, self.ang_tag)
    
    def setup_eqpt(self):
        if self.ang_arr is None:
            self.setup_ang()
        self.eqpt = AUSEquipment(self.ang_arr, self.nu)
    
    def setup_usr_ang_arr(self):
        try:
            self.ua_angr_arr = load.load_usr_haps_angle(self.ua_tag)
        except FileNotFoundError:
            self.setup_eqpt()
            self.ua_angr_arr = haps.get_user_antenna_angle_r_arr(self.shp, self.eqpt)
            save.save_user_HAPS_angle(self.ua_angr_arr, self.ua_tag)


class Simulation():
    def __init__(self, ds: Dataset, alg, SIMidx):
        self.typ = ds.typ
        self.nuk = ds.nuk
        self.nu = ds.nu
        self.nt = ds.nt
        self.r = ds.r
        self.z = ds.z
        self.shp = ds.shp
        self.alg = alg
        self.dsi = ds.dsi
        self.simi = SIMidx
        self.grp_tag = ''
        self.eval_tag = ''
        self.sig_tag = ''
        self.intf_tag = ''
        self.noise_tag = ''
        self.sinr_tag = ''
        self.flop_tag = ''
        self.grp_mAD_tag = ''
        self.usr_mAD_tag = ''
        self.setup()
    
    def setup(self):
        tag1 = f'typ={self.typ}_NuK={self.nuk}_Nu={self.nu}_' + \
               f'r={self.r}_z={self.z}_alg={self.alg}_' + \
               f'DSidx={self.dsi}_SIMidx={self.simi}'
        tag2 = f'typ={self.typ}_NuK={self.nuk}_Nu={self.nu}_' + \
               f'Nt={self.nt}_r={self.r}_z={self.z}_shp={self.shp}_'+\
               f'alg={self.alg}_DSidx={self.dsi}_SIMidx={self.simi}'
        tag3 = f'typ={self.typ}_NuK={self.nuk}_Nu={self.nu}_' + \
               f'Nt={self.nt}_r={self.r}_z={self.z}_'+\
               f'alg={self.alg}_DSidx={self.dsi}_SIMidx={self.simi}'
        self.grp_tag = self.grp_mAD_tag = self.usr_mAD_tag = tag1
        self.eval_tag = self.sig_tag = self.intf_tag = \
                        self.noise_tag = self.sinr_tag = tag2
        self.flop_tag = tag3
    



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
            ev = eval(table, sorted_minAD, usr_ant_angr)
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





        
    