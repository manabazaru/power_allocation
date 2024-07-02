class FigProperty:
    # for histogram of angle
    hist_size = [9, 5]
    az_xlim = [-180, 180]
    el_xlim = [45, 90]
    ang_ylim = {'sendai': [0,2000],
                'tokyo': [0,1500],
                'yagami': [0,1500],
                'nagoya': [0,3000],
                'osaka': [0,1500],
                'rand1' : [0,300],
                'rand2' : [0,300]
               }
    # for cumulative figures
    cumulative_figure_size = (7,4)
    marker = ['k-.', 'b--', 'g-', 'r:', 'c-', 'm--', 'y-.', 'r-']
    gbps = 1.0 * 10**9
    x_label = 'Sum Channel Capacities [Gbps]'
    y_label = 'Cumulative Distribution'
    x_lim = [0, 3]
    y_lim = [0, 1]
    x_range = 0.2
    y_range = 0.1
    fontsize = 20
    fontsize2 = 30
    # for SINR cumulative figures
    sinr_x_label = 'SINR [dB]'
    sinr_y_label = 'cumulative distribution'
    sinr_x_lim = [0, 3000]
    sinr_y_lim = [0,1]
    sinr_x_range = 50
    sinr_y_range = 0.1
    # for minAD cumulative figures
    minAD_x_label = 'minAD [°]'
    minAD_y_label = 'cumulative distribution'
    minAD_x_lim = [10, 40]
    minAD_y_lim = [0,1]
    minAD_x_range = 5
    minAD_y_range = 0.1
