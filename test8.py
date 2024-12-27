import numpy as np
import haps
from base_station import BaseStations
from terrestrial import TerrestrialComunication as tc
from beamforming import TwoStagePrecoding as precoding
from integrated_environment import IntegratedEnvironment as ie
from integrated_environment import IntegratedEnvironment2 as ie2
from matplotlib import pyplot as plt
import load
import save
import utils
import rand_uni as ru
import grouping
import haps
import fig
from eval import SystemEvaluator as eval
from us_equipment import AUSEquipment
from properties import Property as prop
from parameters import Parameter as param
import rand_uni
import datetime
import path
import time
import statistics
import os

def get_uniform_user_dist_from_bs(bs_xy, usr_n, start_deg, r):
    ang_unit = 2*np.pi/usr_n
    rad_arr = np.array([start_deg/180*np.pi+ang_unit*i for i in range(usr_n)])
    base_xy = np.array([r,0])
    usr_xy_list = []
    for rad in rad_arr:
        rotate_matrix = np.array([[np.cos(rad), -np.sin(rad)], [np.sin(rad), np.cos(rad)]])
        usr_xy = np.dot(rotate_matrix, base_xy)
        usr_xy_list.append(usr_xy)
    usr_xy_arr = np.array(usr_xy_list)
    usr_xy_arr[:,0] += bs_xy[0]
    usr_xy_arr[:,1] += bs_xy[1]
    return usr_xy_arr

path.set_cur_dir()
###################################################################
# setting of base station
usrs_per_sec = 1
bs_xy_arr = np.array([[2,0], [0, 7], [-12, 0], [0,-17]])
# bs_xy_arr = np.array([[(10+5*i)*np.cos(np.pi*2/8*i), (10+5*i)*np.sin(np.pi*2/8*i)] for i in range(8)])
# bs_xy_arr = np.array([[3,0], [4,4], [0, 8], [-7,7], [-13,0], [-11,-11], [0,-18], [14, -14]])
bs_size = len(bs_xy_arr)
bs_height_arr = np.zeros(bs_size)+0.051
bs_com_radius_arr = np.zeros(bs_size) + 2
bs_azi_3db_arr = np.zeros(bs_size) + 70
bs_elev_3db_arr = np.zeros(bs_size) + 10
bs_elev_tilt_arr = np.zeros(bs_size) + 1.15
bs_side_att_arr = np.zeros(bs_size) + 25
bs_max_att_arr = np.zeros(bs_size) + 20
bs_max_gain_arr = np.zeros(bs_size) + 14
usr_per_sec_arr = np.zeros(bs_size, dtype=int) + usrs_per_sec
sec_size = 3
bs_pwr = 20
usr_r_from_base = 0.5
bs_usr_xy_arrs = np.array([get_uniform_user_dist_from_bs(bs, 
                                                        sec_size*usrs_per_sec, 
                                                        0, usr_r_from_base)
                         for bs in bs_xy_arr])
###################################################################
# setting of haps
nu_list = [12]
alg_list = ['ACUS4']
side_ant_list = [14]
att_size = 30
haps_usr_n = 1200
haps_com_r = 20
user_type = 'random'+str(haps_usr_n)
haps_altitude = 20
haps_total_pwr = 120
h_type = 'p'
##################################################################
# setting of users
usr_gain = -3
usr_height = 0.001
##################################################################
tgt_xy = np.array([0, -17])
r_lim = 1
range_type = 'square'
b_usr_type = 'r1ang0'
##################################################################
if b_usr_type is 'random':
    bss = BaseStations(bs_size, bs_height_arr, bs_com_radius_arr, bs_xy_arr, 
                    bs_max_gain_arr, bs_azi_3db_arr, bs_elev_3db_arr,
                    bs_elev_tilt_arr, bs_side_att_arr, bs_max_att_arr, sec_size,
                    users_per_sector_arr=usr_per_sec_arr)
else:    
    bss = BaseStations(bs_size, bs_height_arr, bs_com_radius_arr, bs_xy_arr, 
                    bs_max_gain_arr, bs_azi_3db_arr, bs_elev_3db_arr,
                    bs_elev_tilt_arr, bs_side_att_arr, bs_max_att_arr, sec_size,
                    user_xy_arrs=bs_usr_xy_arrs)
bss_xy_arr = bss.get_users_xy_arr()

for side_ant in side_ant_list:
    if h_type == 'p':
        haps_type = haps.VariableAntennaPlanarHAPS(side_ant)
    elif h_type == 'c':
        haps_type = haps.CyrindricalHAPS()
    m = side_ant**2 - bs_size*sec_size*usrs_per_sec
    for nu in nu_list:
        std_arr_list = []
        med_arr_list = []
        for alg in alg_list:
            haps_xy_list = []
            haps_sinr_list = []
            bs_sinr_list = []
            tag = f'ant={side_ant}_shp={h_type}_nu={nu}_alg={alg}_r={haps_com_r}'
            output_list = [['id','xy','signal', 'intf', 'ter_intf', 'noise', 'SINR', 'distance from base station']]
            xy_arr = []
            h_sinr_arr = []
            for att_idx in range(att_size):
                haps_xy_arr = load.load_xy(f'typ={user_type}_r={haps_com_r}_DSidx={att_idx}')
                grp_table = load.load_group_table(f'typ={user_type}_Nu={nu}_r={haps_com_r}_z='+\
                                                  f'{haps_altitude}_alg={alg}_DSidx={att_idx}_' +\
                                                  f'SIMidx=0')
                haps_xy_list.append(haps_xy_arr)
                for idx, mems in enumerate(grp_table):
                    haps_xys = haps_xy_arr[mems]
                    int_nev = ie(bss, haps_type, haps_xys, m, usr_gain, bs_pwr, haps_total_pwr)
                    bs_sinr = int_nev.bs_sinr
                    haps_sinr = int_nev.haps_sinr
                    haps_intf_arr = int_nev.haps_intf_arr
                    haps_sig_arr = int_nev.haps_sig_arr
                    haps_ter_intf_arr = int_nev.haps_ter_intf_arr
                    haps_ns_arr = int_nev.haps_ns_arr
                    info_list = int_nev.info_list
                    bs_sinr_db = 10 * np.log10(bs_sinr)
                    haps_sinr_db = 10 * np.log10(haps_sinr)
                    haps_sinr_list.append(haps_sinr_db)
                    bs_sinr_list.append(bs_sinr_db)
                    for mem_idx in range(len(mems)):
                        xy = haps_xys[mem_idx]
                        flg = False
                        r = np.sqrt(sum((tgt_xy-xy)**2))
                        if range_type is 'square':
                            x_range = [tgt_xy[0]-1, tgt_xy[0]+1]
                            y_range = [tgt_xy[1]-1, tgt_xy[1]+1]   
                            if x_range[0]<xy[0]<x_range[1] and y_range[0]<xy[1]<y_range[1]: flg = True
                        elif range_type is 'circle':
                            if r_lim > r: flg = True
                        if flg:
                            sig = haps_sig_arr[mem_idx]
                            ter_intf = haps_ter_intf_arr[mem_idx]
                            intf = haps_intf_arr[mem_idx]
                            ns = haps_ns_arr[mem_idx]
                            sinr = 10*np.log10(sig/(intf+ter_intf+ns))
                            id = mems[mem_idx]
                            output_list.append(np.array([id,xy, sig, intf, ter_intf, ns, sinr, r]))
                            xy_arr.append(xy)
                            h_sinr_arr.append(sinr)
            # save
            com_tag = tag + f'_attsize={att_size}_241103_tgtxy={tgt_xy}_rlim={r_lim}_busrtyp={b_usr_type}'
            comp_tag = 'datas_' + com_tag
            xy_path = 'xy_' + com_tag
            h_sinr_path = 'h_SINR_' + com_tag
            save.save_test_arr(np.array(xy_arr), xy_path)
            save.save_test_arr(np.array(h_sinr_arr), h_sinr_path)
            # print(output_list)
            # print(np.array(output_list).ndim)
            save.save_test_arr(np.array(output_list), comp_tag)

                    
            



