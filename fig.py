import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import interp1d, griddata
import seaborn as sns
import statistics
import utils
import save
import numpy as np
from fig_properties import FigProperty as fp
from properties import Property as prop

def plt_all_users(xy_arr):
    fig = plt.figure()
    plt.scatter(xy_arr[:,0], xy_arr[:,1])
    plt.show()

def save_plt_all_users(xy_arr, fig_title):
    fig = plt.figure()
    plt.scatter(xy_arr[:,0], xy_arr[:,1])
    plt.show()
    save.save_fig(fig, fig_title)

def save_plt_users_with_colorbar(xy_arr, fig_title, c_arr, c_max, c_min, r):
    fig = plt.figure()
    plt.scatter(xy_arr[:,0], xy_arr[:,1], s=10, c=c_arr, cmap='jet')
    plt.xlim(-r, r)
    plt.ylim(-r, r)
    # カラーバーを表示
    plt.colorbar(ticks=np.arange(c_min, c_max, (c_max-c_min)/10))
    plt.clim(c_min, c_max)
    plt.show()
    # save.save_fig(fig, fig_title)

base_xy = [0, 10]
xy_arr = []
clr_arr = []
xy_arr.append(base_xy)
clr_arr.append(0)
ang_unit = 0.5
for i in range(-20, 20):
    ang = i*ang_unit
    if i == 0:
        continue
    ang_rad = 2 * np.pi * ang / 360
    x = base_xy[0]*np.cos(ang_rad) - base_xy[1]*np.sin(ang_rad)
    y = base_xy[0]*np.sin(ang_rad) + base_xy[1]*np.cos(ang_rad)
    xy_arr.append([x,y])
    c = 20 + np.random.randn(1)
    clr_arr.append(c)
xy_arr = np.array(xy_arr)
save_plt_users_with_colorbar(xy_arr, "test", clr_arr, 25, 0, 20)

xy2_arr = [base_xy]
clr2_arr = [0]
for i in range(10):
    if i == 5:
        continue
    y = 5 + i
    xy = [0, y]
    xy2_arr.append(xy)
    c = 20 + np.random.randn(1)
    clr2_arr.append(c)
xy2_arr = np.array(xy2_arr)
save_plt_users_with_colorbar(xy2_arr, "test2", clr2_arr, 25, 0, 20)

def make_SNR_SINR_figure(usr_list, snr_med, snr_std, sinr_med, sinr_std, fig_title):
    plt.style.use('default')
    sns.set()
    sns.set_style('whitegrid')
    sns.set_palette('Set1')
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.errorbar(usr_list, snr_med, yerr=snr_std, marker='o', label='SNR', capthick=1, capsize=8, lw=1)
    ax.errorbar(usr_list, sinr_med, yerr=sinr_std, marker='o', label='SINR', capthick=1, capsize=8, lw=1)
    ax.set_xlabel('number of users in a group')
    ax.set_ylabel('median SNR/SINR')
    ax.legend()
    plt.show()
    save.save_fig(fig, fig_title)

def make_SINR_figure(nu_list, alg_list, sinr_dict, fig_title):
    plt.style.use('default')
    sns.set()
    sns.set_style('whitegrid')
    sns.set_palette('Set1')
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    for alg in alg_list:
        sinr_arr = sinr_dict[alg]
        med_arr = np.zeros(len(nu_list))
        std_arr = np.zeros(len(nu_list))
        for nu_idx in range(len(nu_list)):
            med = statistics.median(sinr_arr[nu_idx])
            std = np.std(sinr_arr[nu_idx])
            med_arr[nu_idx] = med
            std_arr[nu_idx] = std
        if 'ACUS' in alg:
            lbl = f'ACUS(M={alg[4:]})'
        else:
            lbl = alg
        ax.errorbar(nu_list, med_arr, yerr=std_arr, marker='o', label=lbl, capthick=1, capsize=8, lw=1)
    ax.set_xlabel('number of users in a group')
    ax.set_ylabel('SINR')
    # ax.set_ylim(-40, 50)
    # ax.legend(bbox_to_anchor=(0,0), loc='lower left', borderaxespad=1, fontsize=10)
    plt.show()
    save.save_fig(fig, fig_title)

def make_cos_relativity_figure(nu_list, alg_list, ang_dict, fig_title):
    plt.style.use('default')
    sns.set()
    sns.set_style('whitegrid')
    sns.set_palette('Set1')
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    for alg in alg_list:
        data_list = ang_dict[alg]
        med_arr = data_list[0]
        std_arr = data_list[1]
        if 'ACUS' in alg:
            lbl = f'ACUS(M={alg[4:]})'
        else:
            lbl = alg
        ax.errorbar(nu_list, med_arr, yerr=std_arr, marker='o', label=lbl, capthick=1, capsize=8, lw=1)
    ax.set_xlabel('number of users in a group')
    ax.set_ylabel('Angle')
    ax.set_ylim(20, 100)
    ax.legend(bbox_to_anchor=(0,0), loc='lower left', borderaxespad=1, fontsize=10)
    plt.show()
    save.save_fig(fig, fig_title)


def make_sig_intf_noise_figure(x_list, sig_med, sig_std, intf_med, intf_std, ns_med, ns_std,
                               x_label, y_label, fig_title):
    plt.style.use("default")
    sns.set()
    sns.set_palette('Set1')
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.errorbar(x_list, intf_med, intf_std, marker='o', label='interference', capthick=1, capsize=8, lw=1)
    ax.errorbar(x_list, sig_med, sig_std, marker='o', label='signal', capthick=1, capsize=8, lw=1)
    ax.errorbar(x_list, ns_med, ns_std, marker='o', label='noise', capthick=1, capsize=8, lw=1)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend()
    plt.show()
    save.save_fig(fig, fig_title)

def make_interference_figure(usr_list, i_med, i_std, i_max, i_min, fig_title):
    plt.style.use('default')
    sns.set()
    sns.set_style('whitegrid')
    sns.set_palette('Set1')
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(usr_list, i_max, marker='o', label='interference_max')
    ax.plot(usr_list, i_min, marker='o', label='interference_min')
    ax.errorbar(usr_list, i_med, yerr=i_std, marker='o', label='interference_median', capthick=1, capsize=8, lw=1)
    ax.set_xlabel('number of users in a group')
    ax.set_ylabel('Interference (log10)')
    fig.legend()
    plt.show()
    save.save_fig(fig, fig_title)

def make_capacity_fig_with_std(usr_list, capacity_list, fig_title):
    med_list = []
    std_list = []
    for i in range(len(usr_list)):
        capacity_arr = capacity_list[i] / 10**9
        med = statistics.median(capacity_arr)
        std = np.std(capacity_arr)
        med_list.append(med)
        std_list.append(std)
    plt.style.use('default')
    sns.set()
    sns.set_style('whitegrid')
    sns.set_palette('Set1')
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.errorbar(usr_list, med_list, yerr=std_list, marker='o', label='capacity', capthick=1, capsize=8, lw=1)
    ax.set_xlabel('number of users in a group')
    ax.set_ylabel('capacity [Gbps]')
    plt.show()
    save.save_fig(fig, fig_title)

def make_capacitys_fig_with_std(nu_list, cap_dict, alg_list, fig_title):
    med_dict = {}
    std_dict = {}
    for alg in alg_list:
        cap_arr = cap_dict[alg]
        nu_size = len(cap_arr)
        med_arr = np.zeros(nu_size)
        std_arr = np.zeros(nu_size)
        # calculate median and standard deviation of each nu dataset
        for nu_idx in range(nu_size):
            non_zero_arr = np.where(cap_arr[nu_idx]!=0)[0]
            new_cap_arr = cap_arr[nu_idx, non_zero_arr] / 10**9
            med = statistics.median(new_cap_arr)
            std = np.std(new_cap_arr)
            med_arr[nu_idx] = med
            std_arr[nu_idx] = std
        med_dict[alg] = med_arr
        std_dict[alg] = std_arr
    plt.style.use('default')
    sns.set()
    sns.set_style('whitegrid')
    sns.set_palette('Set1')
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    for alg in alg_list:
        if 'ACUS' in alg:
            lbl = f'ACUS(M={alg[4:]})'
        else:
            lbl = alg
        ax.errorbar(nu_list, med_dict[alg], yerr=std_dict[alg], marker='o', label=lbl, capthick=1, capsize=8, lw=1)
    ax.set_xlabel('number of users in a group')
    ax.set_ylabel('capacity [Gbps]')
    ax.legend(bbox_to_anchor=(0,0), loc='lower left', borderaxespad=1, fontsize=10)
    plt.show()
    save.save_fig(fig, fig_title)

def hist_usr_angle(ang_arr, ds_type, ang_type):
    fig = plt.figure(figsize=fp.hist_size)
    plt.ylim(fp.ang_ylim[ds_type])
    if ang_type == 0:
        plt.xlim(fp.az_xlim)
        plt.xlabel('azimuth [°]', fontsize=30)
        figname = 'azimuth'
    else:
        plt.xlim(fp.el_xlim)
        plt.xlabel('elevation [°]', fontsize=30)
        figname = 'elevation'
    plt.ylabel('user num', fontsize=30)
    plt.grid(True)
    plt.tick_params(labelsize=12)
    plt.hist(ang_arr, alpha=0.5, color='b')
    plt.show()
    path = prop.fig_path + 'hist_' + ds_type + '_' + figname + '.png'

def hist_usr_angles(ang_arr, ds_type):
    data = utils.turn_el(ang_arr)
    for i in range(2):
        hist_usr_angle(data[:,i], ds_type, i)

def make_cumulative_figures(eval_arr_list, label_list, fig_title, x_lim, x_range, save_flg):
    data_n = len(eval_arr_list)
    fig, ax = plt.subplots(figsize=fp.cumulative_figure_size)
    # axins = ax.inset_axes([0.6, 0.2, 0.25, 0.25])
    # axins2 = ax.inset_axes([0.08, 0.6, 0.25, 0.25])
    for i in range(data_n):
        eval_arr = eval_arr_list[i] / fp.gbps
        sorted_eval_arr = utils.sort_arr(eval_arr)
        data = utils.add_cumulative_ratio(sorted_eval_arr)
        plt.plot(data[0], data[1], fp.marker[i], label=label_list[i])
        # axins.plot(data[0], data[1], fp.marker[i], label=label_list[i])
        # axins2.plot(data[0], data[1], fp.marker[i], label=label_list[i])
    plt.rcParams['font.family'] = 'Times New Roman'  
    plt.rcParams['font.size'] = fp.fontsize
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['xtick.top'] = True
    plt.rcParams['ytick.right'] = True
    plt.tick_params(labelsize=18)
    ax.legend(loc='lower center', bbox_to_anchor=(.5, 1), fontsize=20)
    ax.legend()
    ax.set_xlim(x_lim)
    ax.set_ylim(fp.y_lim)
    ax.set_xlabel(fp.x_label, fontsize=fp.fontsize, fontname="MS Gothic")
    ax.set_ylabel(fp.y_label, fontsize=fp.fontsize, fontname="MS Gothic")
    plt.xticks(np.arange(x_lim[0], x_lim[1]+x_range, x_range))
    plt.yticks(np.arange(fp.y_lim[0], fp.y_lim[1]+fp.y_range, fp.y_range))
    # axins.set_xlim(2.42, 2.48)
    # axins.set_ylim(0.7, 0.8)
    # axins.set_xticks([2.42, 2.44, 2.46, 2.48])
    # axins.set_yticks([0.7, 0.75, 0.8])
    # axins2.set_xlim(2.34, 2.38)
    # axins2.set_ylim(0.1, 0.2)
    # axins2.set_xticks([2.34, 2.36, 2.38])
    # axins2.set_yticks([0.1, 0.15, 0.2])
    # ax.indicate_inset_zoom(axins)
    # ax.indicate_inset_zoom(axins2)
    plt.grid()
    plt.show()
    if save_flg:
        save.save_fig(fig, fig_title)

def make_cumulative_SINR(sinr_arr_list, label_list, fig_title, x_lim, x_range, save_flg):
    data_n = len(sinr_arr_list)
    fig, ax = plt.subplots(figsize=fp.cumulative_figure_size)
    # axins = ax.inset_axes([0.6, 0.2, 0.37, 0.37])
    for i in range(data_n):
        sinr_arr = sinr_arr_list[i]
        sorted_sinr_arr = utils.sort_arr(sinr_arr)
        data = utils.add_cumulative_ratio(sorted_sinr_arr)
        ax.plot(data[0], data[1], fp.marker[i], label=label_list[i])
        # axins.plot(data[0], data[1], fp.marker[i], label=label_list[i])
    plt.rcParams['font.family'] = 'Times New Roman'  
    plt.rcParams['font.size'] = fp.fontsize
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['xtick.top'] = True
    plt.rcParams['ytick.right'] = True
    # plt.legend(loc='lower center', bbox_to_anchor=(.5, 1), fontsize=20)
    ax.legend()
    ax.set_title(fig_title, y=-0.15)
    ax.set_xlim(x_lim)
    ax.set_ylim(fp.sinr_y_lim)
    ax.set_xlabel(fp.sinr_x_label, fontsize=fp.fontsize, fontname="MS Gothic")
    ax.set_ylabel(fp.sinr_y_label, fontsize=fp.fontsize, fontname="MS Gothic")
    # axins.set_xlim(18, 18.25)
    # axins.set_ylim(0.42, 0.44)
    # ax.indicate_inset_zoom(axins)
    plt.xticks(np.arange(x_lim[0], x_lim[1]+x_range, x_range))
    plt.yticks(np.arange(fp.sinr_y_lim[0], fp.sinr_y_lim[1]+fp.sinr_y_range, fp.sinr_y_range))
    plt.grid()
    plt.show()
    if save_flg:
        save.save_fig(fig, fig_title)

    plt.rcParams['xtick.direction'] = 'in'


def make_cumulative_SINR2(sinr_arr_list, label_list, fig_title, x_lim, x_range, save_flg):
    data_n = len(sinr_arr_list)
    fig, ax = plt.subplots(figsize=fp.cumulative_figure_size)
    # axins = ax.inset_axes([0.6, 0.2, 0.37, 0.37])
    for i in range(data_n):
        sinr_arr = sinr_arr_list[i]
        sorted_sinr_arr = utils.sort_arr(sinr_arr)
        data = utils.add_cumulative_ratio(sorted_sinr_arr)
        ax.plot(data[0], data[1], fp.marker[i], label=label_list[i])
        # axins.plot(data[0], data[1], fp.marker[i], label=label_list[i])
    plt.rcParams['font.family'] = 'Times New Roman'  
    plt.rcParams['font.size'] = fp.fontsize
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['xtick.top'] = True
    plt.rcParams['ytick.right'] = True
    # plt.legend(loc='lower center', bbox_to_anchor=(.5, 1), fontsize=20)
    ax.legend(fontsize=18)
    # ax.set_title(fig_title, y=-0.15)
    # ax.set_xlim(x_lim)
    ax.set_ylim(fp.sinr_y_lim)
    ax.set_xlabel("Channel Capacity [Mbps]", fontsize=fp.fontsize, fontname="MS Gothic")
    ax.set_ylabel(fp.sinr_y_label, fontsize=fp.fontsize, fontname="MS Gothic")
    # axins.set_xlim(18, 18.25)
    # axins.set_ylim(0.42, 0.44)
    # ax.indicate_inset_zoom(axins)
    # plt.xticks(np.arange(x_lim[0], x_lim[1]+x_range, x_range))
    # plt.yticks(np.arange(fp.sinr_y_lim[0], fp.sinr_y_lim[1]+fp.sinr_y_range, fp.sinr_y_range))
    plt.grid()
    plt.show()
    if save_flg:
        save.save_fig(fig, fig_title)

    plt.rcParams['xtick.direction'] = 'in'


def make_cumulative_minAD(minAD_arr_list, label_list, fig_title, x_lim, xrange, save_flg):
    data_n = len(minAD_arr_list)
    fig = plt.figure(figsize=fp.cumulative_figure_size)
    for i in range(data_n):
        minAD_arr = minAD_arr_list[i]
        sorted_minAD_arr = utils.sort_arr(minAD_arr)
        data = utils.add_cumulative_ratio(sorted_minAD_arr)
        plt.plot(data[0], data[1], fp.marker[i], label=label_list[i])
    plt.rcParams['font.family'] = 'Times New Roman'  
    plt.rcParams['font.size'] = fp.fontsize
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['xtick.top'] = True
    plt.rcParams['ytick.right'] = True
    # plt.legend(loc='lower center', bbox_to_anchor=(.5, 1), fontsize=20)
    plt.legend()
    plt.title(fig_title, y=-0.15)
    plt.xlim(x_lim)
    plt.ylim(fp.minAD_y_lim)
    plt.xlabel(fp.minAD_x_label, fontsize=fp.fontsize, fontname="MS Gothic")
    plt.ylabel(fp.minAD_y_label, fontsize=fp.fontsize, fontname="MS Gothic")
    plt.xticks(np.arange(x_lim[0], x_lim[1]+xrange, xrange))
    plt.yticks(np.arange(fp.minAD_y_lim[0], fp.minAD_y_lim[1]+fp.minAD_y_range, fp.minAD_y_range))
    plt.grid()
    plt.show()
    if save_flg:
        save.save_fig(fig, fig_title)



def make_nu_med_cap(nu_list, data_arr_list, label_list, fig_title, x_lim, x_range, y_lim, y_range, save_flg):
    fig = plt.figure(figsize=fp.cumulative_figure_size)
    for i in range(len(data_arr_list)):
        data_list = []
        for j in range(len(data_arr_list[i])):
            med = np.median(data_arr_list[i][j]) / 10**9
            data_list.append(med)
        plt.plot(nu_list, data_list, fp.marker[i], label=label_list[i], marker='o')
    plt.rcParams['font.family'] = 'Times New Roman'  
    plt.rcParams['font.size'] = fp.fontsize
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['xtick.top'] = True
    plt.rcParams['ytick.right'] = True
    plt.legend(loc='lower center', bbox_to_anchor=(.5, 1), fontsize=20)
    plt.legend()
    plt.xlim(x_lim)
    plt.ylim(y_lim)
    plt.xlabel('No. of Users', fontsize=fp.fontsize, fontname="MS Gothic")
    plt.ylabel('Median of the System Capacities[Gbps]', fontsize=fp.fontsize, fontname="MS Gothic")
    plt.xticks(np.arange(x_lim[0], x_lim[1]+x_range, x_range))
    plt.yticks(np.arange(y_lim[0], y_lim[1]+y_range, y_range))
    plt.grid()
    plt.show()
    if save_flg:
        save.save_fig(fig, fig_title)

def heatmap(r, block_population, fig_title, save_flg):
    print(block_population.shape)
    df = pd.DataFrame(block_population)
    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(np.flipud(df.T), extent=(-r,r,-r,r), cmap='jet')
    ax.set_xlabel('km')
    ax.set_ylabel('km')
    plt.colorbar(im, label='people/sq km')
    plt.show()
    if save_flg:
        save.save_fig(fig, fig_title)
    
def make_flop_table(data_arr, col_label_arr, fig_title):
    fig, ax = plt.subplots(1, 1)
    ax.axis("tight")
    ax.axis("off")
    ax.table(cellText=data_arr, colLabels=col_label_arr, loc="center")
    plt.show()
    save.save_fig(fig, fig_title)