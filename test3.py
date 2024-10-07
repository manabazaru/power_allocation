import numpy as np
import haps
from base_station import BaseStations
from terrestrial import TerrestrialComunication as tc
from beamforming import TwoStagePrecoding as precoding
from parameters import Parameter as param
from integrated_environment import IntegratedEnvironment as ie
from integrated_environment import IntegratedEnvironment2 as ie2
from matplotlib import pyplot as plt
import csv

iter = 1
ang_start = -360
ang_end = -1
ang_dif = 4
bs_r_list = [5, 10, 15]
haps_usr_r_dif = 1
com_r = 20
r_arr = np.array([i for i in range(1, com_r+1, haps_usr_r_dif)])
ang_arr = np.array([i for i in range(ang_start, ang_end+1, ang_dif)])

data = np.zeros([len(bs_r_list), int(com_r/haps_usr_r_dif), int((ang_end-ang_start)/ang_dif+1), iter], dtype=float)
for bs_idx, bs_r in enumerate(bs_r_list):
    for r_idx, r in enumerate(r_arr):
        for ang_idx, ang_deg in enumerate(ang_arr):
            for i in range(iter):
                # print(bs_idx, r_idx, ang_idx, i)
                # print(len(bs_r_list), len(r_arr), len(ang_arr))
                bs_size = 1
                haps_com_r = 20
                usrs_per_sec = 1
                bs_xy_arr = np.array([[bs_r*np.cos(i/180*np.pi), bs_r*np.sin(i/180*np.pi)] for i in range(-180,180,int(360/bs_size))])
                height_arr = np.zeros(bs_size)+0.051
                com_radius_arr = np.zeros(bs_size) + 2
                azi_3db_arr = np.zeros(bs_size) + 70
                elev_3db_arr = np.zeros(bs_size) + 10
                elev_tilt_arr = np.zeros(bs_size) + 1.15
                side_att_arr = np.zeros(bs_size) + 25
                max_att_arr = np.zeros(bs_size) + 20
                max_gain_arr = np.zeros(bs_size) + 14
                usr_per_sec_arr = np.zeros(bs_size, dtype=int) + usrs_per_sec
                sec_size = 3
                usr_height = 0.001
                haps_usr_n = 1
                haps_xy_arr = np.array([[r*np.cos(i/180*np.pi), r*np.sin(i/180*np.pi)] for i in range(ang_deg,0,int(360/haps_usr_n))])
                usr_xy_arr = np.concatenate([haps_xy_arr, bs_xy_arr])
                side_antenna_n = 5
                m = side_antenna_n**2 - bs_size*sec_size*usrs_per_sec
                bs_pwr = 20
                haps_total_pwr = 120
                usr_gain = -3
                bss = BaseStations(bs_size, height_arr, com_radius_arr, bs_xy_arr, max_gain_arr, azi_3db_arr,
                                elev_3db_arr, elev_tilt_arr, side_att_arr, max_att_arr, 
                                sec_size, users_per_sector_arr=usr_per_sec_arr)
                bss_xy_arr = bss.get_users_xy_arr()
                bs_angr_arr = bss.calc_user_bs_sector_angr(usr_xy_arr,usr_height)
                p_haps = haps.VariableAntennaPlanarHAPS(side_antenna_n)
                int_nev = ie(bss, p_haps, haps_xy_arr, m, usr_gain, bs_pwr, haps_total_pwr)
                # int_nev2 = ie2(bss, p_haps, haps_xy_arr, m, usr_gain, bs_pwr, haps_power_arr)
                # bs_sinr_arr = int_nev.bs_sinr
                haps_sinr_arr = int_nev.haps_sinr
                # bs_sinr_arr2 = int_nev2.bs_sinr
                # haps_sinr_arr2 = int_nev2.haps_sinr
                # bs_sinr_db_arr = 10 * np.log10(bs_sinr_arr)
                haps_sinr_db_arr = 10 * np.log10(haps_sinr_arr)
                # bs_sinr_db_arr2 = 10 * np.log10(bs_sinr_arr2)
                # haps_sinr_db_arr2 = 10 * np.log10(haps_sinr_arr2)
                # print("sinr", haps_sinr_db_arr[0])
                data[bs_idx,r_idx, ang_idx, i] = haps_sinr_db_arr[0]

data_ave = np.zeros([len(bs_r_list), int(com_r/haps_usr_r_dif), int((ang_end-ang_start)/ang_dif+1)], dtype=float)
data_ave = np.average(data, axis=3)
x_arr = np.zeros([len(bs_r_list), int(int(com_r/haps_usr_r_dif)*int((ang_end-ang_start)/ang_dif+1))], dtype=float)
y_arr = np.zeros([len(bs_r_list), int(int(com_r/haps_usr_r_dif)*int((ang_end-ang_start)/ang_dif+1))], dtype=float)
c_arr = np.zeros([len(bs_r_list), int(int(com_r/haps_usr_r_dif)*int((ang_end-ang_start)/ang_dif+1))], dtype=float)
for i in range(len(bs_r_list)):
    idx = 0
    for r_idx, r in enumerate(r_arr):
        for ang_idx, ang in enumerate(ang_arr):
            x = r * np.cos(ang/180*np.pi)
            y = r * np.sin(ang/180*np.pi)
            c = data_ave[i, r_idx, ang_idx]
            x_arr[i, idx] = x
            y_arr[i, idx] = y
            c_arr[i, idx] = c
            idx += 1
    fig = plt.figure()
    plt.scatter(x_arr[i], y_arr[i], s=10, c=c_arr[i], cmap='jet')
    plt.xlim(-haps_com_r, haps_com_r)
    plt.ylim(-haps_com_r, haps_com_r)
    plt.clim(-20, 40)
    plt.colorbar()
    plt.show()
with open(f'./test3_ant={param.planar_antenna_size_of_side**2}.csv', 'w') as f:
    writer = csv.writer(f)
    for idx in range(c_arr.shape[1]):
        data = [float(c_arr[0, idx])]
        writer.writerow(data)
    
print(data_ave)
print(ang_arr)
print(r_arr)
"""fig = plt.figure()
plt.scatter(bss_xy_arr[:,0], bss_xy_arr[:,1], s=10, c=bs_sinr_db_arr, cmap='jet')
plt.xlim(-haps_com_r, haps_com_r)
plt.ylim(-haps_com_r, haps_com_r)
plt.clim(-40, 20)
plt.colorbar()
plt.show()

fig2 = plt.figure()
plt.scatter(bss_xy_arr[:,0], bss_xy_arr[:,1], s=10, c=bs_sinr_db_arr2, cmap='jet')
plt.xlim(-haps_com_r, haps_com_r)
plt.ylim(-haps_com_r, haps_com_r)
plt.clim(-40, 20)
plt.colorbar()
plt.show()"""

"""fig3 = plt.figure()
plt.scatter(haps_xy_arr[:,0], haps_xy_arr[:,1], s=10, c=haps_sinr_db_arr, cmap='jet')
plt.xlim(-haps_com_r, haps_com_r)
plt.ylim(-haps_com_r, haps_com_r)
plt.clim(0, 40)
plt.colorbar()
plt.show()

fig3 = plt.figure()
plt.scatter(haps_xy_arr[:,0], haps_xy_arr[:,1], s=10, c=haps_sinr_db_arr2, cmap='jet')
plt.xlim(-haps_com_r, haps_com_r)
plt.ylim(-haps_com_r, haps_com_r)
plt.clim(0,40)
plt.colorbar()
plt.show()
"""