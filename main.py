import path
import simulation

def main():
    # settings
    path.set_cur_dir()
    log = simulation.Log()

    #############################################################################################
    # simulation parameters
    r_list = [20, 50, 100]
    nu_list = [10*i for i in range(2, 20, 2)]
    typ_list = ['tokyo']
    shp_list = ['p', 'c']
    DSidx_dict = {'random2400':[i for i in range(10)], 'random1200':[i for i in range(10)], 
                  'random3600':[i for i in range(10)], 'random4800':[i for i in range(10)],
                  'random6000':[i for i in range(10)], 'random7200':[i for i in range(10)],
                  'tokyo':[0], 'osaka':[0], 'nagoya':[0], 'sendai':[0]}
    t_pwr_list = [120]
    alg_list = ['ACUS3', 'ACUS4', 'ACUS5', 'ACUS6']
    SIMidx_list = [0]
    #############################################################################################

    # dataset
    ds_list = []
    for typ in typ_list:
        for shp in shp_list:
            dsidx_list = DSidx_dict[typ]
            for dsidx in dsidx_list:
                for nu in nu_list:
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