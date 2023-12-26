import load
import save
import fig
import fig_properties
import utils
import simulation
import path
import haps
import beamforming
import rand_uni
from parameters import Parameter as param
from us_equipment import AUSEquipment
import numpy as np
from us_equipment import AUSEquipment


def analysis_main():
    # path setting
    path.set_cur_dir()

    #############################################################################################
    # simulation parameters
    r_list = [5, 10, 20]
    nu_list = [i for i in range(10, 200, 10)]
    nu_typ_loop = True
    typ_list = ['random'+str(i*100) for i in nu_list]
    dsidx_size = 2
    shp = 'c'
    t_pwr_list = [120]
    alg_list = ['ACUS3']
    sim_idx_dict = {}
    for alg in alg_list: sim_idx_dict[alg] = 0  
    grp_dict = {}
    grp_n = 100
    for nu in nu_list:
        grp_dict[nu] = grp_n
    DSidx_dict = {'tokyo':[0], 'osaka':[0], 'nagoya':[0], 'sendai':[0]}
    if nu_typ_loop:
        for typ in typ_list:
            DSidx_dict[typ] = [i for i in range(dsidx_size)]
    #############################################################################################
