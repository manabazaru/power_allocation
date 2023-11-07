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

path.set_cur_dir()
np.set_printoptions(threshold=np.inf)

def test_AUS(usr_n, usrs_per_group):
    start = 0
    end = 50
    filename = 'AUS' + '_random'
    xy_arr = rand_uni.generate_random_uniform_usr_xy(usr_n, 100)
    ang_arr = utils.xy2ang(xy_arr, -param.z)
    eqpt = AUSEquipment(ang_arr, usrs_per_group)
    aus = grouping.AUS(eqpt)
    aus.execute()
    aus.print_group_info(start, 49)
    group_table = aus.get_group_table()
    sorted_min_ad_arr = aus.get_sorted_min_ad_list()
    haps = chaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    save.save_user_HAPS_angle(usr_ant_angr, 'cylindrical', 'random')
    ev = eval(group_table, sorted_min_ad_arr, usr_ant_angr)
    cap_list = ev.get_sum_cap_arr()
    print(cap_list)
    save.save_eval_arr(cap_list, filename)
    fig.make_cumulative_figures(np.array([cap_list]), ['AUS'], "fig_for_20231026", True)
test_AUS(1200, 12)

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
    save.save_user_HAPS_angle(usr_ant_angr, 'planar', city)
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
def generate_interference_SNR_SINR_figure_with_random_users(usr_n_list, rep, radius, cap_title, sn_title, intf_title):
    usr_type_n = len(usr_n_list)
    cap_list = np.zeros([usr_type_n, rep])
    snr_med_std_list = np.zeros([usr_type_n, 2])
    i_med_std_list = np.zeros([usr_type_n, 4])
    sinr_med_std_list = np.zeros([usr_type_n, 2])
    for usr_type_idx, usrs_per_group in enumerate(usr_n_list):
        usr_n = usrs_per_group * rep
        filename = f'random_user={usr_n}_r={radius}'
        ang_arr = load.load_angle(filename)
        if ang_arr is None:
            xy_arr = rand_uni.generate_random_uniform_usr_xy(usr_n, radius)
            ang_arr = utils.xy2ang(xy_arr, -param.z)
            save.save_angle_arr(ang_arr, filename)
            eqpt = AUSEquipment(ang_arr, usrs_per_group)
            rus = grouping.RUS(eqpt)
            rus.execute()
            group_table = rus.get_group_table()
            sorted_min_ad_arr = rus.get_sorted_min_ad_list()
            haps = phaps()
            usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
            ev = eval(group_table, sorted_min_ad_arr, usr_ant_angr)
            cap_arr = ev.get_sum_cap_arr()
            save.save_eval_arr(cap_arr, filename)
            cap_list[usr_type_idx] = cap_arr
            snr = ev.get_SNR()
            intf = ev.get_interference()
            sinr = ev.get_SINR()
            save.save_group_table(group_table, 'no_grouping', filename)
            save.save_snr_arr(snr, filename)
            save.save_interference_arr(intf, filename)
            save.save_sinr_arr(sinr, filename)
        else:
            snr = load.load_snr(filename)
            sinr = load.load_sinr(filename)
            intf = load.load_interference(filename)
            cap_list[usr_type_idx] = load.load_eval(filename)
        snr = 10 * np.log10(snr)
        sinr = 10 * np.log10(sinr)
        intf = np.log10(intf)
        snr_med_std_list[usr_type_idx] = np.array([statistics.median(snr), 
                                                  np.std(snr)])
        sinr_med_std_list[usr_type_idx] = np.array([statistics.median(sinr), 
                                                  np.std(sinr)])
        i_med_std_list[usr_type_idx] = np.array([statistics.median(intf), 
                                                 np.std(intf), 
                                                 max(intf),
                                                 min(intf)])
    fig.make_capacity_fig_with_std(usr_n_list, cap_list, cap_title)
    fig.make_SNR_SINR_figure(usr_n_list, 
                             snr_med_std_list[:,0],
                             snr_med_std_list[:,1],
                             sinr_med_std_list[:,0],
                             sinr_med_std_list[:,1],
                             sn_title)
    fig.make_interference_figure(usr_n_list, 
                                i_med_std_list[:,0],
                                i_med_std_list[:,1],
                                i_med_std_list[:,2],
                                i_med_std_list[:,3],
                                intf_title)

def generate_user_distribution_of_max_min_interference(usr_n_list,
                                                       rep,
                                                       radius,
                                                       alg):
    for usrs_per_group in usr_n_list:
        usr_n = usrs_per_group * rep
        filename = f'random_user={usr_n}_r={radius}'
        fig_dir = prop.fig_path + filename + '/'
        ang_arr = load.load_angle(filename)
        xy_arr = utils.ang2xy(ang_arr, -param.z)
        group_arr = load.load_group_table(filename, alg)
        intf_arr = load.load_interference(filename)
        log10_intf_arr = np.log10(intf_arr)
        min_group_intf_arr = np.zeros(rep)+1*10**100
        max_group_intf_arr = np.zeros(rep)-1*10**100
        ave_group_intf_arr = np.zeros(rep)        
        intf_min = 1*10**100
        intf_max = -1*10**100
        for g_idx in range(rep):
            group_mem = group_arr[g_idx]
            intf_sum = 0
            for mem_idx in range(len(group_mem)):
                usr = group_mem[mem_idx]
                # intf = intf_arr[usr]
                intf = log10_intf_arr[usr]
                intf_sum += intf_arr[usr]
                if intf_min > intf: intf_min = intf
                if intf_max < intf: intf_max = intf
                if max_group_intf_arr[g_idx] < intf:
                    max_group_intf_arr[g_idx] = intf
                if min_group_intf_arr[g_idx] > intf:
                    min_group_intf_arr[g_idx] = intf
            ave_group_intf_arr[g_idx] = intf_sum/len(group_mem)
        # std_intf_arr = intf_arr/intf_max
        std_intf_arr = (log10_intf_arr-intf_min) / (intf_max-intf_min)
        min_group_intf_rank = np.zeros(rep, dtype=int)
        max_group_intf_rank = np.zeros(rep, dtype=int)
        ave_group_intf_rank = np.zeros(rep, dtype=int)
        for i in range(rep):
            min_group_intf_rank[np.argsort(min_group_intf_arr)[i]] = i
            max_group_intf_rank[np.argsort(max_group_intf_arr)[i]] = i
            ave_group_intf_rank[np.argsort(ave_group_intf_arr)[i]] = i
        if not os.path.exists(fig_dir):
            os.mkdir(fig_dir)
        for g_idx in range(rep):
            g_mem = group_arr[g_idx]
            min_rank = min_group_intf_rank[g_idx]
            max_rank = max_group_intf_rank[g_idx]
            ave_rank = ave_group_intf_rank[g_idx]
            fig_name = filename + f"/g={g_idx}_rank_min={min_rank}+max={max_rank}+ave={ave_rank}"
            group_xy_arr = xy_arr[g_mem]
            group_intf_arr = std_intf_arr[g_mem]
            fig.save_plt_users_with_colorbar(group_xy_arr,
                                             fig_name, 
                                             group_intf_arr,
                                             radius)

usr_list = [5*i for i in range(1,21)]
rep = 50
r = 20

cap_title = f'cap_fig_user={usr_list[0]}~{usr_list[-1]}_radius={r}_rep={rep}'
sn_title = f'sn_fig_user={usr_list[0]}~{usr_list[-1]}_radius={r}_rep={rep}'
intf_title = f'intf_fig_user={usr_list[0]}~{usr_list[-1]}_radius={r}_rep={rep}'
# generate_interference_SNR_SINR_figure_with_random_users(usr_list, 50, 20, cap_title, sn_title, intf_title)

# generate_user_distribution_of_max_min_interference(usr_list, rep, r, 'no_grouping')