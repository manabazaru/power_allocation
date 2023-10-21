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

path.set_cur_dir()
np.set_printoptions(threshold=np.inf)

def test_AUS(city):
    start = 0
    end = 50
    filename = 'AUS' + city
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr)
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


def test_MRUS(city, M):
    start = 0
    end = 50
    filename = 'MRUS' + city + '_' + str(M)
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr)
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


def test_MRUS2(city, M):
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr)
    mrus = grouping.MRangeAUS(eqpt, M)
    add = mrus.calc_add_flops()
    mult = mrus.calc_multiple_flops()
    comp = mrus.calc_compare_flops()
    total = mrus.calc_all_flops()
    print('MRUS:', city, 'M = ', M, 'add:',add, 'mult:', mult, 'comp:', comp, 'total:', total)

def evaluate_users_in_line(user_n):
    file_tag = f'in_line_user={user_n}'
    xy_arr = location.generate_user_xy_in_line(user_n, 20)
    angr_arr = utils.xyz2angr(utils.xy2xyz(xy_arr, -param.z))
    ang_arr = utils.angr2ang(angr_arr)
    eqpt = AUSEquipment(ang_arr)
    nogroup = grouping.NoGrouping(eqpt)
    group_table = nogroup.get_group_table()
    sorted_list = nogroup.get_sorted_min_ad_list()
    haps = phaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    ev = eval(group_table, sorted_list, usr_ant_angr)
    cap_list = ev.get_sum_cap_arr()
    save.save_angle_arr(ang_arr, file_tag)
    save.save_group_table(group_table, 'no_grouping', file_tag)
    save.save_eval_arr(cap_list, file_tag)

def evaluate_users_on_circle(user_n, radius):
    file_tag = f'in_circle_user={user_n}_radius={radius}'
    xy_arr = location.generate_user_xy_on_circle(user_n, radius)
    angr_arr = utils.xyz2angr(utils.xy2xyz(xy_arr, -param.z))
    ang_arr = utils.angr2ang(angr_arr)
    eqpt = AUSEquipment(ang_arr)
    nogroup = grouping.NoGrouping(eqpt)
    group_table = nogroup.get_group_table()
    sorted_list = nogroup.get_sorted_min_ad_list()
    haps = phaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    ev = eval(group_table, sorted_list, usr_ant_angr)
    cap_list = ev.get_sum_cap_arr()
    # print(f"""****************cap_list****************\n{cap_list}\n""")
    print(f"""****************SINR****************\n{ev.get_SINR()}\n""")
    save.save_angle_arr(ang_arr, file_tag)
    save.save_group_table(group_table, 'no_grouping', file_tag)
    save.save_eval_arr(cap_list, file_tag)

def evaluate_users_in_circle(user_n, radius, layer_num):
    file_tag = f'in_circle2_user={user_n*layer_num}_radius={radius}_layer={layer_num}'
    for layer_idx in range(layer_num):
        l_radius = (layer_idx+1) * (radius/layer_num)
        xy_l_arr = location.generate_user_xy_on_circle(user_n, l_radius)
        if layer_idx == 0:
            xy_arr = xy_l_arr
        else:
            xy_arr = np.concatenate([xy_arr, xy_l_arr])
    fig.plt_all_users(xy_arr)
    angr_arr = utils.xyz2angr(utils.xy2xyz(xy_arr, -param.z))
    ang_arr = utils.angr2ang(angr_arr)
    eqpt = AUSEquipment(ang_arr)
    nogroup = grouping.NoGrouping(eqpt)
    group_table = nogroup.get_group_table()
    sorted_list = nogroup.get_sorted_min_ad_list()
    haps = phaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    ev = eval(group_table, sorted_list, usr_ant_angr)
    cap_list = ev.get_sum_cap_arr()
    # print(f"""****************cap_list****************\n{cap_list}\n""")
    print(f"""****************SINR****************\n{ev.get_SINR()}\n""")
    save.save_angle_arr(ang_arr, file_tag)
    save.save_group_table(group_table, 'no_grouping', file_tag)
    save.save_eval_arr(cap_list, file_tag)

layer = 5
evaluate_users_in_circle(param.users_per_group//layer, 20, layer)
"""
for r in [5,10,15,20]:
    evaluate_users_on_circle(user_n=param.users_per_group, radius=r)
"""
def print_eval_MRUS(usr_n):
    xy_arr = rand_uni.generate_random_uniform_usr_xy(usr_n, 50)
    angr_arr = utils.xyz2angr(utils.xy2xyz(xy_arr, -param.z))
    ang_arr = utils.angr2ang(angr_arr)
    eqpt = AUSEquipment(ang_arr)
    mrus = grouping.MRangeAUS(eqpt, 3)
    mrus.execute()
    group_table = mrus.get_group_table()
    sorted_min_ad_arr = mrus.get_sorted_min_ad_list()
    haps = phaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    ev = eval(group_table, sorted_min_ad_arr, usr_ant_angr)
    cap_list = ev.get_sum_cap_arr()
    save.save_eval_arr(cap_list, 'random_12_12')
    usr_per_group = param.users_per_group
    capacity = cap_list[int(usr_n/usr_per_group/2)]
    print(f"capacity: {capacity}, cap_per_user: {capacity/usr_per_group}")
    return capacity

def print_n_eval_MRUS(usr_n, n):
    med_cap_list = []
    for i in range(n):
        med_cap = print_eval_MRUS(usr_n)
        med_cap_list.append(med_cap)
    print("****************FINAL RESULTS********************")
    sorted_cap_list = sorted(med_cap_list)

    for i in range(n):
        print(f"{i}: {sorted_cap_list[i]}")
    median = sorted_cap_list[n//2]
    print(f"********median**********\nmedian: {median}")


def test_SAUS():
    city = 'tokyo'
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr)
    saus = grouping.SerialAUS(eqpt)
    saus.init_group_table()
    saus.execute()
    group_table = saus.get_group_table()
    for group in range(len(group_table)):
        print(group, group_table[group])
    saus.set_min_ad_all()
    saus.set_sorted_min_ad_list()
    saus.print_group_info(0,100)

def test_SerialSlideAUS(city):
    city_th = param.city_threshold_ad[city]
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr)
    ssaus = grouping.SerialSlideAUS(eqpt, city_th)
    ssaus.execute()
    ssaus.set_min_ad_all()
    group_table = ssaus.get_group_table()
    sorted_min_ad_arr = ssaus.get_sorted_min_ad_list()
    haps = chaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    save.save_user_HAPS_angle(usr_ant_angr, 'cylindrical', 'SSAUS')
    ev = eval(group_table, sorted_min_ad_arr, usr_ant_angr)
    cap_list = ev.get_sum_cap_arr()
    save.save_eval_arr(cap_list, 'SSAUS_'+city)

def test_AUSwithSampling(city):
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr)
    ssaus = grouping.ASUSwithSampling(eqpt)
    ssaus.execute()
    ssaus.set_min_ad_all()
    add = ssaus.add
    mult = ssaus.mult
    comp = ssaus.comp
    print(f"""
city: {city},
add: {add},
mult: {mult},
comp: {comp},
    """)
    group_table = ssaus.get_group_table()
    sorted_min_ad_arr = ssaus.get_sorted_min_ad_list()
    haps = chaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    save.save_user_HAPS_angle(usr_ant_angr, 'cylindrical', 'SSAUS')
    ev = eval(group_table, sorted_min_ad_arr, usr_ant_angr)
    cap_list = ev.get_sum_cap_arr()
    save.save_eval_arr(cap_list, 'SAUSS_'+city)


def test_SerialSlideAUS2(city):
    city_th = param.city_threshold_ad[city]
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr)
    all_xy = utils.xyz2xy(utils.angr2xyz(utils.ang2angr_with_z(eqpt.get_ang_all(), -param.z)))
    ssaus = grouping.SerialSlideAUS2(eqpt, city_th)
    ssaus.execute()
    ssaus.set_min_ad_all()
    ssaus.set_sorted_min_ad_list()
    ssaus.print_group_info_all()
    unapp_usrs = ssaus.get_unappropriate_users()
    usr_angs = eqpt.get_angs(unapp_usrs)
    usr_angrs = utils.ang2angr_with_z(usr_angs, -param.z)
    usr_xyz = utils.angr2xyz(usr_angrs)
    usr_xy = utils.xyz2xy(usr_xyz)
    fig.plt_all_users(all_xy)
    fig.plt_all_users(usr_xy)

def test_AUS2(city):
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr)
    aus = grouping.AUS(eqpt)
    aus.execute()
    add = aus.calc_add_flops()
    mult = aus.calc_multiple_flops()
    comp = aus.calc_compare_flops()
    total = aus.calc_all_flops()
    print('AUS:', city, 'add:',add, 'mult:', mult, 'comp:', comp, 'total:', total)
    print('add', add)
    print('mult', mult)
    print('comp', comp)
    print('total', total)    

def test_AUS3(city, sample_n_list, rep_n):
    ang_arr = load.load_angle(city)
    print("[INFO AUS] This is AUS sampling test.\n")
    iter_arr = np.arange(len(ang_arr), dtype=int)
    aus_list = [[] for i in range(len(sample_n_list))]
    for sample_iter in range(len(sample_n_list)):
        sample_n = sample_n_list[sample_iter]
        print(f"[INFO AUS] User size: {sample_n}")
        for i in range(rep_n):
            new_usr_arr = np.random.choice(iter_arr, 
                                           sample_n,
                                           replace=False)
            new_ang_arr = ang_arr[new_usr_arr]
            eqpt = AUSEquipment(new_ang_arr)
            aus = grouping.AUS(eqpt)
            aus.execute()
            aus_list[sample_iter].append(aus)
    min_arr = np.zeros([len(sample_n_list), rep_n])
    ave_arr = np.zeros([len(sample_n_list), rep_n])
    max_arr = np.zeros([len(sample_n_list), rep_n])
    print(aus_list)
    for sample_iter in range(len(sample_n_list)):
        for iter in range(len(aus_list[sample_iter])):
            aus = aus_list[sample_iter][iter]
            minad = aus.sorted_min_ad_list[1,0]
            maxad = aus.sorted_min_ad_list[1, -1]
            avead = np.average(aus.sorted_min_ad_list[1])
            min_arr[sample_iter][iter] = minad
            max_arr[sample_iter][iter] = maxad
            ave_arr[sample_iter][iter] = avead
        print(f'<sample size: {sample_n_list[sample_iter]}')
        min_ave = np.average(min_arr[sample_iter])
        ave_ave = np.average(ave_arr[sample_iter])
        max_ave = np.average(max_arr[sample_iter])
        arrays = [min_arr[sample_iter], 
                  ave_arr[sample_iter], 
                  max_arr[sample_iter]]
        aves = [min_ave, ave_ave, max_ave]
        names = ['min', 'ave', 'max']
        for i in range(len(names)):
            arr = arrays[i]
            ave = aves[i]
            name = names[i]
            print(f' ({name})')
            print(f' average: {ave}')
            print(f' {arr}')
            print()



# test_SerialSlideAUS(city)
# SerialSlideAUS 
#  osaka: 2/353, tokyo: 8/578, sendai: 40/604, nagoya: 70/1914
# test_AUS2(city)
"""
city = 'tokyo'
m_list = np.arange(6, 9, dtype=int)
for m in m_list:
    test_MRUS(city, m)

cities = prop.cities
new_city_list = cities.remove('yagami')
new_city_list = cities.remove('tokyo')
m_list = np.arange(5,dtype=int)
for city in new_city_list:
    for m in m_list:
        test_MRUS(city, m)
"""

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

# make_eval_fig('nagoya', [1, 3,5])

def test_SAUSS_randomness(city, rep):
    title = f'system_capacity_of_several_SAUSS_result({city})'
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr)
    haps = chaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    data_dict = {}
    alg_list = []
    eval_list = []
    cap_arr_list = []
    sinr_arr_list = []
    for i in range(rep):
        alg_name = 'SSAUS_' + str(i)
        sauss = grouping.ASUSwithSampling(eqpt)
        sauss.execute()
        sauss_group = sauss.get_group_table()
        sauss_sorted_arr = sauss.get_sorted_min_ad_list()
        data_dict[alg_name] = [sauss_group, sauss_sorted_arr]
        alg_list.append(alg_name)
    for alg_iter in range(len(alg_list)):
        alg_name = alg_list[alg_iter]
        data = data_dict[alg_name]
        ev = eval(data[0], data[1], usr_ant_angr)
        eval_list.append(ev)
        sinr_list = ev.get_SINR()
        sinr_arr_list.append(sinr_list)
        cap_list = ev.get_sum_cap_arr()
        cap_arr_list.append(cap_list)
        save.save_sinr_arr(sinr_list, alg_name)
        save.save_eval_arr(cap_list, alg_name)
    figure = fig.make_cumulative_figures(cap_arr_list, alg_list, title, True)

def make_SINR_fig(city, m_val_list):
    title = 'SINR_' + city
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr)
    haps = chaps()
    usr_ant_angr = haps.get_user_antenna_angle_r_arr(eqpt)
    # 以下, 加えたいアルゴリズムを追加
    data_dict = {}
    alg_list = []
    eval_list = []
    sinr_arr_list = []
    # AUS
    alg_name = 'AUS_' + city
    aus = grouping.AUS(eqpt)
    aus.execute()
    aus_group = aus.get_group_table()
    aus_sorted_arr = aus.get_sorted_min_ad_list()
    data_dict[alg_name] = [aus_group, aus_sorted_arr]
    alg_list.append(alg_name)
    # MRUS
    for m in m_val_list:
        alg_name = 'MRUS_' + city + '_' + str(m)
        mrus = grouping.MRangeAUS(eqpt, m)
        mrus.execute()
        mrus_group = mrus.get_group_table()
        mrus_sorted_arr = mrus.get_sorted_min_ad_list()
        data_dict[alg_name] = [mrus_group, mrus_sorted_arr]
        alg_list.append(alg_name)
    # SAUSS
    alg_name = 'SAUSS_' + city
    sauss = grouping.ASUSwithSampling(eqpt)
    sauss.execute()
    sauss_group = sauss.get_group_table()
    sauss_sorted_arr = sauss.get_sorted_min_ad_list()
    data_dict[alg_name] = [sauss_group, sauss_sorted_arr]
    alg_list.append(alg_name)
    for alg_iter in range(len(alg_list)):
        alg_name = alg_list[alg_iter]
        data = data_dict[alg_name]
        ev = eval(data[0], data[1], usr_ant_angr)
        eval_list.append(ev)
        sinr_list = ev.get_SINR()
        sinr_arr_list.append(sinr_list)
        cap_list = ev.get_sum_cap_arr()
        save.save_sinr_arr(sinr_list, alg_name)
        save.save_eval_arr(cap_list, alg_name)
    figure = fig.make_cumulative_SINR(sinr_arr_list, alg_list, title, True)

def make_SINR_fig_from_eval(city, m0, mend):
    alg_list = []
    sinr_arr_list = []
    title = 'SINR_' + city
    alg_list.append('AUS_'+city)
    alg_list.append('SAUSS_'+city)
    for m in range(m0, mend+1):
        alg_list.append('MRUS_'+city+'_'+str(m))
    for alg in alg_list:
        sinr_arr = load.load_sinr(alg)
        sinr_arr_list.append(sinr_arr)
    figure = fig.make_cumulative_SINR(sinr_arr_list, alg_list, title, True)

def make_minAD_fig(city, m_val_list):
    title = 'minAD_' + city
    ang_arr = load.load_angle(city)
    eqpt = AUSEquipment(ang_arr)
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

"""
cities = prop.main_cities
for city in cities:
    make_SINR_fig(city, 1, 5)
for city in prop.main_cities:
    xy_arr = load.load_xy(city)
    block_pop = utils.get_heatmap_data_from_xy_arr(xy_arr, 40, 20)
    fig.heatmap(block_pop, 'heatmap_'+city, True)
"""