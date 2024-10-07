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
import statistics
import time

# 2023/11/23
# generate heatmap of tokyo whose radius list is [20, 50, 100]
def generate_tokyo_heatmap():
    block_n = 50
    r_list = [20]
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

def generate_maxNu_nt_fig(r, nu_list, nt_list, grp_n_dict, shp, dsidx_list, t_pwr, alg_list, sim_idx_dict):
    pass

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

# 2023/12/19 for analysing the cosine relativity
def generate_cos_relativity_between_h_in_random(r, nu_list, grp_n, dsidx_size, shp, t_pwr, alg_list, sim_idx):
    nu_size = len(nu_list)
    # generate dataset list
    ds_list = [[] for i in range(nu_size)]
    for nu_idx, nu in enumerate(nu_list):
        typ = 'random' + str(int(nu*grp_n))
        for ds_idx in range(dsidx_size):
            ds = simulation.Dataset(typ, nu, r, shp, ds_idx)
            ds_list[nu_idx].append(ds)
    
    # generate cos_relativity data
    data_dict = {}  # key is alg name
    for alg in alg_list:
        med_ang_arr = np.zeros(nu_size)
        std_ang_arr = np.zeros(nu_size)
        for nu_idx, nu in enumerate(nu_list):
            ang_arr = np.zeros(int(nu*grp_n*dsidx_size))
            ang_cnt = 0
            for ds in ds_list[nu_idx]:
                sim = simulation.Simulation(ds, t_pwr, alg, sim_idx)
                h_arr_list = sim.get_h_list()
                for h_arr in h_arr_list:
                    # compare [ai, -bi] to others ([aj, -bj] and [bj, aj])
                    nt = h_arr.shape[1]
                    new_h_arr = np.zeros([nu*2, nt*2])
                    ang_table = np.zeros([nu, nu*2]) + 3600
                    for h_idx, h in enumerate(h_arr):
                        h_real = h.real
                        h_imag = h.imag
                        new_h_arr[h_idx*2] = np.concatenate([h_real, -1*h_imag], 0)
                        new_h_arr[h_idx*2+1] = np.concatenate([h_imag, h_real], 0)
                    for h_idx in range(nu):
                        new_h_idx = h_idx * 2
                        new_h = new_h_arr[new_h_idx]
                        h_norm = sum(new_h**2) ** 0.5
                        for h2_idx in range(h_idx+1, nu):
                            new_h2_idx = h2_idx * 2
                            new_h2 = new_h_arr[new_h2_idx]
                            h2_norm = sum(new_h2**2) ** 0.5
                            h_h2 = sum(new_h * new_h2)
                            cos_theta = h_h2 / (h_norm * h2_norm)
                            theta = np.rad2deg(np.arccos(cos_theta))
                            ang_table[h_idx, new_h2_idx] = theta
                            ang_table[h2_idx, new_h_idx] = theta
                        for h2_idx in range(nu):
                            new_h2_idx = h2_idx * 2 + 1
                            new_h2 = new_h_arr[new_h2_idx]
                            h2_norm = sum(new_h2**2) ** 0.5
                            h_h2 = sum(new_h * new_h2)
                            cos_theta = h_h2 / (h_norm * h2_norm)
                            theta = np.rad2deg(np.arccos(cos_theta))
                            ang_table[h_idx, new_h2_idx] = theta
                        min_ang = min(ang_table[h_idx])
                        ang_arr[ang_cnt] = min_ang
                        ang_cnt += 1
            med_ang = statistics.median(ang_arr)
            std_ang = np.std(ang_arr)
            med_ang_arr[nu_idx] = med_ang
            std_ang_arr[nu_idx] = std_ang
        data_list = [med_ang_arr, std_ang_arr]
        data_dict[alg] = [med_ang_arr, std_ang_arr]
    fig.make_cos_relativity_figure(nu_list, alg_list, data_dict, f"cos_relativity_nu_list={nu_list[0]}~{nu_list[-1]}_r={r}_shp={shp}_size={grp_n*dsidx_size}")

# 2024/06/28
def generate_user_capacity_CDF(typ, nu, r_list, shp_list, dsidx_list, alg_list, t_pwr, sim_idx_dict, x_lim, x_range):
    sinr_arr_list = []
    label_list = []
    for r in r_list:
        # label of r
        if len(r_list) != 1:
            r_label = f'{r}km, '
        else:
            r_label = ''
        for shp in shp_list:
            # label of shape of antenna
            if len(shp_list) != 1:
                shp_label = 'Planar, ' if shp == 'p' else 'Cylinder, '
            else:
                shp_label = ''
            
            # generate dataset
            ds_list = []
            for dsidx in dsidx_list:
                ds = simulation.Dataset(typ, nu, r, shp, dsidx)
                ds_list.append(ds)
            for alg in alg_list:
                # label of alg
                if len(alg_list) != 1:
                    if 'ACUS' in alg or 'MRUS' in alg:
                        m = alg[4:]
                        alg_label = alg[:4] + f'(M={m})'
                    else:
                        alg_label = alg
                else:
                    alg_label = ''
                label = r_label + shp_label + alg_label
                if label[-1] == ' ':
                    label = label[:-2]
                
                # simulation
                sinr_list = []
                for ds in ds_list:
                    for sim_idx in range(sim_idx_dict[alg]+1):
                        sim = simulation.Simulation(ds, t_pwr, alg, sim_idx)
                        sim.execute_all()
                        sinr_arr = 10**(-6) * param.bandwidth * np.log2(1+sim.get_sig_arr() / (sim.get_intf_arr() + sim.get_noise_arr()))
                        sinr_list.append(sinr_arr)
                sinr_list = np.array(sinr_list).flatten()
                sinr_arr_list.append(sinr_list)
                label_list.append(label)
    fig.make_cumulative_SINR2(sinr_arr_list, label_list, f"user_capacity_CDF_typ={typ}_r={r_list}_shp={shp_list}_alg={alg_list}.png", x_lim, x_range, True)

# 2024/2/9
def generate_SINR_CDF(typ, nu, r_list, shp_list, dsidx_list, alg_list, t_pwr, sim_idx_dict, x_lim, x_range):
    sinr_arr_list = []
    label_list = []
    for r in r_list:
        # label of r
        if len(r_list) != 1:
            r_label = f'{r}km, '
        else:
            r_label = ''
        for shp in shp_list:
            # label of shape of antenna
            if len(shp_list) != 1:
                shp_label = 'Planar, ' if shp == 'p' else 'Cylinder, '
            else:
                shp_label = ''
            
            # generate dataset
            ds_list = []
            for dsidx in dsidx_list:
                ds = simulation.Dataset(typ, nu, r, shp, dsidx)
                ds_list.append(ds)
            for alg in alg_list:
                # label of alg
                if len(alg_list) != 1:
                    if 'ACUS' in alg or 'MRUS' in alg:
                        m = alg[4:]
                        alg_label = alg[:4] + f'(M={m})'
                    else:
                        alg_label = alg
                else:
                    alg_label = ''
                label = r_label + shp_label + alg_label
                if label[-1] == ' ':
                    label = label[:-2]
                
                # simulation
                sinr_list = []
                for ds in ds_list:
                    for sim_idx in range(sim_idx_dict[alg]+1):
                        sim = simulation.Simulation(ds, t_pwr, alg, sim_idx)
                        sim.execute_all()
                        sinr_arr = sim.get_sig_arr() / (sim.get_intf_arr() + sim.get_noise_arr())
                        sinr_list.append(10 * np.log10(sinr_arr))
                sinr_list = np.array(sinr_list).flatten()
                sinr_arr_list.append(sinr_list)
                label_list.append(label)
    fig.make_cumulative_SINR(sinr_arr_list, label_list, f"SINR_CDF_typ={typ}_r={r_list}_shp={shp_list}_alg={alg_list}.png", x_lim, x_range, True)

def generate_capacity_CDF(typ, nu, r_list, shp_list, dsidx_list, alg_list, t_pwr, sim_idx_dict, x_lim, x_range):
    cap_arr_list = []
    label_list = []
    for r in r_list:
        # label of r
        if len(r_list) != 1:
            r_label = f'{r}km, '
        else:
            r_label = ''
        for shp in shp_list:
            # label of shape of antenna
            if len(shp_list) != 1:
                shp_label = 'Planar, ' if shp == 'p' else 'Cylinder, '
            else:
                shp_label = ''
            
            # generate dataset
            ds_list = []
            for dsidx in dsidx_list:
                ds = simulation.Dataset(typ, nu, r, shp, dsidx)
                ds_list.append(ds)
            for alg in alg_list:
                # label of alg
                if len(alg_list) != 1:
                    if 'ACUS' in alg or 'MRUS' in alg:
                        m = alg[4:]
                        alg_label = alg[:4] + f'(M={m})'
                    else:
                        alg_label = alg
                else:
                    alg_label = ''
                label = r_label + shp_label + alg_label
                if label[-1] == ' ':
                    label = label[:-2]
                
                # simulation
                cap_list = []
                for ds in ds_list:
                    for sim_idx in range(sim_idx_dict[alg]+1):
                        sim = simulation.Simulation(ds, t_pwr, alg, sim_idx)
                        sim.execute_all()
                        cap_arr = sim.get_cap_arr()
                        cap_list.append(cap_arr)
                cap_list = np.array(cap_list).flatten()
                cap_arr_list.append(cap_list)
                label_list.append(label)
    fig.make_cumulative_figures(cap_arr_list, label_list, f"SumCap_CDF_typ={typ}_r={r_list}_shp={shp_list}_alg={alg_list}.png", x_lim, x_range, True)

def generate_mAD_CDF(typ, nu, r_list, shp_list, dsidx_list, alg_list, t_pwr, sim_idx_dict, x_lim, x_range):
    mAD_arr_list = []
    label_list = []
    for r in r_list:
        # label of r
        if len(r_list) != 1:
            r_label = f'{r}km, '
        else:
            r_label = ''
        for shp in shp_list:
            # label of shape of antenna
            if len(shp_list) != 1:
                shp_label = 'Planar, ' if shp == 'p' else 'Cylinder, '
            else:
                shp_label = ''
            
            # generate dataset
            ds_list = []
            for dsidx in dsidx_list:
                ds = simulation.Dataset(typ, nu, r, shp, dsidx)
                ds_list.append(ds)
            for alg in alg_list:
                # label of alg
                if len(alg_list) != 1:
                    if 'ACUS' in alg or 'MRUS' in alg:
                        m = alg[4:]
                        alg_label = alg[:4] + f'(M={m})'
                    else:
                        alg_label = alg
                else:
                    alg_label = ''
                label = r_label + shp_label + alg_label
                if label[-1] == ' ':
                    label = label[:-2]
                
                # simulation
                mAD_list = []
                for ds in ds_list:
                    for sim_idx in range(sim_idx_dict[alg]+1):
                        sim = simulation.Simulation(ds, t_pwr, alg, sim_idx)
                        sim.execute_grouping()
                        mAD_arr = sim.get_user_mAD_arr()
                        mAD_list.append(mAD_arr)
                mAD_list = np.array(mAD_list).flatten()
                mAD_arr_list.append(mAD_list)
                label_list.append(label)
    fig.make_cumulative_minAD(mAD_arr_list, label_list, f"mAD_CAD_typ={typ}_r={r_list}_shp={shp_list}_alg={alg_list}", x_lim, x_range, True)


def generate_med_cap_nu(dist_typ, grp_n, nu_list, r_list, shp_list, dsidx_list, alg_list, t_pwr, sim_idx_dict, x_lim, x_range, y_lim, y_range):
    cap_arr_list = []
    label_list = []
    for r in r_list:
        # label of r
        if len(r_list) != 1:r_label = f'{r}km, '
        else: r_label = ''
        for shp in shp_list:
            # label of shape of antenna
            if len(shp_list) != 1:
                shp_label = 'Planar, ' if shp == 'p' else 'Cylinder, '
            else: shp_label = ''
            for alg in alg_list:
                # label of alg
                if len(alg_list) != 1:
                    if 'ACUS' in alg or 'MRUS' in alg: alg_label = alg[:4] + f'(M={alg[4:]})'
                    else: alg_label = alg
                else: alg_label = ''
                label = r_label + shp_label + alg_label
                if len(label) != 0:
                    if label[-1] == ' ': label = label[:-2]
            
                # generate dataset
                nu_cap_arr_list = []
                for nu in nu_list:
                    typ = dist_typ + str(grp_n*nu)
                    ds_list = []
                    for dsidx in dsidx_list:
                        ds = simulation.Dataset(typ, nu, r, shp, dsidx)
                        ds_list.append(ds)

                    # simulation
                    cap_list = []
                    for ds in ds_list:
                        for sim_idx in range(sim_idx_dict[alg]+1):
                            sim = simulation.Simulation(ds, t_pwr, alg, sim_idx)
                            sim.execute_all()
                            cap_arr = sim.get_cap_arr()
                            cap_list.append(cap_arr)
                    cap_list = np.array(cap_list).flatten()
                    nu_cap_arr_list.append(cap_list)
                
                cap_arr_list.append(nu_cap_arr_list)
                label_list.append(label)
    print(np.array(cap_arr_list).shape)
    fig.make_nu_med_cap(nu_list, cap_arr_list, label_list, f"capNu_r={r_list}_shp={shp_list}_alg={alg_list}.png", x_lim, x_range, y_lim, y_range, True)


def execute():
    path.set_cur_dir()
    generate_tokyo_heatmap()
    alg_list =['AUS', 'ACUS3', 'ACUS4', 'ACUS5']
    sim_idx_dict = {}
    for alg in alg_list: sim_idx_dict[alg] = 0
    # sim_idx_dict['RUS'] = 1 
    nu_list = [i for i in range(12, 18, 6)]
    grp_dict = {}
    grp_n = 2000
    r = 20
    shp = 'p'
    dsidx_head = 0
    dsidx_size = 1
    dsidx_list = [i for i in range(dsidx_head, dsidx_size+dsidx_head)]
    """for nu in nu_list:
        grp_dict[nu] = grp_n
    generate_sinr_figure_with_random(r, nu_list, grp_dict, shp, [0], 150, alg_list, sim_idx_dict)"""
    # generate_nu_cap_figures_with_random([r], nu_list, grp_dict, [shp], [0], 150, alg_list, sim_idx_dict)
    # generate_cos_relativity_between_h_in_random(r, nu_list, grp_n, 2, 'p', 120, alg_list, 0)
    """generate_med_cap_nu('random', 2000, [i for i in range(10, 140, 10)], [20], ['p'], 
                        [0], alg_list, 150, sim_idx_dict, [10, 130], 10, [0, 10], 1)"""
    x_lim_list = [[0.8, 1.8]]
    x_range_list = [0.2]
    for nu_idx, nu in enumerate(nu_list):
        typ = 'random' + str(nu*grp_n)
        """generate_capacity_CDF(typ, nu, [50], ['p'], 
                              dsidx_list, 
                              alg_list, 120, sim_idx_dict, [1.2, 1.8], 0.05)"""
        # generate_mAD_CDF(typ, nu, [50], ['p'], dsidx_list, alg_list, 120, sim_idx_dict, [15, 50], 10)
        # generate_cumulative_cap(typ, nu, r, shp, dsidx_list, alg_list, 120, sim_idx_dict, x_lim_list[nu_idx], x_range_list[nu_idx])
        # generate_SINR_CDF(typ, nu, [50], ['p'], dsidx_list, alg_list, 120, sim_idx_dict, [-10, 40], 10)
    cities = ['tokyo', 'sendai', 'nagoya', 'osaka']
    # generate_flop_table([20, 40, 60, 80], 100, 20, 'p', 0, alg_list, 120, sim_idx_dict)
    for city in ['tokyo']:
        """generate_capacity_CDF(city, 12, [20], ['p'], 
                              dsidx_list, 
                              alg_list, 120, sim_idx_dict, [2.3, 2.5], 0.1)"""
        # generate_mAD_CDF(typ, nu, [20], ['p'], dsidx_list, alg_list, 120, sim_idx_dict, [15, 50], 5)
        # generate_cumulative_cap(typ, nu, r, shp, dsidx_list, alg_list, 120, sim_idx_dict, x_lim_list[nu_idx], x_range_list[nu_idx])
        # generate_SINR_CDF(city, nu, [20], ['p'], dsidx_list, alg_list, 120, sim_idx_dict, [25, 40], 5)
        # generate_mAD_CDF(city, nu, [20], ['p'], dsidx_list, alg_list, 120, sim_idx_dict, [10, 50], 5)
        # generate_user_capacity_CDF(city, nu, [20], ['p'], dsidx_list, alg_list, 120, sim_idx_dict, [25, 40], 5)
        
execute()