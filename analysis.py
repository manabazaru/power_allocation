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
    fig.make_capacitys_fig_with_std(nu_list, rlt_dict, alg_list, f'capacitys_each_nu_r={r}_shp={shp}_nt={param.planar_antenna_size_of_side**2}')
    
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
                sinr = 10*np.log10(sig_arr / (intf_arr+ns_arr))
                # sinr = sig_arr / (intf_arr+ns_arr)
                sinr_arr[head:tail] = sinr
            sinrs_list[nu_idx] = sinr_arr
        rlt_dict[alg] = sinrs_list
    fig.make_SINR_figure(nu_list, alg_list, rlt_dict, f'SINR(notdB)_each_nu_r={r}_shp={shp}_alg={alg_list}_Nt={param.planar_antenna_size_of_side}')

# 2023/12/03
def generate_cumulative_cap(typ, nu, r, shp, dsidx_list, alg_list, t_pwr, sim_idx_dict, x_lim, x_range):
    ds_size = len(dsidx_list)
    ds_list = [None for i in range(ds_size)]
    for i, dsidx in enumerate(dsidx_list):
        ds = simulation.Dataset(typ, nu, r, shp, dsidx)
        ds_list[i] = ds
    caps_list = []
    for alg in alg_list:
        cap_list = []
        sim_idx = sim_idx_dict[alg]
        for ds in ds_list:
            sim = simulation.Simulation(ds, t_pwr, alg, sim_idx)
            sim.execute_all()
            cap = sim.get_cap_arr()
            cap_list.append(cap)
        cap_arr = np.array(cap_list)
        row, col = cap_arr.shape
        new_cap_arr = cap_arr.reshape(row*col)
        print(f"{alg}: {min(new_cap_arr)}")
        caps_list.append(new_cap_arr)
    fig.make_cumulative_figures(caps_list, alg_list, f'cumulative_capacity_r={r}_typ={typ}_shp={shp}_alg={alg_list}_nt={param.planar_antenna_size_of_side**2}', x_lim, x_range, True)

def generate_flop_table(nu_list, grp_n, r, shp, dsidx, alg_list, t_pwr, sim_idx_dict):
    ds_list = [None for i in range(len(nu_list))]
    for nu_idx, nu in enumerate(nu_list):
        ds = simulation.Dataset('random'+str(nu*grp_n), nu, r, shp, dsidx)
        ds_list[nu_idx] = ds
    data_list = []
    row0 = ['']
    row0.extend([f'Nu = {i}' for i in nu_list])
    for alg in alg_list:
        if 'ACUS' in alg: new_alg = f'ACUS (M = {alg[4:]})'
        else: new_alg = alg
        rowi = [new_alg]
        sim_idx = sim_idx_dict[alg]
        for ds in ds_list:
            sim = simulation.Simulation(ds, t_pwr, alg, sim_idx)
            sim.execute_grouping()
            flop = sim.get_flop_arr()
            print(flop)
            flop = int(flop[-1])
            flop_str = '{:.3e}'.format(flop)
            rowi.append(flop_str)
        data_list.append(rowi)
    data_arr = np.array(data_list)
    fig.make_flop_table(data_arr, row0, f'flop_table_nu={nu_list}_r={r}_alg={alg_list}')

        


def execute():
    path.set_cur_dir()
    # generate_tokyo_heatmap()
    alg_list =['ACUS3']
    sim_idx_dict = {}
    for alg in alg_list: sim_idx_dict[alg] = 0
    # sim_idx_dict['RUS'] = 1 
    nu_list = [i for i in range(10, 105, 10)]
    grp_dict = {}
    grp_n = 100
    for nu in nu_list:
        grp_dict[nu] = grp_n
    generate_sinr_figure_with_random(100, nu_list, grp_dict, 'c', [0,1], 120, alg_list, sim_idx_dict)
    generate_nu_cap_figures_with_random([100], nu_list, grp_dict, 'c', [0,1], 120, alg_list, sim_idx_dict)
    x_lim_list = [[3, 4], [4, 10], [0, 0.01]]
    x_range_list = [0.2, 0.5, 0.001]
    for nu_idx, nu in enumerate(nu_list):
        typ = 'random'+str(nu*grp_n)
        # generate_cumulative_cap(typ, 100, 20, 'p', [i for i in range(4)], alg_list, 120, sim_idx_dict, x_lim_list[nu_idx], x_range_list[nu_idx])
    cities = ['tokyo', 'sendai', 'nagoya', 'osaka']
    # generate_flop_table([20, 40, 60, 80], 100, 20, 'p', 0, alg_list, 120, sim_idx_dict)
    # for city in cities:
        # generate_cumulative_cap(city, 20, 20, 'p', [0], alg_list, 120, sim_idx_dict, [0, 5], 0.2)

    
execute()