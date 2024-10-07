import numpy as np

# args = xyz_arr, angr_arr, xyz, angr, x-y-z or az-el-r
def get_data_from_args(args):
    if len(args) == 1:
        if args[0].ndim == 1:
            d = args[0]
            d1 = d[0]
            d2 = d[1]
            d3 = d[2]
        else:
            d = args[0]
            d1 = d[:,0]
            d2 = d[:,1]
            d3 = d[:,2]
    else:
        d1 = args[0]
        d2 = args[1]
        d3 = args[2]
    return d1, d2, d3

def get_data_in_arr(arr, d1, d2, d3):
    if arr.ndim == 1:
        arr[0] = d1
        arr[1] = d2
        arr[2] = d3
    else:
        arr[:,0] = d1
        arr[:,1] = d2
        arr[:,2] = d3
    return arr

def ints2arr(*args):
    size = len(args)
    arr = np.zeros(size)
    for arg_idx in range(size):
        arr[arg_idx] = args[arg_idx]
    return arr

def cut_last_factor(arr):
    if arr.ndim == 1:
        return arr[:len(arr)-1]
    else:
        return arr[:,:len(arr[0])-1]

def add_factor(arr, factor):
    if arr.ndim == 1:
        new_arr = np.zeros(3)
        new_arr[:2] = arr
        new_arr[2] = factor
    else:
        size = len(arr)
        new_arr = np.zeros([size,3])
        new_arr[:,:2] = arr
        new_arr[:,2] += factor
    return new_arr

def calc_x(*args):
    az, el, r = get_data_from_args(args)
    az_rad = np.deg2rad(az)
    el_rad = np.deg2rad(el)
    x = r * np.cos(el_rad) * np.cos(az_rad)
    return x

def calc_y(*args):
    az, el, r = get_data_from_args(args)
    az_rad = np.deg2rad(az)
    el_rad = np.deg2rad(el)
    y = r * np.cos(el_rad) * np.sin(az_rad)
    return y

def calc_z(*args):
    az, el, r = get_data_from_args(args)
    el_rad = np.deg2rad(el)
    z = r*np.sin(el_rad)
    return z

def calc_az(*args):
    x, y, z = get_data_from_args(args)
    az_rad = np.arctan2(y,x)
    az = np.rad2deg(az_rad)
    return az

def calc_el(*args):
    x, y, z = get_data_from_args(args)
    r = np.sqrt(x**2+y**2+z**2)
    el_rad = np.arcsin(z/r)
    el = np.rad2deg(el_rad)
    return el

def calc_r(*args):
    x, y, z = get_data_from_args(args)
    r = np.sqrt(x**2+y**2+z**2)
    return r

def xyz2angr(xyz_arr):
    angr_arr = np.zeros(xyz_arr.shape)
    az = calc_az(xyz_arr)
    el = calc_el(xyz_arr)
    r = calc_r(xyz_arr)
    angr_arr = get_data_in_arr(angr_arr, az, el, r)
    return angr_arr

def angr2xyz(angr_arr):
    xyz_arr = np.zeros(angr_arr.shape)
    x = calc_x(angr_arr)
    y = calc_y(angr_arr)
    z = calc_z(angr_arr)
    xyz_arr = get_data_in_arr(xyz_arr, x, y, z)
    return xyz_arr

def xyz2xy(xyz_arr):
    xy_arr = cut_last_factor(xyz_arr)
    return xy_arr

def angr2ang(angr_arr):
    ang_arr = cut_last_factor(angr_arr)
    return ang_arr

def xy2xyz(xy_arr, z):
    return add_factor(xy_arr, z)

def ang2angr(ang_arr, r):
    return add_factor(ang_arr, r)

def ang2angr_with_z(ang_arr, z):
    if ang_arr.ndim == 1:
        el = ang_arr[1]
    else:
        el = ang_arr[:,1]
    el_rad = np.deg2rad(el)
    r = z/np.sin(el_rad)
    return add_factor(ang_arr, r)

def rotate_with_yaw(xyz_arr, angle):
    new_xyz_arr = np.zeros(xyz_arr.shape)
    ang_rad = np.deg2rad(angle)
    rotate_matrix = np.array([[np.cos(ang_rad), -1*np.sin(ang_rad), 0],
                              [np.sin(ang_rad), np.cos(ang_rad),    0],
                              [0,               0,                  1]])
    if xyz_arr.ndim == 1:
        new_xyz_arr = np.dot(rotate_matrix, xyz_arr)
    else:
        for usr in range(len(xyz_arr)):
            new_xyz_arr[usr] = np.dot(rotate_matrix, xyz_arr[usr])
    return new_xyz_arr

def rotate_with_pitch(xyz_arr, angle):
    new_xyz_arr = np.zeros(xyz_arr.shape)
    ang_rad = np.deg2rad(angle)
    rotate_matrix = np.array([[np.cos(ang_rad),    0, np.sin(ang_rad)],
                              [0,                  1,               0],
                              [-1*np.sin(ang_rad), 0, np.cos(ang_rad)]])
    if xyz_arr.ndim == 1:
        new_xyz_arr = np.dot(rotate_matrix, xyz_arr)
    else:
        for usr in range(len(xyz_arr)):
            new_xyz_arr[usr] = np.dot(rotate_matrix, xyz_arr[usr])
    return new_xyz_arr

def calc_az_dif(az1, az2):
    az_dif = abs(az1-az2)
    if az_dif > 180:
        az_dif = 360 - az_dif
    return az_dif

def calc_ang_dif(arr1, arr2):
    ang_dif = abs(arr1-arr2)
    az_dif = ang_dif[0]
    if az_dif > 180:
        az_dif = 360 - az_dif
    ang_dif[0] = az_dif
    return ang_dif

def turn_el(ang_arr):
    new_ang_arr = np.zeros(ang_arr.shape)
    new_ang_arr[:,:] = ang_arr[:,:]
    if ang_arr[0,1] < 0:
        new_ang_arr[:,1] *= -1
    return new_ang_arr

def sort_arr(arr):
    new_arr = np.sort(arr)
    return new_arr

def add_cumulative_ratio(arr):
    n = len(arr)
    ratio_arr = np.arange(n) / n
    new_arr = np.stack([arr, ratio_arr])
    return new_arr

def get_heatmap_data_from_xy_arr(xy_arr, block_n, radius):
    scale = radius * 2 / block_n
    block_population = np.zeros([block_n, block_n], dtype=int)
    for xy in xy_arr:
        block_indices = np.array((xy+radius)//scale, dtype=int)
        block_population[block_indices[0], block_indices[1]] += 1
    return block_population

def get_block_indices_of_heatmap_from_xy_arr(xy_arr, block_n, radius):
    scale = radius * 2 / block_n
    block_idc_arr = np.zeros([len(xy_arr), 2], dtype=int)-1
    for xy_idx in range(len(xy_arr)):
        xy = xy_arr[xy_idx]
        block_idc = np.array((xy+radius)//scale, dtype=int)
        block_idc_arr[xy_idx] = block_idc
    return block_idc_arr

def xy2ang(xy_arr, z):
    xyz = xy2xyz(xy_arr, z)
    angr = xyz2angr(xyz)
    ang = angr2ang(angr)
    return ang

def ang2xy(ang_arr, z):
    angr = ang2angr_with_z(ang_arr, z)
    xyz = angr2xyz(angr)
    xy = xyz2xy(xyz)
    return xy