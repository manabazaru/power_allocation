import path
import simulation
 
def main():
    # settings
    path.set_cur_dir()
    log = simulation.Log()

    #############################################################################################
    # simulation parameters
    r_list = [50, 100]
    nu_list = [i for i in range(6, 36, 6)]
    user_scale = 10000
    typ_list = ['random'+str(i * user_scale) for i in nu_list]
    dsidx_size = 1
    dsidx_head = 0
    shp_list = ['pc']
    t_pwr_list = [150]
    alg_list = ['RUS']
    SIMidx_list = [0]
    DSidx_dict = {'tokyo':[0], 'osaka':[0], 'nagoya':[0], 'sendai':[0]}
    nu_typ_loop = True
    if nu_typ_loop:
        for typ in typ_list:
            DSidx_dict[typ] = [i for i in range(dsidx_head, dsidx_head+dsidx_size)]
    #############################################################################################

    # dataset for random
    ds_list = []
    for i,typ in enumerate(typ_list):
        if nu_typ_loop:
            nu = nu_list[i]
            for shp in shp_list:
                dsidx_list = DSidx_dict[typ]
                for dsidx in dsidx_list:
                    for r in r_list:
                        ds = simulation.Dataset(typ, nu, r, shp, dsidx)
                        ds_list.append(ds)
                        log.add_log_string(ds.string)
        else:
            for nu in nu_list:
                for shp in shp_list:
                    dsidx_list = DSidx_dict[typ]
                    for dsidx in dsidx_list:
                        for r in r_list:
                            ds = simulation.Dataset(typ, nu, r, shp, dsidx)
                            ds_list.append(ds)
                            log.add_log_string(ds.string)

    # simulation
    for ds in ds_list:
        for alg in alg_list:
            for t_pwr in t_pwr_list:
                for simidx in SIMidx_list:
                    sim = simulation.Simulation(ds, t_pwr, alg, simidx)
                    sim.execute_all()
                    log.add_log_string(sim.string)

    # log
    log.save_log()



if __name__=='__main__':
    main()