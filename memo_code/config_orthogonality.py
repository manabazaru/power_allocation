import numpy as np
import numpy.linalg as LA
import matplotlib.pyplot as plt

def config_1():
    row = 196
    col = 196
    att = 1000
    config_arr = np.zeros(50, dtype=int)
    h1 = np.random.rand(col*row).reshape(row, col)
    h2 = np.random.rand(col*row).reshape(row, col) * 1j
    h = h1+h2
    h_herm = np.conjugate(h).T
    hherm = np.dot(h, h_herm)
    h_hherm = np.dot(h_herm, LA.inv(hherm))
    hhhh = np.dot(h, h_hherm)
    print(hhhh)
    abs_hhhh = np.sqrt(hhhh * np.conjugate(hhhh))
    abs_hhhh_arr = abs_hhhh.reshape(row*row)
    for num in abs_hhhh_arr:
        idx = -int((np.log10(num)))
        config_arr[idx] += 1
    print(config_arr)

config_1()

def config_2():
    row = 2
    col = 196
    att = 1000
    orth_det_list = []
    for i in range(att):
        orth_total = 0
        h = np.random.randint(1, 1000, col*row).reshape(row, col) * 10**-7
        for row_idx in range(row):
            total = np.sqrt(sum(h[row_idx]**2))
            h[row_idx] = h[row_idx]/total
        for h1_idx in range(row):
            h1 = h[h1_idx]
            for h2_idx in range(h1_idx+1, row):
                if h1_idx == h2_idx:
                    continue
                h2 = h[h2_idx]
                orth_total += sum(h1*h2)
        calc_size = row * (row-1) / 2
        h_herm = np.conjugate(h).T
        hherm = np.dot(h, h_herm)
        h_hherm = np.dot(h_herm, hherm)
        det = 1/LA.det(hherm)
        orth_det = [orth_total/calc_size, det]
        orth_det_list.append(orth_det)
        print(f'{i}: {orth_det}')

    plt_arr = np.array(orth_det_list)
    fig = plt.figure()
    plt.scatter(plt_arr[:,0], plt_arr[:,1])
    plt.show()
