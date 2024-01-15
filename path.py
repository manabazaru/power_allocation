import os

def set_cur_dir():
    dir_str = os.path.dirname(__file__)+'/../'
    os.chdir(dir_str)
    new_dir_str = os.getcwd()
    print(f"[INFO PATH] Current directory is changed to {new_dir_str}")