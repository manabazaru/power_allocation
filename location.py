import numpy as np
from parameters import Parameter as param

def generate_user_xy_in_line(user_n, radius):
    distance = radius / (user_n - 1)
    x = np.arange(user_n, dtype=int)
    y = np.zeros(user_n, dtype=int)
    x = x * distance
    xy = np.array([x,y]).T
    return xy

def generate_user_xy_on_circle(user_n, radius):
    ang_dis = 2 * np.pi / user_n
    ang_arr = np.arange(user_n, dtype=int) * ang_dis
    x = np.cos(ang_arr) * radius
    y = np.sin(ang_arr) * radius
    xy = np.array([x,y]).T
    return xy
