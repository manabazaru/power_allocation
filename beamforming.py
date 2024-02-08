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