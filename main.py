import path
import simulation

def main():
    path.set_cur_dir()
    r = 20
    nu = 12
    typ_list = ['random1200','random2400', 'tokyo', 'osaka', 'nagoya', 'sendai']
    shp_list = ['p', 'c']
    DSidx_dict = {'random2400':[i for i in range(10)], 'random1200':[i for i in range(10)], 
                  'tokyo':[0], 'osaka':[0], 'nagoya':[0], 'sendai':[0]}
    t_pwr = 120
    alg_list = ['RUS', 'AUS', 'ACUS3', 'ACUS4', 'ACUS5']
    ds_list = []
    for typ in typ_list:
        for shp in shp_list:
            dsidx_list = DSidx_dict[typ]
            for dsidx in dsidx_list:
                ds = simulation.Dataset(typ, nu, r, shp, dsidx)
                ds_list.append(ds)
    for ds in ds_list:
        for alg in alg_list:
            sim = simulation.Simulation(ds, t_pwr, alg, 0)
            sim.execute_all()


if __name__=='__main__':
    main()