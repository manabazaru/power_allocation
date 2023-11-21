import path
import simulation as sim

def main():
    path.set_cur_dir()
    r = 20
    z = 20
    typ_list = ['sendai', 'tokyo', 'nagoya', 'osaka']
    for typ in typ_list:
        ds = sim.Dataset(typ, )

if __name__=='__main__':
    main()