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

# bs_xy_arr = np.array([[(10+5*i)*np.cos(np.pi*2/8*i), (10+5*i)*np.sin(np.pi*2/8*i)] for i in range(8)])
bs_xy_arr = np.array([[2,0], [0, 7], [-12, 0], [0,-17]])
new_bs_xy_arr = np.zeros([len(bs_xy_arr),2])
new_bs_xy_arr[:,0] = bs_xy_arr[:,1]
new_bs_xy_arr[:,1] = bs_xy_arr[:,0]
# fig.save_plt_all_users2(new_bs_xy_arr, 'bs_style1', 50)
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
    for i in range(1):
        group_xy_arr = xy_arr[group_table[i]]
        fig.save_plt_all_users2(group_xy_arr, "AUS_user_group_idx="+str(i), radius)
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
test_AUS(1200, 12, 20)
# test_AUS(1200, 12, 100)

def test_AUS2(city, usrs_per_group):
    ang_arr = load.load_angle(city)
    filename = f'AUS_planar_{city}_usrs_per_group={usrs_per_group}'
    eqpt = AUSEquipment(ang_arr, usrs_per_group)
    usr_n = eqpt.get_usr_n()
    start = 0
    end = 20
    aus = grouping.AUS(eqpt)
    aus.execute()
    aus.print_group_info(start, end)
    group_table = aus.get_group_table()
    haps = phaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    # save.save_user_HAPS_angle(usr_ant_angr, 'cylindrical', 'random')
    ev = eval(group_table, usr_ant_angr, param.trans_pwr)
    cap_list = ev.get_sum_cap_arr()
    save.save_eval_arr(cap_list, filename)

def test_RUS(city, usrs_per_group):
    ang_arr = load.load_angle(city)
    filename = f'RUS_planar_{city}_usrs_per_group={usrs_per_group}'
    eqpt = AUSEquipment(ang_arr, usrs_per_group)
    usr_n = eqpt.get_usr_n()
    start = 0
    end = 20
    aus = grouping.RUS(eqpt)
    aus.execute()
    aus.print_group_info(start, end)
    group_table = aus.get_group_table()
    haps = phaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    # save.save_user_HAPS_angle(usr_ant_angr, 'cylindrical', 'random')
    ev = eval(group_table, usr_ant_angr, param.trans_pwr)
    cap_list = ev.get_sum_cap_arr()
    # save.save_eval_arr(cap_list, filename)
    # fig.make_cumulative_figures(np.array([cap_list]), ['RUS'], "fig_for_20231026", True)

def test_RUS_with_random(usr_n, radius, usrs_per_group):
    xy_arr = rand_uni.generate_random_uniform_usr_xy(usr_n, radius)
    ang_arr = utils.xy2ang(xy_arr, -param.z)
    # filename = f'RUS_planar_{city}_usrs_per_group={usrs_per_group}'
    eqpt = AUSEquipment(ang_arr, usrs_per_group)
    usr_n = eqpt.get_usr_n()
    # start = 0
    # end = 20
    aus = grouping.RUS(eqpt)
    aus.execute()
    # aus.print_group_info(start, end)
    group_table = aus.get_group_table()
    haps = chaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    # save.save_user_HAPS_angle(usr_ant_angr, 'cylindrical', 'random')
    ev = eval(group_table, usr_ant_angr, param.trans_pwr)
    # print(ev.cond_list)
    # print("average", np.average(ev.cond_list))
    # print("median", np.median(ev.cond_list))
    cap_list = ev.get_sum_cap_arr()
    # save.save_eval_arr(cap_list, filename)
    fig.make_cumulative_figures(np.array([cap_list]), ['RUS'], "fig_for_20231026", [0,1.8], 0.2, False)
    return ev.cond_list

# test_RUS_with_random(12000, 50, 12)
"""nu = 12
usr = 1200
r = 50
att = 10
grp_n = usr//nu
cond_arrs = np.zeros(grp_n*att)
for i in range(att):
    head = i*grp_n
    cond_arrs[head:head+grp_n] = test_RUS_with_random(usr, r, nu)
print(f"average: {np.average(cond_arrs)}")
print(f"median:  {np.median(cond_arrs)}")"""
"""
y_list = []
label_list = [i for i in range(10, 50, 2)]
start = 10
end = 70
step = 10
rep = 100
r = 5
for usr_n in range(start, end, step):
    test_RUS_with_random(usr_n*rep, r, usr_n)
    with open(f'test_{usr_n}_r={r}_nt={param.planar_antenna_size_of_side**2}.txt', 'r') as f:
        txt = f.readlines()
        total = 0
        abs_list = []
        for i in range(len(txt)):
            num = float(txt[i])
            total+=num
            abs_list.append(num)
        ave = num/len(txt)
        med = statistics.median(abs_list)
        y_list.append(med)
import matplotlib.pyplot as plt
y_list = np.array(y_list)
# y_list = y_list / y_list[0]
# y_list = np.log2(1/y_list)
for i in range(len(y_list)):
    y = y_list[i]
    print(label_list[i], ': ', y)
plt.plot([i for i in range(start, end, step)], y_list)
plt.show()"""

# test_AUS(1200, 12, 100)
# test_RUS(1200, 12, 100)

def test_MRUS_with_random(usr_n, usrs_per_group, radius, M):
    start = 0
    end = usr_n//usrs_per_group-1
    filename = 'MRUS_planar_random_usrs_per_group=' + str(usrs_per_group) + '_' + str(M)
    xy_arr = rand_uni.generate_random_uniform_usr_xy(usr_n, radius)
    ang_arr = utils.xy2ang(xy_arr, -param.z)
    eqpt = AUSEquipment(ang_arr, usrs_per_group)
    mrus = grouping.MRangeAUS(eqpt, M)
    start_time = time.time()
    mrus.execute()
    end_time = time.time()
    mrus.print_group_info(start, end)
    print(f"Calculation time: {end_time-start_time}")
    group_table = mrus.get_group_table()
    for i in range(1):
        group_xy_arr = xy_arr[group_table[i]]
        fig.save_plt_all_users2(group_xy_arr, "ACUS4_user_group_idx="+str(i), radius)
    haps = chaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    # save.save_user_HAPS_angle(usr_ant_angr, 'cylinder', city)
    ev = eval(group_table, usr_ant_angr, param.trans_pwr)
    cap_list = ev.get_sum_cap_arr()
    save.save_eval_arr(cap_list, filename)
    # save.save_user_HAPS_angle(usr_ant_angr, 'planar', 'MRUS_tokyo')

test_MRUS_with_random(1200, 12, 20, 4)

def test_MRUS(city, M, usrs_per_group):
    start = 0
    end = 20
    filename = 'MRUS_planar_' + city + '_usrs_per_group=' + str(usrs_per_group) + '_' + str(M)
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr, usrs_per_group)
    mrus = grouping.MRangeAUS(eqpt, M)
    mrus.execute()
    mrus.print_group_info(start, end)
    mrus.printadave()
    group_table = mrus.get_group_table()
    haps = phaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    save.save_user_HAPS_angle(usr_ant_angr, 'planar', city)
    ev = eval(group_table, usr_ant_angr, param.trans_pwr)
    cap_list = ev.get_sum_cap_arr()
    save.save_eval_arr(cap_list, filename)
    # save.save_user_HAPS_angle(usr_ant_angr, 'planar', 'MRUS_tokyo')

def print_MRUS_flop(usr_n_list, m_val_list, group_n, r):
    m_size = len(m_val_list)
    rlt_list = [[] for i in range(m_size+1)]
    for usr_n in usr_n_list:
        usrs_per_group = int(usr_n/group_n)
        filename = f"random_user={usr_n}_r={r}_1"
        ang_arr = load.load_angle(filename)
        eqpt = AUSEquipment(ang_arr, usrs_per_group)
        for m_idx in range(m_size):
            m = m_val_list[m_idx]
            mrus = grouping.MRangeAUS(eqpt, m)
            flop_list = mrus.get_flop_list()
            rlt_list[m_idx].append(int(flop_list[-1]))
        aus = grouping.AUS(eqpt)
        aus.execute()
        flop_list = aus.get_flop_list()
        rlt_list[-1].append(int(flop_list[-1]))
    rlt_arr = np.array(rlt_list)
    print(rlt_arr)
    save.save_flop_arr(rlt_arr, 'test_MRUS_AUS')
# print_MRUS_flop([1800, 3600, 5400, 7200], [3,4,5], 100, 20)

def make_eval_fig(city, m_val_list):
    ds_types = []
    ds_types.append('RUS_' + city)
    ds_types.append('AUS_' + city)
    ds_types.extend(['MRUS_'+city+'_'+str(i) for i in m_val_list])
    eval_arr_list = []
    label_list = []
    label_list.append('RUS')
    label_list.append('AUS')
    label_list.extend([f'ACUS (M={str(i)})' for i in m_val_list])
    # label_list.append('AUS')
    title = 'system_capacity_' + city
    for ds_type in ds_types:
        eval_arr = load.load_eval(ds_type)
        eval_arr_list.append(eval_arr)
    figure = fig.make_cumulative_figures(eval_arr_list, label_list, title, True)

"""
for usr_per_group in range(12, 40, 12):    
    for m in range(3,6):
        title = f'planar_random_usrs_per_group={usr_per_group}'
        city = 'tokyo'
        test_MRUS(city, m, usr_per_group)
    test_AUS2(city, usr_per_group)
    test_RUS(city, usr_per_group)
    print(f"Now showing the situation of tokyo whose usrs_per_group={usr_per_group}")
    make_eval_fig(title, [3,4,5])
"""
"""
for usr_per_group in range(10, 60, 10):
    title = f'tokyo_usrs_per_group={usr_per_group}'
    make_eval_fig(title, [3,4,5])
"""

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
        save.save_group_minAD_arr(data, alg_name)
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
            haps = phaps()
            usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
            ev = eval(group_table, usr_ant_angr, param.trans_pwr)
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

# for interference/signal/noise figure reported on 2023/11/12
def generate_interference_signal_noise_figure_with_dif_usr(usr_n_list, rep, radius, x_label, y_label, 
                                                                  fig_title):
    usr_type_n = len(usr_n_list)

    sig_med_std_list = np.zeros([usr_type_n, 2])
    i_med_std_list = np.zeros([usr_type_n, 2])
    ns_med_std_list = np.zeros([usr_type_n, 2])
    for usr_type_idx, usrs_per_group in enumerate(usr_n_list):
        usr_n = usrs_per_group * rep
        filename = f'random_user={usr_n}_r={radius}'
        # ang_arr = load.load_angle(filename)
        # if ang_arr is None:
        xy_arr = rand_uni.generate_random_uniform_usr_xy(usr_n, radius)
        ang_arr = utils.xy2ang(xy_arr, -param.z)
        save.save_angle_arr(ang_arr, filename)
        eqpt = AUSEquipment(ang_arr, usrs_per_group)
        rus = grouping.RUS(eqpt)
        rus.execute()
        group_table = rus.get_group_table()
        haps = chaps()
        usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
        ev = eval(group_table, usr_ant_angr, param.trans_pwr)
        sig = ev.get_signal_pwr()
        intf = ev.get_interference()
        ns = ev.get_noise_pwr()
        save.save_group_table(group_table, 'no_grouping', filename)
        save.save_sig_arr(sig, filename)
        save.save_interference_arr(intf, filename)
        save.save_noise_arr(ns, filename)
        """else:
            sig = load.load_sig(filename)
            ns = load.load_noise(filename)
            intf = load.load_interference(filename)"""
        sig = 10*np.log10(sig*1000)
        ns = 10*np.log10(ns*1000)
        intf = 10*np.log10(intf*1000)
        sig_med_std_list[usr_type_idx] = np.array([statistics.median(sig), 
                                                  np.std(sig)])
        ns_med_std_list[usr_type_idx] = np.array([statistics.median(ns), 
                                                  np.std(ns)])
        i_med_std_list[usr_type_idx] = np.array([statistics.median(intf), 
                                                 np.std(intf)])
    fig.make_sig_intf_noise_figure(usr_n_list, 
                             sig_med_std_list[:,0],
                             sig_med_std_list[:,1],
                             i_med_std_list[:,0],
                             i_med_std_list[:,1],
                             ns_med_std_list[:,0],
                             ns_med_std_list[:,1],
                             x_label, y_label, fig_title)


# for interference/signal/noise figure for different distance reported on 2023/11/12
def generate_interference_signal_noise_figure_with_dif_r(r_list, rep, usrs_per_group, x_label, y_label, 
                                                                  fig_title):
    r_list_n = len(r_list)
    sig_med_std_list = np.zeros([r_list_n, 2])
    i_med_std_list = np.zeros([r_list_n, 2])
    ns_med_std_list = np.zeros([r_list_n, 2])
    for r_idx, r in enumerate(r_list):
        usr_n = usrs_per_group * rep
        filename = f'random_user={usr_n}_r={r}'
        ang_arr = load.load_angle(filename)
        # if ang_arr is None:
        xy_arr = rand_uni.generate_random_uniform_usr_xy(usr_n, r)
        ang_arr = utils.xy2ang(xy_arr, -param.z)
        save.save_angle_arr(ang_arr, filename)
        eqpt = AUSEquipment(ang_arr, usrs_per_group)
        rus = grouping.RUS(eqpt)
        rus.execute()
        group_table = rus.get_group_table()
        haps = chaps()
        usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
        ev = eval(group_table, usr_ant_angr, param.trans_pwr)
        sig = ev.get_signal_pwr()
        intf = ev.get_interference()
        ns = ev.get_noise_pwr()
        save.save_group_table(group_table, 'no_grouping', filename)
        save.save_sig_arr(sig, filename)
        save.save_interference_arr(intf, filename)
        save.save_noise_arr(ns, filename)
        # else:
            #sig = load.load_sig(filename)
            #ns = load.load_noise(filename)
            #intf = load.load_interference(filename)
        sig = 10*np.log10(sig*1000)
        ns = 10*np.log10(ns*1000)
        intf = 10*np.log10(intf*1000)
        sig_med_std_list[r_idx] = np.array([statistics.median(sig), 
                                                  np.std(sig)])
        ns_med_std_list[r_idx] = np.array([statistics.median(ns), 
                                                  np.std(ns)])
        i_med_std_list[r_idx] = np.array([statistics.median(intf), 
                                                 np.std(intf)])
    r_log10_list = np.log10(np.array(r_list))
    fig.make_sig_intf_noise_figure(r_log10_list, 
                             sig_med_std_list[:,0],
                             sig_med_std_list[:,1],
                             i_med_std_list[:,0],
                             i_med_std_list[:,1],
                             ns_med_std_list[:,0],
                             ns_med_std_list[:,1],
                             x_label, y_label, fig_title)

# for interference/signal/noise figure for different distance reported on 2023/11/12
def test_of_dif_r(r_list, rep, usrs_per_group, x_label, y_label, fig_title):
    r_list_n = len(r_list)
    sig_med_std_list = np.zeros([r_list_n, 2])
    i_med_std_list = np.zeros([r_list_n, 2])
    ns_med_std_list = np.zeros([r_list_n, 2])
    one_ang = np.pi*2/usrs_per_group
    xy_arr_unit = np.array([[np.cos(i*one_ang), np.sin(i*one_ang)] for i in range(usrs_per_group)])
    for r_idx, r in enumerate(r_list):
        usr_n = usrs_per_group * rep
        filename = f'random_user={usr_n}_r={r}'
        ang_arr = load.load_angle(filename)
        # if ang_arr is None:
        xy_arr = xy_arr_unit * r
        # xy_arr = rand_uni.generate_random_uniform_usr_xy(usr_n, r)
        ang_arr = utils.xy2ang(xy_arr, -param.z)
        save.save_angle_arr(ang_arr, filename)
        eqpt = AUSEquipment(ang_arr, usrs_per_group)
        rus = grouping.RUS(eqpt)
        rus.execute()
        group_table = rus.get_group_table()
        haps = phaps()
        usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
        ev = eval(group_table, usr_ant_angr, param.trans_pwr)
        sig = ev.get_signal_pwr()
        intf = ev.get_interference()
        ns = ev.get_noise_pwr()
        save.save_group_table(group_table, 'no_grouping', filename)
        save.save_sig_arr(sig, filename)
        save.save_interference_arr(intf, filename)
        save.save_noise_arr(ns, filename)
        # else:
            #sig = load.load_sig(filename)
            #ns = load.load_noise(filename)
            #intf = load.load_interference(filename)
        sig = 10*np.log10(sig*1000)
        ns = 10*np.log10(ns*1000)
        intf = 10*np.log10(intf*1000)
        sig_med_std_list[r_idx] = np.array([statistics.median(sig), 
                                                  np.std(sig)])
        ns_med_std_list[r_idx] = np.array([statistics.median(ns), 
                                                  np.std(ns)])
        i_med_std_list[r_idx] = np.array([statistics.median(intf), 
                                                 np.std(intf)])
    r_log10_list = np.log10(np.array(r_list))
    fig.make_sig_intf_noise_figure(r_log10_list, 
                             sig_med_std_list[:,0],
                             sig_med_std_list[:,1],
                             i_med_std_list[:,0],
                             i_med_std_list[:,1],
                             ns_med_std_list[:,0],
                             ns_med_std_list[:,1],
                             x_label, y_label, fig_title)


usr_list = [10*i for i in range(1,26)]
r_list = [10**i for i in range(-3, 5)]
rep = 10
r = 100
users_per_group = 2
style = 'median'


cap_title = f'cap_fig_user={usr_list[0]}~{usr_list[-1]}_radius={r}_rep={rep}'
sn_title = f'sn_fig_user={usr_list[0]}~{usr_list[-1]}_radius={r}_rep={rep}'
intf_title = f'intf_fig_user={usr_list[0]}~{usr_list[-1]}_radius={r}_rep={rep}'
sin_title_dif_usr = f'({style}_sin_fig_user={usr_list[0]}~{usr_list[-1]}_radius={r}_rep={rep}'
sin_title_dif_r = f'{style}_sin_fig_user={users_per_group}_radius={r_list[0]}~{r_list[-1]}_rep={rep}'
# generate_interference_SNR_SINR_figure_with_random_users(usr_list, 50, 20, cap_title, sn_title, intf_title)

# generate_user_distribution_of_max_min_interference(usr_list, rep, r, 'no_grouping')
# generate_interference_signal_noise_figure_with_dif_r(r_list, rep, users_per_group, 'log_10(L[km])', 'median dBm', sin_title_dif_r)
generate_interference_signal_noise_figure_with_dif_usr(usr_list, rep, r, 'users per group', 'median dBm', sin_title_dif_usr)
# test_of_dif_r(r_list, rep, users_per_group, 'log_10(L[km])', 'median dBm', 'test_' + sin_title_dif_r)