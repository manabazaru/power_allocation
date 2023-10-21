import csv
import numpy as np
from properties import Property as prop
import matplotlib.pyplot as plt

def save_csv(data_arr, path):
    dim = data_arr.ndim
    size = len(data_arr)
    if dim == 1:
        new_data_arr = np.zeros([size,1])
        new_data_arr[:,0] = data_arr
        data_arr = new_data_arr
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        for data_idx in range(size):
            data = data_arr[data_idx].tolist()
            writer.writerow(data)

def save_angle_arr(ang_arr, ds_type):
    path = prop.angle_path + ds_type + '.csv'
    save_csv(ang_arr, path)
    print(f'[INFO SAVE] User angle array of {ds_type} is saved in {path}')

def save_xy_arr(xy_arr, ds_type):
    path = prop.xy_path + ds_type + '.csv'
    save_csv(xy_arr, path)
    print(f'[INFO SAVE] User xy array of {ds_type} is saved in {path}')

def save_group_table(group_table, alg, ds_type):
    path = prop.group_path[alg] + '_' + alg + '_' + ds_type + '.csv'
    save_csv(group_table, path)
    print(f'[INFO SAVE] Group table of {ds_type} users with generating {alg} is saved in {path}')

def save_closest_user_arr(cls_usr_arr, ds_type):
    path = prop.cls_usr_path + ds_type + '.csv'
    save_csv(cls_usr_arr, path)
    print(f'[INOF SAVE] Closest user data of {ds_type} is saved in {path}')

def save_eval_arr(eval_arr, ds_type):
    path = prop.eval_path + ds_type + '.csv'
    save_csv(eval_arr, path)
    print(f'[INFO SAVE] Evaluation of each {ds_type} user group is saved in {path}')

# incomplete
def save_user_HAPS_angle(usr_ant_ang_arr, haps_shape, ds_type):
    path = prop.usr_ant_path[haps_shape] + haps_shape + '_' + ds_type + '.csv'
    save_csv(usr_ant_ang_arr, path)
    print(f'[INFO SAVE] Angles between users of {ds_type} and antenna elements of ' +
          f'{haps_shape} HAPS is saved in {path}')
    
def save_fig(fig, fig_name):
    path = prop.fig_path + fig_name + '.png'
    fig.savefig(path, bbox_inches='tight')
    print(f'[INFO SAVE] The figure named {fig_name} has been saved in {path}.')

def save_sinr_arr(sinr_arr, ds_type):
    path = prop.sinr_path + ds_type + '.csv'
    save_csv(sinr_arr, path)
    print(f'[INFO SAVE] SINR of each {ds_type} user group is saved in {path}')

def save_snr_arr(snr_arr, ds_type):
    path = prop.snr_path + ds_type + '.csv'
    save_csv(snr_arr, path)
    print(f'[INFO SAVE] SNR of each {ds_type} user group is saved in {path}')

def save_interference_arr(intf_arr, ds_type):
    path = prop.intf_path + ds_type + '.csv'
    save_csv(intf_arr, path)
    print(f'[INFO SAVE] Interference of each {ds_type} user group is saved in {path}')

def save_minAD_arr(minAD_arr, ds_type):
    path = prop.minAD_path + ds_type + '.csv'
    save_csv(minAD_arr, path)
    print(f'[INFO SAVE] SINR of each {ds_type} user group is saved in {path}')

def save_flop_arr(flop_arr, ds_type):
    path = prop.flop_path + ds_type + '.csv'
    save_csv(flop_arr, path)
    print(f'[INFO SAVE] Flops of {ds_type} is saved in {path}')

def save_flop_arrs(flop_arrs, ds_type):
    path = prop.flop_path + ds_type + '.csv'
    save_csv(flop_arrs, path)
    arr_n = len(flop_arrs)
    print(f'[INFO SAVE] {arr_n} flops data of {ds_type} is saved in {path}')

