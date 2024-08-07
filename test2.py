import numpy as np
import haps
from base_station import BaseStations
from terrestrial import TerrestrialComunication as tc
from beamforming import TwoStagePrecoding as precoding
from parameters import Parameter as param
from integrated_environment import IntegratedEnvironment as ie
from integrated_environment import IntegratedEnvironment2 as ie2
from matplotlib import pyplot as plt

###########################################################
bs_size = 1
haps_com_r = 20
usrs_per_sec = 1
bs_xy_arr = np.array([[15*np.cos(i/180*np.pi), 15*np.sin(i/180*np.pi)] for i in range(-180,180,int(360/bs_size))])
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
haps_usr_n = 12
haps_xy_arr = np.array([[18*np.cos(i/180*np.pi), 18*np.sin(i/180*np.pi)] for i in range(-180,180,int(360/haps_usr_n))])
side_antenna_n = 14
m = side_antenna_n**2 - bs_size*sec_size*usrs_per_sec
bs_pwr = 20
haps_total_pwr = 120
usr_gain = -3
##########################################################
bss = BaseStations(bs_size, height_arr, com_radius_arr, bs_xy_arr, max_gain_arr, azi_3db_arr,
                   elev_3db_arr, elev_tilt_arr, side_att_arr, max_att_arr, 
                   sec_size, users_per_sector_arr=usr_per_sec_arr)
bss_xy_arr = bss.get_users_xy_arr()
p_haps = haps.VariableAntennaPlanarHAPS(side_antenna_n)
int_nev = ie(bss, p_haps, haps_xy_arr, m, usr_gain, bs_pwr, haps_total_pwr)
int_nev2 = ie2(bss, p_haps, haps_xy_arr, m, usr_gain, bs_pwr, haps_total_pwr)
bs_sinr_arr = int_nev.bs_sinr
haps_sinr_arr = int_nev.haps_sinr
bs_sinr_arr2 = int_nev2.bs_sinr
# haps_sinr_arr2 = int_nev2.haps_sinr
bs_sinr_db_arr = 10 * np.log10(bs_sinr_arr)
haps_sinr_db_arr = 10 * np.log10(haps_sinr_arr)
bs_sinr_db_arr2 = 10 * np.log10(bs_sinr_arr2)
# haps_sinr_db_arr2 = 10 * np.log10(haps_sinr_arr2)
# print(haps_sinr_db_arr)
# print(bs_sinr_db_arr)
# print(bs_sinr_db_arr2)
# print(haps_sinr_db_arr2)
# print(f"bs_sinr_db_arr:  average={np.average(bs_sinr_db_arr)}, mid={np.median}")

#########################################################
fig = plt.figure()
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
plt.show()

fig3 = plt.figure()
c1 = np.arange(haps_usr_n) * 30
c2 = np.zeros(bs_size * sec_size * usrs_per_sec) - 1000
c2[int_nev.cls_arr-haps_usr_n] = c1
x_arr = np.concatenate([haps_xy_arr[:,0], bss_xy_arr[:,0]])
y_arr = np.concatenate([haps_xy_arr[:,1], bss_xy_arr[:,1]])
c_arr = np.concatenate([c1, c2])
c_arr2 = np.concatenate([haps_sinr_db_arr, bs_sinr_db_arr])
print(c_arr)
print(f"haps_sinr:{haps_sinr_db_arr}")
print(f"bs_sinr_arr{bs_sinr_db_arr}")
plt.scatter(x_arr, y_arr, s=10, c=c_arr2, cmap='jet')
plt.xlim(-haps_com_r, haps_com_r)
plt.ylim(-haps_com_r, haps_com_r)
plt.colorbar()
plt.show()

fig3 = plt.figure()
plt.scatter(haps_xy_arr[:,0], haps_xy_arr[:,1], s=10, c=haps_sinr_db_arr, cmap='jet')
plt.xlim(-haps_com_r, haps_com_r)
plt.ylim(-haps_com_r, haps_com_r)
plt.colorbar()
plt.show()
