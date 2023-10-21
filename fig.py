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

def make_SNR_interference_SINR_figure(usr_list, snr_med, snr_std, i_med, i_std, sinr_med, sinr_std, fig_title):
    plt.style.use('default')
    sns.set()
    sns.set_style('whitegrid')
    sns.set_palette('Set1')
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.errorbar(usr_list, snr_med, yerr=snr_std, marker='o', label='SNR', capthick=1, capsize=8, lw=1)
    ax.errorbar(usr_list, i_med, yerr=i_std, marker='o', label='I', capthick=1, capsize=8, lw=1)
    ax.errorbar(usr_list, sinr_med, yerr=sinr_std, marker='o', label='SINR', capthick=1, capsize=8, lw=1)
    ax.set_xlabel('number of users in a group')
    ax.set_ylabel('SNR/SINR/I')
    plt.show()
    save.save_fig(fig, fig_title)

def make_capacity_fig_with_std(usr_list, capacity_list, fig_title):
    med_list = []
    std_list = []
    for i in range(len(usr_list)):
        capacity_arr = capacity_list[i]
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
    ax.errorbar(usr_list, med_list, yerr=std_list, marker='o', label='SNR', capthick=1, capsize=8, lw=1)
    ax.set_xlabel('number of users in a group')
    ax.set_ylabel('capacity [Gbps]')
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

def make_cumulative_figures(eval_arr_list, label_list, fig_title, save_flg):
    data_n = len(eval_arr_list)
    fig = plt.figure(figsize=fp.cumulative_figure_size)
    for i in range(data_n):
        eval_arr = eval_arr_list[i] / fp.gbps
        sorted_eval_arr = utils.sort_arr(eval_arr)
        data = utils.add_cumulative_ratio(sorted_eval_arr)
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
    plt.xlim(fp.x_lim)
    plt.ylim(fp.y_lim)
    plt.xlabel(fp.x_label, fontsize=fp.fontsize, fontname="MS Gothic")
    plt.ylabel(fp.y_label, fontsize=fp.fontsize, fontname="MS Gothic")
    plt.xticks(np.arange(fp.x_lim[0], fp.x_lim[1]+fp.x_range, fp.x_range))
    plt.yticks(np.arange(fp.y_lim[0], fp.y_lim[1]+fp.y_range, fp.y_range))
    plt.grid()
    plt.show()
    if save_flg:
        save.save_fig(fig, fig_title)

def make_cumulative_SINR(sinr_arr_list, label_list, fig_title, save_flg):
    data_n = len(sinr_arr_list)
    fig = plt.figure(figsize=fp.cumulative_figure_size)
    for i in range(data_n):
        sinr_arr = sinr_arr_list[i]
        sorted_sinr_arr = utils.sort_arr(sinr_arr)
        data = utils.add_cumulative_ratio(sorted_sinr_arr)
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
    plt.xlim(fp.sinr_x_lim)
    plt.ylim(fp.sinr_y_lim)
    plt.xlabel(fp.sinr_x_label, fontsize=fp.fontsize, fontname="MS Gothic")
    plt.ylabel(fp.sinr_y_label, fontsize=fp.fontsize, fontname="MS Gothic")
    plt.xticks(np.arange(fp.sinr_x_lim[0], fp.sinr_x_lim[1]+fp.sinr_x_range, fp.sinr_x_range))
    plt.yticks(np.arange(fp.sinr_y_lim[0], fp.sinr_y_lim[1]+fp.sinr_y_range, fp.sinr_y_range))
    plt.grid()
    plt.show()
    if save_flg:
        save.save_fig(fig, fig_title)

def make_cumulative_minAD(minAD_arr_list, label_list, fig_title, save_flg):
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
    plt.xlim(fp.minAD_x_lim)
    plt.ylim(fp.minAD_y_lim)
    plt.xlabel(fp.minAD_x_label, fontsize=fp.fontsize, fontname="MS Gothic")
    plt.ylabel(fp.minAD_y_label, fontsize=fp.fontsize, fontname="MS Gothic")
    plt.xticks(np.arange(fp.minAD_x_lim[0], fp.minAD_x_lim[1]+fp.minAD_x_range, fp.minAD_x_range))
    plt.yticks(np.arange(fp.minAD_y_lim[0], fp.minAD_y_lim[1]+fp.minAD_y_range, fp.minAD_y_range))
    plt.grid()
    plt.show()
    if save_flg:
        save.save_fig(fig, fig_title)

def heatmap(block_population, fig_title, save_flg):
    print(block_population.shape)
    df = pd.DataFrame(block_population)
    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(np.flipud(df.T), extent=(-20,20,-20,20), cmap='jet')
    ax.set_xlabel('km')
    ax.set_ylabel('km')
    plt.colorbar(im, label='people/sq km')
    plt.show()
    if save_flg:
        save.save_fig(fig, fig_title)