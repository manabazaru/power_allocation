from parameters import Parameter as param
from beamforming import BeamForming, ZeroForcing
import numpy as np

class GroupEvaluator():
    def __init__(self, bf: BeamForming, trans_pwr):
        self.bf = bf
        self.usr_n = bf.get_usr_n()
        self.h = bf.get_h()
        self.w = bf.get_w()
        self.bandwidth = param.bandwidth
        self.trans_pwr = trans_pwr
        self.noise_fig = param.noise_figure
        self.noise = 0
        self.snr = np.zeros(self.usr_n)
        self.interference = np.zeros(self.usr_n)
        self.noise_pwr_dens = param.noise_power_density
        self.sinr = np.zeros(self.usr_n)
        self.sum_capacity = 0
        self.sig_arr = np.zeros(self.usr_n)
        self.set_all()
    
    def set_noise(self):
        bandwidth_bd = 10 * np.log10(self.bandwidth)
        noise_dbm = self.noise_pwr_dens + bandwidth_bd + self.noise_fig
        self.noise = 10**((noise_dbm-30)/10)
    
    def set_SINR(self):
        pwr_per_usr = self.trans_pwr/self.usr_n
        for usr in range(self.usr_n):
            hu = self.h[usr]
            wu = self.w[:,usr]
            sig = abs(sum(hu*wu))**2 * pwr_per_usr
            intf = 0
            for usr2 in range(self.usr_n):
                if usr == usr2:
                    continue
                wi = self.w[:,usr2]
                intf += abs(sum(hu*wi))**2 * pwr_per_usr
            self.interference[usr] = intf
            self.snr[usr] = sig / self.noise
            self.sinr[usr] = sig / (intf + self.noise)
            self.sig_arr[usr] = sig
            huhu = np.sqrt(sum(hu*np.conjugate(hu)))
            # print(f"h_abs: {huhu}, d_arr: {self.bf.d_arr[usr]}")
            # print(f"{usr}:: sig: {sig}   intf:{intf}  ||hu||:{huhu} d_arr:{self.bf.d_arr[usr,0]}")
    
    def set_sum_capacity(self):
        sum_cap = 0
        for usr in range(self.usr_n):
            sum_cap += np.log2(1 + self.sinr[usr])
        sum_cap *= self.bandwidth
        self.sum_capacity = sum_cap
    
    def set_all(self):
        self.set_noise()
        self.set_SINR()
        self.set_sum_capacity()
    
    def get_sum_capacity(self):
        return self.sum_capacity
    
    def get_user_n(self):
        return self.usr_n
    
    def get_SINR(self):
        return self.sinr
    
    def get_interference(self):
        return self.interference
    
    def get_SNR(self):
        return self.snr
    
    def get_signal_pwr(self):
        return self.sig_arr
    
    def get_noise(self):
        return self.noise

    def get_h(self):
        return self.h
    
    def get_w(self):
        return self.w
    
class SystemEvaluator():
    def __init__(self, group_table, usr_ant_angr_arr, trans_pwr):
        self.group_table = group_table
        self.angr_arr = usr_ant_angr_arr
        self.trans_pwr = trans_pwr
        self.group_n = len(group_table)
        self.usr_n = 0
        self.eval_list = [-1 for i in range(self.group_n)]
        self.sum_cap_arr = np.zeros(self.group_n)
        self.set_all()
    
    def set_eval_list(self):
        print("[INFO EVAL] Initialization of Beamforming matrices is started.")
        print("            Now initializing  [", end="")
        load_period = int(self.group_n/20)
        load_ratio = load_period
        for group in range(self.group_n):
            if group >= load_ratio:
                print("=",end="")
                load_ratio += load_period
            mems = self.group_table[group]
            group_angr_arr = self.angr_arr[mems]
            bf = ZeroForcing(group_angr_arr)
            ev = GroupEvaluator(bf, self.trans_pwr)
            self.eval_list[group] = ev
        print(">] 100 %")

    def set_usr_n(self):
        for group in range(self.group_n):
            eval = self.eval_list[group]
            self.usr_n += eval.get_user_n()            
        
    def set_sum_cap_arr(self):
        print("[INFO EVAL] Calculation of sum capacities is started.")
        print("            Now calculating  [", end="")
        load_period = int(self.group_n/20)
        load_ratio = load_period
        for group in range(self.group_n):
            if -1 in self.eval_list:
                print("[INFO ERROR] Variable <eval_list> has not been set.")
            if group >= load_ratio:
                print("=",end="")
                load_ratio += load_period
            sum_cap = self.eval_list[group].get_sum_capacity()
            self.sum_cap_arr[group] = sum_cap
        print(">] 100 %")
    
    def set_all(self):
        self.set_eval_list()
        self.set_usr_n()
        self.set_sum_cap_arr()
    
    def get_sum_cap_arr(self):
        return self.sum_cap_arr
    
    def get_SINR(self):
        sinr_arr = np.zeros(self.usr_n)
        head = 0
        for eval_iter in range(len(self.eval_list)):
            eval = self.eval_list[eval_iter]
            usr_n = eval.get_user_n()
            sinr_arr[head:head+usr_n] = eval.get_SINR()
            head += usr_n
        return sinr_arr

    def get_SNR(self):
        snr_arr = np.zeros(self.usr_n)
        head = 0
        for eval_iter in range(len(self.eval_list)):
            eval = self.eval_list[eval_iter]
            usr_n = eval.get_user_n()
            snr_arr[head:head+usr_n] = eval.get_SNR()
            head += usr_n
        return snr_arr

    def get_interference(self):
        intf_arr = np.zeros(self.usr_n)
        head = 0
        for eval_iter in range(len(self.eval_list)):
            eval = self.eval_list[eval_iter]
            usr_n = eval.get_user_n()
            intf_arr[head:head+usr_n] = eval.get_interference()
            head += usr_n
        return intf_arr
    
    def get_signal_pwr(self):
        sig_arr = np.zeros(self.usr_n)
        head = 0
        for eval_iter in range(len(self.eval_list)):
            eval = self.eval_list[eval_iter]
            usr_n = eval.get_user_n()
            sig_arr[head:head+usr_n] = eval.get_signal_pwr()
            head += usr_n
        return sig_arr
    
    def get_noise_pwr(self):
        noise_arr = np.zeros(self.usr_n)
        head = 0
        for eval_iter in range(len(self.eval_list)):
            eval = self.eval_list[eval_iter]
            usr_n = eval.get_user_n()
            noise = eval.get_noise()
            noise_arr[head:head+usr_n] += noise
            head += usr_n
        return noise_arr
    
    def get_h_list(self):
        h_list = []
        for ev in self.eval_list:
            h = ev.get_h()
            h_list.append(h)
        return h_list
    
    def get_w_list(self):
        w_list = []
        for ev in self.eval_list:
            w = ev.get_w()
            w_list.append(w)
        return w_list