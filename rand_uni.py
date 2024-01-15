import numpy as np
from parameters import Parameter as param
import fig

def generate_random_uniform_usr_xy(size, com_r):
    com_r_arr = np.sqrt(np.random.random_sample(size)) * com_r
    az_rad = 2*np.pi*(np.random.random_sample(size) - 0.5*np.ones(size))
    x = com_r_arr*np.cos(az_rad)
    y = com_r_arr*np.sin(az_rad)
    xy_arr = np.array([x,y]).T
    print(f"[INFO RANDUNI] Generating random uniform xy_arr (r={com_r}, size={size})")
    return xy_arr

def generate_random_usr_xy_in_donut_erea(size, i_r, o_r):
    com_r_arr = np.sqrt(np.random.random_sample(size) * (1-i_r**2/o_r**2) + i_r**2/o_r**2) * o_r
    az_rad = 2*np.pi*(np.random.random_sample(size)-0.5*np.ones(size))
    x = com_r_arr*np.cos(az_rad)
    y = com_r_arr*np.sin(az_rad)
    xy_arr = np.array([x,y]).T
    return xy_arr

def generate_random_usr_xy_on_edge(size, com_r):
    az_rad = 2*np.pi*(np.random.random_sample(size)-0.5*np.ones(size))
    x = com_r*np.cos(az_rad)
    y = com_r*np.sin(az_rad)
    xy_arr = np.array([x,y]).T
    return xy_arr

def generate_usr_xy1(size, com_r, index):
    com_r_arr = (np.random.random_sample(size))**index * com_r
    az_rad = 2*np.pi*(np.random.random_sample(size) - 0.5*np.ones(size))
    x = com_r_arr*np.cos(az_rad)
    y = com_r_arr*np.sin(az_rad)
    xy_arr = np.array([x, y]).T
    return xy_arr

def generate_usr_xy2(size, com_r, index, point):
    com_r_arr = (np.random.random_sample(size))**index * com_r
    usrs_point = size // point
    surplus = size - usrs_point*point
    az_rad = np.zeros(size)
    for i in range(point):
        for j in range(usrs_point):
            az_rad[surplus+i*usrs_point+j] = (i+1) * 2*np.pi / point
    az_rad += 2*np.pi*np.random.normal(0,1,size) / point / 5
    for i in range(len(az_rad)):
        if az_rad[i] < -np.pi:
            az_rad[i] += np.pi*2
        elif az_rad[i] > np.pi:
            az_rad[i] -= np.pi*2
    x = com_r_arr*np.cos(az_rad)
    y = com_r_arr*np.sin(az_rad)
    xy_arr = np.array([x, y]).T
    return xy_arr