class Property:
    cities = ['sendai', 'tokyo', 'yagami', 'nagoya', 'osaka']
    main_cities = ['sendai', 'tokyo', 'nagoya', 'osaka']
    # type list of dataset. 'random' is added to cities.
    ds_type_list = ['sendai', 'tokyo', 'yagami', 'nagoya', 'osaka', 'random_uniform']
    # userable algorithm list
    alg_list = ['AUS', 'azimuth_US', 'SMUS', 'AAUS']
    # directory or path for each data
    angle_path = './data/csv/angle/ang_'
    xy_path = './data/csv/xy/xy_'
    cls_usr_path = './data/csv/closest_user/cls_'
    eval_path = './data/csv/eval/ev_'
    fig_path = './data/fig/'
    sinr_path = './data/csv/SINR/sinr_'
    snr_path = './data/csv/SNR/snr_'
    intf_path = './data/csv/interference/intf_'
    minAD_path = './data/csv/minAD/minAD_'
    flop_path = './data/csv/flop/flop_'
    group_path = {'AUS'       : './data/csv/group/AUS/grp_',
                  'azimuth_US': './data/csv/group/azimuth/grp_',
                  'SMUS'      : './data/csv/group/SMUS/grp_',
                  'no_grouping': './data/csv/group/no_grouping/grp_'}    
    mat_path = {'sendai': './data/mat/sendai_20km_scale_0.005_date_20210129.mat',
                'tokyo' : './data/mat/tokyo_20km_scale_0.0005_date_20210129.mat',
                'yagami': './data/mat/yagami_20km_scale_0.0005_date_20210129.mat',
                'nagoya': './data/mat/nagoya_20km_scale_0.005_date_20210129.mat',
                'osaka' : './data/mat/osaka_20km_scale_0.0005_date_20210129.mat'}
    usr_ant_path = {'cylindrical': './data/csv/HAPS/cylindrical/ua_',
                    'planar': './data/csv/HAPS/cylindrical/ua_'}
