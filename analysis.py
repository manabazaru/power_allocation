import load
import save
import fig
import fig_properties
import utils
import simulation
import path
import haps
import beamforming
import rand_uni
from parameters import Parameter as param
from us_equipment import AUSEquipment
import numpy as np
from us_equipment import AUSEquipment

# 2023/11/23
# generate heatmap of tokyo whose radius list is [20, 50, 100]
def generate_tokyo_heatmap():
    block_n = 50
    r_list = [20, 50, 100]
    for r in r_list:
        sim = simulation.Dataset('tokyo', 12, r, 'p', 0)
        sim.setup_xy()
        xy_arr = sim.get_xy()
        blk_pop = utils.get_heatmap_data_from_xy_arr(xy_arr, block_n, r)
        fig.heatmap(r, blk_pop, f'heatmap of Tokyo (r={r})', True)
        fig.plt_all_users(xy_arr)

def generate_SINR_markers(typ, nu, r, shp, dsidx, alg_list, t_pwr):
    ds = simulation.Dataset(typ, nu, r, shp, dsidx)
    ds.setup_xy()
    ds.setup_eqpt()
    eqpt: AUSEquipment = ds.get_eqpt()
    xy_arr = ds.get_xy()
    print(xy_arr.shape)
    xy_arr = np.delete(xy_arr, eqpt.rm_usr_arr, axis=0)
    SINR_dB_max = 0
    SINR_dB_min = 100000000
    SINR_dB_arr_list = []
    for alg in alg_list:
        sim = simulation.Simulation(ds, t_pwr, alg, 0)
        sim.execute_all()
        sig_arr = sim.get_sig_arr()
        intf_arr = sim.get_intf_arr()
        ns_arr = sim.get_noise_arr()
        SINR_arr = sig_arr / (intf_arr + ns_arr)
        SINR_dB_arr = 10 * np.log10(SINR_arr)
        s_max = np.max(SINR_dB_arr)
        s_min = np.min(SINR_dB_arr)
        if s_max > SINR_dB_max: SINR_dB_max = s_max 
        if s_min < SINR_dB_min: SINR_dB_min = s_min
        SINR_dB_arr_list.append(SINR_dB_arr)
    for i, alg in enumerate(alg_list):
        fig.save_plt_users_with_colorbar(xy_arr, f'SINR[dB] (alg={alg})', SINR_dB_arr_list[i], 
                                         SINR_dB_max, SINR_dB_min, r)

def show_urban_intf():
    com_n = 10
    urban_n = 50
    com_xy = rand_uni.generate_random_usr_xy_in_donut_erea(com_n, 50, 100)
    urban_xy = rand_uni.generate_random_uniform_usr_xy(urban_n, 50)
    com_ang = utils.xy2ang(com_xy, -param.z)
    urban_ang = utils.xy2ang(urban_xy, -param.z)
    ang_arr = np.concatenate([com_ang, urban_ang])
    eqpt = AUSEquipment(ang_arr, 10)
    hap = haps.CyrindricalHAPS()
    ua_angr_arr = hap.get_user_antenna_angle_r_arr(eqpt)
    com_ua = ua_angr_arr[:com_n]
    urban_ua = ua_angr_arr[com_n:]
    bfzf = beamforming.ZeroForcing(com_ua)
    bf = beamforming.BeamForming(urban_ua)
    bf.set_h()
    com_h = bfzf.get_h()
    com_w = bfzf.get_w()
    urban_h = bf.get_h()
    print(np.dot(com_h, com_w))
    h = np.concatenate([com_h, urban_h])
    w = np.concatenate([com_w, np.zeros([com_w.shape[0], urban_n])], axis=1)
    hw = np.dot(h, w)
    # for i in range(com_n+2):
        # print(hw[i,:10])
    sum_arr = np.sum(hw, axis=1)

# show_urban_intf()

# 2023/11/26
def generate_nu_cap_figure_with_random(r, nu_list, grp_n_dict, shp, dsidx_list, t_pwr, alg_list, sim_idx_dict):
    dsidx_size = len(dsidx_list)
    nu_size = len(nu_list)
    # ds is in order of nu
    ds_list = [[] for i in range(nu_size)]
    max_grp_n = 0
    for nu_idx, nu in enumerate(nu_list):
        grp_n = grp_n_dict[nu]
        if max_grp_n < grp_n: max_grp_n = grp_n
        typ = 'random' + str(int(nu*grp_n))
        for dsidx in dsidx_list:
            ds = simulation.Dataset(typ, nu, r, shp, dsidx)
            ds_list[nu_idx].append(ds)
    
    # dictionary of capacity_data of each algorithm (key: alg)
    rlt_dict = {}
    for alg in alg_list:
        sim_idx = sim_idx_dict[alg]
        # cap_arr: capacity array of all nu situation (nu_size, number of groups)
        cap_arr = np.zeros([nu_size, int(max_grp_n*dsidx_size)])
        for nu_idx in range(nu_size):
            nu = nu_list[nu_idx]
            grp_n = grp_n_dict[nu]
            for dsidx_idx in range(dsidx_size):
                ds = ds_list[nu_idx][dsidx_idx]
                sim = simulation.Simulation(ds, t_pwr, alg, sim_idx)
                sim.execute_all()
                head = int(dsidx_idx*grp_n)
                tail = int((dsidx_idx+1)*grp_n)
                cap_arr[nu_idx, head:tail] = np.array(sim.get_cap_arr())
        rlt_dict[alg] = cap_arr
    fig.make_capacitys_fig_with_std(nu_list, rlt_dict, alg_list, f'capacitys_each_nu_r={r}_shp={shp}')
    
def generate_nu_cap_figures_with_random(r_list, nu_list, grp_n_dict, shp_list, dsidx_list, t_pwr, alg_list, sim_idx_dict):
    for r in r_list:
        for shp in shp_list:
            generate_nu_cap_figure_with_random(r, nu_list, grp_n_dict, shp, dsidx_list, t_pwr, alg_list, sim_idx_dict)

def generate_sinr_figure_with_random(r, nu_list, grp_n_dict, shp, dsidx_list, t_pwr, alg_list, sim_idx_dict):
    dsidx_size = len(dsidx_list)
    nu_size = len(nu_list)
    # ds is in order of nu
    ds_list = [[] for i in range(nu_size)]
    max_grp_n = 0
    for nu_idx, nu in enumerate(nu_list):
        grp_n = grp_n_dict[nu]
        if max_grp_n < grp_n: max_grp_n = grp_n
        typ = 'random' + str(int(nu*grp_n))
        for dsidx in dsidx_list:
            ds = simulation.Dataset(typ, nu, r, shp, dsidx)
            ds_list[nu_idx].append(ds)
    
    # dictionary of capacity_data of each algorithm (key: alg)
    rlt_dict = {}
    for alg in alg_list:
        sim_idx = sim_idx_dict[alg]
        # cap_arr: capacity array of all nu situation (nu_size, number of groups)
        sinrs_list = [[] for i in range(nu_size)]
        for nu_idx in range(nu_size):
            nu = nu_list[nu_idx]
            grp_n = grp_n_dict[nu]
            nuk = nu * grp_n
            sinr_arr = np.zeros(int(nuk*dsidx_size))
            for dsidx_idx in range(dsidx_size):
                ds = ds_list[nu_idx][dsidx_idx]
                sim = simulation.Simulation(ds, t_pwr, alg, sim_idx)
                sim.execute_all()
                head = int(dsidx_idx*nuk)
                tail = int((dsidx_idx+1)*nuk)
                sig_arr = np.array(sim.get_sig_arr())
                intf_arr = np.array(sim.get_intf_arr())
                ns_arr = np.array(sim.get_noise_arr())
                # sinr = 10*np.log10(sig_arr / (intf_arr+ns_arr))
                sinr = sig_arr / (intf_arr+ns_arr)
                sinr_arr[head:tail] = sinr
            sinrs_list[nu_idx] = np.log2(sinr_arr) * nu
        rlt_dict[alg] = sinrs_list
    fig.make_SINR_figure(nu_list, alg_list, rlt_dict, f'SINR_each_nu_r={r}_shp={shp}_alg={alg_list}_Nt={param.planar_antenna_size_of_side}')

def execute():
    path.set_cur_dir()
    # generate_tokyo_heatmap()
    alg_list =['ACUS3', 'ACUS6', 'AUS', 'RUS']
    sim_idx_dict = {}
    for alg in alg_list: sim_idx_dict[alg] = 0 
    nu_list = [i for i in range(20, 200, 20)]
    grp_dict = {}
    grp_n = 100
    for nu in nu_list:
        grp_dict[nu] = grp_n
    generate_sinr_figure_with_random(20,
                                     nu_list,
                                     grp_dict,
                                     'p',
                                     [0,1],
                                     120,
                                     alg_list,
                                     sim_idx_dict)

execute()