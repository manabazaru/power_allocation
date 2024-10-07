import fig
import load
import path
import utils
import numpy as np
import statistics

path.set_cur_dir()
nu = 12
alg = 'ACUS4'
side_ant = 14
h_type= 'p'
haps_com_r = 20
att_size = 30
blk_n = 50
mode = 'min'
# c_lim_dict = {"5_20":[-50, 20], "14_20":[-10,40], "14_50":[-40,40]}
com_tag = f'_ant={side_ant}_shp={h_type}_nu={nu}_alg={alg}_r={haps_com_r}_attsize={att_size}_240916'
xy_tag = "xy" + com_tag
h_sinr_tag = "h_SINR" + com_tag
b_sinr_tag = "b_SINR" + com_tag
xy_arr = load.load_test_arr(xy_tag)
h_sinr_arr = load.load_test_arr(h_sinr_tag)
b_sinr_arr = load.load_test_arr(b_sinr_tag)
usr_n = len(h_sinr_arr)
h_sorted_sinr_arr = sorted(h_sinr_arr)
boarder_idx = int(len(h_sorted_sinr_arr)/2000)
th_sinr = h_sorted_sinr_arr[boarder_idx-1]

usr_list = []
for usr_idx in range(usr_n):
    if h_sinr_arr[usr_idx] <= th_sinr:
        usr_list.append(usr_idx)

# low_sinr_usr_xy = xy_arr[np.array(usr_list)]
# fig.plt_all_users(low_sinr_usr_xy)


def generate_H_user_SINR_heatmap(side_blk_n, r, sinr_arr, xy_arr, mode):
    blk_idc_arr = utils.get_block_indices_of_heatmap_from_xy_arr(xy_arr, side_blk_n, r)
    usr_n = len(xy_arr)
    mid_sinr_arr = np.zeros([side_blk_n, side_blk_n],dtype=float)
    for y in range(side_blk_n):
        for x in range(side_blk_n):
            print(f"x: {x}, y:{y}")
            sinr_list = []
            for usr_idx in range(usr_n):
                blk_idc = blk_idc_arr[usr_idx]
                if blk_idc[0] == x and blk_idc[1] == y:
                    sinr_list.append(sinr_arr[usr_idx])
            if len(sinr_list) == 0:
                mid_sinr = 10000000
            else:
                sinr_db_arr = np.array(sinr_list)
                sinr_list_arr = 10**(sinr_db_arr/10)
                if mode == 'min':
                    mid_sinr = 10*np.log10(np.min(sinr_list_arr))
                elif mode == 'ave':
                    mid_sinr = 10*np.log10(sum(sinr_list_arr)/len(sinr_list_arr))
                elif mode == 'med':
                    mid_sinr = 10*np.log10(statistics.median(sinr_list_arr))
                elif mode == 'max':
                    mid_sinr = 10*np.log10(np.max(sinr_list_arr))
            mid_sinr_arr[y,x] = mid_sinr
    mini = np.min(mid_sinr_arr)
    mid_sinr_arr[mid_sinr_arr == 10000000] = mini - 10
    fig.SINR_heatmap(r, mid_sinr_arr, "heatmap" + com_tag + f"blk_n={side_blk_n}_mode={mode}", True)



generate_H_user_SINR_heatmap(blk_n, haps_com_r, h_sinr_arr, xy_arr, mode)