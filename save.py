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
    print(f'[INFO SAVE] data: angle_arr, path: {path}')

def save_xy_arr(xy_arr, ds_type):
    path = prop.xy_path + ds_type + '.csv'
    save_csv(xy_arr, path)
    print(f'[INFO SAVE] data: xy_arr, path: {path}')

def save_group_table(group_table, ds_type):
    path = prop.group_path + ds_type + '.csv'
    save_csv(group_table, path)
    print(f'[INFO SAVE] data: group_table, path: {path}')

def save_closest_user_arr(cls_usr_arr, ds_type):
    path = prop.cls_usr_path + ds_type + '.csv'
    save_csv(cls_usr_arr, path)
    print(f'[INFO SAVE] data: closest_user, path: {path}')

def save_eval_arr(eval_arr, ds_type):
    path = prop.eval_path + ds_type + '.csv'
    save_csv(eval_arr, path)
    print(f'[INFO SAVE] data: cap_list, path: {path}')

# incomplete
def save_user_HAPS_angle(usr_ant_ang_arr, ds_type):
    data_label = ['azimuth', 'elevation', 'dis']
    for i in range(3):
        path = prop.usr_ant_path[i] + ds_type + '.csv'
        arr = usr_ant_ang_arr[:,:,i]
        save_csv(arr, path)
        print(f'[INFO SAVE] data: ua_{data_label[i]}, path: {path}')
    
def save_fig(fig, fig_name):
    path = prop.fig_path + fig_name + '.png'
    fig.savefig(path, bbox_inches='tight')
    print(f'[INFO SAVE] data: fig, path: {path}')

def save_sinr_arr(sinr_arr, ds_type):
    path = prop.sinr_path + ds_type + '.csv'
    save_csv(sinr_arr, path)
    print(f'[INFO SAVE] data: SINR_arr, path: {path}')

def save_snr_arr(snr_arr, ds_type):
    path = prop.snr_path + ds_type + '.csv'
    save_csv(snr_arr, path)
    print(f'[INFO SAVE] data: SNR_arr, path: {path}')

def save_interference_arr(intf_arr, ds_type):
    path = prop.intf_path + ds_type + '.csv'
    save_csv(intf_arr, path)
    print(f'[INFO SAVE] data: intf_arr, path: {path}')

def save_sig_arr(sig_arr, ds_type):
    path = prop.sig_path + ds_type + '.csv'
    save_csv(sig_arr, path)
    print(f'[INFO SAVE] data: sig_arr, path: {path}')

def save_noise_arr(noise_arr, ds_type):
    path = prop.noise_path + ds_type + '.csv'
    save_csv(noise_arr, path)
    print(f'[INFO SAVE] data: noise_arr, path: {path}')

def save_group_minAD_arr(minAD_arr, ds_type):
    path = prop.group_minAD_path + ds_type + '.csv'
    save_csv(minAD_arr, path)
    print(f'[INFO SAVE] data: group_mAD_arr, path: {path}')

def save_user_minAD_arr(minAD_arr, ds_type):
    path = prop.usr_minAD_path + ds_type + '.csv'
    save_csv(minAD_arr, path)
    print(f'[INFO SAVE] data: user_mAD_arr, path: {path}')

def save_flop_arr(flop_arr, ds_type):
    path = prop.flop_path + ds_type + '.csv'
    save_csv(flop_arr, path)
    print(f'[INFO SAVE] data: flop_arr, path: {path}')

def save_flop_arrs(flop_arrs, ds_type):
    path = prop.flop_path + ds_type + '.csv'
    save_csv(flop_arrs, path)
    arr_n = len(flop_arrs)
    print(f'[INFO SAVE] data: flop_arrs, path: {path}')
