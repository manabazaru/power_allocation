import numpy as np
import parameters as param

class TwoStagePrecoding():
    def __init__(self, angr_arr, bs_usr_n, M):
        self.usr_n = angr_arr.shape[0]
        self.ant_n = angr_arr.shape[1]
        self.ang_arr = angr_arr[:,:,:2]
        self.d_arr = angr_arr[:,:,2]
        self.wv_len = param.c/param.carrier_freq
        self.bs_usr_n = bs_usr_n
        self.ue_usr_n = self.usr_n - self.bs_usr_n
        self.M = M
        # for channel coefficient h
        self.path_loss = np.zeros([self.usr_n, self.ant_n])
        self.phs_rot = np.zeros([self.usr_n, self.ant_n],dtype=np.complex64)
        self.radiat_ptn = np.zeros([self.usr_n, self.ant_n])
        self.h = np.zeros([self.usr_n, self.ant_n],dtype=np.complex64)
        # for gain
        self.bw = param.bandwidth
        self.three_bw_ang = param.three_bandwidth_angle
        self.max_att = param.max_attenuation
        self.sd_att = param.side_lobe_attenuation
        self.trans_gain = param.trans_gain
        self.rcv_gain = param.rcv_gain     
        # for precoding matrix W_nf, W_bf
        self.w_nf = np.zeros([self.ant_n, M], dtype=np.complex64)
        self.w_bf = np.zeros([M, self.ue_usr_n], dtype=np.complex64)
        self.w = np.zeros([self.ant_n, self.ue_usr_n], dtype=np.complex64)

    def herm_transpose(self, matrix):
        return np.conjugate(matrix.T, dtype=np.complex64)
    
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
        gain = 10**(gain_db/20)
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
    
    def set_w_nf(self):
        bs_h = self.h[self.ue_usr_n:]
        u, sigma, vh = np.linalg.svd(bs_h)
        vh_h = self.herm_transpose(vh)
        self.w_nf = vh[:,self.bs_usr_n:self.bs_usr_n+self.M]
    
    def set_w_bf(self):
        ue_h = np.dot(self.h[:self.ue_usr_n], self.w_nf)
        hherm = self.herm_transpose(ue_h)
        h_hherm = np.dot(ue_h, hherm)
        u, s, vh = np.linalg.svd(h_hherm)
        s_inv = np.zeros_like(s)
        
        for i in range(len(s)):
            if s[i] > 1e-20:
                s_inv[i] = 1.0 / s[i]
        
        S_inv = np.diag(s_inv)
        
        h_hherm_inv = vh.conj().T.dot(S_inv).dot(u.conj().T)
        w_unnorm = np.dot(self.w_nf, np.dot(hherm, h_hherm_inv))
        for usr in range(self.ue_usr_n):
            w_vec = w_unnorm[:, usr]
            w_usr_sum = np.sqrt(abs(sum(w_vec*np.conjugate(w_vec))))
            self.w[:,usr] = w_unnorm[:,usr] / w_usr_sum
