class Property:
    cities = ['sendai', 'tokyo', 'yagami', 'nagoya', 'osaka']
    main_cities = ['sendai', 'tokyo', 'nagoya', 'osaka']
    # type list of dataset. 'random' is added to cities.
    ds_type_list = ['sendai', 'tokyo', 'yagami', 'nagoya', 'osaka', 'random_uniform']
    # directory or path for each data
    angle_path = './data/csv/angle/ang_'
    xy_path = './data/csv/xy/xy_'
    cls_usr_path = './data/csv/closest_user/cls_'
    eval_path = './data/csv/eval/ev_'
    fig_path = './data/fig/'
    sinr_path = './data/csv/SINR/sinr_'
    snr_path = './data/csv/SNR/snr_'
    intf_path = './data/csv/interference/intf_'
    sig_path = './data/csv/signal/sig_'
    noise_path = './data/csv/noise/ns_'
    group_minAD_path = './data/csv/group_minAD/grpmAD_'
    usr_minAD_path = './data/csv/user_minAD/usrmAD_'
    flop_path = './data/csv/flop/flop_'
    group_path = './data/csv/group/grp_'
    usr_ant_path = ['./data/csv/HAPS/azimuth/uaaz_',
                    './data/csv/HAPS/elevation/uael_',
                    './data/csv/HAPS/radius/uar_']
    mat_path = {'sendai_20': './data/mat/sendai_20km_scale_0.005_date_20210129.mat',
                'tokyo_20' : './data/mat/tokyo_20km_scale_0.0005_date_20210129.mat',
                'yagami_20': './data/mat/yagami_20km_scale_0.0005_date_20210129.mat',
                'nagoya_20': './data/mat/nagoya_20km_scale_0.005_date_20210129.mat',
                'osaka_20' : './data/mat/osaka_20km_scale_0.0005_date_20210129.mat'}
