class Parameter:
    z = 20
    c = 299792.458   # light speed [km/s]
    # for haps
    side_horizonal_antenna = 31
    side_vertical_antenna = 6
    bottom_antenna = 10
    carrier_freq = 2.5 * 10**9
    antenna_height = 4.4 * 10**-4
    planar_antenna_size_of_side = 14
    distance_ratio_between_planar_antenna = 0.6
    # for beamforming
    distance_unit_correction = {'km':10**3, 'm':1}
    three_bandwidth_angle = 65
    max_attenuation = 30
    side_lobe_attenuation = 30
    trans_gain = 8
    rcv_gain = -3
    # for eval
    noise_figure = 5
    bandwidth = 1.8 * 10**7
    trans_pwr = 120
    noise_power_density = -174
    # for m range
    M = 5
    # for threshold
    threshold_elevation = 10
    threshold_ad = 20
    random_group_n = 2
    random_add_group_n = 2
    threshold = 'el'
    area_n = 9
    area_distance = 2
    sample_user_n = 1200
    city_threshold_ad = {'sendai': [16,20],       # original: 16, 20
                         'tokyo': [19.6, 24.6],   # original: 19.6, 24.5
                         'nagoya': [24.5, 29.5],  # original: 24.5, 29.5
                         'osaka': [18.7, 22]    # original: 18.7, 23.7
                        }