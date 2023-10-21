import numpy as np
import save
import utils
from parameters import Parameter as param
import tqdm

class AUSEquipment():
    def __init__(self, ang_arr, usrs_per_group, *args):
        # Angle array without removed users.
        self.ang_arr = ang_arr
        self.usr_n = len(self.ang_arr)
        self.usrs_per_group = usrs_per_group
        self.args = args
        # Removed user array to adjust number of users for grouping.
        self.rm_usr_arr = self.get_removed_user_arr(ang_arr)
        self.rm_usr_n = len(self.rm_usr_arr)
        # closest user information
        self.cls_arr = np.zeros(self.usr_n, dtype=int)-1
        self.cls_ad = np.zeros(self.usr_n)-1
        self.cls_ang_dif_arr = np.zeros([self.usr_n,2])-1
        # Closest user information before removing.
        self.cls_arr_orig = np.zeros(self.usr_n, dtype =int)
        self.usr_orig_iter = np.zeros(self.usr_n-self.rm_usr_n, dtype=int)
        # Set all variable
        self.set_user_original_iterations()


    def calc_ang_dif(self, usr1, usr2):
        usr1_ang = self.ang_arr[usr1]
        usr2_ang = self.ang_arr[usr2]
        ang_dif = utils.calc_ang_dif(usr1_ang, usr2_ang)
        return ang_dif

    def calc_ad_from_ang_dif(self, ang_dif):
        return np.sqrt(np.sum(ang_dif**2))
    
    def calc_ad(self, usr1, usr2):
        ang_dif = self.calc_ang_dif(usr1, usr2)
        return self.calc_ad_from_ang_dif(ang_dif)
        
    def set_cls_ang_dif(self, usr, ang_dif):
        self.cls_ang_dif_arr[usr] = ang_dif
    
    def set_cls_usr_ad(self, usr, ad):
        self.cls_ad[usr] = ad

    def set_cls_usr(self, usr, cls_usr):
        self.cls_arr[usr] = cls_usr

    def set_closest_user_original(self):
        print("[INFO EQPT] Closest user data will be started to calculate.")
        if len(self.args) == 0 or self.args[0] is None:
            ad_table = np.ones([self.usr_n, self.usr_n])*-1
            print("[INFO EQPT] There is no closest user data in input."+
                  " Start calculating ad_table.")
            for usr1 in tqdm.tqdm(range(self.usr_n)):
                for usr2 in range(usr1+1, self.usr_n):
                    try:
                        ad_table[usr1, usr2] = self.calc_ad(usr1, usr2)
                    except IndexError:
                        print(f"{usr1}, {usr2}")
            print("            Start searching minAD of each user.")
            for usr1 in tqdm.tqdm(range(self.usr_n)):
                min_ad = 360
                cls_usr = -1
                for usr2 in range(self.usr_n):
                    if usr1 < usr2:
                        ad = ad_table[usr1, usr2]
                    elif usr1 > usr2:
                        ad = ad_table[usr2, usr1]
                    else:
                        continue
                    if ad < min_ad:
                        min_ad = ad
                        cls_usr = usr2
                self.cls_arr_orig[usr1] = cls_usr
                if cls_usr == -1:
                    raise TypeError
        else:
            self.cls_arr_orig = self.args[0]
    
    def set_user_original_iterations(self):
        left_usr_n = self.usr_n-self.rm_usr_n
        if self.rm_usr_n == 0:
            self.usr_orig_iter = np.arange(self.usr_n,dtype=int)
        else:
            usr_arr = np.arange(left_usr_n, dtype=int)
            self.usr_orig_iter = self.get_usr_iter_origs(usr_arr)
    
    def set_closest_user(self):
        print('[INFO ANGDIF] Starting to set up AUSEquipment class object.')
        recheck_usr_list = []
        for usr in range(self.usr_n):
            if usr in self.rm_usr_arr:
                continue
            elif self.cls_arr_orig[usr] in self.rm_usr_arr:
                recheck_usr_list.append(usr)
        for usr in tqdm.tqdm(range(self.usr_n)):
            if usr in self.rm_usr_arr:
                continue
            if usr in recheck_usr_list:
                min_ad = 360
                min_dif = np.zeros(2)
                cls_usr = -1
                for usr2 in range(self.usr_n):
                    if usr2 in self.rm_usr_arr:
                        continue
                    ang_dif = self.calc_ang_dif(usr, usr2)
                    ad = self.calc_ad_from_ang_dif(ang_dif)
                    if ad < min_ad:
                        min_ad = ad
                        min_dif = ang_dif
                        cls_usr = usr2
            else:
                cls_usr = self.cls_arr_orig[usr]
                min_dif = self.calc_ang_dif(usr, cls_usr)
                min_ad = self.calc_ad_from_ang_dif(min_dif)
            self.cls_arr[usr] = cls_usr
            self.cls_ad[usr] = min_ad
            self.cls_ang_dif_arr[usr] = min_dif                   

    def set_closest_user_all(self, ds_type):
        self.set_closest_user_original()
        self.save_closest_user_arr_original(ds_type)
        self.set_closest_user()

    def get_removed_user_arr(self, ang_arr):
        usr_n = len(ang_arr)
        rm_usr_n = usr_n % self.usrs_per_group
        if rm_usr_n == 0:
            return np.array([])
        group_size = int(usr_n/rm_usr_n)
        rm_usr_arr = np.array([i for i in range(0,usr_n,group_size)])
        return rm_usr_arr

    def get_usr_iter_orig(self, usr):
        usr_orig = usr
        for rm_usr in self.rm_usr_arr:
            if usr_orig < rm_usr:
                break
            usr_orig += 1
        return usr_orig

    def get_usr_iter_origs(self, usr):
        try:
            usr_iter_arr = np.zeros(len(usr), dtype=int)-1
            for usr_idx in range(len(usr_iter_arr)):
                usr_iter_arr[usr_idx] = self.get_usr_iter_orig(usr[usr_idx])
            return usr_iter_arr
        except TypeError:
            print("typeerror")
            return self.get_usr_iter_orig(usr)
    
    def get_usr_n(self):
        return self.usr_n - self.rm_usr_n
    
    def get_ang_all(self):
        if self.rm_usr_n == 0:
            new_ang_arr = self.ang_arr[:,:]
        else:
            new_ang_arr = np.delete(self.ang_arr, self.rm_usr_arr, 0)
        return new_ang_arr
    
    def get_angs(self, usr):
        usr_iter = self.usr_orig_iter[usr]
        return self.ang_arr[usr_iter]
    
    def get_closest_user_arr(self):
        if self.rm_usr_n == 0:
            return self.cls_arr[:]
        new_ang_arr = np.delete(self.cls_arr, self.rm_usr_arr, 0)
        return new_ang_arr

    def get_closest_ad_arr(self):
        if self.rm_usr_n == 0:
            return self.cls_ad[:]
        new_ad_arr = np.delete(self.cls_arr, self.rm_usr_arr, 0)
        return new_ad_arr
    
    def get_closest_ang_dif(self):
        if self.rm_usr_n == 0:
            return self.cls_ang_dif_arr[:,:]
        new_ang_dif_arr = np.delete(self.cls_ang_dif_arr, self.rm_usr_arr, 0)
        return new_ang_dif_arr

    def get_ad(self, usr1, usr2):
        usr_origs = self.usr_orig_iter[np.array([usr1,usr2])]
        ad = self.calc_ad(usr_origs[0], usr_origs[1])
        return ad

    def get_ang_dif(self, usr1, usr2):
        usr_origs = self.usr_orig_iter[np.array([usr1,usr2])]
        ang_dif = self.calc_ang_dif(usr_origs[0], usr_origs[1])
        return ang_dif
    
    def get_users_per_group(self):
        return self.usrs_per_group
    
    def get_closest_user_arr_original(self):
        return self.cls_arr_orig
    
    def save_closest_user_arr_original(self, ds_type):
        save.save_closest_user_arr(self.cls_arr_orig, ds_type)
