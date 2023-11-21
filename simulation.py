import load
import save
import utils
import rand_uni as ru
import grouping
import haps
from eval import SystemEvaluator as eval
from us_equipment import AUSEquipment
from properties import Property as prop
from parameters import Parameter as param
import rand_uni
import numpy as np

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
                city = self.typ + '_' + str(self.r)  # ex. tokyo_20
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
            if self.xy_arr is None:
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
            if self.eqpt is None:
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
    def __init__(self, ds: Dataset, t_pwr, alg, SIMidx):
        # basic parameters
        self.ds: Dataset = ds
        self.typ = ds.typ
        self.nu = ds.nu
        self.nt = ds.nt
        self.r = ds.r
        self.z = ds.z
        self.shp = ds.shp
        self.t_pwr = t_pwr
        self.alg = alg
        self.dsi = ds.dsi
        self.simi = SIMidx  # index of simulation
        self.print_simulation_status()

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
    
    def print_simulation_status(self):
        print()
        blank_mass = " " * 10
        print("[INFO SIM] Simulation has started.")
        print(f"{blank_mass} <settings>")
        print(f"{blank_mass} type : {self.typ}")
        print(f"{blank_mass} Nu   : {self.nu}")
        print(f"{blank_mass} Nt   : {self.nt}")
        print(f"{blank_mass} r    : {self.r}")
        print(f"{blank_mass} z    : {self.z}")
        print(f"{blank_mass} shp  : {self.shp}")
        print(f"{blank_mass} t_pwr: {self.t_pwr}")
        print(f"{blank_mass} alg  : {self.alg}")
        print(f"{blank_mass} DSi  : {self.dsi}")
        print(f"{blank_mass} SIMi : {self.simi}")
        print()

    # set tags for loading (execute 1st)
    def setup_tag(self):
        tag1 = f'typ={self.typ}_Nu={self.nu}_' + \
               f'r={self.r}_z={self.z}_alg={self.alg}_' + \
               f'DSidx={self.dsi}_SIMidx={self.simi}'
        tag2 = f'typ={self.typ}_Nu={self.nu}_Nt={self.nt}_' + \
               f'r={self.r}_z={self.z}_shp={self.shp}_tp={self.t_pwr}_'+\
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
            self.flop_arr = load.load_flop(self.flop_tag)
        except FileNotFoundError:
            # generate
            if self.ds.eqpt is None:
                self.ds.setup_eqpt()
            eqpt :AUSEquipment = self.ds.get_eqpt()
            if self.alg == 'RUS':
                grp = grouping.RUS(eqpt)
            elif self.alg == 'AUS':
                grp = grouping.AUS(eqpt)
            elif 'MRUS' in self.alg or 'ACUS' in self.alg:
                # set 'M' (cluster size)
                m = int(self.alg[4:])
                grp = grouping.MRangeAUS(eqpt, m)
            else:
                raise Exception("[ERROR] Invalid algorithm is entered.")
            grp.execute()
            self.group_table = grp.get_group_table()
            self.grp_mAD_arr = grp.get_min_ad_arr()
            self.usr_mAD_arr = grp.get_user_mAD_arr()
            self.flop_arr = np.array(grp.get_flop_list())

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
            if self.ds.ua_angr_arr is None:
                self.ds.setup_ua_angr_arr()  # calculate ua_angr_arr in Dataset obj
            ua_angr_arr = self.ds.get_ua_angr_arr()
            ev = eval(self.group_table, ua_angr_arr, self.t_pwr)
            self.sig_arr = ev.get_signal_pwr()
            self.intf_arr = ev.get_interference()
            self.noise_arr = ev.get_noise_pwr()
            self.cap_arr = np.array(ev.get_sum_cap_arr())

            # save
            save.save_sig_arr(self.sig_arr, self.sig_tag)
            save.save_interference_arr(self.intf_arr, self.intf_tag)
            save.save_noise_arr(self.noise_arr, self.noise_tag)
            save.save_eval_arr(self.cap_arr, self.cap_tag)