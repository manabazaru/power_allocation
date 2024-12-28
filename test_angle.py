import fig
import load
import path
import utils
import numpy as np
import statistics

path.set_cur_dir()

# setting
haps_com_r = 20
haps_height = 20
blk_n = 160
blk_edge_unit = haps_com_r*2/blk_n

r = 2.5
azi_dif = 6
elev_dif = 4
total_dif = 10
bs_n = 6
mode = "separate" # "separate" or "integrate"
# generate bs xy array and array of each block's center xy
bs_xy_arr = np.array([[r*np.cos(np.pi*2/bs_n*i), r*np.sin(np.pi*2/bs_n*i)] for i in range(bs_n)])
blk_xy_arr = np.zeros([blk_n, blk_n, 2], dtype=float)
for idx in range(blk_n):
    blk_xy_arr[:, idx, 0] = -haps_com_r + blk_edge_unit * (idx+0.5)
    blk_xy_arr[idx, :, 1] = haps_com_r - blk_edge_unit * (idx+0.5)

# generate heatmap of angle (in limited angle: 10, only in haps com_r: 5, out of haps com_r: 0)
heatmap_arr = np.zeros([blk_n, blk_n], dtype=float)
for y_idx in range(blk_n):
    for x_idx in range(blk_n):
        blk_xy = blk_xy_arr[y_idx, x_idx]
        # wether out of com_r or not
        if np.sqrt(np.sum(blk_xy**2)) > haps_com_r:
            heatmap_arr[y_idx, x_idx] = 0
            continue
        val = 5
        for bs_idx in range(bs_n):
            bs_xy = bs_xy_arr[bs_idx]
            xy_dif = bs_xy - blk_xy
            if abs(xy_dif[0]) < blk_edge_unit and abs(xy_dif[1]) < blk_edge_unit:
                val = 20
                print(f"bs place: x={x_idx}, y={y_idx}")
                break
            bs_ang = utils.xy2ang(bs_xy, -haps_height)
            blk_ang = utils.xy2ang(blk_xy, -haps_height)
            ang_dif = bs_ang - blk_ang
            if abs(ang_dif[0]) > 180:
                ang_dif[0] = 360 - abs(ang_dif[0])
            for idx in range(2): ang_dif[idx] = abs(ang_dif[idx])
            if mode is "separate":
                if ang_dif[0] < azi_dif and ang_dif[1] < elev_dif:
                    val = 10
            elif mode is "integrate":
                if np.sqrt(np.sum(ang_dif**2)) < total_dif:
                    val = 10
            if val > 6:
                break
        heatmap_arr[y_idx, x_idx] = val
np.set_printoptions(threshold=blk_n**2)

# generate heatmap
ang_tag = f"azi={azi_dif}_elev={elev_dif}" if mode == "separate" else f"total={total_dif}"
fig.SINR_heatmap(haps_com_r, heatmap_arr, 
                 f"heatmap_angImage_mode=({mode})_{ang_tag}_r={haps_com_r}_bsn={bs_n}_blk={blk_n}",
                 False)


def generate_H_user_SINR_heatmap(side_blk_n, r, sinr_arr, xy_arr, mode):
    blk_idc_arr = utils.get_block_indices_of_heatmap_from_xy_arr(xy_arr, side_blk_n, r)
    usr_n = len(xy_arr)
    print(blk_idc_arr)
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
