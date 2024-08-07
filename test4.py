import load
import save
import utils
import rand_uni as ru
import grouping
import fig
import path
import rand_uni
from haps import CyrindricalHAPS as chaps
from haps import PlanarHAPS as phaps
from beamforming import BeamForming, ZeroForcing
from eval import SystemEvaluator as eval
from us_equipment import AUSEquipment
from properties import Property as prop
from parameters import Parameter as param
import numpy as np
import time
import location
import statistics
import os
from matplotlib import pyplot as plt

def cos_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def test_AUS(usr_n, usrs_per_group, radius):
    start = 0
    end = usr_n // usrs_per_group -1
    filename = 'AUS' + '_random'
    xy_arr = rand_uni.generate_random_uniform_usr_xy(usr_n, radius)
    ang_arr = utils.xy2ang(xy_arr, -param.z)
    eqpt = AUSEquipment(ang_arr, usrs_per_group)
    aus = grouping.AUS(eqpt)
    start_time = time.time()
    aus.execute()
    end_time = time.time()
    aus.print_group_info(start, end)
    print(f"Calculation time: {end_time-start_time}")
    group_table = aus.get_group_table()
    haps = chaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    # save.save_user_HAPS_angle(usr_ant_angr, 'cylindrical', 'random')
    ev = eval(group_table, usr_ant_angr, param.trans_pwr)
    # print(ev.cond_list)
    # print(np.average(ev.cond_list))
    cap_list = ev.get_sum_cap_arr()
    # print(np.average((ev.get_SNR())))
    # save.save_eval_arr(cap_list, filename)
    fig.make_cumulative_figures(np.array([cap_list]), ['AUS'], "fig_for_20231026", [0,1.8],0.2, False)


def test_ang_dif_vs_h_similarity(null_xy, att_cnt, com_r):
    null_ang = utils.xy2ang(null_xy, -param.z)
    rand_xy_arr = np.zeros([att_cnt, 2], dtype=float)
    ang_dif_arr = np.zeros(att_cnt, dtype=float)
    null_usr_xy_arr = np.zeros([2,2], dtype=float)
    score_arr = np.zeros(att_cnt, dtype=float)
    null_usr_xy_arr[0] = null_xy
    haps = phaps()
    usr_ant_angr = np.zeros([2, haps.ant_n, 3], dtype=float)
    usr_ant_angr[0] = haps.get_user_antenna_angle_r_arr_from_user_xy_arr(np.array([null_xy]))[0]
    s2_cnt = 0
    for att in range(att_cnt):
        rand_xy = rand_uni.generate_random_uniform_usr_xy(1, com_r)[0]
        rand_xy_arr[att] = rand_xy
        rand_ang = utils.xy2ang(rand_xy, -param.z)
        ang_dif = utils.calc_ang_dif(null_ang, rand_ang)
        ang_dif_arr[att] = np.sum(ang_dif**2)
        null_usr_xy_arr[1] = rand_xy
        usr_ant_angr[1] = haps.get_user_antenna_angle_r_arr_from_user_xy_arr(np.array([rand_xy]))[0]
        bf = BeamForming(usr_ant_angr)
        bf.set_h()
        h = bf.get_h()
        h_null = h[0]
        h_rand = h[1]
        hnr = np.real(h_null)
        hni = np.imag(h_null)
        hrr = np.real(h_rand)
        hri = np.real(h_rand)
        v1 = np.concatenate([hrr, -1*hri])
        v2 = np.concatenate([hnr, -1*hni])
        v3 = np.concatenate([hni, hnr])
        s1 = abs(cos_similarity(v1, v2))
        s2 = abs(cos_similarity(v1, v3))
        s = max(s1, s2)
        if s1 < s2: s2_cnt+=1
        s_ang = np.arccos(s) /np.pi*180
        score_arr[att] = s_ang
    print(f"Number that s2 is selected: {s2_cnt}")
    return rand_xy_arr, score_arr, ang_dif_arr

null_xy = np.array([10,10])
r = 20
rand_xy_arr, score_arr, ang_dif_arr = test_ang_dif_vs_h_similarity(null_xy, 2000, r)
print('min_score:', min(score_arr))
fig = plt.figure()
plt.scatter(ang_dif_arr, score_arr)
plt.show()

fig = plt.figure()
plt.scatter(rand_xy_arr[:,0], rand_xy_arr[:,1], s=10, c=score_arr, cmap='jet')
plt.xlim(-r, r)
plt.ylim(-r, r)
plt.colorbar()
plt.show()
        
