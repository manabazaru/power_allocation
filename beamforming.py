from parameters import Parameter as param
import numpy as np
from base_station import BaseStation as base
import utils

def cos_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

class TwoStagePrecoding():
    def __init__(self, angr_arr, bs_usr_n, M):
        self.usr_n = angr_arr.shape[0]
        self.ant_n = angr_arr.shape[1]
        self.angr_arr = angr_arr
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
        self.w_nf_test = np.zeros(self.w_nf.shape, dtype=np.complex64)
        self.bs_test = 0
        self.set_all()
        
    def set_all(self):
        self.set_h()
        self.set_w_nf()
        self.set_w_bf()
    
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
    
    def set_w_nf(self):
        bs_h = self.h[self.ue_usr_n:]
        u, sigma, vh = np.linalg.svd(bs_h)
        vh_h = self.herm_transpose(vh)
        self.w_nf = vh_h[:,self.bs_usr_n:self.bs_usr_n+self.M]
        for i in range(len(self.w_nf)):
            for j in range(len(self.w_nf[i])):
                self.w_nf_test[i][j] = self.w_nf[i][j]
        self.bs_test = bs_h
    
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
    
    def get_power_allocation(self, total_pwr):
        score_arr = np.zeros(self.ue_usr_n)
        cls_usr_idx = np.zeros(self.ue_usr_n, dtype=int)
        for h_idx in range(self.ue_usr_n):
            minimum = 999999999999999
            min_idx = -1
            h_angr = self.angr_arr[h_idx]
            h_xyz = utils.angr2xyz(h_angr)
            for b_idx in range(self.bs_usr_n):
                b_angr = self.angr_arr[self.ue_usr_n+b_idx]
                b_xyz = utils.angr2xyz(b_angr)
                dis = np.sum((h_xyz-b_xyz)**2)
                if dis < minimum:
                    min_idx = b_idx
                    minimum = dis
            cls_usr_idx[h_idx] = min_idx
            haps_h = self.h[h_idx]
            bs_h = self.h[min_idx]
            haps_h_real = np.real(haps_h)
            haps_h_img = np.imag(haps_h)
            bs_h_real = np.real(bs_h)
            bs_h_img = np.imag(bs_h)
            v1 = np.concatenate([haps_h_real, -1*haps_h_img])
            v2 = np.concatenate([bs_h_real, -1*bs_h_img])
            v3 = np.concatenate([bs_h_img, bs_h_real])
            s1 = abs(cos_similarity(v1, v2))
            s2 = abs(cos_similarity(v1, v3))
            s = max(s1, s2)
            score_arr[h_idx] = s
        return score_arr, cls_usr_idx

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
        self.phs_rot = np.zeros([self.usr_n, self.ant_n],dtype=np.complex64)
        self.radiat_ptn = np.zeros([self.usr_n, self.ant_n])
        self.h = np.zeros([self.usr_n, self.ant_n],dtype=np.complex64)
        self.w = np.zeros([self.usr_n, self.ant_n],dtype=np.complex64).T
        # for gain
        self.bw = param.bandwidth
        self.three_bw_ang = param.three_bandwidth_angle
        self.max_att = param.max_attenuation
        self.sd_att = param.side_lobe_attenuation
        self.trans_gain = param.trans_gain
        self.rcv_gain = param.rcv_gain
         
        
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
        self.cond = 0
        self.set_all()

    def set_w(self):
        hherm = self.herm_transpose(self.h)
        h_hherm = np.dot(self.h, hherm)
        self.cond = np.linalg.cond(h_hherm)
        u, s, vh = np.linalg.svd(h_hherm, full_matrices=False)  # full_matrices=Falseでu, vhの形状をarrに合わせる
        s_inv = np.zeros_like(s)

        # ゼロでない特異値の逆数を計算
        for i in range(len(s)):
            if s[i] > 1e-20:  # ゼロに近い値を無視
                s_inv[i] = 1.0 / s[i]

        # S_invを対角行列にする
        S_inv = np.diag(s_inv)

        # 複素数行列の場合は共役転置を使用
        h_hherm_inv = vh.conj().T.dot(S_inv).dot(u.conj().T)
        # h_hherm_inv = np.linalg.inv(h_hherm)
        w_unnorm = np.dot(hherm, h_hherm_inv)
        total_w = 0
        for usr in range(self.usr_n):
            w_vec = w_unnorm[:,usr]
            w_usr_sum = np.sqrt(abs(sum(w_vec*np.conjugate(w_vec))))
            self.w[:,usr] = w_unnorm[:,usr] / w_usr_sum
            total_w += w_usr_sum
        """
        ave = total_w / self.usr_n
        with open(f'test_{self.usr_n}_r={5}_Nt={param.planar_antenna_size_of_side**2}.txt', 'a') as f:
            f.write(str(ave)+'\n')
        """
        
    def get_cond(self):
        return self.cond

class ZeroForcing2(BeamForming):
    def __init__(self, angr_arr, haps_usr_n):
        super().__init__(angr_arr)
        self.haps_usr_n = haps_usr_n
        self.w = np.zeros([self.haps_usr_n, self.ant_n],dtype=np.complex64).T
        self.cond = 0
        self.set_all()

    def set_w(self):
        haps_h = self.h[:self.haps_usr_n]
        hherm = self.herm_transpose(haps_h)
        h_hherm = np.dot(haps_h, hherm)
        self.cond = np.linalg.cond(h_hherm)
        u, s, vh = np.linalg.svd(h_hherm, full_matrices=False)  # full_matrices=Falseでu, vhの形状をarrに合わせる
        s_inv = np.zeros_like(s)

        # ゼロでない特異値の逆数を計算
        for i in range(len(s)):
            if s[i] > 1e-20:  # ゼロに近い値を無視
                s_inv[i] = 1.0 / s[i]

        # S_invを対角行列にする
        S_inv = np.diag(s_inv)

        # 複素数行列の場合は共役転置を使用
        h_hherm_inv = vh.conj().T.dot(S_inv).dot(u.conj().T)
        # h_hherm_inv = np.linalg.inv(h_hherm)
        w_unnorm = np.dot(hherm, h_hherm_inv)
        total_w = 0
        for usr in range(self.haps_usr_n):
            w_vec = w_unnorm[:,usr]
            w_usr_sum = np.sqrt(abs(sum(w_vec*np.conjugate(w_vec))))
            self.w[:,usr] = w_unnorm[:,usr] / w_usr_sum
            total_w += w_usr_sum
        """
        ave = total_w / self.usr_n
        with open(f'test_{self.usr_n}_r={5}_Nt={param.planar_antenna_size_of_side**2}.txt', 'a') as f:
            f.write(str(ave)+'\n')
        """
        
    def get_cond(self):
        return self.cond