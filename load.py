import numpy as np
import csv
import scipy.io as scio
from properties import Property as prop

def load_csv(path):
    with open(path, 'r') as f:
        reader = csv.reader(f)
        load_list = [row for row in reader]
    data_arr = np.array(load_list)
    factor_n = data_arr.shape[1]
    if factor_n == 1:
        data_arr = data_arr[:,0]
    return data_arr

def load_mat(city):
    path = prop.mat_path[city]
    loc_load = scio.loadmat(path)['all_UE']
    usr_xy = np.zeros((loc_load.shape[0],2))
    usr_xy[:,0] = loc_load[:,0]
    usr_xy[:,1] = loc_load[:,1]
    usr_xy /= 1000
    print(f'[INFO LOAD] data: mat_xy_arr, path: {path}')
    return usr_xy

def load_angle(ds_type):
    path = prop.angle_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(float)
    print(f"[INFO LOAD] data: angle_arr,  path: {path}")
    return data_arr

def load_xy(ds_type):
    path = prop.xy_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(float)
    print(f"[INFO LOAD] data: xy_arr,  path: {path}")
    return data_arr

def load_group_table(ds_type):
    path = prop.group_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(int)
    print(f"[INFO LOAD] data: group_table,  path: {path}")
    return data_arr

def load_eval(ds_type):
    path = prop.eval_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(float)
    print(f"[INFO LOAD] data: cap_list,  path: {path}")
    return data_arr

def load_closest_user(ds_type):
    path = prop.cls_usr_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(int)
    print(f"[INFO LOAD] data: closest_user,  path: {path}")
    return data_arr

def load_usr_haps_angle(ds_type):
    data_label = ['azimuth', 'elevation', 'distance']
    for i in range(3):
        path = prop.usr_ant_path[i] + ds_type + '.csv'
        arr = load_csv(path).astype(float)
        print(f"[INFO LOAD] data: ua_{data_label[i]},  path: {path}")
        if i==0:
            row, col = arr.shape
            data_arr = np.zeros([row, col, 3], dtype=float)
            data_arr[:,:,0] = arr
        else:
            data_arr[:,:,i] = arr
    return data_arr

def load_sinr(ds_type):
    path = prop.sinr_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(float)
    print(f"[INFO LOAD] data: SINR,  path: {path}")
    return data_arr

def load_snr(ds_type):
    path = prop.snr_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(float)
    print(f"[INFO LOAD] data: SNR,  path: {path}")
    return data_arr

def load_interference(ds_type):
    path = prop.intf_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(float)
    print(f"[INFO LOAD] data: intf_arr  path: {path}")
    return data_arr

def load_noise(ds_type):
    path = prop.noise_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(float)
    print(f"[INFO LOAD] data: noise_arr,  path: {path}")
    return data_arr

def load_sig(ds_type):
    path = prop.sig_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(float)
    print(f"[INFO LOAD] data: sig_arr,  path: {path}")
    return data_arr

def load_group_minAD_arr(ds_type):
    path = prop.group_minAD_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(float)
    print(f"[INFO LOAD] data: group_mAD_arr,  path: {path}")
    return data_arr

def load_user_minAD_arr(ds_type):
    path = prop.usr_minAD_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(float)
    print(f"[INFO LOAD] data: user_mAD_arr,  path: {path}")
    return data_arr

def load_flop(ds_type):
    path = prop.flop_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(float)
    print(f"[INFO LOAD] data: flop_arr,  path: {path}")
    return data_arr

def load_test_arr(ds_type):
    path = prop.test_path + ds_type + '.csv'
    data_arr = load_csv(path).astype(float)
    print(f"[INFO LOAD] data: test_arr,  path: {path}")
    return data_arr