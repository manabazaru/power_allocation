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
bs_size = 6
haps_com_r = 20
usrs_per_sec = 1
bs_xy_arr = np.array([[10*np.cos(i/180*np.pi), 10*np.sin(i/180*np.pi)] for i in range(-180,180,int(360/bs_size))])
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
haps_usr_n = 30
haps_xy_arr = np.array([[15*np.cos(i/180*np.pi), 15*np.sin(i/180*np.pi)] for i in range(-180,180,int(360/haps_usr_n))])
usr_xy_arr = np.concatenate([haps_xy_arr, bs_xy_arr])
side_antenna_n = 14
m = side_antenna_n**2 - bs_size*sec_size*usrs_per_sec
bs_pwr = 20
haps_power_arr = np.zeros(haps_usr_n)+10
usr_gain = -3
##########################################################
bss = BaseStations(bs_size, height_arr, com_radius_arr, bs_xy_arr, max_gain_arr, azi_3db_arr,
                   elev_3db_arr, elev_tilt_arr, side_att_arr, max_att_arr, 
                   sec_size, users_per_sector_arr=usr_per_sec_arr)
bss_xy_arr = bss.get_users_xy_arr()
bs_angr_arr = bss.calc_user_bs_sector_angr(usr_xy_arr)
p_haps = haps.VariableAntennaPlanarHAPS(side_antenna_n)
int_nev = ie(bss, p_haps, haps_xy_arr, m, usr_gain, bs_pwr, haps_power_arr)
int_nev2 = ie2(bss, p_haps, haps_xy_arr, m, usr_gain, bs_pwr, haps_power_arr)
bs_sinr_arr = int_nev.bs_sinr
haps_sinr_arr = int_nev.haps_sinr
bs_sinr_arr2 = int_nev2.bs_sinr
haps_sinr_arr2 = int_nev2.haps_sinr
bs_sinr_db_arr = 10 * np.log10(bs_sinr_arr)
haps_sinr_db_arr = 10 * np.log10(haps_sinr_arr)
bs_sinr_db_arr2 = 10 * np.log10(bs_sinr_arr2)
haps_sinr_db_arr2 = 10 * np.log10(haps_sinr_arr2)
print(haps_sinr_db_arr)
print(bs_sinr_db_arr)
print(bs_sinr_db_arr2)
print(haps_sinr_db_arr2)

#########################################################
fig = plt.figure()
plt.scatter(bss_xy_arr[:,0], bss_xy_arr[:,1], s=10, c=bs_sinr_db_arr, cmap='jet')
plt.xlim(-haps_com_r, haps_com_r)
plt.ylim(-haps_com_r, haps_com_r)
plt.colorbar()
plt.show()

fig2 = plt.figure()
plt.scatter(bss_xy_arr[:,0], bss_xy_arr[:,1], s=10, c=bs_sinr_db_arr2, cmap='jet')
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

fig3 = plt.figure()
plt.scatter(haps_xy_arr[:,0], haps_xy_arr[:,1], s=10, c=haps_sinr_db_arr2, cmap='jet')
plt.xlim(-haps_com_r, haps_com_r)
plt.ylim(-haps_com_r, haps_com_r)
plt.colorbar()
plt.show()
