import numpy as np
import haps
from base_station import BaseStations
from terrestrial import TerrestrialComunication as tc
from beamforming import TwoStagePrecoding as precoding
from beamforming import ZeroForcing2 as zf2
from parameters import Parameter as param

class IntegratedEnvironment():
    def __init__(self, base_stations:BaseStations, haps: haps.PlanarHAPS, haps_usr_xy_arr, M, usr_gain,
                 bs_pwr, haps_power_arr):
        self.bss = base_stations
        self.haps = haps
        self.haps_usr_xy_arr = haps_usr_xy_arr
        self.bs_usr_xy_arr, self.bs_usr_bs_sec_main_arr = self.bss.get_users_xy_arr_with_bs_sector_idx_arr()
        self.haps_usr_n = len(self.haps_usr_xy_arr)
        self.bs_usr_n = len(self.bs_usr_xy_arr)
        self.usr_xy_arr = np.concatenate([self.haps_usr_xy_arr, self.bs_usr_xy_arr])
        self.haps_usr_ant_angr_arr = self.haps.get_user_antenna_angle_r_arr_from_user_xy_arr(self.usr_xy_arr)
        self.usr_bs_sector_angr_arr = self.bss.calc_user_bs_sector_angr(self.usr_xy_arr, usr_height=0.001)
        self.M = M
        self.usr_gain = usr_gain
        self.precoder = precoding(self.haps_usr_ant_angr_arr, self.bs_usr_n, self.M)
        self.haps_usr_h = self.precoder.h[:self.haps_usr_n]
        self.terr_usr_h = self.precoder.h[self.haps_usr_n:]
        self.tc = tc(self.usr_bs_sector_angr_arr, self.bs_usr_n, self.bss, self.usr_gain)
        self.g = self.tc.g
        self.haps_g = self.tc.g[:self.tc.ue_usr_n]
        self.bs_g = self.tc.g[self.tc.ue_usr_n:]
        self.bandwidth = param.bandwidth
        self.noise_pwr_dens = param.noise_power_density
        self.noise_fig = param.noise_figure
        self.noise = 0
        self.haps_sinr = np.zeros([self.haps_usr_n])
        self.bs_sinr = np.zeros([self.bs_usr_n])
        self.w = self.precoder.w
        self.bs_n = self.bss.bs_n
        self.sec_n = self.bss.sec_size
        self.set_noise()
        self.set_SINR(bs_pwr, haps_power_arr)
        
    def set_noise(self):
        bandwidth_bd = 10 * np.log10(self.bandwidth)
        noise_dbm = self.noise_pwr_dens + bandwidth_bd + self.noise_fig
        self.noise = 10**((noise_dbm-30)/10)

    def set_SINR(self, bs_pwr, haps_power_arr):
        # haps user
        for usr in range(self.haps_usr_n):
            hu = self.haps_usr_h[usr]
            wu = self.w[:,usr]
            sig = abs(sum(hu*wu))**2 * haps_power_arr[usr]
            intf = 0
            for usr2 in range(self.haps_usr_n):
                if usr == usr2:
                    continue
                wi = self.w[:,usr2]
                intf += abs(sum(hu*wi))**2 * haps_power_arr[usr2]
            for bs_idx in range(self.bs_n):
                for sec_idx in range(self.sec_n):
                    g = self.haps_g[usr, bs_idx, sec_idx]
                    intf += abs(g)**2 * bs_pwr
            self.haps_sinr[usr] = sig / (intf + self.noise)
            print('haps', sig, intf, self.noise)
        # terrestrial user
        for usr in range(self.bs_usr_n):
            bs_sec_idx = self.bs_usr_bs_sec_main_arr[usr]
            bs_idx = bs_sec_idx[0]
            sec_idx = bs_sec_idx[1]
            g = self.bs_g[usr, bs_idx, sec_idx]
            sig = abs(g)**2 * bs_pwr
            intf = 0
            for bs_idx2 in range(self.bs_n):
                for sec_idx2 in range(self.sec_n):
                    if bs_idx==bs_idx2 and sec_idx==sec_idx2:
                        continue
                    g = self.bs_g[usr, bs_idx2, sec_idx2]
                    intf += abs(g)**2 * bs_pwr
            hu = self.terr_usr_h[usr]
            for usr2 in range(self.haps_usr_n):
                w = self.w[:,usr2]
                intf += abs(sum(hu*w))**2 * haps_power_arr[usr2]
            self.bs_sinr[usr] = sig / (intf + self.noise)
            print("ter", sig, intf, self.noise)

    
class IntegratedEnvironment2():
    def __init__(self, base_stations:BaseStations, haps: haps.PlanarHAPS, haps_usr_xy_arr, M, usr_gain,
                 bs_pwr, haps_power_arr):
        self.bss = base_stations
        self.haps = haps
        self.haps_usr_xy_arr = haps_usr_xy_arr
        self.bs_usr_xy_arr, self.bs_usr_bs_sec_main_arr = self.bss.get_users_xy_arr_with_bs_sector_idx_arr()
        self.haps_usr_n = len(self.haps_usr_xy_arr)
        self.bs_usr_n = len(self.bs_usr_xy_arr)
        self.usr_xy_arr = np.concatenate([self.haps_usr_xy_arr, self.bs_usr_xy_arr])
        self.haps_usr_ant_angr_arr = self.haps.get_user_antenna_angle_r_arr_from_user_xy_arr(self.usr_xy_arr)
        self.usr_bs_sector_angr_arr = self.bss.calc_user_bs_sector_angr(self.usr_xy_arr, usr_height=0.001)
        self.M = M
        self.usr_gain = usr_gain
        self.precoder = zf2(self.haps_usr_ant_angr_arr, self.haps_usr_n)
        self.haps_usr_h = self.precoder.h[:self.haps_usr_n]
        self.terr_usr_h = self.precoder.h[self.haps_usr_n:]
        self.tc = tc(self.usr_bs_sector_angr_arr, self.bs_usr_n, self.bss, self.usr_gain)
        self.g = self.tc.g
        self.haps_g = self.tc.g[:self.tc.ue_usr_n]
        self.bs_g = self.tc.g[self.tc.ue_usr_n:]
        self.bandwidth = param.bandwidth
        self.noise_pwr_dens = param.noise_power_density
        self.noise_fig = param.noise_figure
        self.noise = 0
        self.haps_sinr = np.zeros([self.haps_usr_n])
        self.bs_sinr = np.zeros([self.bs_usr_n])
        self.w = self.precoder.w
        self.bs_n = self.bss.bs_n
        self.sec_n = self.bss.sec_size
        self.set_noise()
        self.set_SINR(bs_pwr, haps_power_arr)
        
    def set_noise(self):
        bandwidth_bd = 10 * np.log10(self.bandwidth)
        noise_dbm = self.noise_pwr_dens + bandwidth_bd + self.noise_fig
        self.noise = 10**((noise_dbm-30)/10)

    def set_SINR(self, bs_pwr, haps_power_arr):
        # haps user
        for usr in range(self.haps_usr_n):
            hu = self.haps_usr_h[usr]
            wu = self.w[:,usr]
            sig = abs(sum(hu*wu))**2 * haps_power_arr[usr]
            intf = 0
            for usr2 in range(self.haps_usr_n):
                if usr == usr2:
                    continue
                wi = self.w[:,usr2]
                intf += abs(sum(hu*wi))**2 * haps_power_arr[usr2]
            for bs_idx in range(self.bs_n):
                for sec_idx in range(self.sec_n):
                    g = self.haps_g[usr, bs_idx, sec_idx]
                    intf += abs(g)**2 * bs_pwr
            self.haps_sinr[usr] = sig / (intf + self.noise)
            print('haps', sig, intf, self.noise)
        # haps user
        for usr in range(self.bs_usr_n):
            bs_sec_idx = self.bs_usr_bs_sec_main_arr[usr]
            bs_idx = bs_sec_idx[0]
            sec_idx = bs_sec_idx[1]
            g = self.bs_g[usr, bs_idx, sec_idx]
            sig = abs(g)**2 * bs_pwr
            intf = 0
            for bs_idx2 in range(self.bs_n):
                for sec_idx2 in range(self.sec_n):
                    if bs_idx==bs_idx2 and sec_idx==sec_idx2:
                        continue
                    g = self.bs_g[usr, bs_idx2, sec_idx2]
                    intf += abs(g)**2 * bs_pwr
            hu = self.terr_usr_h[usr]
            for usr2 in range(self.haps_usr_n):
                w = self.w[:,usr2]
                intf += abs(sum(hu*w))**2 * haps_power_arr[usr2]
            self.bs_sinr[usr] = sig / (intf + self.noise)
            print("ter", sig, intf, self.noise)



            
