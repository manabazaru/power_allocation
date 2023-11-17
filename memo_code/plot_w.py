import matplotlib.pyplot as plt
import numpy as np
w = [37381328.43,
3738254.037,
375040.2545,
51307.46292,
84087.57028,
29544313.6,
81690629125,
9.20972E+13]
h = [4.46208392e-10,
4.46207807e-10,
4.46149349e-10,
4.40351155e-10,
1.41825923e-10,
5.21366705e-15,
5.84315565e-18,
4.59326926e-20]

w = np.log10(w)
h = np.log10(np.array(h)**0.5)

x = ['0.001', '0.01', '0.1', '1', '10', '100','1000', '10000']
fig = plt.figure()
plt.scatter(x, h)
plt.xlabel('distance from center to user')
plt.ylabel('log_10(||h||)')
plt.show()
fig.savefig("C:/Users/manab/Documents/231115/image/fig_4.png")