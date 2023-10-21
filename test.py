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

path.set_cur_dir()
np.set_printoptions(threshold=np.inf)

def test_AUS(city, usrs_per_group):
    start = 0
    end = 50
    filename = 'AUS' + city
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr, usrs_per_group)
    aus = grouping.AUS(eqpt)
    aus.execute()
    aus.print_group_info(start, end)
    group_table = aus.get_group_table()
    sorted_min_ad_arr = aus.get_sorted_min_ad_list()
    haps = phaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    save.save_user_HAPS_angle(usr_ant_angr, 'planar', city)
    ev = eval(group_table, sorted_min_ad_arr, usr_ant_angr)
    cap_list = ev.get_sum_cap_arr()
    save.save_eval_arr(cap_list, filename)

def test_MRUS(city, M, usrs_per_group):
    start = 0
    end = 50
    filename = 'MRUS' + city + '_' + str(M)
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr, usrs_per_group)
    mrus = grouping.MRangeAUS(eqpt, M)
    mrus.execute()
    mrus.print_group_info(start, end)
    group_table = mrus.get_group_table()
    sorted_min_ad_arr = mrus.get_sorted_min_ad_list()
    haps = phaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    save.save_user_HAPS_angle(usr_ant_angr, 'cylindrical', city)
    ev = eval(group_table, sorted_min_ad_arr, usr_ant_angr)
    cap_list = ev.get_sum_cap_arr()
    save.save_eval_arr(cap_list, filename)
    save.save_user_HAPS_angle(usr_ant_angr, 'planar', 'MRUS_tokyo')

def make_eval_fig(city, m_val_list):
    ds_types = []
    ds_types.append('AUS_' + city)
    ds_types.extend(['MRUS_'+city+'_'+str(i) for i in m_val_list])
    eval_arr_list = []
    label_list = []
    label_list.append('AUS')
    label_list.extend(['m='+str(i) for i in m_val_list])
    # label_list.append('AUS')
    title = 'system_capacity_' + city
    for ds_type in ds_types:
        eval_arr = load.load_eval(ds_type)
        eval_arr_list.append(eval_arr)
    figure = fig.make_cumulative_figures(eval_arr_list, label_list, title, True)

def make_minAD_fig(city, m_val_list, usrs_per_group):
    title = 'minAD_' + city
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr, usrs_per_group)
    # 以下, 加えたいアルゴリズムを追加
    data_dict = {}
    alg_list = []
    minAD_arr_list = []
    # AUS
    alg_name = 'AUS_' + city
    aus = grouping.AUS(eqpt)
    aus.execute()
    aus_group = aus.get_group_table()
    aus_sorted_arr = aus.get_sorted_min_ad_list()
    data_dict[alg_name] = aus_sorted_arr
    alg_list.append(alg_name)
    # MRUS
    for m in m_val_list:
        alg_name = 'MRUS_' + city + '_' + str(m)
        mrus = grouping.MRangeAUS(eqpt, m)
        mrus.execute()
        mrus.set_min_ad_all()
        mrus.set_sorted_min_ad_list()
        mrus_group = mrus.get_group_table()
        mrus_sorted_arr = mrus.get_sorted_min_ad_list()
        data_dict[alg_name] = mrus_sorted_arr
        alg_list.append(alg_name)
    # SAUSS
    alg_name = 'SAUSS_' + city
    sauss = grouping.ASUSwithSampling(eqpt)
    sauss.execute()
    sauss.set_min_ad_all()
    sauss.set_sorted_min_ad_list()
    sauss_group = sauss.get_group_table()
    sauss_sorted_arr = sauss.get_sorted_min_ad_list()
    data_dict[alg_name] = sauss_sorted_arr
    alg_list.append(alg_name)
    for alg_iter in range(len(alg_list)):
        alg_name = alg_list[alg_iter]
        data = data_dict[alg_name][1]
        minAD_arr_list.append(data)
        save.save_minAD_arr(data, alg_name)
    figure = fig.make_cumulative_minAD(minAD_arr_list, alg_list, title, True)  

# for SNR/I/SINR/capacity(with standard deviation) figure reported on 2023/10/21
def generate_interference_SNR_SINR_figure_with_random_users(usr_n_list, rep, radius, cap_title, sn_title):
    usr_type_n = len(usr_n_list)
    cap_list = np.zeros([usr_type_n, rep])
    snr_med_std_list = np.zeros([usr_type_n, 2])
    i_med_std_list = np.zeros([usr_type_n, 2])
    sinr_med_std_list = np.zeros([usr_type_n, 2])
    file_existence = True
    for usr_type_idx, usrs_per_group in enumerate(usr_n_list):
        usr_n = usrs_per_group * rep
        filename = f'random_user={usr_n}_r={radius}'
        ang_arr = load.load_angle(filename)
        if ang_arr == None:
            xy_arr = rand_uni.generate_random_uniform_usr_xy(usr_n, radius)
            ang_arr = utils.xy2ang(xy_arr, -param.z)
            save.save_angle_arr(ang_arr, filename)
            file_existence = False
        eqpt = AUSEquipment(ang_arr, usrs_per_group)
        rus = grouping.RUS(eqpt)
        rus.execute()
        group_table = rus.get_group_table()
        sorted_min_ad_arr = rus.get_sorted_min_ad_list()
        haps = phaps()
        usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
        ev = eval(group_table, sorted_min_ad_arr, usr_ant_angr)
        cap_list[usr_type_idx] = ev.get_sum_cap_arr()
        snr = ev.get_SNR()
        intf = ev.get_interference()
        sinr = ev.get_SINR()
        if not file_existence:
            save.save_snr_arr(snr, filename)
            save.save_interference_arr(intf, filename)
            save.save_sinr_arr(sinr, filename)
        snr_med_std_list[usr_type_idx] = np.array([statistics.median(snr), 
                                                  np.std(snr)])
        sinr_med_std_list[usr_type_idx] = np.array([statistics.median(sinr), 
                                                  np.std(sinr)])
        i_med_std_list[usr_type_idx] = np.array([statistics.median(intf), 
                                                  np.std(intf)])
    fig.make_capacity_fig_with_std(usr_n_list, cap_list, cap_title)
    fig.make_SNR_interference_SINR_figure(usr_n_list, 
                                          snr_med_std_list[:,0],
                                          snr_med_std_list[:,1],
                                          i_med_std_list[:,0],
                                          i_med_std_list[:,1],
                                          sinr_med_std_list[:,0],
                                          sinr_med_std_list[:,1],
                                          sn_title)
        
usr_list = [5*i for i in range(1,21)]
rep = 50
r = 20
cap_title = f'cap_fig_user={usr_list[0]}~{usr_list[-1]}_radius={r}_rep={rep}'
sn_title = f'sn_fig_user={usr_list[0]}~{usr_list[-1]}_radius={r}_rep={rep}'
generate_interference_SNR_SINR_figure_with_random_users(usr_list, 50, 20, cap_title, sn_title)