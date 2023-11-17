from parameters import Parameter as param
import numpy as np

class BeamForming():
    def __init__(self, angr_arr):
        self.usr_n = angr_arr.shape[0]
        self.ant_n = angr_arr.shape[1]
        self.ang_arr = angr_arr[:,:,:2]
        self.d_arr = angr_arr[:,:,2]
        self.wv_len = param.c/param.carrier_freq
        self.is_set = False
        # for channel coefficient h
        self.path_loss = np.zeros([self.usr_n, self.ant_n])
        self.phs_rot = np.zeros([self.usr_n, self.ant_n],dtype=complex)
        self.radiat_ptn = np.zeros([self.usr_n, self.ant_n])
        self.h = np.zeros([self.usr_n, self.ant_n],dtype=complex)
        self.w = np.zeros([self.usr_n, self.ant_n],dtype=complex).T
        # for gain
        self.bw = param.bandwidth
        self.three_bw_ang = param.three_bandwidth_angle
        self.max_att = param.max_attenuation
        self.sd_att = param.side_lobe_attenuation
        self.trans_gain = param.trans_gain
        self.rcv_gain = param.rcv_gain
        
        
    def herm_transpose(self, matrix):
        return np.conjugate(matrix.T)
    
    def set_path_loss(self):
        p = 1 / (4*np.pi*self.d_arr/self.wv_len)
        self.path_loss = p
    
    def set_phase_rotation(self):
        phs_rot = np.exp(2*np.pi*self.d_arr / self.wv_len * 1j)
        self.phs_rot = phs_rot
    
    def calc_gain(self, ang):
        az = ang[0]
        el = ang[1]
        v_radiat = -min(12*(el/self.three_bw_ang)**2, self.sd_att)
        h_radiat = -min(12*(az/self.three_bw_ang)**2, self.max_att)
        radiat = -min(-(v_radiat+h_radiat), self.max_att)
        gain_db = self.trans_gain + radiat + self.rcv_gain
        gain = 10**(gain_db/10)
        return gain

    def set_radiation_pattern(self):
        for usr in range(self.usr_n):
            for ant in range(self.ant_n):
                ang = self.ang_arr[usr, ant]
                gain = self.calc_gain(ang)
                self.radiat_ptn[usr, ant] = gain
    
    def set_h(self):
        self.set_path_loss()
        self.set_phase_rotation()
        self.set_radiation_pattern()
        self.h = self.path_loss*self.phs_rot*self.radiat_ptn
    
    def set_w(self):
        for usr in range(self.usr_n):
            w = 1/len(self.w[:,usr])
            self.w[:,usr] = w
    
    def set_all(self):
        self.set_h()
        self.set_w()
        self.is_set = True

    def get_usr_n(self):
        return self.usr_n
    
    def get_h(self):
        return self.h
    
    def get_w(self):
        return self.w
    
    def get_is_set(self):
        return self.is_set

class ZeroForcing(BeamForming):
    def __init__(self, angr_arr):
        super().__init__(angr_arr)
        self.set_all()

    def set_w(self):
        hherm = self.herm_transpose(self.h)
        h_hherm = np.dot(self.h, hherm)
        w_unnorm = np.dot(hherm, np.linalg.inv(h_hherm))
        for usr in range(self.usr_n):
            w_vec = w_unnorm[:,usr]
            w_usr_sum = np.sqrt(abs(sum(w_vec*np.conjugate(w_vec))))
            self.w[:,usr] = w_unnorm[:,usr] / w_usr_sum
        """
        total_w_usr_sum = 0
        absw_list = []        
            absw_list.append(w_usr_sum)
            total_w_usr_sum += w_usr_sum
        hhhh = np.dot(self.h, w_unnorm)
        abs_h = np.sqrt(self.h*np.conjugate(self.h))
        abs_hhhh = np.sqrt(hhhh * np.conjugate(hhhh))
        h1_h2 = self.h[0] * np.conjugate(self.h[1])
        h1_unit = self.h[0] / np.sum(self.h[0]*np.conjugate(self.h[0]))**0.5
        h2_unit = self.h[1] / np.sum(self.h[1]*np.conjugate(self.h[1]))**0.5
        h1_h2_unit = h1_unit * np.conjugate(h2_unit)
        inner_prct = np.sum(h1_h2_unit * np.conjugate(h1_h2_unit))
        inner_prct2 = np.sum(h1_h2 * np.conjugate(h1_h2))
        print(f"inner_product = {inner_prct}")
        print(f"inner_product2 = {inner_prct2}")
        print(f"absw_usr_sum: {absw_list}")
        print(f"||g|| = {np.sum(self.radiat_ptn**2, 1)}")
        print(f"||p|| = {np.sum(self.path_loss**2, 1)}")
        print(f"||h|| = {np.sum(self.h*np.conjugate(self.h), 1)}")
        abs_hhhh_arr = abs_hhhh.reshape(len(self.h)**2)
        config_arr = np.zeros(50, dtype=int)
        for num in abs_hhhh_arr:
            if abs(num)==0:
                continue
            idx = -int((np.log10(num)))
            config_arr[idx] += 1
        print(config_arr)
        """