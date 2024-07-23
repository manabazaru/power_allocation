import numpy as np
from base_station import BaseStations
from parameters import Parameter as param
class TerrestrialComunication():
    def __init__(self, usr_base_sector_angr_arr, bs_usr_n, base_stations: BaseStations, 
                 usr_gain):
        self.usr_n = usr_base_sector_angr_arr.shape[0]
        self.bs_n = usr_base_sector_angr_arr.shape[1]
        self.sec_n = usr_base_sector_angr_arr.shape[2]
        self.ang_arr = usr_base_sector_angr_arr[:,:,:,:2]
        self.d_arr = usr_base_sector_angr_arr[:,:,:,2]
        self.wv_len = param.c/param.carrier_freq
        self.freq = param.carrier_freq
        self.bw = param.bandwidth
        self.usr_height = 0.001
        self.bs_usr_n = bs_usr_n
        self.ue_usr_n = self.usr_n - self.bs_usr_n
        self.bss = base_stations
        # for channel coefficient h
        self.rcv_gain = usr_gain
        self.radiat_ptn = np.zeros([self.usr_n, self.bs_n, self.sec_n])
        self.path_loss = np.zeros([self.usr_n, self.bs_n, self.sec_n])
        self.fading = np.zeros([self.usr_n, self.bs_n, self.sec_n], dtype=np.complex64)
        self.g = np.zeros([self.usr_n, self.bs_n, self.sec_n], dtype=np.complex64)
        self.set_all()
        
    def herm_transpose(self, matrix):
        return np.conjugate(matrix.T, dtype=np.complex64)
    
    def calc_hata_path_loss(self, f, height_m, usr_height_m, dis_km, com_type):
        loss = 46.3 + 33.9*np.log10(f) - 13.82*np.log10(height_m) + (44.9-6.55*np.log10(height_m))*np.log10(dis_km)
        loss -= (1.1*np.log10(f)-0.7)*usr_height_m - (1.56*np.log10(f)-0.8)
        if com_type == 'urban':
            loss += 3
        path_loss = 10**(-loss/20)
        return path_loss
    
    def set_all(self):
        bs_list = self.bss.bs_list
        for bs_idx, bs in enumerate(bs_list):
            tilt = bs.elev_tilt
            azi_3db = bs.azi_3db
            elev_3db = bs.elev_3db
            sd_att = bs.side_attenuation
            max_att = bs.max_attenuation
            max_gain = bs.max_gain
            height = bs.height
            for usr_idx in range(self.usr_n):
                for sec_idx in range(self.sec_n):
                    # set radiation pattern
                    ang = self.ang_arr[usr_idx, bs_idx, sec_idx]
                    az = ang[0]
                    el = ang[1]
                    v_radiat = -min(12*((el+tilt)/elev_3db)**2, sd_att)
                    h_radiat = -min(12*(az/azi_3db)**2, max_att)
                    radiat = -min(-(v_radiat+h_radiat), max_att)
                    gain_db = max_gain + radiat + self.rcv_gain
                    gain = 10**(gain_db/20)
                    self.radiat_ptn[usr_idx, bs_idx, sec_idx] = gain
                    # path loss
                    loss = self.calc_hata_path_loss(self.freq, height*1000, self.usr_height*1000,
                                                    self.d_arr[usr_idx, bs_idx, sec_idx], 'suburban')
                    self.path_loss[usr_idx, bs_idx, sec_idx] = loss
                    # fading
                    x = np.random.normal(0, 1, [self.usr_n, self.bs_n, self.sec_n])
                    y = np.random.normal(0, 1, [self.usr_n, self.bs_n, self.sec_n])
                    self.fading = (x + 1j * y) / np.sqrt(2)
        self.g = self.path_loss * self.radiat_ptn * self.fading       
    