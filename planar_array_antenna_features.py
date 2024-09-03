import rand_uni
import haps
import fig
import numpy as np

def calc_gain(ang, t_gain, r_gain):
        az = ang[0]
        el = ang[1]
        v_radiat = -min(12*(el/65)**2, 30)
        h_radiat = -min(12*(az/65)**2, 30)
        radiat = -min(-(v_radiat+h_radiat), 30)
        gain_db = t_gain + radiat + r_gain
        gain = 10**(gain_db/10)
        return gain    


side_ant_n = 5
ant_n = side_ant_n**2
usr_n = 360
usr_xy_arr = rand_uni.generate_equal_interval_usr_xy(usr_n, 10)
phaps = haps.VariableAntennaPlanarHAPS(side_ant_n)
usr_ant_angr = phaps.get_user_antenna_angle_r_arr_from_user_xy_arr(usr_xy_arr)
radiat_ptn = np.zeros([usr_n, ant_n])
print(usr_ant_angr)

for usr in range(usr_n):
    for ant in range(ant_n):
        ang = usr_ant_angr[usr, ant,:2]
        gain = calc_gain(ang, 14, -3)
        radiat_ptn[usr, ant] = gain

ans = np.sqrt(np.sum(radiat_ptn**2, axis=1))
print(ans)



        